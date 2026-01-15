"""
File Operations Portmanteau Tool for Windows Operations MCP.

Consolidates core file operations (read, write, delete, move, copy) into a single portmanteau tool.
These are the most frequently used file operations.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Literal

from ...logging_config import get_logger

logger = get_logger(__name__)


def file_operations(
    action: Literal["read", "write", "delete", "move", "copy", "list", "info", "exists"],
    path: str,
    content: Optional[str] = None,
    destination: Optional[str] = None,
    overwrite: bool = False,
    encoding: str = "utf-8",
    create_dirs: bool = False
) -> Dict[str, Any]:
    """
    Perform core file operations with comprehensive error handling.

    FEATURES:
    - All essential file operations in single tool (read, write, delete, move, copy)
    - Directory listing and information retrieval
    - Safe operations with overwrite protection
    - Unicode encoding support (UTF-8 default)
    - Automatic parent directory creation
    - Comprehensive error handling and validation

    Args:
        action: The file operation to perform. Must be one of:
            - "read": Read file content as text
            - "write": Create or overwrite file with content
            - "delete": Delete file or directory (recursive for directories)
            - "move": Move file/directory to new location
            - "copy": Copy file/directory to new location
            - "list": List directory contents with metadata
            - "info": Get detailed file/directory information
            - "exists": Check if path exists and get basic info
        path: File or directory path (required, validated for existence where needed)
        content: Text content to write (required for "write" action)
        destination: Destination path (required for "move" and "copy" actions)
        overwrite: Whether to overwrite existing files/directories (default: False)
        encoding: Text encoding for read/write operations (default: "utf-8")
        create_dirs: Create parent directories automatically (default: False, for write operations)

    Returns:
        FastMCP 2.14.1+ enhanced response with:
            - success: bool - Whether the operation succeeded
            - action: str - The action that was performed
            - data: dict - Action-specific result data (varies by operation)
            - error: str - Error message (only present if success is False)

    Examples:
        # Read a text file
        result = await file_operations(action="read", path="config.txt")
        if result["success"]:
            print(f"File content: {result['data']['content']}")

        # Write to a file with directory creation
        result = await file_operations(
            action="write",
            path="logs/app.log",
            content="Application started",
            create_dirs=True
        )

        # Check if file exists
        result = await file_operations(action="exists", path="important.txt")
        if result["success"] and result["data"]["exists"]:
            print(f"File exists: {result['data']['is_file']}")

        # List directory contents
        result = await file_operations(action="list", path=".")
        if result["success"]:
            print(f"Found {result['data']['count']} items")

        # Move file safely
        result = await file_operations(
            action="move",
            path="temp.txt",
            destination="archive/temp.txt",
            overwrite=False
        )

    Notes:
        - All paths are validated and normalized
        - Directory operations handle both files and directories appropriately
        - Unicode encoding ensures proper text handling
        - Overwrite protection prevents accidental data loss
        - Recursive deletion for directories (use with caution)
        - File info includes size, timestamps, and permissions
    """
    logger.info("file_operations_started", action=action, path=path)

    try:
        # Validate path
        if not path or not isinstance(path, str):
            return {
                "success": False,
                "action": action,
                "error": "Path must be a non-empty string"
            }

        path_obj = Path(path)

        # Route to appropriate action
        if action == "read":
            if not path_obj.exists():
                return {
                    "success": False,
                    "action": action,
                    "error": f"File does not exist: {path}"
                }

            if not path_obj.is_file():
                return {
                    "success": False,
                    "action": action,
                    "error": f"Path is not a file: {path}"
                }

            try:
                with open(path_obj, 'r', encoding=encoding) as f:
                    content = f.read()
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "content": content,
                        "size": len(content),
                        "encoding": encoding
                    }
                }
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "action": action,
                    "error": f"File cannot be read with encoding {encoding}: {path}"
                }

        elif action == "write":
            if content is None:
                return {
                    "success": False,
                    "action": action,
                    "error": "Content is required for write action"
                }

            if path_obj.exists() and not overwrite:
                return {
                    "success": False,
                    "action": action,
                    "error": f"File already exists and overwrite=False: {path}"
                }

            if create_dirs:
                path_obj.parent.mkdir(parents=True, exist_ok=True)

            try:
                with open(path_obj, 'w', encoding=encoding) as f:
                    f.write(content)
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "path": str(path_obj),
                        "size": len(content),
                        "encoding": encoding
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Failed to write file: {str(e)}"
                }

        elif action == "delete":
            if not path_obj.exists():
                return {
                    "success": False,
                    "action": action,
                    "error": f"Path does not exist: {path}"
                }

            try:
                if path_obj.is_file():
                    path_obj.unlink()
                elif path_obj.is_dir():
                    shutil.rmtree(path_obj)
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "path": str(path_obj),
                        "was_directory": path_obj.is_dir()
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Failed to delete: {str(e)}"
                }

        elif action == "move":
            if destination is None:
                return {
                    "success": False,
                    "action": action,
                    "error": "Destination is required for move action"
                }

            if not path_obj.exists():
                return {
                    "success": False,
                    "action": action,
                    "error": f"Source does not exist: {path}"
                }

            dest_obj = Path(destination)
            if dest_obj.exists() and not overwrite:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Destination already exists and overwrite=False: {destination}"
                }

            try:
                shutil.move(str(path_obj), str(dest_obj))
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "from": str(path_obj),
                        "to": str(dest_obj)
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Failed to move: {str(e)}"
                }

        elif action == "copy":
            if destination is None:
                return {
                    "success": False,
                    "action": action,
                    "error": "Destination is required for copy action"
                }

            if not path_obj.exists():
                return {
                    "success": False,
                    "action": action,
                    "error": f"Source does not exist: {path}"
                }

            dest_obj = Path(destination)
            if dest_obj.exists() and not overwrite:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Destination already exists and overwrite=False: {destination}"
                }

            try:
                if path_obj.is_file():
                    shutil.copy2(str(path_obj), str(dest_obj))
                elif path_obj.is_dir():
                    shutil.copytree(str(path_obj), str(dest_obj), dirs_exist_ok=overwrite)
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "from": str(path_obj),
                        "to": str(dest_obj),
                        "was_directory": path_obj.is_dir()
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Failed to copy: {str(e)}"
                }

        elif action == "list":
            if not path_obj.exists():
                return {
                    "success": False,
                    "action": action,
                    "error": f"Path does not exist: {path}"
                }

            if not path_obj.is_dir():
                return {
                    "success": False,
                    "action": action,
                    "error": f"Path is not a directory: {path}"
                }

            try:
                items = []
                for item in path_obj.iterdir():
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "is_file": item.is_file(),
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0
                    })

                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "path": str(path_obj),
                        "items": items,
                        "count": len(items)
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Failed to list directory: {str(e)}"
                }

        elif action == "info":
            if not path_obj.exists():
                return {
                    "success": False,
                    "action": action,
                    "error": f"Path does not exist: {path}"
                }

            try:
                stat = path_obj.stat()
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "path": str(path_obj),
                        "name": path_obj.name,
                        "is_file": path_obj.is_file(),
                        "is_dir": path_obj.is_dir(),
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "created": stat.st_ctime,
                        "mode": oct(stat.st_mode)
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Failed to get info: {str(e)}"
                }

        elif action == "exists":
            return {
                "success": True,
                "action": action,
                "data": {
                    "path": str(path_obj),
                    "exists": path_obj.exists(),
                    "is_file": path_obj.is_file() if path_obj.exists() else False,
                    "is_dir": path_obj.is_dir() if path_obj.exists() else False
                }
            }

        else:
            return {
                "success": False,
                "action": action,
                "error": f"Unknown action: {action}"
            }

    except Exception as e:
        error_msg = f"File operation failed: {str(e)}"
        logger.error("file_operations_error", action=action, path=path, error=error_msg, exc_info=True)
        return {
            "success": False,
            "action": action,
            "error": error_msg
        }


def register_file_operations(mcp):
    """Register the file operations portmanteau tool with FastMCP."""
    mcp.tool(file_operations)