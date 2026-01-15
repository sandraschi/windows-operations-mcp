"""
File Attributes Portmanteau Tool

Consolidates file attributes and dates operations into a single tool.
"""

import logging
from typing import Any, Literal, Optional

from fastmcp import FastMCP

# Import existing functions
from ..file_operations.attributes import get_file_attributes_tool, set_file_attributes_tool
from ..file_operations.dates import get_file_dates_tool, set_file_dates_tool

logger = logging.getLogger(__name__)


def register_file_attributes_tool(mcp: FastMCP) -> None:
    """Register the file attributes portmanteau tool."""

    @mcp.tool()
    async def file_attributes(
        action: Literal["get_attributes", "set_attributes", "get_dates", "set_dates"],
        file_path: str,
        attributes: Optional[dict[str, bool]] = None,
        created: Optional[str] = None,
        modified: Optional[str] = None,
        accessed: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Comprehensive file attributes and dates portmanteau tool.
        
        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 4 separate tools (one per operation), this tool consolidates related
        file attribute and date operations into a single interface. This design:
        - Prevents tool explosion (4 tools → 1 tool) while maintaining full functionality
        - Improves discoverability by grouping related operations together
        - Reduces cognitive load when working with file metadata
        - Enables atomic batch operations across multiple attribute actions
        - Follows FastMCP 2.12+ best practices for feature-rich MCP servers
        
        Args:
            action (Literal["get_attributes", "set_attributes", "get_dates", "set_dates"]): The operation to perform.
                Required for all operations. Must be one of:
                - "get_attributes": Get file attributes
                - "set_attributes": Set file attributes
                - "get_dates": Get file dates
                - "set_dates": Set file dates
            
            file_path (str): Path to the file. Required for all operations.
            
            attributes (dict[str, bool] | None): Dictionary of attribute names to boolean values.
                Required for: set_attributes operation. Optional for: other operations.
                Example: {"readonly": True, "hidden": False, "archive": True}
            
            created (str | None): ISO format datetime string for creation date. Optional for all operations.
                Required for: set_dates operation (at least one date must be provided).
                Format: "YYYY-MM-DDTHH:MM:SS" or "YYYY-MM-DDTHH:MM:SS+HH:MM"
            
            modified (str | None): ISO format datetime string for modification date. Optional for all operations.
                Required for: set_dates operation (at least one date must be provided).
                Format: "YYYY-MM-DDTHH:MM:SS" or "YYYY-MM-DDTHH:MM:SS+HH:MM"
            
            accessed (str | None): ISO format datetime string for access date. Optional for all operations.
                Required for: set_dates operation (at least one date must be provided).
                Format: "YYYY-MM-DDTHH:MM:SS" or "YYYY-MM-DDTHH:MM:SS+HH:MM"
        
        Returns:
            Dict containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict | Any): Operation-specific result data
                - error (str): Error message if success is False
        
        Examples:
            # Get file attributes
            result = await file_attributes(action="get_attributes", file_path="C:\\file.txt")
            
            # Set file attributes
            result = await file_attributes(
                action="set_attributes",
                file_path="C:\\file.txt",
                attributes={"readonly": True, "hidden": False}
            )
            
            # Get file dates
            result = await file_attributes(action="get_dates", file_path="C:\\file.txt")
            
            # Set file dates
            result = await file_attributes(
                action="set_dates",
                file_path="C:\\file.txt",
                modified="2024-01-15T10:30:00"
            )
        """
        try:
            if action not in ["get_attributes", "set_attributes", "get_dates", "set_dates"]:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'",
                    "action": action,
                }

            logger.info(f"Executing file_attributes action: {action}")

            if action == "get_attributes":
                result = get_file_attributes_tool(file_path=file_path)
                return {"success": result.get("success", False), "action": action, "data": result}

            elif action == "set_attributes":
                if not attributes:
                    return {"success": False, "error": "attributes is required for set_attributes", "action": action}
                result = set_file_attributes_tool(file_path=file_path, attributes=attributes)
                return {"success": result.get("success", False), "action": action, "data": result}

            elif action == "get_dates":
                result = get_file_dates_tool(file_path=file_path)
                return {"success": result.get("success", False), "action": action, "data": result}

            elif action == "set_dates":
                if not any([created, modified, accessed]):
                    return {"success": False, "error": "At least one date (created, modified, accessed) is required", "action": action}
                result = set_file_dates_tool(
                    file_path=file_path,
                    created=created,
                    modified=modified,
                    accessed=accessed
                )
                return {"success": result.get("success", False), "action": action, "data": result}

        except Exception as e:
            logger.error(f"Error in file_attributes action '{action}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute {action}: {str(e)}",
                "action": action,
            }

