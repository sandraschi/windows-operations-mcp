"""
Media Metadata Portmanteau Tool

Consolidates media metadata operations into a single tool.
"""

import logging
from typing import Any, Literal, Optional

from fastmcp import FastMCP

# Import existing functions
from ..media_metadata import (
    get_media_metadata,
    update_media_metadata,
    get_image_metadata,
    update_image_metadata,
    get_mp3_metadata,
    update_mp3_metadata,
)

logger = logging.getLogger(__name__)


def register_media_metadata_tool(mcp: FastMCP) -> None:
    """Register the media metadata portmanteau tool."""

    @mcp.tool()
    async def media_metadata(
        action: Literal["get_media", "update_media", "get_image", "update_image", "get_mp3", "update_mp3"],
        file_path: str,
        metadata: Optional[dict[str, Any]] = None,
        save_copy: bool = False,
    ) -> dict[str, Any]:
        """
        Comprehensive media metadata portmanteau tool.
        
        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 6 separate tools (one per operation), this tool consolidates related
        media metadata operations into a single interface. This design:
        - Prevents tool explosion (6 tools → 1 tool) while maintaining full functionality
        - Improves discoverability by grouping related operations together
        - Reduces cognitive load when working with media files
        - Enables consistent metadata handling across different media types
        - Follows FastMCP 2.12+ best practices for feature-rich MCP servers
        
        Args:
            action (Literal["get_media", "update_media", "get_image", "update_image", "get_mp3", "update_mp3"]):
                The operation to perform. Required for all operations. Must be one of:
                - "get_media": Get metadata from any media file
                - "update_media": Update metadata for any media file
                - "get_image": Get EXIF metadata from image
                - "update_image": Update EXIF metadata for image
                - "get_mp3": Get ID3 metadata from MP3
                - "update_mp3": Update ID3 metadata for MP3
            
            file_path (str): Path to the media file. Required for all operations.
            
            metadata (dict[str, Any] | None): Dictionary of metadata to update. Required for: update_media,
                update_image, update_mp3 operations. Optional for: get operations.
                Example: {"title": "My Song", "artist": "Artist Name", "album": "Album Name"}
            
            save_copy (bool): Save to a copy instead of modifying original. Optional for all operations.
                Default: False. Used by: update_media, update_image, update_mp3 operations.
        
        Returns:
            Dict containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict | Any): Operation-specific result data (includes metadata fields)
                - error (str): Error message if success is False
        
        Examples:
            # Get image metadata
            result = await media_metadata(action="get_image", file_path="C:\\photo.jpg")
            
            # Update MP3 metadata
            result = await media_metadata(
                action="update_mp3",
                file_path="C:\\song.mp3",
                metadata={"title": "New Title", "artist": "New Artist"}
            )
            
            # Get media metadata (auto-detects type)
            result = await media_metadata(action="get_media", file_path="C:\\media.mp4")
        """
        try:
            if action not in ["get_media", "update_media", "get_image", "update_image", "get_mp3", "update_mp3"]:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'",
                    "action": action,
                }

            logger.info(f"Executing media_metadata action: {action}")

            if action == "get_media":
                result = get_media_metadata(file_path=file_path)
                return {"success": True, "action": action, "data": result}

            elif action == "update_media":
                if not metadata:
                    return {"success": False, "error": "metadata is required for update_media action", "action": action}
                result = update_media_metadata(file_path=file_path, metadata=metadata, save_copy=save_copy)
                return {"success": True, "action": action, "data": result}

            elif action == "get_image":
                result = get_image_metadata(image_path=file_path)
                return {"success": True, "action": action, "data": result}

            elif action == "update_image":
                if not metadata:
                    return {"success": False, "error": "metadata is required for update_image action", "action": action}
                result = update_image_metadata(image_path=file_path, metadata=metadata, save_copy=save_copy)
                return {"success": True, "action": action, "data": result}

            elif action == "get_mp3":
                result = get_mp3_metadata(mp3_path=file_path)
                return {"success": True, "action": action, "data": result}

            elif action == "update_mp3":
                if not metadata:
                    return {"success": False, "error": "metadata is required for update_mp3 action", "action": action}
                result = update_mp3_metadata(mp3_path=file_path, metadata=metadata, save_copy=save_copy)
                return {"success": True, "action": action, "data": result}

        except Exception as e:
            logger.error(f"Error in media_metadata action '{action}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute {action}: {str(e)}",
                "action": action,
            }

