"""
System Management Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides Windows system diagnostics, health checks, and port testing with telemetry.
"""

import socket
import time
import asyncio
import platform
import psutil
from typing import Any, Dict, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def system_management(
    action: Literal["info", "health", "test_port", "help"],
    detailed: bool = False,
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout_seconds: int = 5,
    category: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform system management operations with comprehensive error handling and agentic telemetry.

    RATIONALE:
    Consolidates system info, health checks, and network connectivity into a single portmanteau.
    Integrates with FastMCP 3.2 Context for real-time progress reporting and LLM-in-the-loop diagnostics.

    Args:
        action: The system operation to perform.
        detailed: Include additional technical details (default: False).
        host: Target hostname for port testing.
        port: Target port for connectivity verification.
        timeout_seconds: Connection timeout (default: 5s).
        category: Help category filter.
        ctx: FastMCP Context for telemetry and sampling (injected).

    Examples:
        - system_management(action="health", detailed=True)
        - system_management(action="test_port", host="8.8.8.8", port=53)
    """
    if ctx:
        ctx.info(f"System Management: {action}")
        ctx.report_progress(10, 100)

    try:
        if action == "info":
            if ctx: ctx.report_progress(50, 100)
            data = {
                "platform": platform.platform(),
                "python": platform.python_version(),
                "machine": platform.machine(),
                "cpu_cores": psutil.cpu_count(logical=False),
                "memory_total": psutil.virtual_memory().total,
            }
            if detailed:
                data.update({
                    "boot_time": psutil.boot_time(),
                    "users": [u.name for u in psutil.users()],
                    "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                })
            return {"success": True, "action": action, "data": data}

        elif action == "health":
            if ctx: ctx.report_progress(30, 100)
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:\\').percent
            
            status = "healthy"
            if cpu > 90 or mem > 90 or disk > 95:
                status = "unhealthy"
            elif cpu > 70 or mem > 80 or disk > 85:
                status = "degraded"
                
            health_data = {
                "status": status,
                "cpu_percent": cpu,
                "memory_percent": mem,
                "disk_percent": disk,
            }
            if detailed:
                health_data["disk_details"] = psutil.disk_usage('C:\\')._asdict()
            
            if status != "healthy" and ctx:
                ctx.warning(f"System status is {status}. Sampling for optimizations...")
                try:
                    advice = await ctx.sample(f"Window system is {status} (CPU: {cpu}%, MEM: {mem}%, Disk: {disk}%). Suggest 3 quick fixes.", max_tokens=150)
                    if advice and advice.content:
                        health_data["sampling_advice"] = advice.content[0].text
                except: pass
                
            return {"success": True, "action": action, "data": health_data}

        elif action == "test_port":
            if not host or not port:
                return {"success": False, "error": "Host and port required for test_port"}
            
            if ctx: ctx.report_progress(50, 100)
            reachable = await _check_port(host, port, timeout_seconds)
            return {
                "success": True, 
                "action": action, 
                "data": {"host": host, "port": port, "reachable": reachable}
            }

        elif action == "help":
            return {"success": True, "action": action, "data": {"categories": ["system", "files", "services", "agentic"]}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"System Management Error: {e}"
        if ctx: ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

async def _check_port(host: str, port: int, timeout: int) -> bool:
    """Async port connectivity check."""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

def register_system_management(mcp) -> None:
    """Register the modernized system management tool."""
    mcp.tool()(system_management)