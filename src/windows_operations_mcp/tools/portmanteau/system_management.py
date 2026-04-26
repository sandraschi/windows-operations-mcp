"""
System Management - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_sys":
  winops_sys/info      - OS and hardware information
  winops_sys/health    - Health status (CPU/mem/disk thresholds)
  winops_sys/test_port - TCP connectivity check
"""

import asyncio
import platform
from typing import Annotated, Any

import psutil
from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

_SAMPLE_TIMEOUT = 10.0


def register_system_management(parent_mcp: FastMCP) -> None:
    """Mount atomic system management tools under namespace 'winops_sys'."""
    ns = FastMCP(name="winops_sys")

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def info(
        detailed: Annotated[bool, Field(description="Include boot time, users, and CPU frequency.")] = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Return OS platform, Python version, CPU core count, and total memory.

        ## Return Format
        ```json
        {"success": true, "platform": str, "python": str, "machine": str,
         "cpu_cores": int, "memory_total": int,
         "boot_time": float, "users": [str], "cpu_freq": {...}}  // detailed only
        ```

        ## Examples
            info()
            info(detailed=True)
        """
        data: dict[str, Any] = {
            "success": True,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "memory_total": psutil.virtual_memory().total,
        }
        if detailed:
            freq = psutil.cpu_freq()
            data.update({
                "boot_time": psutil.boot_time(),
                "users": [u.name for u in psutil.users()],
                "cpu_freq": freq._asdict() if freq else None,
            })
        return data

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def health(
        detailed: Annotated[bool, Field(description="Include full disk usage breakdown.")] = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Check system health against CPU/memory/disk thresholds.

        ## Return Format
        ```json
        {
          "success": true,
          "status": "healthy" | "degraded" | "unhealthy",
          "cpu_percent": float, "memory_percent": float, "disk_percent": float,
          "sampling_advice": str  // only when degraded/unhealthy and sampling available
        }
        ```

        ## Examples
            health()
            health(detailed=True)

        Notes:
         - degraded: cpu>70% or mem>80% or disk>85%
         - unhealthy: cpu>90% or mem>90% or disk>95%
        """
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent

        if cpu > 90 or mem > 90 or disk > 95:
            status = "unhealthy"
        elif cpu > 70 or mem > 80 or disk > 85:
            status = "degraded"
        else:
            status = "healthy"

        data: dict[str, Any] = {
            "success": True,
            "status": status,
            "cpu_percent": cpu,
            "memory_percent": mem,
            "disk_percent": disk,
        }

        if detailed:
            data["disk_details"] = psutil.disk_usage("C:\\")._asdict()

        if status != "healthy" and ctx:
            try:
                advice = await asyncio.wait_for(
                    ctx.sample(
                        f"Windows system is {status} (CPU: {cpu}%, MEM: {mem}%, Disk: {disk}%). Suggest 3 quick fixes.",
                        max_tokens=150,
                    ),
                    timeout=_SAMPLE_TIMEOUT,
                )
                if advice and advice.content:
                    data["sampling_advice"] = advice.content[0].text
            except Exception:
                pass

        return data

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)
    )
    async def test_port(
        host: Annotated[str, Field(description="Hostname or IP to connect to.")],
        port: Annotated[int, Field(description="TCP port to test.", ge=1, le=65535)],
        timeout_seconds: Annotated[int, Field(description="Connection timeout.", ge=1, le=30)] = 5,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Test TCP connectivity to a host:port.

        ## Return Format
        ```json
        {"success": true, "host": str, "port": int, "reachable": bool}
        ```

        ## Examples
            test_port(host="8.8.8.8", port=53)
            test_port(host="localhost", port=10800)
        """
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout_seconds
            )
            writer.close()
            await writer.wait_closed()
            reachable = True
        except Exception:
            reachable = False

        return {"success": True, "host": host, "port": port, "reachable": reachable}

    parent_mcp.mount(ns, prefix="winops_sys")
    logger.info("Mounted atomic tools: winops_sys/info, /health, /test_port")
