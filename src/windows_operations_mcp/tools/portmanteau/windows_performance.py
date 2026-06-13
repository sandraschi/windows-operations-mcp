"""
Windows Performance - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_perf":
  winops_perf/system   - System-wide CPU, memory, disk, network snapshot
  winops_perf/process  - Per-process performance for a given PID
"""

import asyncio
from typing import Annotated, Any

import psutil
from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)


def register_windows_performance(parent_mcp: FastMCP) -> None:
    """Mount atomic performance tools under namespace 'winops_perf'."""
    ns = FastMCP(name="winops_perf")

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def system(
        include_network: Annotated[bool, Field(description="Include network I/O counters.")] = True,
        sample_interval: Annotated[float, Field(description="CPU sampling interval in seconds.", ge=0.1, le=5.0)] = 1.0,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Snapshot system-wide CPU (per-core), memory, disk I/O, and optionally network I/O.

        ## Return Format
        ```json
        {
          "success": true,
          "cpu_percent_per_core": [float],
          "memory": {...},
          "disk_io": {...},
          "network_io": {...}  // only if include_network=true
        }
        ```

        ## Examples
            system()
            system(include_network=False, sample_interval=0.5)

        Notes:
         - CPU sampling blocks for sample_interval seconds in a thread pool (not the event loop).
        """
        cpu = await asyncio.to_thread(psutil.cpu_percent, sample_interval, True)
        mem = psutil.virtual_memory()._asdict()
        disk_raw = psutil.disk_io_counters()
        disk = disk_raw._asdict() if disk_raw else {}

        data: dict[str, Any] = {"success": True, "cpu_percent_per_core": cpu, "memory": mem, "disk_io": disk}

        if include_network:
            net_raw = psutil.net_io_counters()
            data["network_io"] = net_raw._asdict() if net_raw else {}

        return data

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def process(
        pid: Annotated[int, Field(description="Process ID to measure.")],
        sample_interval: Annotated[float, Field(description="CPU sampling interval in seconds.", ge=0.1, le=5.0)] = 0.5,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Get CPU, memory, thread count, and I/O counters for a specific process.

        ## Return Format
        ```json
        {
          "success": bool,
          "pid": int, "name": str,
          "cpu_percent": float, "memory_info": {...},
          "num_threads": int, "io_counters": {...}
        }
        ```

        ## Examples
            process(pid=1234)

        Errors:
         - Returns success=false with error if PID does not exist.
        """
        try:
            p = psutil.Process(pid)
            with p.oneshot():
                cpu = await asyncio.to_thread(p.cpu_percent, sample_interval)
                return {
                    "success": True,
                    "pid": pid,
                    "name": p.name(),
                    "cpu_percent": cpu,
                    "memory_info": p.memory_info()._asdict(),
                    "num_threads": p.num_threads(),
                    "io_counters": p.io_counters()._asdict() if hasattr(p, "io_counters") else None,
                }
        except psutil.NoSuchProcess:
            return fail_response(f"Process {pid} not found", suggestions=["Verify PID with winops_process/list."])

    parent_mcp.mount(ns, prefix="winops_perf")
    logger.info("Mounted atomic tools: winops_perf/system, winops_perf/process")
