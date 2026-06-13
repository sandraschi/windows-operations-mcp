"""
Common utilities for Windows operations.
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def create_temp_file(suffix: str = ".txt", content: str | None = None) -> str:
    """Create a temporary file and return its path."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=suffix, encoding="utf-8") as f:
        temp_path = f.name
        if content:
            f.write(content)
    return temp_path


def safe_cleanup_file(file_path: str) -> None:
    """Safely remove a temporary file."""
    try:
        os.unlink(file_path)
    except Exception as e:
        logger.warning(f"Failed to clean up temp file {file_path}: {e}")


def validate_directory(directory: str) -> dict[str, Any]:
    """Validate a directory path and return status."""
    if not directory:
        return {"valid": False, "error": "Directory path is empty"}

    dir_path = Path(directory)
    if not dir_path.exists():
        return {"valid": False, "error": f"Directory does not exist: {directory}"}

    if not dir_path.is_dir():
        return {"valid": False, "error": f"Path is not a directory: {directory}"}

    return {"valid": True, "path": str(dir_path.absolute())}


def get_execution_result(
    success: bool,
    command: str,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
    execution_time: float = 0.0,
    working_directory: str = "",
    error: str | None = None,
) -> dict[str, Any]:
    """Create a standardized execution result dictionary."""
    return {
        "success": success,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
        "exit_code": exit_code,
        "execution_time": round(execution_time, 3),
        "command": command,
        "working_directory": working_directory,
        **({"error": error} if error else {}),
    }


def fail_response(message: str, *, error: str | None = None, **extra: Any) -> dict[str, Any]:
    """Standardized error response with conversational message (FastMCP convention).

    Every error return should use this instead of inline dicts.
    The ``message`` key gives the LLM a conversational summary while
    ``error`` preserves the technical detail for debugging.

    Args:
        message: Human-readable conversational summary (shown as ``message``).
        error: Technical error string (defaults to message if omitted).

    Returns:
        A dict with ``success=False``, ``message``, ``error``, and any extra keys.
    """
    return {
        "success": False,
        "message": message,
        "error": error or message,
        **extra,
    }


def measure_execution_time(func):
    """Decorator to measure function execution time."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        if isinstance(result, dict):
            result["execution_time"] = round(execution_time, 3)

        return result

    return wrapper
