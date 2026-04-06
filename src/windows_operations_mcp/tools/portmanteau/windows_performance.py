"""
Windows Performance Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows Performance monitoring with agentic telemetry.
"""

import asyncio
import psutil
from typing import Any, Dict, List, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def windows_performance(
    action: Literal["system", "process", "counters"],
    pid: Optional[int] = None,
    include_network: bool = True,
    duration_seconds: int = 1,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform Windows Performance monitoring with comprehensive error handling and agentic telemetry.

    RATIONALE:
    Consolidates system-wide, process-specific, and low-level counter monitoring into a single portmanteau.
    Integrates with FastMCP 3.2 Context for real-time progress reporting and LLM-in-the-loop diagnostics.

    Args:
        action: The performance operation to perform.
        pid: Specific process ID to monitor (for "process").
        include_network: Include network I/O stats.
        duration_seconds: Interval for CPU sampling (default: 1s).
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Performance Op: {action}")
        ctx.report_progress(10, 100)

    try:
        if action == "system":
            if ctx: ctx.report_progress(50, 100)
            cpu = psutil.cpu_percent(interval=duration_seconds, percpu=True)
            mem = psutil.virtual_memory()._asdict()
            disk = psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
            
            data = {
                "cpu_percent_per_core": cpu,
                "memory": mem,
                "disk_io": disk,
            }
            if include_network:
                data["network_io"] = psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            
            return {"success": True, "action": action, "data": data}

        elif action == "process":
            if not pid: return {"success": False, "error": "PID required for process performance"}
            if ctx: ctx.report_progress(50, 100)
            p = psutil.Process(pid)
            with p.oneshot():
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "pid": pid,
                        "name": p.name(),
                        "cpu_percent": p.cpu_percent(interval=duration_seconds),
                        "memory_info": p.memory_info()._asdict(),
                        "num_threads": p.num_threads(),
                        "io_counters": p.io_counters()._asdict() if hasattr(p, 'io_counters') else None
                    }
                }

        elif action == "counters":
             # Placeholder for specialized PDH counters (would require pywin32)
             return {"success": False, "error": "PDH Counters not yet implemented in SOTA v14.0 wrapper. Use 'system' for core metrics."}

        return {"success": False, "error": f"Unknown action: {action}"}

    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process {pid} not found"}
    except Exception as e:
        error_msg = f"Performance Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(f"Windows Performance monitor failed ({action}). Error: {e}. Suggest alternative diagnostics.", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except: pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

def register_windows_performance(mcp) -> None:
    """Register the modernized Windows performance tool."""
    mcp.tool()(windows_performance)
