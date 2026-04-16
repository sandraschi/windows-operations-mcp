"""
Windows Permissions Management Tools for Windows Operations MCP.

This module provides comprehensive Windows permissions and security management functionality
including file permissions, share permissions, and access control management.
"""

import os
import stat
from datetime import datetime
from pathlib import Path
from typing import Any

from ..decorators import tool
from ..logging_config import get_logger

logger = get_logger(__name__)


def _get_permission_string(mode: int) -> str:
    """Convert numeric permissions to readable string."""
    permissions = []

    # Owner permissions
    if mode & stat.S_IRUSR:
        permissions.append("r")
    else:
        permissions.append("-")

    if mode & stat.S_IWUSR:
        permissions.append("w")
    else:
        permissions.append("-")

    if mode & stat.S_IXUSR:
        permissions.append("x")
    else:
        permissions.append("-")

    # Group permissions
    if mode & stat.S_IRGRP:
        permissions.append("r")
    else:
        permissions.append("-")

    if mode & stat.S_IWGRP:
        permissions.append("w")
    else:
        permissions.append("-")

    if mode & stat.S_IXGRP:
        permissions.append("x")
    else:
        permissions.append("-")

    # Other permissions
    if mode & stat.S_IROTH:
        permissions.append("r")
    else:
        permissions.append("-")

    if mode & stat.S_IWOTH:
        permissions.append("w")
    else:
        permissions.append("-")

    if mode & stat.S_IXOTH:
        permissions.append("x")
    else:
        permissions.append("-")

    return "".join(permissions)


def _get_file_type(mode: int) -> str:
    """Get file type from mode."""
    if stat.S_ISDIR(mode):
        return "directory"
    elif stat.S_ISREG(mode):
        return "file"
    elif stat.S_ISLNK(mode):
        return "symbolic_link"
    elif stat.S_ISCHR(mode):
        return "character_device"
    elif stat.S_ISBLK(mode):
        return "block_device"
    elif stat.S_ISFIFO(mode):
        return "fifo"
    elif stat.S_ISSOCK(mode):
        return "socket"
    else:
        return "unknown"


