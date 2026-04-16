"""
File operations tool registration for FastMCP.
"""

from fastmcp import FastMCP


def register_file_operations(mcp: FastMCP) -> None:
    """Register all file operation tools with FastMCP."""
    from .edit import register_edit_tools
    from .file_operations import copy_file, delete_file, move_file, read_file, write_file
    from .folder_operations import (
        copy_directory_safe,
        create_directory_safe,
        delete_directory_safe,
        list_directory_contents,
        move_directory_safe,
    )

    # Register file operations
    mcp.tool(read_file)
    mcp.tool(write_file)
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
