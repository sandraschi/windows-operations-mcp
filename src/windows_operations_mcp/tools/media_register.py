"""
Media Metadata Tools Registration for FastMCP

Registers all media metadata-related tools with FastMCP.
"""
from typing import Any

from fastmcp import FastMCP

def register_media_tools(mcp: FastMCP) -> None:
    """Register all media metadata tools with FastMCP."""
    from .media_metadata import (
        get_media_metadata,
        update_media_metadata,
        get_image_metadata,
        update_image_metadata,
        get_mp3_metadata,
        update_mp3_metadata
    )
    
    # Register media metadata tools
    mcp.tool(get_media_metadata, name="get_media_metadata")
    mcp.tool(update_media_metadata, name="update_media_metadata")
    mcp.tool(get_image_metadata, name="get_image_metadata")
    mcp.tool(update_image_metadata, name="update_image_metadata")
    mcp.tool(get_mp3_metadata, name="get_mp3_metadata")
    mcp.tool(update_mp3_metadata, name="update_mp3_metadata")
