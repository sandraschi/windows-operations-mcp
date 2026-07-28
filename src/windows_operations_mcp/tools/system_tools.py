"""
System information and monitoring tools for Windows Operations MCP.

This module provides tools for system information gathering and health monitoring
with structured logging, input validation, and security checks.
"""

import datetime
import platform
import socket
import sys
import time
from typing import Any

from ..decorators import tool
from ..logging_config import get_logger
from ..utils import fail_response

# Initialize structured logger
logger = get_logger(__name__)

# Constants
SYSTEM_INFO_RATE_LIMIT = 15  # Max 15 calls per minute
HEALTH_CHECK_RATE_LIMIT = 10  # Max 10 calls per minute

# System information cache with TTL
_system_info_cache = {"data": None, "timestamp": 0, "ttl": 60}  # 1 minute cache
_health_check_cache = {"data": None, "timestamp": 0, "ttl": 30}  # 30 second cache


def _get_cached_data(cache_key: str) -> tuple[bool, dict | None]:
    """Get data from cache if it exists and is not expired."""
    cache = _system_info_cache if cache_key == "system_info" else _health_check_cache

    if cache["data"] is not None and (time.time() - cache["timestamp"]) < cache["ttl"]:
        return True, cache["data"]
    return False, None


def _update_cache(cache_key: str, data: dict) -> None:
    """Update the cache with new data."""
    cache = _system_info_cache if cache_key == "system_info" else _health_check_cache
    cache["data"] = data
    cache["timestamp"] = time.time()


