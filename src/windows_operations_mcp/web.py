import asyncio
import csv
import io
import json
import logging
import platform
import threading
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
import psutil
from fastapi import Body, Depends, FastAPI, HTTPException, Response
from fastmcp import FastMCP

from .ai import AIRouter

_RING_CAPACITY = 5000


class _RingBufferHandler(logging.Handler):
    """In-memory log ring buffer backing GET /api/logs."""

    def __init__(self, capacity: int = _RING_CAPACITY) -> None:
        super().__init__()
        self._buffer: deque[dict] = deque(maxlen=capacity)
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = {
                "id": str(uuid4()),
                "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
                "level": record.levelname,
                "kind": "tool_call" if "tool" in (record.name or "").lower() else "server",
                "detail": record.getMessage(),
                "meta": {"logger": record.name},
            }
            with self._lock:
                self._buffer.append(entry)
        except Exception:
            pass

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()


_ring = _RingBufferHandler()
logging.getLogger().addHandler(_ring)

# httpx/httpcore log every request at INFO — pure noise in console + ring buffer
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def _query_logs(
    limit: int,
    offset: int,
    level: str,
    kind: str,
    search: str,
    sort: str,
    after_id: str | None,
) -> tuple[list[dict], int]:
    with _ring._lock:
        entries = list(_ring._buffer)
    if level:
        entries = [e for e in entries if e["level"] == level.upper()]
    if kind:
        entries = [e for e in entries if e["kind"] == kind]
    if search:
        needle = search.lower()
        entries = [e for e in entries if needle in e["detail"].lower()]
    entries.sort(key=lambda e: e["timestamp"], reverse=(sort != "asc"))
    if after_id:
        try:
            idx = next(i for i, e in enumerate(entries) if e["id"] == after_id)
            entries = entries[:idx]
        except StopIteration:
            pass
    total = len(entries)
    return entries[offset : offset + limit], total


async def _probe_llm_provider(key: str, url: str, container: str, field: str) -> tuple[str, list[dict]]:
    models: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(url)
            if r.status_code == 200:
                payload = r.json()
                items = payload.get(container) or []
                models = [{"name": m.get(field)} for m in items if m.get(field)]
    except Exception:
        pass
    return key, models


async def authenticate():
    """Simple standard authentication dependency placeholder."""
    return "sandra"