@tool(
    name="get_file_permissions",
    description="Get detailed file and directory permissions information",
    parameters={
        "file_path": {"type": "string", "description": "Path to the file or directory"},
        "include_owner": {"type": "boolean", "description": "Include owner information", "default": True},
        "include_group": {"type": "boolean", "description": "Include group information", "default": True},
    },
    required=["file_path"],
    returns={
        "type": "object",
        "properties": {"success": {"type": "boolean"}, "permissions": {"type": "object"}, "error": {"type": "string"}},
    },
)
def get_file_permissions(file_path: str, include_owner: bool = True, include_group: bool = True) -> dict[str, Any]:
    """
    Get detailed file and directory permissions information.

    Args:
        file_path: Path to the file or directory
        include_owner: Include owner information
        include_group: Include group information

    Returns:
        Dictionary with detailed permissions information
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {"success": False, "error": f"Path does not exist: {file_path}"}

        # Get file stats
        stat_info = path.stat()

        # Get file mode and permissions
        mode = stat_info.st_mode
        permissions = _get_permission_string(mode)
        file_type = _get_file_type(mode)

        result = {
            "path": str(path),
            "type": file_type,
            "permissions": permissions,
            "mode": oct(mode),
            "size": stat_info.st_size,
            "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            "created_time": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
        }

        # Get owner information
        if include_owner:
            try:
                import grp
                import pwd

                # Get owner and group info
                try:
                    owner_info = pwd.getpwuid(stat_info.st_uid)
                    result["owner"] = {
                        "uid": stat_info.st_uid,
                        "name": owner_info.pw_name,
                        "gecos": owner_info.pw_gecos,
                    }
                except (AttributeError, KeyError, ImportError):
                    result["owner"] = {"uid": stat_info.st_uid, "name": "Unknown"}

                try:
                    group_info = grp.getgrgid(stat_info.st_gid)
                    result["group"] = {"gid": stat_info.st_gid, "name": group_info.gr_name}
                except (AttributeError, KeyError, ImportError):
                    result["group"] = {"gid": stat_info.st_gid, "name": "Unknown"}

            except ImportError:
                # Unix-style user/group info not available on Windows
                result["owner"] = {"uid": "N/A", "name": "Windows User"}
                result["group"] = {"gid": "N/A", "name": "Windows Group"}

        return {"success": True, "permissions": result}

    except Exception as e:
        return {"success": False, "error": f"Failed to get permissions: {e!s}"}


@tool(
    name="set_file_permissions",
    description="Set file or directory permissions",
    parameters={
        "file_path": {"type": "string", "description": "Path to the file or directory"},
        "permissions": {"type": "string", "description": "Permission string (e.g., 'rwxr-xr-x')"},
        "recursive": {
            "type": "boolean",
            "description": "Apply permissions recursively to directories",
            "default": False,
        },
    },
    required=["file_path", "permissions"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "applied_to": {"type": "array", "items": {"type": "string"}},
        },
    },
)
def set_file_permissions(file_path: str, permissions: str, recursive: bool = False) -> dict[str, Any]:
    """
    Set file or directory permissions.

    Args:
        file_path: Path to the file or directory
        permissions: Permission string (e.g., 'rwxr-xr-x')
        recursive: Apply permissions recursively to directories

    Returns:
        Dictionary with operation result
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {"success": False, "error": f"Path does not exist: {file_path}"}

        applied_to = []

        if path.is_file():
            # Set permissions on single file
            try:
                os.chmod(file_path, int(permissions, 8))
                applied_to.append(str(path))
            except Exception as e:
                return {"success": False, "error": f"Failed to set permissions on {file_path}: {e!s}"}

        elif path.is_dir() and recursive:
            # Set permissions recursively on directory
            for root, _dirs, files in os.walk(file_path):
                for file in files:
                    file_path_full = os.path.join(root, file)
                    try:
                        os.chmod(file_path_full, int(permissions, 8))
                        applied_to.append(file_path_full)
                    except Exception as e:
                        logger.warning(f"Failed to set permissions on {file_path_full}: {e}")

        elif path.is_dir():
            # Set permissions on directory only
            try:
                os.chmod(file_path, int(permissions, 8))
                applied_to.append(str(path))
            except Exception as e:
                return {"success": False, "error": f"Failed to set permissions on {file_path}: {e!s}"}

        return {
            "success": True,
            "message": f"Permissions set successfully on {len(applied_to)} items",
            "applied_to": applied_to,
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to set permissions: {e!s}"}


@tool(
    name="analyze_directory_permissions",
    description="Analyze permissions for all files and directories in a directory tree",
    parameters={
        "directory_path": {"type": "string", "description": "Path to the directory to analyze"},
        "max_depth": {"type": "integer", "description": "Maximum depth to analyze", "default": 3},
        "include_files": {"type": "boolean", "description": "Include files in analysis", "default": True},
        "include_directories": {"type": "boolean", "description": "Include directories in analysis", "default": True},
    },
    required=["directory_path"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "analysis": {"type": "object"},
            "directory_path": {"type": "string"},
        },
    },
)
def analyze_directory_permissions(
    directory_path: str, max_depth: int = 3, include_files: bool = True, include_directories: bool = True
) -> dict[str, Any]:
    """
    Analyze permissions for all files and directories in a directory tree.

    Args:
        directory_path: Path to the directory to analyze
        max_depth: Maximum depth to analyze
        include_files: Include files in analysis
        include_directories: Include directories in analysis

    Returns:
        Dictionary with permission analysis
    """
    try:
        path = Path(directory_path)

        if not path.exists() or not path.is_dir():
            return {"success": False, "error": f"Directory does not exist: {directory_path}"}

        permission_stats = {}
        analyzed_items = []

        for root, dirs, files in os.walk(directory_path):
            current_depth = len(Path(root).relative_to(path).parts)

            if current_depth > max_depth:
                dirs.clear()  # Don't recurse deeper
                continue

            # Analyze directories
            if include_directories:
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        stat_info = os.stat(dir_path)
                        permissions = _get_permission_string(stat_info.st_mode)

                        if permissions not in permission_stats:
                            permission_stats[permissions] = {"count": 0, "type": "directory"}

                        permission_stats[permissions]["count"] += 1

                        analyzed_items.append(
                            {"path": dir_path, "type": "directory", "permissions": permissions, "depth": current_depth}
                        )

                    except Exception as e:
                        logger.warning(f"Failed to analyze directory {dir_path}: {e}")

            # Analyze files
            if include_files:
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    try:
                        stat_info = os.stat(file_path)
                        permissions = _get_permission_string(stat_info.st_mode)

                        if permissions not in permission_stats:
                            permission_stats[permissions] = {"count": 0, "type": "file"}

                        permission_stats[permissions]["count"] += 1

                        analyzed_items.append(
                            {"path": file_path, "type": "file", "permissions": permissions, "depth": current_depth}
                        )

                    except Exception as e:
                        logger.warning(f"Failed to analyze file {file_path}: {e}")

        return {
            "success": True,
            "analysis": {
                "permission_stats": permission_stats,
                "analyzed_items": analyzed_items[:100],  # Limit to first 100 for performance
                "total_analyzed": len(analyzed_items),
            },
            "directory_path": directory_path,
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to analyze directory permissions: {e!s}"}


@tool(
    name="fix_file_permissions",
    description="Fix common file permission issues",
    parameters={
        "file_path": {"type": "string", "description": "Path to the file or directory to fix"},
        "fix_type": {
            "type": "string",
            "description": "Type of permission fix (readable, writable, executable)",
            "default": "readable",
        },
        "recursive": {"type": "boolean", "description": "Apply fix recursively", "default": False},
    },
    required=["file_path"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "fixed_items": {"type": "array", "items": {"type": "string"}},
        },
    },
)
def fix_file_permissions(file_path: str, fix_type: str = "readable", recursive: bool = False) -> dict[str, Any]:
    """
    Fix common file permission issues.

    Args:
        file_path: Path to the file or directory to fix
        fix_type: Type of permission fix (readable, writable, executable)
        recursive: Apply fix recursively

    Returns:
        Dictionary with fix result
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {"success": False, "error": f"Path does not exist: {file_path}"}

        fixed_items = []

        if fix_type == "readable":
            # Make file readable by owner, group, and others
            new_permissions = "644"  # rw-r--r--
        elif fix_type == "writable":
            # Make file writable by owner
            new_permissions = "664"  # rw-rw-r--
        elif fix_type == "executable":
            # Make file executable by owner
            new_permissions = "755"  # rwxr-xr-x
        else:
            return {"success": False, "error": f"Unknown fix type: {fix_type}"}

        if path.is_file():
            try:
                os.chmod(file_path, int(new_permissions, 8))
                fixed_items.append(str(path))
            except Exception as e:
                return {"success": False, "error": f"Failed to fix permissions on {file_path}: {e!s}"}

        elif path.is_dir() and recursive:
            # Fix permissions recursively
            for root, _dirs, files in os.walk(file_path):
                for file in files:
                    file_path_full = os.path.join(root, file)
                    try:
                        os.chmod(file_path_full, int(new_permissions, 8))
                        fixed_items.append(file_path_full)
                    except Exception as e:
                        logger.warning(f"Failed to fix permissions on {file_path_full}: {e}")

        elif path.is_dir():
            # Fix permissions on directory only
            try:
                os.chmod(file_path, int(new_permissions, 8))
                fixed_items.append(str(path))
            except Exception as e:
                return {"success": False, "error": f"Failed to fix permissions on {file_path}: {e!s}"}

        return {
            "success": True,
            "message": f"Fixed permissions on {len(fixed_items)} items",
            "fixed_items": fixed_items,
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to fix file permissions: {e!s}"}


def register_windows_permissions_tools(mcp):
    """Register Windows permissions management tools with FastMCP."""
    # Register the Windows permissions tools with MCP
    mcp.tool(get_file_permissions)
    mcp.tool(set_file_permissions)
    mcp.tool(analyze_directory_permissions)
    mcp.tool(fix_file_permissions)

    logger.info(
        "windows_permissions_tools_registered",
        tools=["get_file_permissions", "set_file_permissions", "analyze_directory_permissions", "fix_file_permissions"],
    )
