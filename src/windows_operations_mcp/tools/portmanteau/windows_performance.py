"""
Windows Performance Portmanteau Tool

Consolidates Windows Performance monitoring operations into a single tool.
"""

import logging
from typing import Any, Literal, Optional

from fastmcp import FastMCP

# Import existing functions
from ..windows_performance import (
    get_windows_performance_counters,
    monitor_windows_performance,
    get_windows_system_performance,
)

logger = logging.getLogger(__name__)


def register_windows_performance_tool(mcp: FastMCP) -> None:
    """Register the Windows Performance portmanteau tool."""

    @mcp.tool()
    async def windows_performance(
        action: Literal["get_counters", "monitor", "get_system"],
        counter_names: Optional[list[str]] = None,
        object_name: str = "Processor",
        instance_name: str = "_Total",
        duration_seconds: int = 10,
        interval_seconds: float = 1.0,
        include_cpu: bool = True,
        include_memory: bool = True,
        include_disk: bool = True,
        include_network: bool = True,
    ) -> dict[str, Any]:
        """
        Comprehensive Windows Performance portmanteau tool.
        
        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 3 separate tools (one per operation), this tool consolidates related
        Windows Performance monitoring operations into a single interface. This design:
        - Prevents tool explosion (3 tools → 1 tool) while maintaining full functionality
        - Improves discoverability by grouping related operations together
        - Reduces cognitive load when working with performance monitoring
        - Enables atomic batch operations across multiple performance actions
        - Follows FastMCP 2.12+ best practices for feature-rich MCP servers
        
        Args:
            action (Literal["get_counters", "monitor", "get_system"]): The operation to perform.
                Required for all operations. Must be one of:
                - "get_counters": Get performance counter values
                - "monitor": Monitor performance over time
                - "get_system": Get comprehensive system performance
            
            counter_names (list[str] | None): List of counter names to query. Required for: get_counters,
                monitor operations. Optional for: get_system operation.
                Example: ["% Processor Time", "Available MBytes"]
            
            object_name (str): Performance object name. Optional for all operations. Default: "Processor"
                Used by: get_counters, monitor operations. Common: "Processor", "Memory", "Disk", "Network"
            
            instance_name (str): Instance name. Optional for all operations. Default: "_Total"
                Used by: get_counters, monitor operations. "_Total" = aggregate, specific names = individual instances
            
            duration_seconds (int): Monitoring duration in seconds. Optional for all operations. Default: 10
                Used by: monitor operation.
            
            interval_seconds (float): Sampling interval in seconds. Optional for all operations. Default: 1.0
                Used by: monitor operation.
            
            include_cpu (bool): Include CPU metrics. Optional for all operations. Default: True
                Used by: get_system operation.
            
            include_memory (bool): Include memory metrics. Optional for all operations. Default: True
                Used by: get_system operation.
            
            include_disk (bool): Include disk metrics. Optional for all operations. Default: True
                Used by: get_system operation.
            
            include_network (bool): Include network metrics. Optional for all operations. Default: True
                Used by: get_system operation.
        
        Returns:
            Dict containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict | Any): Operation-specific result data
                - error (str): Error message if success is False
        
        Examples:
            # Get performance counters
            result = await windows_performance(
                action="get_counters",
                counter_names=["% Processor Time"],
                object_name="Processor"
            )
            
            # Monitor performance over time
            result = await windows_performance(
                action="monitor",
                counter_names=["% Processor Time", "Available MBytes"],
                duration_seconds=30,
                interval_seconds=2.0
            )
            
            # Get comprehensive system performance
            result = await windows_performance(
                action="get_system",
                include_cpu=True,
                include_memory=True
            )
        """
        try:
            if action not in ["get_counters", "monitor", "get_system"]:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Available: get_counters, monitor, get_system",
                    "action": action,
                }

            logger.info(f"Executing windows_performance action: {action}")

            if action == "get_counters":
                if not counter_names:
                    return {"success": False, "error": "counter_names is required for get_counters action", "action": action}
                result = get_windows_performance_counters(
                    counter_names=counter_names,
                    object_name=object_name,
                    instance_name=instance_name
                )
                return {"success": True, "action": action, "data": result}

            elif action == "monitor":
                if not counter_names:
                    return {"success": False, "error": "counter_names is required for monitor action", "action": action}
                result = monitor_windows_performance(
                    counter_names=counter_names,
                    object_name=object_name,
                    instance_name=instance_name,
                    duration_seconds=duration_seconds,
                    interval_seconds=interval_seconds
                )
                return {"success": True, "action": action, "data": result}

            elif action == "get_system":
                result = get_windows_system_performance(
                    include_cpu=include_cpu,
                    include_memory=include_memory,
                    include_disk=include_disk,
                    include_network=include_network
                )
                return {"success": True, "action": action, "data": result}

        except Exception as e:
            logger.error(f"Error in windows_performance action '{action}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute {action}: {str(e)}",
                "action": action,
            }

