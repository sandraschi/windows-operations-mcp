"""
Windows Services - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_svc":
  winops_svc/list    - List Windows services
  winops_svc/status  - Query a single service's status
  winops_svc/start   - Start a service
  winops_svc/stop    - Stop a service
  winops_svc/restart - Restart a service
"""

import asyncio
import time
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

try:
    from prefab_ui import Card, Table, Text
    HAS_PREFAB = True
except ImportError:
    HAS_PREFAB = False


def _get_status_str(code: int) -> str:
    try:
        import win32service
        m = {
            win32service.SERVICE_STOPPED: "stopped",
            win32service.SERVICE_START_PENDING: "starting",
            win32service.SERVICE_STOP_PENDING: "stopping",
            win32service.SERVICE_RUNNING: "running",
        }
        return m.get(code, "other")
    except Exception:
        return str(code)


def _list_services_blocking(filter_status: str | None, include_system: bool) -> dict[str, Any]:
    import win32service
    hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
    try:
        status = win32service.EnumServicesStatus(hscm, win32service.SERVICE_WIN32, win32service.SERVICE_STATE_ALL)
        services = []
        for s_name, d_name, s_stat in status:
            cur = _get_status_str(s_stat[1])
            if not include_system and s_name.lower().startswith(("win", "microsoft", "sys")):
                continue
            if filter_status and filter_status != "all" and cur != filter_status:
                continue
            services.append({"name": s_name, "display_name": d_name, "status": cur})
        return {"services": services, "count": len(services)}
    finally:
        win32service.CloseServiceHandle(hscm)


async def _wait_for_status(name: str, target: str, timeout: int, ctx: Context | None) -> dict[str, Any]:
    import win32serviceutil
    start = time.time()
    while time.time() - start < timeout:
        status = await asyncio.to_thread(win32serviceutil.QueryServiceStatus, name)
        cur = _get_status_str(status[1])
        if cur == target:
            return {"name": name, "status": cur}
        await asyncio.sleep(1)
    return {"name": name, "status": "timeout", "error": f"Did not reach '{target}' within {timeout}s"}


def register_windows_services(parent_mcp: FastMCP) -> None:
    """Mount atomic service management tools under namespace 'winops_svc'."""
    ns = FastMCP(name="winops_svc")

    @ns.tool(
        name="list", annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def list_services(
        filter_status: Annotated[str | None, Field(description="Filter by status: running, stopped, or all.")] = None,
        include_system: Annotated[bool, Field(description="Include Windows system services.")] = True,
        ctx: Context | None = None,
    ) -> Any:
        """List Windows services, optionally filtered by status.

        ## Return Format
        ```json
        {"success": true, "services": [{"name": str, "display_name": str, "status": str}], "count": int}
        ```

        ## Examples
            list(filter_status="running")
            list(include_system=False)

        Errors:
         - Returns success=false if pywin32 is not installed.
        """
        try:
            data = await asyncio.to_thread(_list_services_blocking, filter_status, include_system)
            result: dict[str, Any] = {"success": True, **data}

            if HAS_PREFAB and data["services"]:
                from fastmcp.utilities.types import ToolResult
                component = Table(
                    title=f"Windows Services ({data['count']})",
                    columns=["Name", "Display Name", "Status"],
                    rows=[[s["name"], s["display_name"], s["status"]] for s in data["services"]],
                )
                return ToolResult(content=str(result), structured_content=component)

            return result
        except ImportError:
            return {"success": False, "error": "pywin32 not installed",
                    "suggestions": ["Run: uv pip install pywin32"]}

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def status(
        service_name: Annotated[str, Field(description="Windows service name (not display name).")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Query the current status of a Windows service.

        ## Return Format
        ```json
        {"success": bool, "name": str, "status": str}
        ```

        ## Examples
            status(service_name="wuauserv")
        """
        try:
            import win32serviceutil
            raw = await asyncio.to_thread(win32serviceutil.QueryServiceStatus, service_name)
            return {"success": True, "name": service_name, "status": _get_status_str(raw[1])}
        except ImportError:
            return {"success": False, "error": "pywin32 not installed"}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Verify the service name with winops_svc/list."]}

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
    )
    async def start(
        service_name: Annotated[str, Field(description="Windows service name to start.")],
        wait_timeout: Annotated[int, Field(description="Seconds to wait for running state.", ge=5, le=120)] = 30,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Start a Windows service and wait for it to reach running state.

        ## Return Format
        ```json
        {"success": bool, "name": str, "status": str}
        ```

        ## Examples
            start(service_name="wuauserv")
        """
        try:
            import win32serviceutil
            await asyncio.to_thread(win32serviceutil.StartService, service_name)
            result = await _wait_for_status(service_name, "running", wait_timeout, ctx)
            return {"success": "error" not in result, **result}
        except ImportError:
            return {"success": False, "error": "pywin32 not installed"}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Check service name and elevation. Use winops_svc/status to verify."]}

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
    )
    async def stop(
        service_name: Annotated[str, Field(description="Windows service name to stop.")],
        wait_timeout: Annotated[int, Field(description="Seconds to wait for stopped state.", ge=5, le=120)] = 30,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Stop a Windows service and wait for it to reach stopped state.

        ## Return Format
        ```json
        {"success": bool, "name": str, "status": str}
        ```

        ## Examples
            stop(service_name="wuauserv")
        """
        try:
            import win32serviceutil
            await asyncio.to_thread(win32serviceutil.StopService, service_name)
            result = await _wait_for_status(service_name, "stopped", wait_timeout, ctx)
            return {"success": "error" not in result, **result}
        except ImportError:
            return {"success": False, "error": "pywin32 not installed"}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Ensure the service is running. Use winops_svc/status to verify."]}

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
    )
    async def restart(
        service_name: Annotated[str, Field(description="Windows service name to restart.")],
        wait_timeout: Annotated[int, Field(description="Seconds to wait for running state.", ge=5, le=120)] = 30,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Restart a Windows service and wait for running state.

        ## Return Format
        ```json
        {"success": bool, "name": str, "status": str}
        ```

        ## Examples
            restart(service_name="spooler")
        """
        try:
            import win32serviceutil
            await asyncio.to_thread(win32serviceutil.RestartService, service_name)
            result = await _wait_for_status(service_name, "running", wait_timeout, ctx)
            return {"success": "error" not in result, **result}
        except ImportError:
            return {"success": False, "error": "pywin32 not installed"}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Use winops_svc/status to check current state."]}

    parent_mcp.mount(ns, prefix="winops_svc")
    logger.info("Mounted atomic tools: winops_svc/list, /status, /start, /stop, /restart")
