"""
Process monitoring and management tools for Windows Operations MCP.

This module provides tools for process monitoring and management with
structured logging, input validation, and security checks.
"""

import platform
import time
from typing import Dict, Any, List, Optional, Tuple

# Check if psutil is available
try:
    import psutil
    from psutil import NoSuchProcess, AccessDenied, ZombieProcess
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from ..logging_config import get_logger
from ..decorators import tool

# Initialize structured logger
logger = get_logger(__name__)

# Constants
MAX_PROCESSES = 1000
DEFAULT_MAX_PROCESSES = 100
SYSTEM_PROCESSES = {
    'System', 'Registry', 'csrss.exe', 'winlogon.exe', 
    'services.exe', 'lsass.exe', 'smss.exe', 'wininit.exe',
    'svchost.exe', 'dwm.exe', 'taskhostw.exe'
}

def _validate_process_inputs(
    filter_name: Optional[str] = None,
    include_system: bool = False,
    max_processes: int = DEFAULT_MAX_PROCESSES,
    pid: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """Validate process tool input parameters."""
    if filter_name is not None and not isinstance(filter_name, str):
        return False, "Filter name must be a string or None"
    
    if not isinstance(max_processes, int) or not (1 <= max_processes <= MAX_PROCESSES):
        return False, f"Max processes must be an integer between 1 and {MAX_PROCESSES}"
    
    if pid is not None:
        if not isinstance(pid, int) or pid <= 0:
            return False, "Process ID must be a positive integer"
    
    return True, None

def _get_process_basic_info(proc: 'psutil.Process') -> Dict[str, Any]:
    """Get basic information about a process."""
    try:
        with proc.oneshot():
            return {
                "pid": proc.pid,
                "name": proc.name(),
                "username": proc.username() or "N/A",
                "status": proc.status(),
                "memory_mb": round(proc.memory_info().rss / 1024 / 1024, 2),
                "cpu_percent": proc.cpu_percent(interval=0.1) or 0.0,
                "create_time": proc.create_time(),
                "exe": proc.exe() if proc.exe() else "N/A",
                "cmdline": proc.cmdline(),
                "parent_pid": proc.ppid()
            }
    except (NoSuchProcess, AccessDenied, ZombieProcess) as e:
        logger.warning("Failed to get basic process info", pid=proc.pid, error=str(e))
        return {"error": f"Failed to get process info: {e}"}

def register_process_tools(mcp):
    """Register process tools with FastMCP."""
    # Register the process tools with MCP
    mcp.tool(get_process_list)
    mcp.tool(get_process_info)
    mcp.tool(get_system_resources)
    
    @tool(
        name="get_process_list",
        description="Get list of running processes with filtering options",
        parameters={
            "filter_name": {
                "type": "string",
                "description": "Filter processes by name (optional)"
            },
            "include_system": {
                "type": "boolean",
                "description": "Include system processes",
                "default": False
            },
            "max_processes": {
                "type": "integer",
                "description": "Maximum number of processes to return",
                "default": 100
            }
        },
        required=[],
        returns={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "processes": {"type": "array"},
                "total_count": {"type": "integer"},
                "error": {"type": "string"}
            }
        }
    )
    def get_process_list(
        filter_name: Optional[str] = None,
        include_system: bool = False,
        max_processes: int = DEFAULT_MAX_PROCESSES
    ) -> Dict[str, Any]:
        """Get list of running processes with filtering options."""
        logger.info("get_process_list_started", filter_name=filter_name, include_system=include_system, max_processes=max_processes)
        
        is_valid, error_msg = _validate_process_inputs(filter_name=filter_name, include_system=include_system, max_processes=max_processes)
        if not is_valid:
            return {"success": False, "error": f"Invalid input: {error_msg}", "processes": [], "total_count": 0}
        
        if not HAS_PSUTIL:
            return {"success": False, "error": "psutil not available. Install with: pip install psutil", "processes": [], "total_count": 0}
        
        processes = []
        start_time = time.time()
        
        try:
            sys_info = {
                "platform": platform.platform(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "timestamp": time.time()
            }
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if len(processes) >= max_processes:
                        break
                    
                    pinfo = _get_process_basic_info(proc)
                    if "error" in pinfo:
                        continue
                    
                    if filter_name and filter_name.lower() not in pinfo['name'].lower():
                        continue
                    
                    if not include_system and pinfo['name'] in SYSTEM_PROCESSES:
                        continue
                    
                    processes.append(pinfo)
                        
                except (NoSuchProcess, AccessDenied, ZombieProcess):
                    continue
            
            processes.sort(key=lambda x: x.get('memory_mb', 0), reverse=True)
            execution_time = (time.time() - start_time) * 1000
            
            result = {
                "success": True,
                "processes": processes,
                "total_count": len(processes),
                "system_info": sys_info,
                "execution_time_ms": round(execution_time, 2),
                "filter_applied": filter_name,
                "include_system": include_system
            }
            
            logger.info("get_process_list_completed", process_count=len(processes), execution_time_ms=round(execution_time, 2))
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error getting process list: {str(e)}"
            logger.error("get_process_list_error", error=error_msg, exc_info=True)
            return {"success": False, "error": error_msg, "processes": [], "total_count": 0}

    @tool(
        name="get_process_info",
        description="Get detailed information about a specific process",
        parameters={
            "pid": {
                "type": "integer",
                "description": "Process ID to get information for"
            }
        },
        required=["pid"],
        returns={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "process": {"type": "object"},
                "error": {"type": "string"}
            }
        }
    )
    def get_process_info(pid: int) -> Dict[str, Any]:
        """Get detailed information about a specific process."""
        logger.info("get_process_info_started", pid=pid)
        
        is_valid, error_msg = _validate_process_inputs(pid=pid)
        if not is_valid:
            return {"success": False, "error": f"Invalid process ID: {error_msg}"}
        
        if not HAS_PSUTIL:
            return {"success": False, "error": "psutil not available. Install with: pip install psutil"}
        
        start_time = time.time()
        
        try:
            proc = psutil.Process(pid)
            
            with proc.oneshot():
                process_info = _get_process_basic_info(proc)
                if "error" in process_info:
                    return {"success": False, "error": process_info["error"]}
                
                try:
                    mem_info = proc.memory_full_info()
                    process_info.update({
                        "memory": {
                            "rss_mb": round(mem_info.rss / 1024 / 1024, 2),
                            "vms_mb": round(mem_info.vms / 1024 / 1024, 2),
                            "percent": round(proc.memory_percent(), 2),
                            "uss_mb": round(mem_info.uss / 1024 / 1024, 2) if hasattr(mem_info, 'uss') else None,
                            "pss_mb": round(mem_info.pss / 1024 / 1024, 2) if hasattr(mem_info, 'pss') else None,
                            "swap_mb": round(mem_info.swap / 1024 / 1024, 2) if hasattr(mem_info, 'swap') else None
                        },
                        "cpu": {
                            "percent": proc.cpu_percent(interval=0.1),
                            "num_ctx_switches": proc.num_ctx_switches()._asdict() if proc.num_ctx_switches() else {},
                            "cpu_num": proc.cpu_num(),
                            "cpu_affinity": proc.cpu_affinity()
                        },
                        "io_counters": proc.io_counters()._asdict() if proc.io_counters() else {},
                        "num_handles": proc.num_handles() if hasattr(proc, 'num_handles') else None,
                        "num_threads": proc.num_threads(),
                        "threads": [
                            {"id": t.id, "user_time": t.user_time, "system_time": t.system_time}
                            for t in proc.threads()
                        ] if proc.threads() else []
                    })
                    
                    try:
                        process_info["environ"] = proc.environ()
                    except (AccessDenied, AttributeError):
                        process_info["environ"] = "Access denied or not available"
                    
                    try:
                        open_files = proc.open_files()
                        process_info["open_files"] = [
                            {"path": f.path, "fd": f.fd} for f in open_files[:50]
                        ] if open_files else []
                    except (AccessDenied, AttributeError):
                        process_info["open_files"] = "Access denied or not available"
                    
                    try:
                        connections = proc.connections()
                        process_info["connections"] = [
                            {
                                "fd": conn.fd,
                                "family": str(conn.family),
                                "type": str(conn.type),
                                "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                                "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                                "status": conn.status
                            }
                            for conn in connections[:20]
                        ]
                    except (AccessDenied, AttributeError):
                        process_info["connections"] = "Access denied or not available"
                        
                except (NoSuchProcess, AccessDenied, ZombieProcess) as e:
                    logger.warning("Failed to get detailed process info", pid=pid, error=str(e))
            
            process_info["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
            logger.info("get_process_info_completed", pid=pid, execution_time_ms=process_info["execution_time_ms"])
            return {"success": True, "process": process_info}
            
        except NoSuchProcess:
            error_msg = f"Process with PID {pid} not found"
            logger.error("get_process_info_not_found", pid=pid, error=error_msg)
            return {"success": False, "error": error_msg}
        except AccessDenied:
            error_msg = f"Access denied for process PID {pid} (elevated privileges may be required)"
            logger.error("get_process_info_access_denied", pid=pid, error=error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error getting process info: {str(e)}"
            logger.error("get_process_info_error", pid=pid, error=error_msg, exc_info=True)
            return {"success": False, "error": error_msg}

    @tool(
        name="get_system_resources",
        description="Get comprehensive system resource usage information",
        parameters={},
        required=[],
        returns={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "resources": {"type": "object"},
                "error": {"type": "string"}
            }
        }
    )
    def get_system_resources() -> Dict[str, Any]:
        """Get comprehensive system resource usage information."""
        logger.info("get_system_resources_started")
        start_time = time.time()
        
        if not HAS_PSUTIL:
            return {"success": False, "error": "psutil not available. Install with: pip install psutil"}
        
        try:
            # Basic system info
            system_info = {
                "platform": platform.platform(),
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "boot_time": psutil.boot_time(),
                "users": [u._asdict() for u in psutil.users()] if hasattr(psutil, 'users') else []
            }
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=0.5, percpu=True)
            cpu_times = psutil.cpu_times_percent(interval=0.5)
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "percent": cpu_percent,
                "avg_percent": sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0,
                "times": {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "idle": cpu_times.idle
                }
            }
            
            # Memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_info = {
                "virtual": {
                    "total_gb": round(memory.total / (1024 ** 3), 2),
                    "available_gb": round(memory.available / (1024 ** 3), 2),
                    "used_gb": round(memory.used / (1024 ** 3), 2),
                    "free_gb": round(memory.free / (1024 ** 3), 2),
                    "percent": memory.percent
                },
                "swap": {
                    "total_gb": round(swap.total / (1024 ** 3), 2),
                    "used_gb": round(swap.used / (1024 ** 3), 2),
                    "free_gb": round(swap.free / (1024 ** 3), 2),
                    "percent": swap.percent
                }
            }
            
            # Disk info
            disk_info = {"partitions": []}
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disk_info["partitions"].append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total_gb": round(usage.total / (1024 ** 3), 2),
                        "used_gb": round(usage.used / (1024 ** 3), 2),
                        "free_gb": round(usage.free / (1024 ** 3), 2),
                        "percent_used": usage.percent
                    })
                except Exception:
                    pass
            
            result = {
                "success": True,
                "system": {
                    "info": system_info,
                    "cpu": cpu_info,
                    "memory": memory_info,
                    "disk": disk_info,
                    "timestamp": time.time(),
                    "execution_time_ms": round((time.time() - start_time) * 1000, 2)
                }
            }
            
            logger.info("get_system_resources_completed", execution_time_ms=result["system"]["execution_time_ms"])
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error getting system resources: {str(e)}"
            logger.error("get_system_resources_error", error=error_msg, exc_info=True)
            return {"success": False, "error": error_msg}
    
    logger.info("process_tools_registered", tools=["get_process_list", "get_process_info", "get_system_resources"])
