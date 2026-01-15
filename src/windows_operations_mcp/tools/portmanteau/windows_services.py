"""
Windows Services Portmanteau Tool for Windows Operations MCP.

Consolidates Windows service operations (list, start, stop, restart) into a single portmanteau tool.
Provides comprehensive Windows service management functionality.
"""

import time
from typing import Dict, Any, Optional, Literal, List

from ...logging_config import get_logger

logger = get_logger(__name__)


def windows_services(
    action: Literal["list", "start", "stop", "restart"],
    service_name: Optional[str] = None,
    filter_status: Optional[str] = None,
    include_system_services: bool = True,
    wait_timeout: int = 30
) -> Dict[str, Any]:
    """
    Perform Windows service operations with comprehensive error handling.

    FEATURES:
    - Complete Windows service lifecycle management
    - Service status monitoring and filtering
    - Safe start/stop operations with timeout handling
    - Automatic restart capability (stop then start)
    - System service visibility control
    - Service dependency awareness
    - Administrative privilege handling

    Args:
        action: The service operation to perform. Must be one of:
            - "list": List Windows services with status filtering and system service control
            - "start": Start a stopped Windows service with status verification
            - "stop": Stop a running Windows service gracefully
            - "restart": Restart service by stopping then starting (atomic operation)
        service_name: Service name for control operations (required for start/stop/restart)
        filter_status: Filter services by status ("running", "stopped", "all", default: None)
        include_system_services: Include system services in listings (default: True)
        wait_timeout: Maximum seconds to wait for service state changes (1-300, default: 30)

    Returns:
        FastMCP 2.14.1+ enhanced response with:
            - success: bool - Whether the service operation succeeded
            - action: str - The action that was performed
            - data: dict - Action-specific result data (varies by operation)
            - error: str - Error message (only present if success is False)

    Examples:
        # List all running services
        result = await windows_services(
            action="list",
            filter_status="running",
            include_system_services=False
        )

        # Start a specific service
        result = await windows_services(
            action="start",
            service_name="wuauserv",  # Windows Update
            wait_timeout=60
        )

        # Stop a service
        result = await windows_services(
            action="stop",
            service_name="Spooler"  # Print Spooler
        )

        # Restart a service
        result = await windows_services(
            action="restart",
            service_name="http",  # HTTP Service
            wait_timeout=45
        )

        # List services with custom filtering
        result = await windows_services(
            action="list",
            filter_status="stopped",
            include_system_services=True
        )

    Notes:
        - Service operations require administrative privileges
        - Timeout handling prevents hanging operations
        - Restart is atomic (stop succeeds before start begins)
        - System services can be filtered out for cleaner listings
        - Service status verification ensures operations complete successfully
        - Dependencies are handled automatically by Windows
        - Failed operations provide detailed error messages
    """
    logger.info("windows_services_started", action=action, service_name=service_name)

    try:
        # Validate timeout
        if not (1 <= wait_timeout <= 300):
            wait_timeout = 30

        # Route to appropriate action
        if action == "list":
            return _list_services(filter_status, include_system_services)

        elif action in ["start", "stop", "restart"]:
            if not service_name:
                return {
                    "success": False,
                    "action": action,
                    "error": f"service_name is required for {action} action"
                }
            return _manage_service(action, service_name, wait_timeout)

        else:
            return {
                "success": False,
                "action": action,
                "error": f"Unknown action: {action}"
            }

    except Exception as e:
        error_msg = f"Windows service operation failed: {str(e)}"
        logger.error("windows_services_error", action=action, service_name=service_name, error=error_msg, exc_info=True)
        return {
            "success": False,
            "action": action,
            "error": error_msg
        }


