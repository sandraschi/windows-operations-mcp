"""
Process Management - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_process":
  winops_process/list      - List running processes
  winops_process/info      - Detailed info for a single process by PID
  winops_process/resources - System-wide CPU/memory snapshot
  winops_process/kill      - Terminate a process by PID
"""

import asyncio
from datetime import datetime
from typing import Annotated, Any

import psutil
from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)

try:
    from prefab_ui import BarChart, Card, Table

    HAS_PREFAB = True
except ImportError:
    HAS_PREFAB = False


def register_process_management(parent_mcp: FastMCP) -> None:
    """Mount atomic process management tools under namespace 'winops_process'."""
    ns = FastMCP(name="winops_process", mask_error_details=True)

    @ns.tool(
        name="list",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    )
    async def list_processes(
        name_filter: Annotated[str | None, Field(description="Substring filter on process name.")] = None,
        include_system: Annotated[bool, Field(description="Include SYSTEM/LOCAL SERVICE processes.")] = False,
        limit: Annotated[int, Field(description="Max processes to return (1-500).", ge=1, le=500)] = 50,
        ctx: Context | None = None,
    ) -> Any:
        """List running Windows processes with CPU and memory usage.

        ## Return Format
        ```json
        {
          "success": true,
          "processes": [{"pid": int, "name": str, "user": str, "cpu": float, "mem": float}],
          "count": int,
          "has_more": bool
        }
        ```

        ## Examples
            list(name_filter="python", limit=20)
            list(include_system=True, limit=100)

        Notes:
         - Result is bounded by `limit`. If count == limit, has_more may be true.
        """
        if ctx:
            await ctx.report_progress(10, 100)

        procs = []
        for p in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent"]):
            try:
                info = p.info
                name = info.get("name", "")
                user = info.get("username", "") or "unknown"
                if not include_system and user.upper() in ("SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE"):
                    continue
                if name_filter and name_filter.lower() not in name.lower():
                    continue
                procs.append(
                    {
                        "pid": info["pid"],
                        "name": name,
                        "user": user,
                        "cpu": info["cpu_percent"],
                        "mem": round(info["memory_percent"], 2),
                    }
                )
                if len(procs) >= limit:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if ctx:
            await ctx.report_progress(100, 100)

        data: dict[str, Any] = {
            "success": True,
            "processes": procs,
            "count": len(procs),
            "has_more": len(procs) == limit,
        }

        if HAS_PREFAB and procs:
            from fastmcp.utilities.types import ToolResult

            component = Table(
                title=f"Windows Processes ({len(procs)})",
                columns=["PID", "Name", "User", "CPU%", "Mem%"],
                rows=[[p["pid"], p["name"], p["user"], p["cpu"], p["mem"]] for p in procs],
            )
            return ToolResult(content=str(data), structured_content=component)

        return data

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def info(
        pid: Annotated[int, Field(description="Process ID to inspect.")],
        ctx: Context | None = None,
    ) -> Any:
        """Get detailed information for a single process by PID.

        ## Return Format
        ```json
        {
          "success": bool,
          "pid": int, "name": str, "status": str, "started": str,
          "cmdline": [str], "cpu_percent": float, "memory_info": {...}, "num_threads": int
        }
        ```

        ## Examples
            info(pid=1234)

        Errors:
         - Returns success=false with error="Process not found" if PID does not exist.
        """
        try:
            p = psutil.Process(pid)
            data: dict[str, Any] = {
                "success": True,
                "pid": p.pid,
                "name": p.name(),
                "status": p.status(),
                "started": datetime.fromtimestamp(p.create_time()).isoformat(),
                "cmdline": p.cmdline(),
                "cpu_percent": await asyncio.to_thread(p.cpu_percent, 0.1),
                "memory_info": p.memory_info()._asdict(),
                "num_threads": p.num_threads(),
            }

            if HAS_PREFAB:
                from fastmcp.utilities.types import ToolResult

                component = Card(
                    title=f"Process: {data['name']} ({pid})",
                    content=[
                        f"**Status**: {data['status']}",
                        f"**Started**: {data['started']}",
                        f"**CPU**: {data['cpu_percent']}%",
                        f"**Threads**: {data['num_threads']}",
                        f"**Command**: `{' '.join(data['cmdline'])}`",
                    ],
                )
                return ToolResult(content=str(data), structured_content=component)

            return data
        except psutil.NoSuchProcess:
            return fail_response(
                f"Process {pid} not found",
                suggestions=["Verify the PID with winops_process/list first."],
            )

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def resources(
        ctx: Context | None = None,
    ) -> Any:
        """Snapshot system-wide CPU and memory utilisation.

        ## Return Format
        ```json
        {"success": true, "cpu_percent": float, "virtual_memory": {...}}
        ```

        ## Examples
            resources()
        """
        cpu = await asyncio.to_thread(psutil.cpu_percent, 0.1)
        mem = psutil.virtual_memory()
        data: dict[str, Any] = {"success": True, "cpu_percent": cpu, "virtual_memory": mem._asdict()}

        if HAS_PREFAB:
            from fastmcp.utilities.types import ToolResult

            component = BarChart(
                title="System Resource Utilisation",
                data=[{"label": "CPU Usage", "value": cpu}, {"label": "Memory Usage", "value": mem.percent}],
                max_value=100,
                unit="%",
            )
            return ToolResult(content=str(data), structured_content=component)

        return data

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=False)
    )
    async def kill(
        pid: Annotated[int, Field(description="PID of the process to terminate.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Terminate a process by PID (SIGTERM).

        ## Return Format
        ```json
        {"success": bool, "terminated_pid": int}
        ```

        ## Examples
            kill(pid=9876)

        Errors:
         - Returns success=false if process not found or access denied.
        """
        try:
            p = psutil.Process(pid)
            p.terminate()
            return {"success": True, "terminated_pid": pid}
        except psutil.NoSuchProcess:
            return fail_response(
                f"Process {pid} not found",
                suggestions=["Verify the PID with winops_process/list."],
            )
        except psutil.AccessDenied:
            return fail_response(
                f"Access denied terminating PID {pid}",
                suggestions=["Run MCP server as Administrator to kill system processes."],
            )

    parent_mcp.mount(ns, namespace="winops_process")
    logger.info("Mounted atomic tools: winops_process/list, /info, /resources, /kill")
