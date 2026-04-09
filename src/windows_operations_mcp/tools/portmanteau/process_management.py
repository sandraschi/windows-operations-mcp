"""
Process Management Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows process monitoring and control with agentic telemetry.
"""

import asyncio
import json
import psutil
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

try:
    from prefab_ui import Table, BarChart, Text, Card
    HAS_PREFAB = True
except ImportError:
    HAS_PREFAB = False

logger = get_logger(__name__)

async def process_management(
    action: Literal["list", "info", "resources", "kill"],
    pid: Optional[int] = None,
    name_filter: Optional[str] = None,
    include_system: bool = False,
    max_processes: int = 50,
    ctx: Optional[Context] = None,
) -> Any:
    """
    Perform process management operations with comprehensive monitoring and agentic telemetry.
    Returns: Union[Dict, ToolResult] depending on action and availability of prefab-ui.
    """
    if ctx:
        ctx.info(f"Process Management: {action} (Target: {pid or name_filter or 'ALL'})")
        ctx.report_progress(10, 100)

    try:
        data = {}
        component = None

        if action == "list":
            if ctx: ctx.report_progress(30, 100)
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    p_info = p.info
                    name = p_info.get('name', '')
                    user = p_info.get('username', '') or 'unknown'
                    
                    if not include_system and user.upper() in ['SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE']:
                        continue
                    if name_filter and name_filter.lower() not in name.lower():
                        continue
                        
                    procs.append({
                        "pid": p_info['pid'],
                        "name": name,
                        "user": user,
                        "cpu": p_info['cpu_percent'],
                        "mem": round(p_info['memory_percent'], 2)
                    })
                    if len(procs) >= max_processes: break
                except (psutil.NoSuchProcess, psutil.AccessDenied): continue
            
            data = {"processes": procs, "count": len(procs)}
            if HAS_PREFAB and procs:
                component = Table(
                    title=f"Windows Processes ({len(procs)})",
                    columns=["PID", "Name", "User", "CPU%", "Mem%"],
                    rows=[[p["pid"], p["name"], p["user"], p["cpu"], p["mem"]] for p in procs]
                )

        elif action == "info":
            if not pid: return {"success": False, "error": "PID required for info"}
            if ctx: ctx.report_progress(50, 100)
            p = psutil.Process(pid)
            data = {
                "pid": p.pid,
                "name": p.name(),
                "status": p.status(),
                "started": datetime.fromtimestamp(p.create_time()).isoformat(),
                "cmdline": p.cmdline(),
                "cpu_percent": p.cpu_percent(interval=0.1),
                "memory_info": p.memory_info()._asdict(),
                "num_threads": p.num_threads(),
            }
            if HAS_PREFAB:
                component = Card(
                    title=f"Process Info: {data['name']} ({pid})",
                    content=[
                        f"**Status**: {data['status']}",
                        f"**Started**: {data['started']}",
                        f"**CPU**: {data['cpu_percent']}%",
                        f"**Threads**: {data['num_threads']}",
                        f"**Command**: `{' '.join(data['cmdline'])}`"
                    ]
                )

        elif action == "resources":
            if ctx: ctx.report_progress(50, 100)
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            data = {
                "cpu_percent": cpu,
                "virtual_memory": mem._asdict(),
            }
            if HAS_PREFAB:
                component = BarChart(
                    title="System Resource Utilization",
                    data=[
                        {"label": "CPU Usage", "value": cpu},
                        {"label": "Memory Usage", "value": mem.percent}
                    ],
                    max_value=100,
                    unit="%"
                )

        elif action == "kill":
            if not pid: return {"success": False, "error": "PID required for kill"}
            if ctx: ctx.warning(f"TERMINATING PROCESS {pid}...")
            p = psutil.Process(pid)
            p.terminate()
            data = {"terminated_pid": pid}
            if HAS_PREFAB:
                component = Text(text=f"✅ Process {pid} terminated successfully.")

        if HAS_PREFAB and component:
            return [
                Text(text=json.dumps({"success": True, "action": action, "data": data}, indent=2)),
                component
            ]

        return {"success": True, "action": action, "data": data}

    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process {pid} not found"}
    except Exception as e:
        error_msg = f"Process Error: {e}"
        if ctx: ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

def register_process_management(mcp) -> None:
    """Register the modernized process management tool."""
    mcp.tool()(process_management)