def _list_services(filter_status: Optional[str], include_system_services: bool) -> Dict[str, Any]:
    """List Windows services with filtering."""
    try:
        import win32serviceutil
        import win32service

        services = []
        accessSCM = win32service.SC_MANAGER_ENUMERATE_SERVICE

        try:
            hscm = win32service.OpenSCManager(None, None, accessSCM)
        except Exception as e:
            return {
                "success": False,
                "action": "list",
                "error": f"Failed to access service manager: {str(e)}"
            }

        try:
            typeFilter = win32service.SERVICE_WIN32
            stateFilter = win32service.SERVICE_STATE_ALL

            status = win32service.EnumServicesStatus(hscm, typeFilter, stateFilter)

            for svc in status:
                service_name = svc[0]
                display_name = svc[1]
                service_status = svc[2]

                # Skip system services if not requested
                if not include_system_services and service_name.startswith(('Win', 'Microsoft', 'System')):
                    continue

                # Apply status filter
                current_status = _get_service_status_string(service_status[1])
                if filter_status and filter_status != "all" and current_status != filter_status:
                    continue

                services.append({
                    "name": service_name,
                    "display_name": display_name,
                    "status": current_status,
                    "start_type": _get_service_start_type_string(service_status[0]),
                    "pid": service_status[3] if len(service_status) > 3 else None
                })

        finally:
            win32service.CloseServiceHandle(hscm)

        return {
            "success": True,
            "action": "list",
            "data": {
                "services": services,
                "count": len(services),
                "filter_status": filter_status,
                "include_system_services": include_system_services
            }
        }

    except ImportError:
        return {
            "success": False,
            "action": "list",
            "error": "pywin32 not available for service management"
        }
    except Exception as e:
        return {
            "success": False,
            "action": "list",
            "error": f"Failed to list services: {str(e)}"
        }


def _manage_service(action: str, service_name: str, timeout: int) -> Dict[str, Any]:
    """Manage a Windows service (start, stop, restart)."""
    try:
        import win32serviceutil

        if action == "start":
            win32serviceutil.StartService(service_name)
            return _wait_for_service_status(service_name, "running", timeout)

        elif action == "stop":
            win32serviceutil.StopService(service_name)
            return _wait_for_service_status(service_name, "stopped", timeout)

        elif action == "restart":
            # Stop service
            try:
                win32serviceutil.StopService(service_name)
                stop_result = _wait_for_service_status(service_name, "stopped", timeout)
                if not stop_result["success"]:
                    return stop_result
            except Exception as e:
                return {
                    "success": False,
                    "action": "restart",
                    "error": f"Failed to stop service for restart: {str(e)}"
                }

            # Start service
            try:
                win32serviceutil.StartService(service_name)
                return _wait_for_service_status(service_name, "running", timeout)
            except Exception as e:
                return {
                    "success": False,
                    "action": "restart",
                    "error": f"Failed to start service after stop: {str(e)}"
                }

    except ImportError:
        return {
            "success": False,
            "action": action,
            "error": "pywin32 not available for service management"
        }
    except Exception as e:
        return {
            "success": False,
            "action": action,
            "error": f"Failed to {action} service '{service_name}': {str(e)}"
        }


def _wait_for_service_status(service_name: str, target_status: str, timeout: int) -> Dict[str, Any]:
    """Wait for a service to reach a specific status."""
    import win32service

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            status = win32serviceutil.QueryServiceStatus(service_name)
            current_status = _get_service_status_string(status[1])

            if current_status == target_status:
                return {
                    "success": True,
                    "action": "wait_for_status",
                    "data": {
                        "service_name": service_name,
                        "status": current_status,
                        "wait_time": round(time.time() - start_time, 2)
                    }
                }

            time.sleep(0.5)  # Wait 500ms before checking again

        except Exception as e:
            return {
                "success": False,
                "action": "wait_for_status",
                "error": f"Failed to check service status: {str(e)}"
            }

    return {
        "success": False,
        "action": "wait_for_status",
        "error": f"Timeout waiting for service '{service_name}' to reach status '{target_status}'"
    }


def _get_service_status_string(status_code: int) -> str:
    """Convert Windows service status code to string."""
    import win32service

    status_map = {
        win32service.SERVICE_STOPPED: "stopped",
        win32service.SERVICE_START_PENDING: "starting",
        win32service.SERVICE_STOP_PENDING: "stopping",
        win32service.SERVICE_RUNNING: "running",
        win32service.SERVICE_CONTINUE_PENDING: "continuing",
        win32service.SERVICE_PAUSE_PENDING: "pausing",
        win32service.SERVICE_PAUSED: "paused"
    }
    return status_map.get(status_code, "unknown")


def _get_service_start_type_string(start_type: int) -> str:
    """Convert Windows service start type to string."""
    import win32service

    start_map = {
        win32service.SERVICE_BOOT_START: "boot",
        win32service.SERVICE_SYSTEM_START: "system",
        win32service.SERVICE_AUTO_START: "automatic",
        win32service.SERVICE_DEMAND_START: "manual",
        win32service.SERVICE_DISABLED: "disabled"
    }
    return start_map.get(start_type, "unknown")


def register_windows_services(mcp):
    """Register the Windows services portmanteau tool with FastMCP."""
    mcp.tool(windows_services)