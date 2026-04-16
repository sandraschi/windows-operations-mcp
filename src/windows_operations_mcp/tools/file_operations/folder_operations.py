"""
Folder Operations Module

Provides safe directory operations including creation, deletion, moving, and listing
contents with Windows-specific handling and error management.
"""

import shutil
from typing import Any

from .base import FileOperationError, handle_operation, normalize_path


def list_directory_contents(
    directory_path: str, include_hidden: bool = False, pattern: str | None = None
) -> dict[str, Any]:
    """
    List contents of a directory with optional filtering.

    Args:
        directory_path: Path to the directory to list
        include_hidden: Whether to include hidden files/folders
        pattern: Optional glob pattern to filter results

    Returns:
        Dictionary containing the operation result and directory contents
    """

    @handle_operation("list directory contents")
    def _list_directory():
        dir_path = normalize_path(directory_path)
        if not dir_path.exists() or not dir_path.is_dir():
            raise FileOperationError(f"Directory not found: {directory_path}")

        items = []
        for item in dir_path.iterdir():
            if not include_hidden and item.name.startswith("."):
                continue

            if pattern and not item.match(pattern):
                continue

            item_info = {
                "name": item.name,
                "path": str(item.absolute()),
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": item.stat().st_mtime,
            }
            items.append(item_info)

        return {"path": str(dir_path.absolute()), "exists": True, "is_dir": True, "items": items, "count": len(items)}

    return _list_directory()


def create_directory_safe(directory_path: str, create_parents: bool = True, exist_ok: bool = True) -> dict[str, Any]:
    """
    Safely create a directory with parent directory creation options.

    Args:
        directory_path: Path of the directory to create
        create_parents: Whether to create parent directories if they don't exist
        exist_ok: If False, raise an error if directory already exists

    Returns:
        Dictionary containing the operation result
    """

    @handle_operation("create directory")
    def _create_directory():
        dir_path = normalize_path(directory_path)

        if dir_path.exists():
            if not exist_ok:
                raise FileOperationError(f"Directory already exists: {directory_path}")
            if not dir_path.is_dir():
                raise FileOperationError(f"Path exists but is not a directory: {directory_path}")
            return {"path": str(dir_path), "created": False}

        try:
            dir_path.mkdir(parents=create_parents, exist_ok=exist_ok)
            return {
                "path": str(dir_path.absolute()),
                "created": True,
                "parent_created": create_parents and not dir_path.parent.exists(),
            }
        except Exception as e:
            raise FileOperationError(f"Failed to create directory: {e!s}") from e

    return _create_directory()


def delete_directory_safe(directory_path: str, recursive: bool = False, require_empty: bool = True) -> dict[str, Any]:
    """
    Safely delete a directory with protection against accidental deletion.

    Args:
        directory_path: Path to the directory to delete
        recursive: If True, delete directory and all its contents
        require_empty: If True, only delete empty directories

    Returns:
        Dictionary containing the operation result
    """

    @handle_operation("delete directory")
    def _delete_directory():
        dir_path = normalize_path(directory_path)

        if not dir_path.exists():
            raise FileOperationError(f"Directory not found: {directory_path}")

        if not dir_path.is_dir():
            raise FileOperationError(f"Path is not a directory: {directory_path}")

        if require_empty and any(dir_path.iterdir()):
            raise FileOperationError(f"Directory is not empty and require_empty=True: {directory_path}")

        try:
            if recursive:
                shutil.rmtree(dir_path)
            else:
                dir_path.rmdir()

            return {"path": str(dir_path), "deleted": True, "recursive": recursive}
        except Exception as e:
            raise FileOperationError(f"Failed to delete directory: {e!s}") from e

    return _delete_directory()


def move_directory_safe(source_path: str, destination_path: str, overwrite: bool = False) -> dict[str, Any]:
    """
    Safely move/rename a directory with overwrite protection.

    Args:
        source_path: Path to the source directory
        destination_path: Path to the destination directory
        overwrite: If True, overwrite destination if it exists

    Returns:
        Dictionary containing the operation result
    """

    @handle_operation("move directory")
    def _move_directory():
        src = normalize_path(source_path)
        dst = normalize_path(destination_path)

        if not src.exists():
            raise FileOperationError(f"Source directory not found: {source_path}")

        if not src.is_dir():
            raise FileOperationError(f"Source is not a directory: {source_path}")

        if dst.exists():
            if not overwrite:
                raise FileOperationError(f"Destination already exists and overwrite=False: {destination_path}")
            if not dst.is_dir():
                raise FileOperationError(f"Destination exists but is not a directory: {destination_path}")

        try:
            shutil.move(str(src), str(dst))
            return {"source": str(src), "destination": str(dst), "moved": True, "overwritten": dst.exists()}
        except Exception as e:
            raise FileOperationError(f"Failed to move directory: {e!s}") from e

    return _move_directory()


def copy_directory_safe(source_path: str, destination_path: str, overwrite: bool = False) -> dict[str, Any]:
    """
    Safely copy a directory recursively.

    Args:
        source_path: Path to the source directory
        destination_path: Path to the destination directory
        overwrite: If True, overwrite destination if it exists

    Returns:
        Dictionary containing the operation result
    """

    @handle_operation("copy directory")
    def _copy_directory():
        src = normalize_path(source_path)
        dst = normalize_path(destination_path)

        if not src.exists():
            raise FileOperationError(f"Source directory not found: {source_path}")

        if not src.is_dir():
            raise FileOperationError(f"Source is not a directory: {source_path}")

        if dst.exists():
            if not overwrite:
                raise FileOperationError(f"Destination already exists and overwrite=False: {destination_path}")
            if not dst.is_dir():
                raise FileOperationError(f"Destination exists but is not a directory: {destination_path}")

        try:
            if dst.exists() and overwrite:
                shutil.rmtree(dst)

            shutil.copytree(str(src), str(dst))
            return {
                "source": str(src),
                "destination": str(dst),
                "copied": True,
                "overwritten": dst.exists() and overwrite,
            }
        except Exception as e:
            if dst.exists() and not dst.samefile(src):
                shutil.rmtree(dst, ignore_errors=True)
            raise FileOperationError(f"Failed to copy directory: {e!s}") from e

    return _copy_directory()
