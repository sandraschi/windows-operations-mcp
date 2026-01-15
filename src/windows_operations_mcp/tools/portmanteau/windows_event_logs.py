"""
Windows Event Logs Portmanteau Tool

Consolidates Windows Event Log operations into a single tool.
"""

import logging
from typing import Any, Literal, Optional

from fastmcp import FastMCP

# Import existing functions
from ..windows_event_logs import (
    query_windows_event_log,
    export_windows_event_log,
    clear_windows_event_log,
    monitor_windows_event_log,
)

logger = logging.getLogger(__name__)


def register_windows_event_logs_tool(mcp: FastMCP) -> None:
    """Register the Windows Event Logs portmanteau tool."""

    @mcp.tool()
    async def windows_event_logs(
        action: Literal["query", "export", "clear", "monitor"],
        log_name: str = "Application",
        event_source: Optional[str] = None,
        event_id: Optional[int] = None,
        output_file: str = "",
        format: str = "csv",
        backup_before_clear: bool = True,
        backup_file: Optional[str] = None,
        max_events: int = 100,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        level: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Comprehensive Windows Event Logs portmanteau tool.
        
        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 4 separate tools (one per operation), this tool consolidates related
        Windows Event Log operations into a single interface. This design:
        - Prevents tool explosion (4 tools → 1 tool) while maintaining full functionality
        - Improves discoverability by grouping related operations together
        - Reduces cognitive load when working with event logs
        - Enables atomic batch operations across multiple log actions
        - Follows FastMCP 2.12+ best practices for feature-rich MCP servers
        
        Args:
            action (Literal["query", "export", "clear", "monitor"]): The operation to perform.
                Required for all operations. Must be one of:
                - "query": Query event log entries
                - "export": Export event log to file
                - "clear": Clear event log
                - "monitor": Monitor event log in real-time
            
            log_name (str): Event log name. Optional for all operations. Default: "Application"
                Common values: "Application", "System", "Security", "Setup"
            
            event_source (str | None): Filter by event source. Optional for all operations.
                Default: None. Used by: query, monitor operations.
            
            event_id (int | None): Filter by event ID. Optional for all operations.
                Default: None. Used by: query, monitor operations.
            
            output_file (str): Output file path. Required for: export operation.
                Optional for: other operations.
            
            format (str): Export format. Optional for all operations. Default: "csv"
                Used by: export operation. Valid: "csv", "xml", "txt"
            
            backup_before_clear (bool): Create backup before clearing. Optional for all operations.
                Default: True. Used by: clear operation.
            
            backup_file (str | None): Backup file path. Optional for all operations.
                Default: None. Used by: clear operation. If None, auto-generates filename.
            
            max_events (int): Maximum events to return. Optional for all operations. Default: 100
                Used by: query, monitor operations.
            
            start_time (str | None): Start time filter. Optional for all operations.
                Default: None. Used by: query operation. Format: ISO datetime string.
            
            end_time (str | None): End time filter. Optional for all operations.
                Default: None. Used by: query operation. Format: ISO datetime string.
            
            level (str | None): Event level filter. Optional for all operations.
                Default: None. Used by: query operation. Valid: "Critical", "Error", "Warning", "Information", "Verbose"
        
        Returns:
            Dict containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict | Any): Operation-specific result data
                - error (str): Error message if success is False
        
        Examples:
            # Query event log
            result = await windows_event_logs(
                action="query",
                log_name="Application",
                max_events=50
            )
            
            # Export event log
            result = await windows_event_logs(
                action="export",
                log_name="System",
                output_file="C:\\events.csv",
                format="csv"
            )
            
            # Clear event log with backup
            result = await windows_event_logs(
                action="clear",
                log_name="Application",
                backup_before_clear=True
            )
        """
        try:
            if action not in ["query", "export", "clear", "monitor"]:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Available: query, export, clear, monitor",
                    "action": action,
                }

            logger.info(f"Executing windows_event_logs action: {action}")

            if action == "query":
                result = query_windows_event_log(
                    log_name=log_name,
                    event_source=event_source,
                    event_id=event_id,
                    max_events=max_events,
                    start_time=start_time,
                    end_time=end_time,
                    level=level
                )
                return {"success": True, "action": action, "data": result}

            elif action == "export":
                if not output_file:
                    return {"success": False, "error": "output_file is required for export action", "action": action}
                result = export_windows_event_log(
                    log_name=log_name,
                    output_file=output_file,
                    format=format
                )
                return {"success": result.get("success", False), "action": action, "data": result}

            elif action == "clear":
                result = clear_windows_event_log(
                    log_name=log_name,
                    backup_before_clear=backup_before_clear,
                    backup_file=backup_file
                )
                return {"success": result.get("success", False), "action": action, "data": result}

            elif action == "monitor":
                result = monitor_windows_event_log(
                    log_name=log_name,
                    event_source=event_source,
                    event_id=event_id,
                    max_events=max_events
                )
                return {"success": True, "action": action, "data": result}

        except Exception as e:
            logger.error(f"Error in windows_event_logs action '{action}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute {action}: {str(e)}",
                "action": action,
            }

