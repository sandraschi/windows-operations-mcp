"""
JSON Tools Registration for FastMCP

Registers all JSON-related tools with FastMCP.
"""

from fastmcp import FastMCP


def register_json_tools(mcp: FastMCP) -> None:
    """Register all JSON tools with FastMCP."""
    from .json_tools import (
        convert_to_json,
        extract_json_from_text,
        format_json_string,
        read_json_file,
        validate_json,
        write_json_file,
    )

    # Register JSON tools
    mcp.tool(read_json_file, name="read_json_file")
    mcp.tool(write_json_file, name="write_json_file")
    mcp.tool(validate_json, name="validate_json")
    mcp.tool(format_json_string, name="format_json")
    mcp.tool(convert_to_json, name="to_json")
    mcp.tool(extract_json_from_text, name="extract_json")