def setup_webapp(app: FastAPI, mcp_app: FastMCP):
    """Setup standard SOTA web endpoints for Windows Operations Hub."""
    ai_router = AIRouter(mcp_app)

    @app.get("/health")
    @app.get("/api/health")
    async def health_check():
        """Standard SOTA health check."""
        return {
            "status": "healthy",
            "service": "windows-operations-mcp",
            "version": "14.2.0",
            "platform": platform.system(),
        }

    @app.get("/api/status")
    async def get_status(user: str = Depends(authenticate)):
        return {
            "status": "connected",
            "user": user,
            "mcp": mcp_app.name,
            "platform": platform.system(),
            "release": platform.release(),
            "python_version": platform.python_version(),
            "host": platform.node(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
        }

    @app.get("/api/system-stats")
    async def get_system_stats(user: str = Depends(authenticate)):
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage("C:\\")._asdict(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/processes")
    async def get_processes(user: str = Depends(authenticate), limit: int = 10, search: str = ""):
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                # Some processes might terminate during iteration
                info = p.info
                if info["cpu_percent"] is None:
                    info["cpu_percent"] = 0.0
                if info["memory_percent"] is None:
                    info["memory_percent"] = 0.0
                procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        if search:
            needle = search.lower()
            procs = [p for p in procs if needle in p["name"].lower()]

        # Sort by CPU usage and take top N (default 10, cap 500)
        sorted_procs = sorted(procs, key=lambda x: x["cpu_percent"], reverse=True)[
            : min(max(limit, 1), 500)
        ]
        return {"processes": sorted_procs, "count": len(sorted_procs), "total": len(procs)}

    @app.delete("/api/processes/{pid}")
    async def kill_process(pid: int, _user: str = Depends(authenticate)):
        """Terminate a process by PID."""

        def _kill() -> str:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=5)
            return proc.status()

        try:
            status = await asyncio.to_thread(_kill)
        except psutil.NoSuchProcess:
            raise HTTPException(status_code=404, detail=f"Process {pid} not found")
        except psutil.AccessDenied:
            raise HTTPException(status_code=403, detail=f"Access denied terminating process {pid}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return {"success": True, "pid": pid, "status": status}

    @app.get("/api/services")
    async def get_services(
        _user: str = Depends(authenticate),
        filter_status: str = "",
        include_system: bool = True,
    ):
        """List Windows services (reuses the winops_svc portmanteau helper)."""
        from windows_operations_mcp.tools.portmanteau.windows_services import _list_services_blocking

        try:
            data = await asyncio.to_thread(
                _list_services_blocking, filter_status or None, include_system
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"pywin32 unavailable: {e}")
        return {"success": True, **data}

    @app.post("/api/services/{name}/action")
    async def service_action(
        name: str, action: str = Body(..., embed=True), _user: str = Depends(authenticate)
    ):
        """Start, stop, or restart a Windows service by name."""
        if action not in ("start", "stop", "restart"):
            raise HTTPException(status_code=400, detail=f"Unknown action '{action}'")
        import win32serviceutil

        from windows_operations_mcp.tools.portmanteau.windows_services import _get_status_str

        def _run() -> str:
            if action == "start":
                win32serviceutil.StartService(name)
            elif action == "stop":
                win32serviceutil.StopService(name)
            else:
                win32serviceutil.RestartService(name)
            return _get_status_str(win32serviceutil.QueryServiceStatus(name)[1])

        try:
            status = await asyncio.to_thread(_run)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{action} failed for '{name}': {e}")
        return {"success": True, "name": name, "action": action, "status": status}

    @app.get("/api/eventlogs/channels")
    async def eventlog_channels(_user: str = Depends(authenticate)):
        """List available Windows Event Log channels (wevtutil el)."""
        from windows_operations_mcp.tools.portmanteau.windows_event_logs import _wevtutil

        try:
            out = await _wevtutil("el")
            channels = [line.strip() for line in out.splitlines() if line.strip()]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"wevtutil failed: {e}")
        return {"channels": channels, "count": len(channels)}

    @app.get("/api/eventlogs")
    async def get_eventlogs(
        _user: str = Depends(authenticate),
        channel: str = "System",
        limit: int = 50,
        hours: int = 24,
        event_id: int | None = None,
    ):
        """Query recent events from a Windows Event Log channel."""
        from windows_operations_mcp.tools.portmanteau.windows_event_logs import _query_events_blocking

        try:
            events = await asyncio.to_thread(
                _query_events_blocking,
                channel,
                min(max(limit, 1), 500),
                min(max(hours, 1), 720),
                event_id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Event log query failed: {e}")
        return {"log_name": channel, "events": events, "count": len(events), "has_more": len(events) >= limit}

    @app.get("/api/skills")
    async def list_skills():
        """List available skills from the skills directory."""
        skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
        results = []
        if skills_dir.is_dir():
            for d in skills_dir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists():
                    results.append(
                        {
                            "name": d.name,
                            "description": (d / "SKILL.md").read_text(encoding="utf-8")[:200],
                        }
                    )
        if not results:
            results = [
                {
                    "name": "windows-expert",
                    "description": "Windows system administration, registry, services, accounts, event logs, networking, permissions, automation, and performance monitoring.",
                },
            ]
        return results

    @app.get("/api/tools")
    async def list_tools(_user: str = Depends(authenticate)):
        tools = await ai_router.get_tools_list()
        return {"tools": tools}

    @app.get("/api/workflows")
    async def list_workflows(_user: str = Depends(authenticate)):
        workflows = await ai_router.get_workflows_list()
        return {"workflows": workflows}

    @app.post("/api/chat")
    async def chat(query: str = Body(..., embed=True), user: str = Depends(authenticate)):
        try:
            response = await ai_router.process_command(query)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/llm/providers")
    async def llm_providers():
        """Probe local LLM providers (Ollama, LM Studio) and list available models."""
        probes = [
            ("ollama", "http://127.0.0.1:11434/api/tags", "models", "name"),
            ("lm_studio", "http://127.0.0.1:1234/v1/models", "data", "id"),
        ]
        results = await asyncio.gather(
            *[_probe_llm_provider(k, u, c, f) for k, u, c, f in probes]
        )
        return {key: models for key, models in results}

    @app.get("/api/logs")
    async def get_logs(
        limit: int = 50,
        offset: int = 0,
        level: str = "",
        kind: str = "",
        search: str = "",
        sort: str = "desc",
        after_id: str | None = None,
    ):
        """Query the in-memory log ring buffer (paginated, filterable)."""
        bounded = min(max(limit, 1), 500)
        entries, total = _query_logs(bounded, max(offset, 0), level, kind, search, sort, after_id)
        return {"entries": entries, "total": total}

    @app.get("/api/logs/export")
    async def export_logs(format: str = "json", level: str = "", kind: str = "", search: str = ""):
        """Export the log ring buffer as JSON or CSV."""
        entries, _ = _query_logs(_RING_CAPACITY, 0, level, kind, search, "desc", None)
        if format == "csv":
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["timestamp", "level", "kind", "detail"])
            for e in entries:
                writer.writerow([e["timestamp"], e["level"], e["kind"], e["detail"]])
            return Response(
                buf.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="logs.csv"'},
            )
        return Response(
            json.dumps(entries, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="logs.json"'},
        )

    @app.delete("/api/logs")
    async def clear_logs():
        """Clear the in-memory log ring buffer."""
        _ring.clear()
        return {"cleared": True}
