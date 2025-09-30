"""
Windows Services Management Tools for Windows Operations MCP.

This module provides comprehensive Windows services management functionality
including listing, starting, stopping, configuring, and troubleshooting services.
"""

import winreg
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..logging_config import get_logger
from ..decorators import tool

logger = get_logger(__name__)

# Service status constants
SERVICE_STOPPED = 1
SERVICE_START_PENDING = 2
SERVICE_STOP_PENDING = 3
SERVICE_RUNNING = 4
SERVICE_CONTINUE_PENDING = 5
SERVICE_PAUSE_PENDING = 6
SERVICE_PAUSED = 7

# Service startup types
SERVICE_AUTO_START = 2
SERVICE_DEMAND_START = 3
SERVICE_DISABLED = 4

def _get_service_status_name(status_code: int) -> str:
    """Convert service status code to readable name."""
    status_map = {
        SERVICE_STOPPED: "Stopped",
        SERVICE_START_PENDING: "Start Pending",
        SERVICE_STOP_PENDING: "Stop Pending",
        SERVICE_RUNNING: "Running",
        SERVICE_CONTINUE_PENDING: "Continue Pending",
        SERVICE_PAUSE_PENDING: "Pause Pending",
        SERVICE_PAUSED: "Paused"
    }
    return status_map.get(status_code, f"Unknown ({status_code})")

def _get_startup_type_name(startup_type: int) -> str:
    """Convert startup type code to readable name."""
    startup_map = {
        SERVICE_AUTO_START: "Automatic",
        SERVICE_DEMAND_START: "Manual",
        SERVICE_DISABLED: "Disabled"
    }
    return startup_map.get(startup_type, f"Unknown ({startup_type})")

@tool(
    name="list_windows_services",
    description="List Windows services with filtering and detailed information",
    parameters={
        "filter_status": {
            "type": "string",
            "description": "Filter by service status (running, stopped, all)",
            "default": "all"
        },
        "filter_name": {
            "type": "string",
            "description": "Filter by service name (partial match)"
        },
        "include_system_services": {
            "type": "boolean",
            "description": "Include system services in results",
            "default": True
        }
    },
    required=[],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "services": {"type": "array"},
            "total_count": {"type": "integer"},
            "filtered_count": {"type": "integer"}
        }
    }
)
def list_windows_services(
    filter_status: str = "all",
    filter_name: Optional[str] = None,
    include_system_services: bool = True
) -> Dict[str, Any]:
    """
    List Windows services with optional filtering.

    Args:
        filter_status: Filter by status ("running", "stopped", "all")
        filter_name: Filter by service name (partial match)
        include_system_services: Include system services in results

    Returns:
        Dictionary with services list and metadata
    """
    try:
        import win32service
        import win32serviceutil

        services = []
        manager = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)

        try:
            services_list = win32service.EnumServicesStatus(manager)

            for service in services_list:
                service_name = service[0]
                display_name = service[1]

                # Skip system services if not requested
                if not include_system_services and service_name.startswith(('Win', 'W32', 'Rpc', 'Net')):
                    continue

                # Get service status
                try:
                    status = win32serviceutil.QueryServiceStatus(service_name)[1]
                    status_name = _get_service_status_name(status)
                except Exception:
                    status = SERVICE_STOPPED
                    status_name = "Unknown"

                # Apply name filter first
                if filter_name and filter_name.lower() not in service_name.lower() and filter_name.lower() not in display_name.lower():
                    continue

                # Get additional service info
                try:
                    config = win32serviceutil.QueryServiceConfig(service_name)
                    startup_type = config[1]
                    startup_name = _get_startup_type_name(startup_type)
                except Exception:
                    startup_type = SERVICE_DEMAND_START  # Default to Manual
                    startup_name = "Unknown"

                # Apply status filter after we have all the data
                if filter_status != "all":
                    if filter_status == "running" and status != SERVICE_RUNNING:
                        continue
                    elif filter_status == "stopped" and status != SERVICE_STOPPED:
                        continue

                services.append({
                    "name": service_name,
                    "display_name": display_name,
                    "status": status_name,
                    "status_code": status,
                    "startup_type": startup_name,
                    "startup_code": startup_type
                })

        finally:
            win32service.CloseServiceHandle(manager)

        return {
            "success": True,
            "services": services,
            "total_count": len(services),
            "filtered_count": len(services)
        }

    except ImportError:
        return {
            "success": False,
            "error": "pywin32 not available. Install with: pip install pywin32"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list services: {str(e)}"
        }