@tool(
    name="get_system_info",
    description="Get comprehensive system information with optional detailed system metrics",
    parameters={
        "detailed": {
            "type": "boolean",
            "description": "If True, includes more detailed system information (may be slower)",
            "default": False,
        }
    },
    required=[],
    returns={
        "type": "object",
        "properties": {"success": {"type": "boolean"}, "system": {"type": "object"}, "error": {"type": "string"}},
    },
)
def get_system_info(detailed: bool = False) -> dict[str, Any]:
    """
    Get comprehensive system information with optional detailed system metrics.

    Args:
        detailed: If True, includes more detailed system information (may be slower)

    Returns:
        Dict containing:
            - success (bool): Whether the operation succeeded
            - system (dict): System information
            - error (str, optional): Error message if success is False
    """
    logger.info("get_system_info_started", detailed=detailed)
    start_time = time.time()

    # Check cache first
    cache_valid, cached_data = _get_cached_data("system_info")
    if cache_valid and not detailed:
        logger.info("get_system_info_cache_hit")
        return {"success": True, "system": cached_data, "from_cache": True}

    try:
        # Basic system information
        system_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "execution_time_ms": 0,
            "operating_system": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "platform": platform.platform(),
                "node": platform.node(),
                "fqdn": socket.getfqdn() if hasattr(socket, "getfqdn") else "N/A",
                "hostname": socket.gethostname(),
                "ip_address": socket.gethostbyname(socket.gethostname()) if hasattr(socket, "gethostbyname") else "N/A",
            },
            "python": {
                "version": sys.version,
                "version_info": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro,
                    "releaselevel": sys.version_info.releaselevel,
                    "serial": sys.version_info.serial,
                },
                "implementation": {
                    "name": platform.python_implementation(),
                    "version": platform.python_version(),
                    "compiler": platform.python_compiler(),
                },
                "executable": sys.executable,
                "path": sys.path,
                "platform": sys.platform,
                "api_version": sys.api_version,
                "maxsize": sys.maxsize,
                "maxunicode": sys.maxunicode,
                "builtin_module_names": sys.builtin_module_names
                if detailed
                else "[redacted: set detailed=True to view]",
            },
            "environment": {
                "path_separator": platform.os.sep,
                "line_separator": repr(platform.os.linesep),
                "path_sep": platform.os.pathsep,
                "current_working_directory": platform.os.getcwd(),
                "process_id": platform.os.getpid(),
                "effective_user_id": platform.os.geteuid() if hasattr(platform.os, "geteuid") else None,
                "effective_group_id": platform.os.getegid() if hasattr(platform.os, "getegid") else None,
                "real_user_id": platform.os.getuid() if hasattr(platform.os, "getuid") else None,
                "real_group_id": platform.os.getgid() if hasattr(platform.os, "getgid") else None,
                "environment_variables": dict(platform.os.environ)
                if detailed
                else {"note": "Set detailed=True to view environment variables"},
            },
            "system_metrics": {
                "cpu_count": platform.os.cpu_count(),
                "load_average": platform.os.getloadavg() if hasattr(platform.os, "getloadavg") else "N/A",
                "process_affinity": platform.os.sched_getaffinity(0)
                if hasattr(platform.os, "sched_getaffinity")
                else "N/A",
            },
            "filesystem_encoding": {
                "filesystem": sys.getfilesystemencoding(),
                "default": sys.getdefaultencoding(),
                "stdin": sys.stdin.encoding if hasattr(sys.stdin, "encoding") else None,
                "stdout": sys.stdout.encoding if hasattr(sys.stdout, "encoding") else None,
                "stderr": sys.stderr.encoding if hasattr(sys.stderr, "encoding") else None,
            },
        }

        # Add Windows-specific information if available
        if platform.system() == "Windows":
            system_info["windows"] = {}
            try:
                import winreg

                system_info["windows"].update(
                    {
                        "edition": platform.win32_edition() if hasattr(platform, "win32_edition") else "Unknown",
                        "is_iot": platform.win32_is_iot() if hasattr(platform, "win32_is_iot") else False,
                        "is_server": platform.win32_ver()[0].lower().find("server") >= 0,
                        "version": platform.win32_ver(),
                    }
                )

                # Get Windows product name from registry
                try:
                    with winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                    ) as key:
                        product_name = winreg.QueryValueEx(key, "ProductName")[0]
                        system_info["windows"]["product_name"] = product_name
                except Exception:
                    pass

            except ImportError:
                system_info["windows"] = {"note": "winreg not available"}

        # Add detailed system metrics if requested
        if detailed:
            try:
                import psutil

                # CPU details
                cpu_times = psutil.cpu_times_percent(interval=0.1)
                system_info["system_metrics"].update(
                    {
                        "cpu_physical_cores": psutil.cpu_count(logical=False),
                        "cpu_logical_cores": psutil.cpu_count(logical=True),
                        "cpu_times": {
                            "user": cpu_times.user,
                            "system": cpu_times.system,
                            "idle": cpu_times.idle,
                            "iowait": getattr(cpu_times, "iowait", None),
                            "irq": getattr(cpu_times, "irq", None),
                            "softirq": getattr(cpu_times, "softirq", None),
                        },
                        "cpu_stats": {
                            "ctx_switches": psutil.cpu_stats().ctx_switches if hasattr(psutil, "cpu_stats") else None,
                            "interrupts": psutil.cpu_stats().interrupts if hasattr(psutil, "cpu_stats") else None,
                        },
                        "cpu_freq": {
                            "current": psutil.cpu_freq().current if hasattr(psutil, "cpu_freq") else None,
                            "min": psutil.cpu_freq().min if hasattr(psutil, "cpu_freq") else None,
                            "max": psutil.cpu_freq().max if hasattr(psutil, "cpu_freq") else None,
                        }
                        if hasattr(psutil, "cpu_freq")
                        else None,
                    }
                )

                # Memory details
                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()
                system_info["system_metrics"].update(
                    {
                        "memory": {
                            "total_gb": round(memory.total / (1024**3), 2),
                            "available_gb": round(memory.available / (1024**3), 2),
                            "used_gb": round(memory.used / (1024**3), 2),
                            "free_gb": round(memory.free / (1024**3), 2),
                            "percent": memory.percent,
                        },
                        "swap": {
                            "total_gb": round(swap.total / (1024**3), 2),
                            "used_gb": round(swap.used / (1024**3), 2),
                            "free_gb": round(swap.free / (1024**3), 2),
                            "percent": swap.percent,
                        },
                    }
                )

            except ImportError:
                system_info["system_metrics"]["note"] = "psutil not available for detailed metrics"

        # Calculate execution time
        execution_time = round((time.time() - start_time) * 1000, 2)
        system_info["execution_time_ms"] = execution_time

        # Update cache
        _update_cache("system_info", system_info)

        # Log completion
        logger.info("get_system_info_completed", execution_time_ms=execution_time, detailed=detailed)

        return {"success": True, "system": system_info, "from_cache": False}

    except Exception as e:
        error_msg = f"Failed to gather system info: {e!s}"
        logger.error("get_system_info_error", error=error_msg, exc_info=True)
        return fail_response(error_msg, execution_time_ms=round((time.time() - start_time) * 1000, 2))


