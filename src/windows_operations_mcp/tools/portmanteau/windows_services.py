"""
Windows Services Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows service management with agentic telemetry.
"""

import time
import asyncio
from typing import Any, Dict, List, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def windows_services(
    action: Literal["list", "start", "stop", "restart", "status"],
    service_name: Optional[str] = None,
    filter_status: Optional[str] = None,
    include_system_services: bool = True,
    wait_timeout: int = 30,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform Windows service operations with comprehensive error handling and agentic telemetry.

    RATIONALE:
    Consolidates lifecycle management (Start, Stop, Restart) into a single async portmanteau.
    Uses asyncio.to_thread for blocking pywin32 calls to maintain MCP responsiveness.

    Args:
        action: The service operation to perform.
        service_name: Name of the target service (required for control ops).
        filter_status: Filter by status ("running", "stopped", "all").
        include_system_services: Include Windows/System/Microsoft services in listings.
        wait_timeout: Timeout for state transitions (default 30s).
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Service Op: {action} on {service_name or 'ALL'}")
        ctx.report_progress(10, 100)

    try:
        import win32service
        import win32serviceutil

        if action == "list":
            return await asyncio.to_thread(_list_services, filter_status, include_system_services, ctx)

        if not service_name:
             return {"success": False, "error": f"service_name required for {action}"}

        if action == "status":
            status = await asyncio.to_thread(win32serviceutil.QueryServiceStatus, service_name)
            return {"success": True, "action": action, "data": {"name": service_name, "status": _get_status_str(status[1])}}

        if action == "start":
            if ctx: ctx.info(f"Starting {service_name}...")
            await asyncio.to_thread(win32serviceutil.StartService, service_name)
            return await _wait_for_status(service_name, "running", wait_timeout, ctx)

        if action == "stop":
            if ctx: ctx.info(f"Stopping {service_name}...")
            await asyncio.to_thread(win32serviceutil.StopService, service_name)
            return await _wait_for_status(service_name, "stopped", wait_timeout, ctx)

        if action == "restart":
            if ctx: ctx.info(f"Restarting {service_name}...")
            await asyncio.to_thread(win32serviceutil.RestartService, service_name)
            return await _wait_for_status(service_name, "running", wait_timeout, ctx)

        return {"success": False, "error": f"Unknown action: {action}"}

    except ImportError:
        return {"success": False, "error": "pywin32 not installed on this system"}
    except Exception as e:
        error_msg = f"Service Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(f"Windows service '{service_name}' failed {action}. Error: {e}. Analyze and suggest fix.", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except: pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

def _list_services(filter_status, include_system_services, ctx):
    """Blocking list implementation."""
    import win32service
    hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
    try:
        status = win32service.EnumServicesStatus(hscm, win32service.SERVICE_WIN32, win32service.SERVICE_STATE_ALL)
        services = []
        for svc in status:
            s_name, d_name, s_stat = svc
            cur_stat = _get_status_str(s_stat[1])
            if not include_system_services and s_name.lower().startswith(("win", "microsoft", "sys")):
                continue
            if filter_status and filter_status != "all" and cur_stat != filter_status:
                continue
            services.append({"name": s_name, "display_name": d_name, "status": cur_stat})
        return {"success": True, "action": "list", "data": {"services": services, "count": len(services)}}
    finally:
        win32service.CloseServiceHandle(hscm)

async def _wait_for_status(name, target, timeout, ctx):
    """Async wait for status transition."""
    import win32serviceutil
    start = time.time()
    while time.time() - start < timeout:
        status = await asyncio.to_thread(win32serviceutil.QueryServiceStatus, name)
        cur = _get_status_str(status[1])
        if cur == target:
            return {"success": True, "action": "wait", "data": {"name": name, "status": cur}}
        await asyncio.sleep(1)
    return {"success": False, "error": f"Timeout waiting for {target}"}

def _get_status_str(code):
    import win32service
    m = {
        win32service.SERVICE_STOPPED: "stopped",
        win32service.SERVICE_START_PENDING: "starting",
        win32service.SERVICE_STOP_PENDING: "stopping",
        win32service.SERVICE_RUNNING: "running",
    }
    return m.get(code, "other")

def register_windows_services(mcp) -> None:
    """Register the modernized Windows services tool."""
    mcp.tool()(windows_services)