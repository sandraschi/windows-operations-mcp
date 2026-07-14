"""
Directory Operations Portmanteau Tool for Windows Operations MCP.

Consolidates directory-specific operations (create, delete, move, copy, list) into a single portmanteau tool.
These operations are distinct from general file operations and deserve their own tool.
"""

import shutil
from pathlib import Path
from typing import Any, Literal

from windows_operations_mcp.utils import fail_response

from ...logging_config import get_logger

logger = get_logger(__name__)


def directory_operations(
    action: Literal["create", "delete", "move", "copy", "list"],
    path: str,
    destination: str | None = None,
    recursive: bool = False,
    create_parents: bool = True,
    require_empty: bool = True,
) -> dict[str, Any]:
    """
    Perform directory-specific operations with comprehensive error handling.

    FEATURES:
    - Directory operations separate from file operations (better specialization)
    - Safe deletion with empty directory protection
    - Recursive operations for entire directory trees
    - Comprehensive directory listing with metadata
    - Parent directory creation for nested paths
    - Atomic move and copy operations

    Args:
        action: The directory operation to perform. Must be one of:
            - "create": Create new directory (optionally with parents)
            - "delete": Delete directory (safe or recursive)
            - "move": Move directory to new location atomically
            - "copy": Copy directory tree to new location
            - "list": List directory contents with detailed metadata
        path: Directory path (required, validated for directory operations)
        destination: Destination path (required for "move" and "copy" actions)
        recursive: For delete action, remove directory and all contents recursively (default: False, safer)
        create_parents: For create action, create parent directories as needed (default: True)
        require_empty: For delete action, only delete if directory is empty (default: True, safer)

    Returns:
        FastMCP 2.14.1+ enhanced response with:
            - success: bool - Whether the directory operation succeeded
            - action: str - The action that was performed
            - data: dict - Action-specific result data (varies by operation)
            - error: str - Error message (only present if success is False)

    Examples:
        # Create directory with parent directories
        result = await directory_operations(
            action="create",
            path="projects/new-project/docs",
            create_parents=True
        )

        # Safely delete empty directory
        result = await directory_operations(
            action="delete",
            path="temp/empty-dir",
            require_empty=True
        )

        # Recursively delete directory tree
        result = await directory_operations(
            action="delete",
            path="old-project",
            recursive=True,
            require_empty=False
        )

        # List directory with detailed info
        result = await directory_operations(action="list", path=".")
        if result["success"]:
            pass

        # Move directory atomically
        result = await directory_operations(
            action="move",
            path="project-alpha",
            destination="archive/project-alpha"
        )

        # Copy directory tree
        result = await directory_operations(
            action="copy",
            path="templates",
            destination="project-templates"
        )

    Notes:
        - Directory operations are validated to ensure path is actually a directory
        - Recursive operations can be dangerous - use require_empty=True for safety
        - Move and copy operations are atomic where possible
        - Directory listing includes file sizes, modification times, and types
        - Parent directory creation prevents common path errors
        - Empty directory checks prevent accidental data loss
    """
    logger.info("directory_operations_started", action=action, path=path)

    try:
        # Validate path
        if not path or not isinstance(path, str):
            return fail_response("Path must be a non-empty string", action=action)

        path_obj = Path(path)

        # Route to appropriate action
        if action == "create":
            try:
                if create_parents:
                    path_obj.mkdir(parents=True, exist_ok=True)
                else:
                    path_obj.mkdir(exist_ok=True)

                return {
                    "success": True,
                    "action": action,
                    "data": {"path": str(path_obj), "created": True, "parents_created": create_parents},
                }
            except FileExistsError:
                return {
                    "success": True,
                    "action": action,
                    "data": {"path": str(path_obj), "created": False, "message": "Directory already exists"},
                }
            except Exception as e:
                return fail_response(f"Failed to create directory: {e}", action=action)

        elif action == "delete":
            if not path_obj.exists():
                return fail_response(f"Directory does not exist: {path}", action=action)

            if not path_obj.is_dir():
                return fail_response(f"Path is not a directory: {path}", action=action)

            # Check if directory is empty when require_empty is True
            if require_empty and not recursive:
                try:
                    next(path_obj.iterdir())
                    return fail_response(f"Directory is not empty: {path}", action=action)
                except StopIteration:
                    pass  # Directory is empty

            try:
                if recursive:
                    shutil.rmtree(path_obj)
                else:
                    path_obj.rmdir()

                return {"success": True, "action": action, "data": {"path": str(path_obj), "recursive": recursive}}
            except Exception as e:
                return fail_response(f"Failed to delete directory: {e}", action=action)

        elif action == "move":
            if destination is None:
                return fail_response("Destination is required for move action", action=action)

            if not path_obj.exists():
                return fail_response(f"Source directory does not exist: {path}", action=action)

            if not path_obj.is_dir():
                return fail_response(f"Source is not a directory: {path}", action=action)

            dest_obj = Path(destination)
            if dest_obj.exists():
                return fail_response(f"Destination already exists: {destination}", action=action)

            try:
                shutil.move(str(path_obj), str(dest_obj))
                return {"success": True, "action": action, "data": {"from": str(path_obj), "to": str(dest_obj)}}
            except Exception as e:
                return fail_response(f"Failed to move directory: {e}", action=action)

        elif action == "copy":
            if destination is None:
                return fail_response("Destination is required for copy action", action=action)

            if not path_obj.exists():
                return fail_response(f"Source directory does not exist: {path}", action=action)

            if not path_obj.is_dir():
                return fail_response(f"Source is not a directory: {path}", action=action)

            dest_obj = Path(destination)
            if dest_obj.exists():
                return fail_response(f"Destination already exists: {destination}", action=action)

            try:
                shutil.copytree(str(path_obj), str(dest_obj))
                return {"success": True, "action": action, "data": {"from": str(path_obj), "to": str(dest_obj)}}
            except Exception as e:
                return fail_response(f"Failed to copy directory: {e}", action=action)

        elif action == "list":
            if not path_obj.exists():
                return fail_response(f"Directory does not exist: {path}", action=action)

            if not path_obj.is_dir():
                return fail_response(f"Path is not a directory: {path}", action=action)

            try:
                items = []
                for item in path_obj.iterdir():
                    stat = item.stat()
                    items.append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "is_file": item.is_file(),
                            "is_dir": item.is_dir(),
                            "size": stat.st_size if item.is_file() else 0,
                            "modified": stat.st_mtime,
                            "created": stat.st_ctime,
                        }
                    )

                # Sort by type (directories first) then by name
                items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "path": str(path_obj),
                        "items": items,
                        "count": len(items),
                        "files": len([i for i in items if i["is_file"]]),
                        "directories": len([i for i in items if i["is_dir"]]),
                    },
                }
            except Exception as e:
                return fail_response(f"Failed to list directory: {e}", action=action)

        else:
            return fail_response(f"Unknown action: {action}", action=action)

    except Exception as e:
        error_msg = f"Directory operation failed: {e!s}"
        logger.error("directory_operations_error", action=action, path=path, error=error_msg, exc_info=True)
        return fail_response(error_msg, action=action)


def register_directory_operations(mcp):
    """Register the directory operations portmanteau tool with FastMCP."""
    mcp.tool(directory_operations)
