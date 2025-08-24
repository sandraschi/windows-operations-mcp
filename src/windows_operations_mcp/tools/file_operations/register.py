"""
File operations tool registration for FastMCP.
"""
from typing import Any, Dict

from fastmcp import FastMCP

def register_file_operations(mcp: FastMCP) -> None:
    """Register all file operation tools with FastMCP."""
    from .file_operations import (
        create_file,
        delete_file,
        move_file,
        copy_file
    )
    
    from .folder_operations import (
        list_directory_contents,
        create_directory_safe,
        delete_directory_safe,
        move_directory_safe,
        copy_directory_safe
    )
    
    from .edit import register_edit_tools
    
    # Register file operations
    mcp.tool(create_file)
    mcp.tool(delete_file)
    mcp.tool(move_file)
    mcp.tool(copy_file)
    
    # Register folder operations
    mcp.tool(list_directory_contents, name="list_directory")
    mcp.tool(create_directory_safe, name="create_directory")
    mcp.tool(delete_directory_safe, name="delete_directory")
    mcp.tool(move_directory_safe, name="move_directory")
    mcp.tool(copy_directory_safe, name="copy_directory")
    
    # Register edit tools
    register_edit_tools(mcp)
