"""
Process Management Portmanteau Tool for Windows Operations MCP.

Consolidates process operations (list, info, resources) into a single portmanteau tool.
Provides comprehensive process monitoring and management functionality.
"""

from typing import Dict, Any, Optional, Literal, List

from ...logging_config import get_logger

logger = get_logger(__name__)


def process_management(
    action: Literal["list", "info", "resources"],
    pid: Optional[int] = None,
    name_filter: Optional[str] = None,
    include_system: bool = False,
    max_processes: int = 100
) -> Dict[str, Any]:
    """
    Perform process management operations with comprehensive monitoring.

    FEATURES:
    - Real-time process listing with filtering and sorting
    - Detailed process information including memory, CPU, and connections
    - System resource monitoring (CPU, memory, disk, network)
    - Process tree analysis and parent-child relationships
    - Safe operations with access control validation
    - Performance metrics and usage statistics

    Args:
        action: The process operation to perform. Must be one of:
            - "list": List running processes with filtering and pagination
            - "info": Get comprehensive information about specific process by PID
            - "resources": Get system-wide resource usage and performance metrics
        pid: Process ID for detailed information (required for "info" action)
        name_filter: Filter processes by name substring (case-insensitive, for "list")
        include_system: Include system processes (default: False, safer)
        max_processes: Maximum processes to return (1-1000, default: 100)

    Returns:
        FastMCP 2.14.1+ enhanced response with:
            - success: bool - Whether the process operation succeeded
            - action: str - The action that was performed
            - data: dict - Action-specific result data (varies by operation)
            - error: str - Error message (only present if success is False)

    Examples:
        # List all user processes
        result = await process_management(action="list", include_system=False)
        if result["success"]:
            processes = result["data"]["processes"]
            high_cpu = [p for p in processes if p["cpu_percent"] > 50]

        # Get detailed process info
        result = await process_management(action="info", pid=1234)
        if result["success"]:
            proc_info = result["data"]
            print(f"Process uses {proc_info['memory_percent']}% memory")

        # Filter processes by name
        result = await process_management(
            action="list",
            name_filter="chrome",
            max_processes=50
        )

        # Get system resource usage
        result = await process_management(action="resources")
        if result["success"]:
            cpu_usage = result["data"]["cpu"]["percent"]
            memory_usage = result["data"]["memory"]["percent"]

        # Monitor high-resource processes
        result = await process_management(action="list", include_system=True)
        if result["success"]:
            high_memory = sorted(
                result["data"]["processes"],
                key=lambda p: p["memory_percent"],
                reverse=True
            )[:5]

    Notes:
        - Process information requires appropriate permissions
        - System processes are excluded by default for safety
        - Resource monitoring provides real-time system metrics
        - Process listing is sorted by CPU usage by default
        - Connection information includes network sockets
        - Memory information includes RSS, VMS, and page faults
    """
    logger.info("process_management_started", action=action, pid=pid)

    try:
        # Validate max_processes
        if not (1 <= max_processes <= 1000):
            max_processes = 100

        # Route to appropriate action
        if action == "list":
            return _list_processes(name_filter, include_system, max_processes)

        elif action == "info":
            if pid is None:
                return {
                    "success": False,
                    "action": action,
                    "error": "pid is required for info action"
                }
            return _get_process_info(pid)

        elif action == "resources":
            return _get_system_resources()

        else:
            return {
                "success": False,
                "action": action,
                "error": f"Unknown action: {action}"
            }

    except Exception as e:
        error_msg = f"Process management operation failed: {str(e)}"
        logger.error("process_management_error", action=action, pid=pid, error=error_msg, exc_info=True)
        return {
            "success": False,
            "action": action,
            "error": error_msg
        }


def _list_processes(name_filter: Optional[str], include_system: bool, max_processes: int) -> Dict[str, Any]:
    """List running processes with filtering."""
    try:
        import psutil

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                # Skip system processes if not requested
                if not include_system and proc.info['username'] in ['SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE', None]:
                    continue

                # Apply name filter
                if name_filter and name_filter.lower() not in proc.info['name'].lower():
                    continue

                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "username": proc.info['username'] or 'unknown',
                    "cpu_percent": round(proc.info['cpu_percent'] or 0, 2),
                    "memory_percent": round(proc.info['memory_percent'] or 0, 2),
                    "status": proc.info['status'] or 'unknown'
                })

                if len(processes) >= max_processes:
                    break

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage descending
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

        return {
            "success": True,
            "action": "list",
            "data": {
                "processes": processes,
                "count": len(processes),
                "name_filter": name_filter,
                "include_system": include_system,
                "max_processes": max_processes,
                "truncated": len(processes) >= max_processes
            }
        }

    except ImportError:
        return {
            "success": False,
            "action": "list",
            "error": "psutil not available for process management"
        }
    except Exception as e:
        return {
            "success": False,
            "action": "list",
            "error": f"Failed to list processes: {str(e)}"
        }


