"""
Windows Permissions Portmanteau Tool

Consolidates Windows Permissions operations into a single tool.
"""

import logging
from typing import Any, Literal, Optional

from fastmcp import FastMCP

# Import existing functions
from ..windows_permissions import (
    get_file_permissions,
    set_file_permissions,
    analyze_directory_permissions,
    fix_file_permissions,
)

logger = logging.getLogger(__name__)


def register_windows_permissions_tool(mcp: FastMCP) -> None:
    """Register the Windows Permissions portmanteau tool."""

    @mcp.tool()
    async def windows_permissions(
        action: Literal["get_file", "set_file", "analyze_directory", "fix"],
        file_path: str,
        permissions: Optional[str] = None,
        recursive: bool = False,
        include_owner: bool = True,
        include_group: bool = True,
        max_depth: int = 3,
        include_files: bool = True,
        fix_type: str = "readable",
    ) -> dict[str, Any]:
        """
        Comprehensive Windows Permissions portmanteau tool.
        
        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 4 separate tools (one per operation), this tool consolidates related
        Windows Permissions operations into a single interface. This design:
        - Prevents tool explosion (4 tools → 1 tool) while maintaining full functionality
        - Improves discoverability by grouping related operations together
        - Reduces cognitive load when working with file permissions
        - Enables atomic batch operations across multiple permission actions
        - Follows FastMCP 2.12+ best practices for feature-rich MCP servers
        
        Args:
            action (Literal["get_file", "set_file", "analyze_directory", "fix"]): The operation to perform.
                Required for all operations. Must be one of:
                - "get_file": Get file/directory permissions
                - "set_file": Set file/directory permissions
                - "analyze_directory": Analyze directory permissions recursively
                - "fix": Fix common permission issues
            
            file_path (str): Path to file or directory. Required for all operations.
            
            permissions (str | None): Permissions string. Required for: set_file operation.
                Optional for: other operations. Format: Windows ACL string (e.g., "Users:F").
            
            recursive (bool): Apply recursively. Optional for all operations. Default: False
                Used by: set_file, fix operations.
            
            include_owner (bool): Include owner information. Optional for all operations. Default: True
                Used by: get_file operation.
            
            include_group (bool): Include group information. Optional for all operations. Default: True
                Used by: get_file operation.
            
            max_depth (int): Maximum recursion depth. Optional for all operations. Default: 3
                Used by: analyze_directory operation.
            
            include_files (bool): Include files in analysis. Optional for all operations. Default: True
                Used by: analyze_directory operation.
            
            fix_type (str): Fix type. Optional for all operations. Default: "readable"
                Used by: fix operation. Valid: "readable", "writable", "executable"
        
        Returns:
            Dict containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict | Any): Operation-specific result data
                - error (str): Error message if success is False
        
        Examples:
            # Get file permissions
            result = await windows_permissions(
                action="get_file",
                file_path="C:\\file.txt"
            )
            
            # Set file permissions
            result = await windows_permissions(
                action="set_file",
                file_path="C:\\file.txt",
                permissions="Users:F"
            )
            
            # Analyze directory permissions
            result = await windows_permissions(
                action="analyze_directory",
                file_path="C:\\project",
                max_depth=5
            )
            
            # Fix permissions
            result = await windows_permissions(
                action="fix",
                file_path="C:\\file.txt",
                fix_type="readable"
            )
        """
        try:
            if action not in ["get_file", "set_file", "analyze_directory", "fix"]:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Available: get_file, set_file, analyze_directory, fix",
                    "action": action,
                }

            logger.info(f"Executing windows_permissions action: {action}")

            if action == "get_file":
                result = get_file_permissions(
                    file_path=file_path,
                    include_owner=include_owner,
                    include_group=include_group
                )
                return {"success": result.get("success", False), "action": action, "data": result}

            elif action == "set_file":
                if not permissions:
                    return {"success": False, "error": "permissions is required for set_file action", "action": action}
                result = set_file_permissions(
                    file_path=file_path,
                    permissions=permissions,
                    recursive=recursive
                )
                return {"success": result.get("success", False), "action": action, "data": result}

            elif action == "analyze_directory":
                result = analyze_directory_permissions(
                    directory_path=file_path,
                    max_depth=max_depth,
                    include_files=include_files
                )
                return {"success": result.get("success", False), "action": action, "data": result}

            elif action == "fix":
                result = fix_file_permissions(
                    file_path=file_path,
                    fix_type=fix_type,
                    recursive=recursive
                )
                return {"success": result.get("success", False), "action": action, "data": result}

        except Exception as e:
            logger.error(f"Error in windows_permissions action '{action}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute {action}: {str(e)}",
                "action": action,
            }

