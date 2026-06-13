"""
Base module for file operations.

This module provides common utilities, error handling, and base functionality
used across all file operation modules.
"""

import ctypes
import os
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar, cast

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

# Type variable for generic function type
F = TypeVar("F", bound=Callable[..., Any])

# Windows API constants
if os.name == "nt":
    from ctypes.wintypes import BOOL, DWORD, HANDLE, LPCWSTR

    # File access constants
    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002
    FILE_ATTRIBUTE_NORMAL = 0x00000080
    OPEN_EXISTING = 3
    INVALID_HANDLE_VALUE = -1

    # File attribute constants
    FILE_ATTRIBUTE_READONLY = 0x1
    FILE_ATTRIBUTE_HIDDEN = 0x2
    FILE_ATTRIBUTE_SYSTEM = 0x4
    FILE_ATTRIBUTE_ARCHIVE = 0x20
    FILE_ATTRIBUTE_NORMAL = 0x80
    FILE_ATTRIBUTE_TEMPORARY = 0x100
    FILE_ATTRIBUTE_OFFLINE = 0x1000
    FILE_ATTRIBUTE_ENCRYPTED = 0x4000

    # File time structure (ctypes; distinct from wintypes.FILETIME for kernel32 bindings)
    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", DWORD), ("dwHighDateTime", DWORD)]

    # Windows API functions
    _CreateFileW = ctypes.windll.kernel32.CreateFileW
    _CreateFileW.argtypes = [LPCWSTR, DWORD, DWORD, ctypes.c_void_p, DWORD, DWORD, HANDLE]
    _CreateFileW.restype = HANDLE

    _GetFileAttributesW = ctypes.windll.kernel32.GetFileAttributesW
    _GetFileAttributesW.argtypes = [LPCWSTR]
    _GetFileAttributesW.restype = DWORD

    _SetFileAttributesW = ctypes.windll.kernel32.SetFileAttributesW
    _SetFileAttributesW.argtypes = [LPCWSTR, DWORD]
    _SetFileAttributesW.restype = BOOL

    _GetFileTime = ctypes.windll.kernel32.GetFileTime
    _GetFileTime.argtypes = [HANDLE, ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME)]
    _GetFileTime.restype = BOOL

    _SetFileTime = ctypes.windll.kernel32.SetFileTime
    _SetFileTime.argtypes = [HANDLE, ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME)]
    _SetFileTime.restype = BOOL

    _CloseHandle = ctypes.windll.kernel32.CloseHandle
    _CloseHandle.argtypes = [HANDLE]
    _CloseHandle.restype = BOOL

# Logger
logger = get_logger(__name__)


class FileOperationError(Exception):
    """Base exception for file operations."""

    pass


def validate_file_path(file_path: str, must_exist: bool = False, check_type: bool = True) -> tuple[bool, str]:
    """
    Validate a file path.

    Args:
        file_path: Path to validate
        must_exist: Whether the path must exist
        check_type: Whether to verify it's a file (if must_exist is True)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path or not isinstance(file_path, str):
        return False, "Path must be a non-empty string"

    try:
        path = Path(file_path)

        # Check for path traversal
        if ".." in path.parts or "~" in path.parts:
            return False, "Path traversal is not allowed"

        # Check for invalid characters
        invalid_chars = ["<", ">", "|", '"', "?", "*"]
        if any(char in str(path) for char in invalid_chars):
            return False, f"Path contains invalid characters: {invalid_chars}"

        # Check existence if required
        if must_exist:
            if not path.exists():
                return False, f"Path does not exist: {file_path}"
            if check_type and not path.is_file():
                return False, f"Path is not a file: {file_path}"

        return True, ""

    except Exception as e:
        return False, f"Invalid path: {e!s}"


def normalize_path(file_path: str) -> Path:
    """
    Normalize a file path to an absolute Path object.

    Args:
        file_path: Path to normalize

    Returns:
        Normalized Path object

    Raises:
        FileOperationError: If path is invalid
    """
    is_valid, error = validate_file_path(file_path)
    if not is_valid:
        raise FileOperationError(error)

    try:
        path = Path(file_path).resolve()
        return path
    except Exception as e:
        raise FileOperationError(f"Failed to normalize path: {e!s}") from e


def log_operation(operation: str, **kwargs) -> Callable[[F], F]:
    """
    Decorator to log the start and completion of file operations.

    Args:
        operation: Name of the operation being performed
        **kwargs: Additional context to include in logs

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **inner_kwargs):
            # Log operation start
            logger.info(
                f"{operation}_started",
                operation=operation,
                **{**kwargs, **{k: v for k, v in inner_kwargs.items() if k != "self"}},
            )

            try:
                # Execute the function
                result = func(*args, **inner_kwargs)

                # Log operation completion
                logger.info(
                    f"{operation}_completed",
                    operation=operation,
                    success=True,
                    **{**kwargs, **{k: v for k, v in inner_kwargs.items() if k != "self"}},
                )

                return result

            except Exception as e:
                # Log operation failure
                logger.error(
                    f"{operation}_error",
                    operation=operation,
                    error=str(e),
                    exc_info=True,
                    **{**kwargs, **{k: v for k, v in inner_kwargs.items() if k != "self"}},
                )
                raise

        return cast(F, wrapper)

    return decorator


def handle_operation(operation: str, must_exist: bool = False, **defaults) -> Callable[[F], F]:
    """
    Decorator to handle common file operation patterns including validation,
    error handling, and result formatting with SOTA metadata support.

    Args:
        operation: Name of the operation
        must_exist: Whether the target path must exist for validation
        **defaults: Default values for the operation

    Returns:
        Decorated function
    """
    import datetime

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Merge defaults with provided kwargs
            params = {**defaults, **kwargs}

            try:
                # Validate inputs
                if "path" in params:
                    # Specific check: read_file/delete_file should exist, write_file shouldn't necessarily
                    is_valid, error = validate_file_path(params["path"], must_exist=must_exist)
                    if not is_valid:
                        return fail_response(
                            f"Invalid path: {error}",
                            path=params["path"],
                            _metadata={
                                "success": False,
                                "operation": operation,
                                "timestamp": datetime.datetime.now().isoformat(),
                            },
                        )

                # Execute the operation
                result = func(*args, **params)

                # Ensure result has success flag and metadata
                if isinstance(result, dict):
                    if "success" not in result:
                        result["success"] = True

                    # Add industrial metadata if missing
                    if "_metadata" not in result:
                        result["_metadata"] = {
                            "success": result.get("success", True),
                            "operation": operation,
                            "timestamp": datetime.datetime.now().isoformat(),
                        }

                return result

            except FileOperationError as e:
                return fail_response(
                    str(e),
                    path=params.get("path", "unknown"),
                    _metadata={
                        "success": False,
                        "operation": operation,
                        "timestamp": datetime.datetime.now().isoformat(),
                    },
                )

            except Exception as e:
                return fail_response(
                    f"Unexpected error during {operation}: {e!s}",
                    path=params.get("path", "unknown"),
                    _metadata={
                        "success": False,
                        "operation": operation,
                        "timestamp": datetime.datetime.now().isoformat(),
                    },
                )

        return cast(F, wrapper)

    return decorator
