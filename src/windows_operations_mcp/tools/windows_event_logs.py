"""
Windows Event Log Tools for Windows Operations MCP.

This module provides comprehensive Windows event log management functionality
including querying, filtering, exporting, and monitoring event logs.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from ..logging_config import get_logger
from ..decorators import tool

logger = get_logger(__name__)

# Event log types
EVENTLOG_ERROR_TYPE = 1
EVENTLOG_WARNING_TYPE = 2
EVENTLOG_INFORMATION_TYPE = 4
EVENTLOG_AUDIT_SUCCESS = 8
EVENTLOG_AUDIT_FAILURE = 16

def _get_event_type_name(event_type: int) -> str:
    """Convert event type code to readable name."""
    type_map = {
        EVENTLOG_ERROR_TYPE: "Error",
        EVENTLOG_WARNING_TYPE: "Warning",
        EVENTLOG_INFORMATION_TYPE: "Information",
        EVENTLOG_AUDIT_SUCCESS: "Audit Success",
        EVENTLOG_AUDIT_FAILURE: "Audit Failure"
    }
    return type_map.get(event_type, f"Unknown ({event_type})")

@tool(
    name="query_windows_event_log",
    description="Query Windows event logs with filtering and time range options",
    parameters={
        "log_name": {
            "type": "string",
            "description": "Name of the event log to query (Application, System, Security, etc.)",
            "default": "Application"
        },
        "event_source": {
            "type": "string",
            "description": "Filter by event source"
        },
        "event_id": {
            "type": "integer",
            "description": "Filter by specific event ID"
        },
        "event_type": {
            "type": "string",
            "description": "Filter by event type (Error, Warning, Information, Audit Success, Audit Failure)"
        },
        "time_range_hours": {
            "type": "integer",
            "description": "Query events from the last N hours",
            "default": 24
        },
        "max_events": {
            "type": "integer",
            "description": "Maximum number of events to return",
            "default": 100
        }
    },
    required=["log_name"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "events": {"type": "array"},
            "total_count": {"type": "integer"},
            "log_name": {"type": "string"}
        }
    }
)
def query_windows_event_log(
    log_name: str = "Application",
    event_source: Optional[str] = None,
    event_id: Optional[int] = None,
    event_type: Optional[str] = None,
    time_range_hours: int = 24,
    max_events: int = 100
) -> Dict[str, Any]:
    """
    Query Windows event logs with filtering options.

    Args:
        log_name: Name of the event log to query
        event_source: Filter by event source
        event_id: Filter by specific event ID
        event_type: Filter by event type
        time_range_hours: Query events from the last N hours
        max_events: Maximum number of events to return

    Returns:
        Dictionary with events and metadata
    """
    try:
        import win32evtlog
        import win32evtlogutil
        import win32security

        events = []
        start_time = datetime.now() - timedelta(hours=time_range_hours)

        # Open the event log
        handle = win32evtlog.OpenEventLog(None, log_name)
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        try:
            event_count = 0
            while event_count < max_events:
                # Read events in batches
                events_batch = win32evtlog.ReadEventLog(handle, flags, 0)

                if not events_batch:
                    break

                for event in events_batch:
                    # Check if event is within time range
                    event_time = datetime.fromtimestamp(event.TimeGenerated)
                    if event_time < start_time:
                        continue

                    # Apply filters
                    if event_source and event_source.lower() not in event.SourceName.lower():
                        continue

                    if event_id and event.EventID != event_id:
                        continue

                    if event_type:
                        event_type_lower = event_type.lower()
                        if event_type_lower == "error" and event.EventType != EVENTLOG_ERROR_TYPE:
                            continue
                        elif event_type_lower == "warning" and event.EventType != EVENTLOG_WARNING_TYPE:
                            continue
                        elif event_type_lower == "information" and event.EventType != EVENTLOG_INFORMATION_TYPE:
                            continue
                        elif event_type_lower == "audit success" and event.EventType != EVENTLOG_AUDIT_SUCCESS:
                            continue
                        elif event_type_lower == "audit failure" and event.EventType != EVENTLOG_AUDIT_FAILURE:
                            continue

                    # Format event data
                    try:
                        event_data = {
                            "timestamp": event_time.isoformat(),
                            "event_id": event.EventID,
                            "event_type": _get_event_type_name(event.EventType),
                            "event_type_code": event.EventType,
                            "source": event.SourceName,
                            "category": event.EventCategory,
                            "computer": event.ComputerName,
                            "message": event.StringInserts[0] if event.StringInserts else "",
                            "raw_data": event.Data.decode('utf-8', errors='ignore') if event.Data else ""
                        }
                        events.append(event_data)
                        event_count += 1

                        if event_count >= max_events:
                            break
                    except Exception as e:
                        logger.warning(f"Error processing event: {e}")
                        continue

                if len(events_batch) == 0:
                    break

        finally:
            win32evtlog.CloseEventLog(handle)

        return {
            "success": True,
            "events": events,
            "total_count": len(events),
            "log_name": log_name
        }

    except ImportError:
        return {
            "success": False,
            "error": "pywin32 not available. Install with: pip install pywin32"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to query event log: {str(e)}"
        }

@tool(
    name="export_windows_event_log",
    description="Export Windows event log entries to a file",
    parameters={
        "log_name": {
            "type": "string",
            "description": "Name of the event log to export",
            "default": "Application"
        },
        "output_file": {
            "type": "string",
            "description": "Path where to save the exported log"
        },
        "format": {
            "type": "string",
            "description": "Export format (csv, json, txt)",
            "default": "csv"
        },
        "time_range_hours": {
            "type": "integer",
            "description": "Export events from the last N hours",
            "default": 24
        },
        "event_source": {
            "type": "string",
            "description": "Filter by event source"
        },
        "event_type": {
            "type": "string",
            "description": "Filter by event type"
        }
    },
    required=["log_name", "output_file"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "output_file": {"type": "string"},
            "exported_count": {"type": "integer"}
        }
    }
)
def export_windows_event_log(
    log_name: str = "Application",
    output_file: str = "",
    format: str = "csv",
    time_range_hours: int = 24,
    event_source: Optional[str] = None,
    event_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Export Windows event log entries to a file.

    Args:
        log_name: Name of the event log to export
        output_file: Path where to save the exported log
        format: Export format (csv, json, txt)
        time_range_hours: Export events from the last N hours
        event_source: Filter by event source
        event_type: Filter by event type

    Returns:
        Dictionary with export result
    """
    try:
        import win32evtlog
        import win32evtlogutil
        import csv
        import json

        # First, query the events
        query_result = query_windows_event_log(
            log_name=log_name,
            event_source=event_source,
            event_type=event_type,
            time_range_hours=time_range_hours,
            max_events=10000  # Allow more events for export
        )

        if not query_result["success"]:
            return query_result

        events = query_result["events"]

        # Export based on format
        if format.lower() == "csv":
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                if events:
                    fieldnames = events[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(events)

        elif format.lower() == "json":
            with open(output_file, 'w', encoding='utf-8') as jsonfile:
                json.dump({
                    "log_name": log_name,
                    "export_time": datetime.now().isoformat(),
                    "time_range_hours": time_range_hours,
                    "events": events
                }, jsonfile, indent=2, ensure_ascii=False)

        elif format.lower() == "txt":
            with open(output_file, 'w', encoding='utf-8') as txtfile:
                txtfile.write(f"Windows Event Log Export\n")
                txtfile.write(f"Log Name: {log_name}\n")
                txtfile.write(f"Export Time: {datetime.now().isoformat()}\n")
                txtfile.write(f"Time Range: Last {time_range_hours} hours\n")
                txtfile.write(f"Total Events: {len(events)}\n")
                txtfile.write("\n" + "="*80 + "\n\n")

                for event in events:
                    txtfile.write(f"Timestamp: {event['timestamp']}\n")
                    txtfile.write(f"Event ID: {event['event_id']}\n")
                    txtfile.write(f"Type: {event['event_type']}\n")
                    txtfile.write(f"Source: {event['source']}\n")
                    txtfile.write(f"Computer: {event['computer']}\n")
                    txtfile.write(f"Message: {event['message']}\n")
                    txtfile.write("\n" + "-"*40 + "\n\n")

        return {
            "success": True,
            "message": f"Successfully exported {len(events)} events to {output_file}",
            "output_file": output_file,
            "exported_count": len(events)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to export event log: {str(e)}"
        }

@tool(
    name="clear_windows_event_log",
    description="Clear Windows event log entries",
    parameters={
        "log_name": {
            "type": "string",
            "description": "Name of the event log to clear",
            "default": "Application"
        },
        "backup_before_clear": {
            "type": "boolean",
            "description": "Create a backup before clearing",
            "default": True
        },
        "backup_file": {
            "type": "string",
            "description": "Path for backup file (if backup_before_clear is True)"
        }
    },
    required=["log_name"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "backup_file": {"type": "string"}
        }
    }
)
def clear_windows_event_log(
    log_name: str = "Application",
    backup_before_clear: bool = True,
    backup_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clear Windows event log entries.

    Args:
        log_name: Name of the event log to clear
        backup_before_clear: Create a backup before clearing
        backup_file: Path for backup file

    Returns:
        Dictionary with clear result
    """
    try:
        import win32evtlog

        # Create backup if requested
        if backup_before_clear:
            if not backup_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{log_name}_backup_{timestamp}.evtx"

            # Export current log before clearing
            export_result = export_windows_event_log(
                log_name=log_name,
                output_file=backup_file,
                format="json"
            )

            if not export_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create backup: {export_result['error']}"
                }

        # Clear the event log
        win32evtlog.ClearEventLog(None, log_name)

        return {
            "success": True,
            "message": f"Successfully cleared event log '{log_name}'",
            "backup_file": backup_file if backup_before_clear else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to clear event log: {str(e)}"
        }

@tool(
    name="monitor_windows_event_log",
    description="Monitor Windows event log for specific events in real-time",
    parameters={
        "log_name": {
            "type": "string",
            "description": "Name of the event log to monitor",
            "default": "Application"
        },
        "event_source": {
            "type": "string",
            "description": "Monitor only events from this source"
        },
        "event_id": {
            "type": "integer",
            "description": "Monitor only this specific event ID"
        },
        "event_type": {
            "type": "string",
            "description": "Monitor only this event type"
        },
        "monitor_duration": {
            "type": "integer",
            "description": "How long to monitor (seconds)",
            "default": 300
        },
        "check_interval": {
            "type": "integer",
            "description": "How often to check for new events (seconds)",
            "default": 5
        }
    },
    required=["log_name"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "events": {"type": "array"},
            "monitoring_duration": {"type": "number"},
            "message": {"type": "string"}
        }
    }
)
def monitor_windows_event_log(
    log_name: str = "Application",
    event_source: Optional[str] = None,
    event_id: Optional[int] = None,
    event_type: Optional[str] = None,
    monitor_duration: int = 300,
    check_interval: int = 5
) -> Dict[str, Any]:
    """
    Monitor Windows event log for specific events in real-time.

    Args:
        log_name: Name of the event log to monitor
        event_source: Monitor only events from this source
        event_id: Monitor only this specific event ID
        event_type: Monitor only this event type
        monitor_duration: How long to monitor (seconds)
        check_interval: How often to check for new events (seconds)

    Returns:
        Dictionary with monitoring results
    """
    try:
        import win32evtlog
        import win32evtlogutil

        events = []
        start_time = time.time()

        # Open the event log
        handle = win32evtlog.OpenEventLog(None, log_name)
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        try:
            last_check = 0
            while time.time() - start_time < monitor_duration:
                current_time = time.time()

                # Check for new events periodically
                if current_time - last_check >= check_interval:
                    try:
                        # Read recent events
                        events_batch = win32evtlog.ReadEventLog(handle, flags, 0)

                        for event in events_batch:
                            event_time = datetime.fromtimestamp(event.TimeGenerated)

                            # Apply filters
                            if event_source and event_source.lower() not in event.SourceName.lower():
                                continue

                            if event_id and event.EventID != event_id:
                                continue

                            if event_type:
                                event_type_lower = event_type.lower()
                                if event_type_lower == "error" and event.EventType != EVENTLOG_ERROR_TYPE:
                                    continue
                                elif event_type_lower == "warning" and event.EventType != EVENTLOG_WARNING_TYPE:
                                    continue
                                elif event_type_lower == "information" and event.EventType != EVENTLOG_INFORMATION_TYPE:
                                    continue

                            # Format event data
                            event_data = {
                                "timestamp": event_time.isoformat(),
                                "event_id": event.EventID,
                                "event_type": _get_event_type_name(event.EventType),
                                "source": event.SourceName,
                                "message": event.StringInserts[0] if event.StringInserts else ""
                            }
                            events.append(event_data)

                    except Exception as e:
                        logger.warning(f"Error reading events during monitoring: {e}")

                    last_check = current_time

                time.sleep(0.1)  # Small delay to prevent busy waiting

        finally:
            win32evtlog.CloseEventLog(handle)

        return {
            "success": True,
            "events": events,
            "monitoring_duration": time.time() - start_time,
            "message": f"Monitored {log_name} for {time.time() - start_time:.1f} seconds, found {len(events)} matching events"
        }

    except ImportError:
        return {
            "success": False,
            "error": "pywin32 not available. Install with: pip install pywin32"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to monitor event log: {str(e)}"
        }

def register_windows_event_log_tools(mcp):
    """Register Windows event log tools with FastMCP."""
    # Register the Windows event log tools with MCP
    mcp.tool(query_windows_event_log)
    mcp.tool(export_windows_event_log)
    mcp.tool(clear_windows_event_log)
    mcp.tool(monitor_windows_event_log)

    logger.info("windows_event_log_tools_registered", tools=[
        "query_windows_event_log", "export_windows_event_log",
        "clear_windows_event_log", "monitor_windows_event_log"
    ])