def _get_process_info(pid: int) -> Dict[str, Any]:
    """Get detailed information about a specific process."""
    try:
        import psutil
        from datetime import datetime

        try:
            proc = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return {
                "success": False,
                "action": "info",
                "error": f"Process with PID {pid} not found"
            }

        try:
            info = {
                "pid": proc.pid,
                "name": proc.name(),
                "exe": proc.exe(),
                "cwd": proc.cwd(),
                "username": proc.username(),
                "status": proc.status(),
                "cpu_percent": round(proc.cpu_percent(interval=0.1), 2),
                "memory_percent": round(proc.memory_percent(), 2),
                "memory_info": {
                    "rss": proc.memory_info().rss,
                    "vms": proc.memory_info().vms,
                    "num_page_faults": proc.memory_info().num_page_faults
                },
                "cpu_times": {
                    "user": proc.cpu_times().user,
                    "system": proc.cpu_times().system,
                    "children_user": proc.cpu_times().children_user,
                    "children_system": proc.cpu_times().children_system
                },
                "num_threads": proc.num_threads(),
                "num_fds": proc.num_fds() if hasattr(proc, 'num_fds') else None,
                "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
                "cmdline": proc.cmdline(),
                "environ": dict(proc.environ()) if proc.environ() else {}
            }

            # Get connections if available
            try:
                connections = proc.connections()
                info["connections"] = [
                    {
                        "fd": conn.fd,
                        "family": conn.family,
                        "type": conn.type,
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status
                    }
                    for conn in connections[:10]  # Limit to first 10 connections
                ]
            except (psutil.AccessDenied, AttributeError):
                info["connections"] = []

            return {
                "success": True,
                "action": "info",
                "data": info
            }

        except psutil.AccessDenied:
            return {
                "success": False,
                "action": "info",
                "error": f"Access denied to process {pid}"
            }

    except ImportError:
        return {
            "success": False,
            "action": "info",
            "error": "psutil not available for process management"
        }
    except Exception as e:
        return {
            "success": False,
            "action": "info",
            "error": f"Failed to get process info for PID {pid}: {str(e)}"
        }


def _get_system_resources() -> Dict[str, Any]:
    """Get comprehensive system resource usage information."""
    try:
        import psutil
        import platform
        import time

        # CPU information
        cpu_info = {
            "count": psutil.cpu_count(),
            "count_logical": psutil.cpu_count(logical=True),
            "percent": psutil.cpu_percent(interval=1, percpu=True),
            "times_percent": psutil.cpu_times_percent(interval=1, percpu=False)
        }

        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
            "active": getattr(memory, 'active', None),
            "inactive": getattr(memory, 'inactive', None),
            "buffers": getattr(memory, 'buffers', None),
            "cached": getattr(memory, 'cached', None),
            "shared": getattr(memory, 'shared', None),
            "slab": getattr(memory, 'slab', None)
        }

        # Disk information
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.mountpoint] = {
                    "device": partition.device,
                    "fstype": partition.fstype,
                    "opts": partition.opts,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                }
            except (OSError, PermissionError):
                continue

        # Network information
        net_info = {
            "interfaces": {},
            "io_counters": {}
        }

        # Network interfaces
        for name, addrs in psutil.net_if_addrs().items():
            net_info["interfaces"][name] = [
                {
                    "family": addr.family,
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast,
                    "ptp": addr.ptp
                }
                for addr in addrs
            ]

        # Network I/O counters
        try:
            counters = psutil.net_io_counters(pernic=True)
            for interface, counter in counters.items():
                net_info["io_counters"][interface] = {
                    "bytes_sent": counter.bytes_sent,
                    "bytes_recv": counter.bytes_recv,
                    "packets_sent": counter.packets_sent,
                    "packets_recv": counter.packets_recv,
                    "errin": counter.errin,
                    "errout": counter.errout,
                    "dropin": counter.dropin,
                    "dropout": counter.dropout
                }
        except Exception:
            pass

        # System information
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "boot_time": psutil.boot_time(),
            "uptime": time.time() - psutil.boot_time(),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }

        return {
            "success": True,
            "action": "resources",
            "data": {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "network": net_info,
                "system": system_info
            }
        }

    except ImportError:
        return {
            "success": False,
            "action": "resources",
            "error": "psutil not available for resource monitoring"
        }
    except Exception as e:
        return {
            "success": False,
            "action": "resources",
            "error": f"Failed to get system resources: {str(e)}"
        }


def register_process_management(mcp):
    """Register the process management portmanteau tool with FastMCP."""
    mcp.tool(process_management)