@tool(
    name="start_windows_service",
    description="Start a Windows service",
    parameters={
        "service_name": {
            "type": "string",
            "description": "Name of the service to start"
        },
        "wait_timeout": {
            "type": "integer",
            "description": "Maximum time to wait for service to start (seconds)",
            "default": 30
        }
    },
    required=["service_name"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "final_status": {"type": "string"}
        }
    }
)
def start_windows_service(service_name: str, wait_timeout: int = 30) -> Dict[str, Any]:
    """
    Start a Windows service.

    Args:
        service_name: Name of the service to start
        wait_timeout: Maximum time to wait for service to start

    Returns:
        Dictionary with operation result
    """
    try:
        import win32serviceutil

        # Start the service
        win32serviceutil.StartService(service_name)

        # Wait for it to actually start
        start_time = time.time()
        while time.time() - start_time < wait_timeout:
            try:
                status = win32serviceutil.QueryServiceStatus(service_name)[1]
                if status == SERVICE_RUNNING:
                    return {
                        "success": True,
                        "message": f"Service '{service_name}' started successfully",
                        "final_status": "Running"
                    }
                elif status == SERVICE_START_PENDING:
                    time.sleep(1)  # Wait 1 second before checking again
                else:
                    return {
                        "success": False,
                        "message": f"Service '{service_name}' failed to start (status: {_get_service_status_name(status)})",
                        "final_status": _get_service_status_name(status)
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error checking service status: {str(e)}"
                }

        return {
            "success": False,
            "message": f"Service '{service_name}' start timed out after {wait_timeout} seconds"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to start service '{service_name}': {str(e)}"
        }

@tool(
    name="stop_windows_service",
    description="Stop a Windows service",
    parameters={
        "service_name": {
            "type": "string",
            "description": "Name of the service to stop"
        },
        "wait_timeout": {
            "type": "integer",
            "description": "Maximum time to wait for service to stop (seconds)",
            "default": 30
        }
    },
    required=["service_name"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "final_status": {"type": "string"}
        }
    }
)
def stop_windows_service(service_name: str, wait_timeout: int = 30) -> Dict[str, Any]:
    """
    Stop a Windows service.

    Args:
        service_name: Name of the service to stop
        wait_timeout: Maximum time to wait for service to stop

    Returns:
        Dictionary with operation result
    """
    try:
        import win32serviceutil

        # Stop the service
        win32serviceutil.StopService(service_name)

        # Wait for it to actually stop
        start_time = time.time()
        while time.time() - start_time < wait_timeout:
            try:
                status = win32serviceutil.QueryServiceStatus(service_name)[1]
                if status == SERVICE_STOPPED:
                    return {
                        "success": True,
                        "message": f"Service '{service_name}' stopped successfully",
                        "final_status": "Stopped"
                    }
                elif status == SERVICE_STOP_PENDING:
                    time.sleep(1)  # Wait 1 second before checking again
                else:
                    return {
                        "success": False,
                        "message": f"Service '{service_name}' failed to stop (status: {_get_service_status_name(status)})",
                        "final_status": _get_service_status_name(status)
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error checking service status: {str(e)}"
                }

        return {
            "success": False,
            "message": f"Service '{service_name}' stop timed out after {wait_timeout} seconds"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to stop service '{service_name}': {str(e)}"
        }

@tool(
    name="restart_windows_service",
    description="Restart a Windows service",
    parameters={
        "service_name": {
            "type": "string",
            "description": "Name of the service to restart"
        },
        "stop_timeout": {
            "type": "integer",
            "description": "Maximum time to wait for service to stop (seconds)",
            "default": 30
        },
        "start_timeout": {
            "type": "integer",
            "description": "Maximum time to wait for service to start (seconds)",
            "default": 30
        }
    },
    required=["service_name"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "final_status": {"type": "string"}
        }
    }
)
def restart_windows_service(
    service_name: str,
    stop_timeout: int = 30,
    start_timeout: int = 30
) -> Dict[str, Any]:
    """
    Restart a Windows service.

    Args:
        service_name: Name of the service to restart
        stop_timeout: Maximum time to wait for service to stop
        start_timeout: Maximum time to wait for service to start

    Returns:
        Dictionary with operation result
    """
    try:
        import win32serviceutil

        # Stop the service first
        stop_result = stop_windows_service(service_name, stop_timeout)
        if not stop_result["success"]:
            return stop_result

        # Wait a moment before starting
        time.sleep(2)

        # Start the service
        start_result = start_windows_service(service_name, start_timeout)
        return start_result

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to restart service '{service_name}': {str(e)}"
        }

def register_windows_services_tools(mcp):
    """Register Windows services management tools with FastMCP."""
    # Register the Windows services tools with MCP
    mcp.tool(list_windows_services)
    mcp.tool(start_windows_service)
    mcp.tool(stop_windows_service)
    mcp.tool(restart_windows_service)

    logger.info("windows_services_tools_registered", tools=[
        "list_windows_services", "start_windows_service",
        "stop_windows_service", "restart_windows_service"
    ])