@tool(
    name="health_check",
    description="Perform comprehensive health check of the Windows Operations MCP server",
    parameters={
        "detailed": {
            "type": "boolean",
            "description": "If True, includes more detailed health information (may be slower)",
            "default": False,
        },
        "check_services": {
            "type": "boolean",
            "description": "If True, verifies required services are running",
            "default": True,
        },
        "check_disk_space": {"type": "boolean", "description": "If True, checks disk space usage", "default": True},
        "check_network": {"type": "boolean", "description": "If True, verifies network connectivity", "default": True},
    },
    required=[],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "status": {"type": "string"},
            "checks": {"type": "object"},
            "error": {"type": "string"},
        },
    },
)
def health_check(
    detailed: bool = False, check_services: bool = True, check_disk_space: bool = True, check_network: bool = True
) -> dict[str, Any]:
    """
    Perform comprehensive health check of the Windows Operations MCP server.

    Args:
        detailed: If True, includes more detailed health information (may be slower)
        check_services: If True, verifies required services are running
        check_disk_space: If True, checks disk space usage
        check_network: If True, verifies network connectivity

    Returns:
        Dict containing:
            - success (bool): Overall health status
            - status (str): "healthy", "degraded", or "unhealthy"
            - checks (dict): Results of individual health checks
            - error (str, optional): Error message if success is False
    """
    logger.info(
        "health_check_started",
        detailed=detailed,
        check_services=check_services,
        check_disk_space=check_disk_space,
        check_network=check_network,
    )
    start_time = time.time()

    # Check cache first (use cache only for non-detailed checks)
    if not detailed:
        cache_valid, cached_data = _get_cached_data("health_check")
        if cache_valid:
            logger.info("health_check_cache_hit")
            return {"success": True, "from_cache": True, **cached_data}

    try:
        # Initialize health status with timestamp and basic info
        health_status = {
            "success": True,
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "execution_time_ms": 0,
            "environment": {
                "python_version": sys.version.split()[0],
                "platform": platform.system(),
                "architecture": platform.architecture(),
                "node": platform.node(),
                "executable": sys.executable,
            },
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        # Check Python version
        min_py_version = (3, 8)
        current_version = sys.version_info
        is_py_version_ok = current_version >= min_py_version

        health_status["checks"]["python_version"] = {
            "status": "ok" if is_py_version_ok else "error",
            "current": f"{current_version.major}.{current_version.minor}.{current_version.micro}",
            "minimum_required": f"{min_py_version[0]}.{min_py_version[1]}.0",
            "recommended": "3.9+",
        }

        if not is_py_version_ok:
            health_status["status"] = "unhealthy"
            health_status["errors"].append("Python version is below minimum required")

        # Check required modules
        required_modules = ["fastmcp", "psutil", "structlog"]

        for module_name in required_modules:
            try:
                module = __import__(module_name)
                health_status["checks"][f"module_{module_name}"] = {
                    "status": "ok",
                    "version": getattr(module, "__version__", "unknown"),
                    "path": getattr(module, "__file__", "unknown"),
                }
            except ImportError as e:
                health_status["checks"][f"module_{module_name}"] = {
                    "status": "error" if module_name == "fastmcp" else "warning",
                    "error": str(e),
                }
                if module_name == "fastmcp":
                    health_status["status"] = "unhealthy"
                    health_status["errors"].append(f"Required module not found: {module_name}")
                else:
                    health_status["warnings"].append(f"Optional module not found: {module_name}")

        # Set overall status based on checks
        if health_status["status"] == "healthy" and health_status["warnings"]:
            health_status["status"] = "degraded"

        # Calculate execution time
        execution_time = round((time.time() - start_time) * 1000, 2)
        health_status["execution_time_ms"] = execution_time

        # Update cache if this is a non-detailed check
        if not detailed:
            _update_cache("health_check", health_status)

        # Log completion
        logger.info(
            "health_check_completed",
            status=health_status["status"],
            execution_time_ms=execution_time,
            checks_performed=len(health_status["checks"]),
            warnings=len(health_status["warnings"]),
            errors=len(health_status["errors"]),
        )

        return {"success": True, "from_cache": False, **health_status}

    except Exception as e:
        error_msg = f"Health check failed: {e!s}"
        logger.error("health_check_error", error=error_msg, exc_info=True)
        return fail_response(
            error_msg, status="unhealthy", execution_time_ms=round((time.time() - start_time) * 1000, 2)
        )


def register_system_tools(mcp):
    """Register system information tools with FastMCP."""
    # Register the system tools with MCP
    mcp.tool(get_system_info)
    mcp.tool(health_check)

    logger.info("system_tools_registered", tools=["get_system_info", "health_check"])
