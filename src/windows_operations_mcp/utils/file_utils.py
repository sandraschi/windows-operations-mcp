"""
File utility functions for Windows Operations MCP.

This module provides file-related utility functions including temporary file handling,
safe cleanup, and directory validation.
"""

import os
import tempfile
from pathlib import Path


def create_temp_file(suffix: str = ".tmp", content: bytes | None = None) -> str:
    """
    Create a temporary file with optional content.

    Args:
        suffix: File suffix/extension
        content: Optional content to write to the file

    Returns:
        Path to the created temporary file
    """
    try:
        fd, path = tempfile.mkstemp(suffix=suffix)
        if content:
            with os.fdopen(fd, "wb") as f:
                f.write(content)
        else:
            os.close(fd)
        return path
    except Exception as e:
        raise RuntimeError(f"Failed to create temporary file: {e!s}")


def safe_cleanup_file(path: str | Path) -> bool:
    """
    Safely remove a file if it exists.

    Args:
        path: Path to the file to remove

    Returns:
        bool: True if file was removed or didn't exist, False on error
    """
    try:
        path = Path(path) if not isinstance(path, Path) else path
        if path.exists():
            path.unlink()
        return True
    except Exception:
        return False


def validate_directory(directory: str | Path) -> tuple[bool, str]:
    """
    Validate that a directory exists and is accessible.

    Args:
        directory: Path to the directory to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path = Path(directory) if not isinstance(directory, Path) else directory

        if not path.exists():
            return False, f"Directory does not exist: {path}"

        if not path.is_dir():
            return False, f"Path is not a directory: {path}"

        # Try to create a test file to check write permissions
        test_file = path / ".permission_test"
        try:
            test_file.touch(exist_ok=True)
            test_file.unlink()
        except PermissionError:
            return False, f"Insufficient permissions to write to directory: {path}"

        return True, ""

    except Exception as e:
        return False, f"Error validating directory {directory}: {e!s}"
