"""
Process Management Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows process monitoring and control with agentic telemetry.
"""

import asyncio
import psutil
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def process_management(
    action: Literal["list", "info", "resources", "kill"],
    pid: Optional[int] = None,
    name_filter: Optional[str] = None,
    include_system: bool = False,
    max_processes: int = 50,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform process management operations with comprehensive monitoring and agentic telemetry.

    RATIONALE:
    Consolidates process listing, resource analysis, and termination into a single portmanteau.
    Integrates with FastMCP 3.2 Context for real-time progress reporting and LLM-in-the-loop diagnostics.

    Args:
        action: The process operation to perform.
        pid: Process ID for detailed info or termination.
        name_filter: Substring filter for process names.
        include_system: Include system processes (SYSTEM, LOCAL SERVICE, etc.).
        max_processes: Truncation limit for process listing (default: 50).
        ctx: FastMCP Context for telemetry and sampling (injected).

    Examples:
        - process_management(action="list", name_filter="chrome")
        - process_management(action="info", pid=1234)
    """
    if ctx:
        ctx.info(f"Process Management: {action} (Target: {pid or name_filter or 'ALL'})")
        ctx.report_progress(10, 100)

    try:
        if action == "list":
            if ctx: ctx.report_progress(30, 100)
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    info = p.info
                    name = info.get('name', '')
                    user = info.get('username', '') or 'unknown'
                    
                    if not include_system and user.upper() in ['SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE']:
                        continue
                    if name_filter and name_filter.lower() not in name.lower():
                        continue
                        
                    procs.append({
                        "pid": info['pid'],
                        "name": name,
                        "user": user,
                        "cpu": info['cpu_percent'],
                        "mem": info['memory_percent']
                    })
                    if len(procs) >= max_processes: break
                except (psutil.NoSuchProcess, psutil.AccessDenied): continue
            
            return {"success": True, "action": action, "data": {"processes": procs, "count": len(procs)}}

        elif action == "info":
            if not pid: return {"success": False, "error": "PID required for info"}
            if ctx: ctx.report_progress(50, 100)
            p = psutil.Process(pid)
            info = {
                "pid": p.pid,
                "name": p.name(),
                "status": p.status(),
                "started": datetime.fromtimestamp(p.create_time()).isoformat(),
                "cmdline": p.cmdline(),
                "cpu_percent": p.cpu_percent(interval=0.1),
                "memory_info": p.memory_info()._asdict(),
                "num_threads": p.num_threads(),
            }
            return {"success": True, "action": action, "data": info}

        elif action == "resources":
            if ctx: ctx.report_progress(50, 100)
            return {
                "success": True,
                "action": action,
                "data": {
                    "cpu_percent": psutil.cpu_percent(interval=None),
                    "virtual_memory": psutil.virtual_memory()._asdict(),
                    "swap_memory": psutil.swap_memory()._asdict(),
                }
            }

        elif action == "kill":
            if not pid: return {"success": False, "error": "PID required for kill"}
            if ctx: ctx.warning(f"TERMINATING PROCESS {pid}...")
            p = psutil.Process(pid)
            p.terminate()
            return {"success": True, "action": action, "data": {"terminated_pid": pid}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process {pid} not found"}
    except psutil.AccessDenied:
        error_msg = f"Access denied to process {pid}. Elevated privileges may be required."
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(f"Access denied to process {pid}. User: {psutil.Process().username()}. How to fix?", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except: pass
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Process Error: {e}"
        if ctx: ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

def register_process_management(mcp) -> None:
    """Register the modernized process management tool."""
    mcp.tool()(process_management)