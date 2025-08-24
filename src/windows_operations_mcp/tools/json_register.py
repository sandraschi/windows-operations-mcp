"""
JSON Tools Registration for FastMCP

Registers all JSON-related tools with FastMCP.
"""
from typing import Any

from fastmcp import FastMCP

def register_json_tools(mcp: FastMCP) -> None:
    """Register all JSON tools with FastMCP."""
    from .json_tools import (
        read_json_file,
        write_json_file,
        validate_json,
        format_json_string,
        convert_to_json,
        extract_json_from_text
    )
    
    # Register JSON tools
    mcp.tool(read_json_file, name="read_json_file")
    mcp.tool(write_json_file, name="write_json_file")
    mcp.tool(validate_json, name="validate_json")
    mcp.tool(format_json_string, name="format_json")
    mcp.tool(convert_to_json, name="to_json")
    mcp.tool(extract_json_from_text, name="extract_json")
