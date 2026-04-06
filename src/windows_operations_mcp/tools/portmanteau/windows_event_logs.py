"""
Windows Event Logs Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows Event Log management with agentic telemetry.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def windows_event_logs(
    action: Literal["query", "clear", "export"],
    log_name: str = "Application",
    max_events: int = 50,
    time_range_hours: int = 24,
    event_id: Optional[int] = None,
    output_path: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform Windows Event Log operations with comprehensive error handling and agentic telemetry.

    RATIONALE:
    Consolidates querying, clearing, and exporting logs into a single async portmanteau.
    Uses asyncio.to_thread for blocking pywin32 calls to maintain MCP responsiveness.

    Args:
        action: The log operation to perform.
        log_name: Name of the event log (Application, System, Security, etc.).
        max_events: Maximum events to return (for "query").
        time_range_hours: Lookback window (for "query").
        event_id: Filter by specific Event ID.
        output_path: Destination for exported logs (for "export").
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"EventLog Op: {action} on {log_name}")
        ctx.report_progress(10, 100)

    try:
        import win32evtlog

        if action == "query":
            return await asyncio.to_thread(_query_logs, log_name, max_events, time_range_hours, event_id, ctx)

        if action == "clear":
            if ctx: ctx.warning(f"Clearing {log_name} log...")
            await asyncio.to_thread(win32evtlog.ClearEventLog, None, log_name)
            return {"success": True, "action": action, "data": {"cleared_log": log_name}}

        if action == "export":
             # Implementation for export using PowerShell or win32
             return {"success": False, "error": "Export action not yet implemented in SOTA v14.0 wrapper."}

        return {"success": False, "error": f"Unknown action: {action}"}

    except ImportError:
        return {"success": False, "error": "pywin32 not installed"}
    except Exception as e:
        error_msg = f"EventLog Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(f"Windows Event Log '{log_name}' failed {action}. Error: {e}. Suggest fix.", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except: pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

def _query_logs(log_name, max_events, hours, event_id, ctx):
    """Blocking query implementation."""
    import win32evtlog
    handle = win32evtlog.OpenEventLog(None, log_name)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    start_time = datetime.now() - timedelta(hours=hours)
    
    events = []
    try:
        while len(events) < max_events:
            batch = win32evtlog.ReadEventLog(handle, flags, 0)
            if not batch: break
            for ev in batch:
                ev_time = datetime.fromtimestamp(ev.TimeGenerated)
                if ev_time < start_time: continue
                if event_id and ev.EventID != event_id: continue
                
                events.append({
                    "timestamp": ev_time.isoformat(),
                    "id": ev.EventID,
                    "source": ev.SourceName,
                    "level": _get_level(ev.EventType),
                    "message": ev.StringInserts[0] if ev.StringInserts else ""
                })
                if len(events) >= max_events: break
        return {"success": True, "action": "query", "data": {"events": events, "count": len(events)}}
    finally:
        win32evtlog.CloseEventLog(handle)

def _get_level(code):
    m = {1: "Error", 2: "Warning", 4: "Info", 8: "AuditSuccess", 16: "AuditFailure"}
    return m.get(code, "Other")

def register_windows_event_logs(mcp) -> None:
    """Register the modernized Windows event logs tool."""
    mcp.tool()(windows_event_logs)
