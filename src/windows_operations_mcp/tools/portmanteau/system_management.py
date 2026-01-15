"""
System Management Portmanteau Tool for Windows Operations MCP.

Consolidates system information, health checking, network testing, and help into a single portmanteau tool.
This provides core system management functionality.
"""

import socket
import time
from typing import Dict, Any, Optional, Literal

from ...logging_config import get_logger

logger = get_logger(__name__)


def system_management(
    action: Literal["info", "health", "test_port", "help"],
    detailed: bool = False,
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout_seconds: int = 5,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform system management operations including info, health checks, and network testing.

    FEATURES:
    - Comprehensive system information gathering (hardware, software, resources)
    - Automated health monitoring with configurable thresholds
    - Network connectivity testing with detailed diagnostics
    - Help system with categorized tool documentation
    - Performance metrics and system resource analysis
    - Platform-specific information (Windows, Python, hardware)
    - Real-time system status and diagnostics

    Args:
        action: The system operation to perform. Must be one of:
            - "info": Get comprehensive system information (hardware, software, resources)
            - "health": Perform automated system health check with status indicators
            - "test_port": Test network port connectivity with timing and diagnostics
            - "help": Get categorized help information for available tools
        detailed: Include additional detailed information (default: False)
        host: Hostname or IP address for port testing (required for "test_port")
        port: Port number to test connectivity (1-65535, required for "test_port")
        timeout_seconds: Connection timeout in seconds (1-300, default: 5)
        category: Help category filter ("file", "system", "network", etc.)

    Returns:
        FastMCP 2.14.1+ enhanced response with:
            - success: bool - Whether the system operation succeeded
            - action: str - The action that was performed
            - data: dict - Action-specific result data (varies by operation)
            - error: str - Error message (only present if success is False)

    Examples:
        # Get basic system information
        result = await system_management(action="info")
        if result["success"]:
            print(f"Platform: {result['data']['platform']}")

        # Get detailed system information
        result = await system_management(action="info", detailed=True)
        # Includes CPU cores, memory details, network interfaces, etc.

        # Perform system health check
        result = await system_management(action="health", detailed=True)
        if result["success"]:
            status = result["data"]["status"]  # "healthy", "degraded", "unhealthy"

        # Test network port connectivity
        result = await system_management(
            action="test_port",
            host="google.com",
            port=443,
            timeout_seconds=10
        )
        if result["success"] and result["data"]["reachable"]:
            print(f"Port open, response time: {result['data']['response_time']}s")

        # Get help for specific category
        result = await system_management(action="help", category="system")
        # Returns tools related to system management

        # Get general help
        result = await system_management(action="help")
        # Returns all available tool categories and descriptions

    Notes:
        - System information includes hardware, OS, Python version, and resources
        - Health checks monitor CPU, memory, disk usage with configurable thresholds
        - Network testing uses socket connections with timeout protection
        - Help system provides categorized tool documentation
        - Detailed mode provides additional metrics and diagnostics
        - All operations are read-only and safe for production systems
        - Resource monitoring uses psutil for accurate system metrics
    """
    logger.info("system_management_started", action=action)

    try:
        # Route to appropriate action
        if action == "info":
            return _get_system_info(detailed)

        elif action == "health":
            return _perform_health_check(detailed)

        elif action == "test_port":
            if host is None or port is None:
                return {
                    "success": False,
                    "action": action,
                    "error": "Host and port are required for test_port action"
                }
            return _test_port(host, port, timeout_seconds)

        elif action == "help":
            return _get_help(category)

        else:
            return {
                "success": False,
                "action": action,
                "error": f"Unknown action: {action}"
            }

    except Exception as e:
        error_msg = f"System management operation failed: {str(e)}"
        logger.error("system_management_error", action=action, error=error_msg, exc_info=True)
        return {
            "success": False,
            "action": action,
            "error": error_msg
        }


def _get_system_info(detailed: bool) -> Dict[str, Any]:
    """Get comprehensive system information."""
    try:
        import platform
        import psutil
        import datetime

        info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            }
        }

        if detailed:
            info.update({
                "boot_time": psutil.boot_time(),
                "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                "network": {
                    "interfaces": list(psutil.net_if_addrs().keys()),
                    "connections": len(psutil.net_connections())
                },
                "processes": len(list(psutil.process_iter()))
            })

        return {
            "success": True,
            "action": "info",
            "data": info
        }

    except ImportError:
        return {
            "success": False,
            "action": "info",
            "error": "psutil not available for detailed system information"
        }
    except Exception as e:
        return {
            "success": False,
            "action": "info",
            "error": f"Failed to get system info: {str(e)}"
        }


def _perform_health_check(detailed: bool) -> Dict[str, Any]:
    """Perform comprehensive system health check."""
    try:
        import psutil

        health = {
            "timestamp": time.time(),
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": []
        }

        # CPU check
        cpu_percent = psutil.cpu_percent(interval=0.1)
        health["checks"]["cpu"] = {
            "status": "ok" if cpu_percent < 90 else "warning",
            "value": cpu_percent,
            "threshold": 90
        }

        # Memory check
        memory = psutil.virtual_memory()
        health["checks"]["memory"] = {
            "status": "ok" if memory.percent < 90 else "warning",
            "value": memory.percent,
            "threshold": 90
        }

        # Disk check
        disk = psutil.disk_usage('/')
        health["checks"]["disk"] = {
            "status": "ok" if disk.percent < 90 else "warning",
            "value": disk.percent,
            "threshold": 90
        }

        # Network connectivity check
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            health["checks"]["network"] = {"status": "ok"}
        except:
            health["checks"]["network"] = {"status": "error"}
            health["errors"].append("Network connectivity check failed")

        # Determine overall status
        if any(check.get("status") == "error" for check in health["checks"].values()):
            health["status"] = "unhealthy"
        elif any(check.get("status") == "warning" for check in health["checks"].values()):
            health["status"] = "degraded"

        if detailed:
            health["processes"] = len(list(psutil.process_iter()))
            health["boot_time"] = psutil.boot_time()

        return {
            "success": True,
            "action": "health",
            "data": health
        }

    except ImportError:
        return {
            "success": False,
            "action": "health",
            "error": "psutil not available for health check"
        }
    except Exception as e:
        return {
            "success": False,
            "action": "health",
            "error": f"Health check failed: {str(e)}"
        }


def _test_port(host: str, port: int, timeout: int) -> Dict[str, Any]:
    """Test network port connectivity."""
    if not isinstance(port, int) or port < 1 or port > 65535:
        return {
            "success": False,
            "action": "test_port",
            "error": "Port must be an integer between 1 and 65535"
        }

    start_time = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        response_time = time.time() - start_time

        return {
            "success": True,
            "action": "test_port",
            "data": {
                "host": host,
                "port": port,
                "reachable": result == 0,
                "response_time": round(response_time, 3),
                "timeout": timeout
            }
        }

    except Exception as e:
        return {
            "success": False,
            "action": "test_port",
            "error": f"Port test failed: {str(e)}",
            "data": {
                "host": host,
                "port": port,
                "timeout": timeout
            }
        }


def _get_help(category: Optional[str]) -> Dict[str, Any]:
    """Get help information."""
    help_info = {
        "categories": ["file", "directory", "system", "network", "windows"],
        "tools": [
            "command_execution: Execute PowerShell and CMD commands",
            "file_operations: Basic file operations (read, write, delete, move, copy)",
            "directory_operations: Directory-specific operations",
            "system_management: System info, health checks, network testing",
            "archive_management: Create and extract archives",
            "git_operations: Git repository management",
            "json_operations: JSON file handling",
            "process_management: Process monitoring and control",
            "windows_services: Windows service management",
            "windows_event_logs: Event log querying and management",
            "windows_performance: Performance monitoring",
            "windows_permissions: File and directory permissions"
        ]
    }

    if category:
        # Filter help by category
        if category == "file":
            help_info["tools"] = [t for t in help_info["tools"] if "file" in t]
        elif category == "system":
            help_info["tools"] = [t for t in help_info["tools"] if "system" in t or "windows" in t]
        elif category == "network":
            help_info["tools"] = [t for t in help_info["tools"] if "network" in t]

    return {
        "success": True,
        "action": "help",
        "data": help_info
    }


def register_system_management(mcp):
    """Register the system management portmanteau tool with FastMCP."""
    mcp.tool(system_management)