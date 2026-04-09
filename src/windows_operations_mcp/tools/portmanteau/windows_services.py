import time
import json
import asyncio
from typing import Any, Dict, List, Literal, Optional, Union

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

try:
    from prefab_ui import Table, Text, Card
    HAS_PREFAB = True
except ImportError:
    HAS_PREFAB = False

logger = get_logger(__name__)

async def windows_services(
    action: Literal["list", "start", "stop", "restart", "status"],
    service_name: Optional[str] = None,
    filter_status: Optional[str] = None,
    include_system_services: bool = True,
    wait_timeout: int = 30,
    ctx: Optional[Context] = None,
) -> Any:
    """
    Perform Windows service operations with comprehensive error handling and agentic telemetry.
    Returns: Union[Dict, ToolResult] depending on action and availability of prefab-ui.
    """
    if ctx:
        ctx.info(f"Service Op: {action} on {service_name or 'ALL'}")
        ctx.report_progress(10, 100)

    try:
        import win32service
        import win32serviceutil

        data = {}
        component = None

        if action == "list":
            res = await asyncio.to_thread(_list_services, filter_status, include_system_services, ctx)
            data = res["data"]
            if HAS_PREFAB and data["services"]:
                component = Table(
                    title=f"Windows Services ({len(data['services'])})",
                    columns=["Name", "Display Name", "Status"],
                    rows=[[s["name"], s["display_name"], s["status"]] for s in data["services"]]
                )

        elif not service_name:
             return {"success": False, "error": f"service_name required for {action}"}

        elif action == "status":
            status = await asyncio.to_thread(win32serviceutil.QueryServiceStatus, service_name)
            stat_str = _get_status_str(status[1])
            data = {"name": service_name, "status": stat_str}
            if HAS_PREFAB:
                component = Card(
                    title=f"Service Status: {service_name}",
                    content=[f"**Current State**: {stat_str}"]
                )

        elif action in ["start", "stop", "restart"]:
            if ctx: ctx.info(f"Executing {action} on {service_name}...")
            if action == "start":
                await asyncio.to_thread(win32serviceutil.StartService, service_name)
            elif action == "stop":
                await asyncio.to_thread(win32serviceutil.StopService, service_name)
            elif action == "restart":
                await asyncio.to_thread(win32serviceutil.RestartService, service_name)
            
            res = await _wait_for_status(service_name, "running" if action != "stop" else "stopped", wait_timeout, ctx)
            data = res.get("data", {})
            if HAS_PREFAB:
                component = Text(text=f"✅ Service {service_name} {action}ed successfully.")

        if HAS_PREFAB and component:
            return [
                Text(text=json.dumps({"success": True, "action": action, "data": data}, indent=2)),
                component
            ]

        return {"success": True, "action": action, "data": data}

    except ImportError:
        return {"success": False, "error": "pywin32 not installed on this system"}
    except Exception as e:
        error_msg = f"Service Error: {e}"
        if ctx: ctx.error(error_msg)
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