"""
File Editing Portmanteau Tool

Consolidates file editing operations into a single tool.
"""

import logging
from typing import Any, Literal, Optional

from fastmcp import FastMCP

# Import existing functions
from ..file_operations.edit import edit_file, fix_markdown

logger = logging.getLogger(__name__)


def register_file_editing_tool(mcp: FastMCP) -> None:
    """Register the file editing portmanteau tool."""

    @mcp.tool()
    async def file_editing(
        action: Literal["edit", "fix_markdown"],
        file_path: str,
        edit_function: Optional[str] = None,
        encoding: str = "utf-8",
        backup: bool = True,
        backup_dir: Optional[str] = None,
        create_dirs: bool = True,
    ) -> dict[str, Any]:
        """
        Comprehensive file editing portmanteau tool.
        
        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 2 separate tools (one per operation), this tool consolidates related
        file editing operations into a single interface. This design:
        - Prevents tool explosion (2 tools → 1 tool) while maintaining full functionality
        - Improves discoverability by grouping related operations together
        - Reduces cognitive load when working with file editing tasks
        - Enables consistent backup and error handling across edit operations
        - Follows FastMCP 2.12+ best practices for feature-rich MCP servers
        
        Args:
            action (Literal["edit", "fix_markdown"]): The operation to perform. Required for all operations.
                Must be one of:
                - "edit": Edit file using a Python function
                - "fix_markdown": Fix common Markdown formatting issues
            
            file_path (str): Path to the file to edit. Required for all operations.
            
            edit_function (str | None): Python code string defining an 'edit' function. Required for: edit operation.
                Optional for: fix_markdown operation. The function must be named 'edit' and take content as parameter.
                Example: 'def edit(content): return content.replace("old", "new")'
            
            encoding (str): File encoding. Optional for all operations. Default: "utf-8"
                Used by: all operations.
            
            backup (bool): Create backup before editing. Optional for all operations. Default: True
                Used by: all operations.
            
            backup_dir (str | None): Directory for backups. Optional for all operations. Default: None
                (uses same directory as file). Used by: all operations.
            
            create_dirs (bool): Create parent directories if needed. Optional for all operations.
                Default: True. Used by: all operations.
        
        Returns:
            Dict containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict | Any): Operation-specific result data (includes modified status, backup path)
                - error (str): Error message if success is False
        
        Examples:
            # Edit file with custom function
            result = await file_editing(
                action="edit",
                file_path="C:\\file.txt",
                edit_function='def edit(content): return content.upper()'
            )
            
            # Fix Markdown formatting
            result = await file_editing(
                action="fix_markdown",
                file_path="C:\\readme.md"
            )
        """
        try:
            if action not in ["edit", "fix_markdown"]:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Available: edit, fix_markdown",
                    "action": action,
                }

            logger.info(f"Executing file_editing action: {action}")

            if action == "edit":
                if not edit_function:
                    return {"success": False, "error": "edit_function is required for edit action", "action": action}
                
                # Create namespace for edit function
                namespace = {}
                exec(edit_function, globals(), namespace)
                
                if 'edit' not in namespace or not callable(namespace['edit']):
                    return {
                        "success": False,
                        "error": 'edit_function must define a function named "edit"',
                        "action": action,
                    }
                
                editor_func = namespace['edit']
                result = edit_file(
                    filepath=file_path,
                    editor_func=editor_func,
                    encoding=encoding,
                    backup=backup,
                    backup_dir=backup_dir,
                    create_dirs=create_dirs
                )
                return {"success": True, "action": action, "data": result}

            elif action == "fix_markdown":
                result = edit_file(
                    filepath=file_path,
                    editor_func=fix_markdown,
                    encoding=encoding,
                    backup=backup,
                    backup_dir=backup_dir,
                    create_dirs=create_dirs
                )
                return {"success": True, "action": action, "data": result}

        except Exception as e:
            logger.error(f"Error in file_editing action '{action}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute {action}: {str(e)}",
                "action": action,
            }

