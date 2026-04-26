"""
Windows Event Logs - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_evtlog":
  winops_evtlog/query  - Query recent events from a log channel
  winops_evtlog/list   - List available log channels
  winops_evtlog/export - Export a log channel to .evtx file
  winops_evtlog/clear  - Clear a log channel
"""

import asyncio
from datetime import datetime, timedelta
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def _wevtutil(*args: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        "wevtutil.exe", *args,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode(errors="replace").strip())
    return stdout.decode(errors="replace").strip()


def _query_events_blocking(log_name: str, max_events: int, hours: int, event_id: int | None) -> list[dict]:
    import win32evtlog
    handle = win32evtlog.OpenEventLog(None, log_name)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    cutoff = datetime.now() - timedelta(hours=hours)
    level_map = {1: "Error", 2: "Warning", 4: "Info", 8: "AuditSuccess", 16: "AuditFailure"}
    events = []
    try:
        while len(events) < max_events:
            batch = win32evtlog.ReadEventLog(handle, flags, 0)
            if not batch:
                break
            for ev in batch:
                ev_time = datetime.fromtimestamp(ev.TimeGenerated)
                if ev_time < cutoff:
                    continue
                if event_id and ev.EventID != event_id:
                    continue
                events.append({
                    "timestamp": ev_time.isoformat(),
                    "id": ev.EventID,
                    "source": ev.SourceName,
                    "level": level_map.get(ev.EventType, "Other"),
                    "message": ev.StringInserts[0] if ev.StringInserts else "",
                })
                if len(events) >= max_events:
                    break
    finally:
        win32evtlog.CloseEventLog(handle)
    return events


def register_windows_event_logs(parent_mcp: FastMCP) -> None:
    """Mount atomic event log tools under namespace 'winops_evtlog'."""
    ns = FastMCP(name="winops_evtlog")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def query(
        log_name: Annotated[str, Field(description="Log channel name (Application, System, Security, etc.).")] = "Application",
        max_events: Annotated[int, Field(description="Max events to return (1-500).", ge=1, le=500)] = 50,
        time_range_hours: Annotated[int, Field(description="Lookback window in hours.", ge=1, le=720)] = 24,
        event_id: Annotated[int | None, Field(description="Filter by specific Event ID.")] = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Query recent events from a Windows Event Log channel.

        ## Return Format
        ```json
        {
          "success": bool,
          "log_name": str,
          "events": [{"timestamp": str, "id": int, "source": str, "level": str, "message": str}],
          "count": int,
          "has_more": bool
        }
        ```

        ## Examples
            query(log_name="System", max_events=20, time_range_hours=1)
            query(log_name="Application", event_id=1000)

        Errors:
         - Returns success=false if pywin32 is not installed or log_name is invalid.
        """
        try:
            events = await asyncio.to_thread(_query_events_blocking, log_name, max_events, time_range_hours, event_id)
            return {"success": True, "log_name": log_name, "events": events,
                    "count": len(events), "has_more": len(events) == max_events}
        except ImportError:
            return {"success": False, "error": "pywin32 not installed",
                    "suggestions": ["Run: uv pip install pywin32"]}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Use winops_evtlog/list to see available log channels."]}

    @ns.tool(name="list", annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def list_channels(ctx: Context | None = None) -> dict[str, Any]:
        """List all available Windows Event Log channels.

        ## Return Format
        ```json
        {"success": bool, "channels": [str], "count": int}
        ```

        ## Examples
            list()
        """
        try:
            raw = await _wevtutil("el")
            channels = raw.splitlines()
            return {"success": True, "channels": channels, "count": len(channels)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def export(
        log_name: Annotated[str, Field(description="Log channel to export.")],
        output_path: Annotated[str, Field(description="Destination .evtx file path.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Export a Windows Event Log channel to an .evtx file.

        ## Return Format
        ```json
        {"success": bool, "log_name": str, "output_path": str}
        ```

        ## Examples
            export(log_name="System", output_path="D:\\\\logs\\\\system.evtx")
        """
        try:
            await _wevtutil("epl", log_name, output_path)
            return {"success": True, "log_name": log_name, "output_path": output_path}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Ensure output directory exists and you have write permission."]}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False))
    async def clear(
        log_name: Annotated[str, Field(description="Log channel to clear.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Clear all events from a Windows Event Log channel. Requires Administrator.

        ## Return Format
        ```json
        {"success": bool, "cleared_log": str}
        ```

        ## Examples
            clear(log_name="Application")
        """
        try:
            import win32evtlog
            await asyncio.to_thread(win32evtlog.ClearEventLog, None, log_name)
            return {"success": True, "cleared_log": log_name}
        except ImportError:
            return {"success": False, "error": "pywin32 not installed"}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Run as Administrator to clear Security log."]}

    parent_mcp.mount(ns, prefix="winops_evtlog")
    logger.info("Mounted atomic tools: winops_evtlog/query, /list, /export, /clear")
