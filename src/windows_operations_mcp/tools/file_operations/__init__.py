"""
File Operations Module

This package provides tools for file system operations including file attributes,
date manipulation, and file information retrieval.
"""

from .attributes import get_file_attributes, get_file_attributes_tool, set_file_attributes, set_file_attributes_tool
from .base import FileOperationError, handle_operation, log_operation, normalize_path, validate_file_path
from .dates import get_file_dates, get_file_dates_tool, set_file_dates, set_file_dates_tool
from .edit import (
    AtomicWriteError,
    BackupError,
    EditError,
    atomic_write,
    create_backup,
    detect_line_endings,
    edit_file,
    fix_markdown,
    is_text_file,
    normalize_line_endings,
    register_edit_tools,
)
from .file_operations import copy_file, delete_file, move_file, read_file, write_file
from .folder_operations import (
    copy_directory_safe,
    create_directory_safe,
    delete_directory_safe,
    list_directory_contents,
    move_directory_safe,
)
from .info import get_file_info, get_file_info_tool, list_directory_tool
from .register import register_file_operations

# Export all public symbols
__all__ = [
    "AtomicWriteError",
    "BackupError",
    # Edit Tools
    "EditError",
    # Base
    "FileOperationError",
    "atomic_write",
    "copy_directory_safe",
    "copy_file",
    "create_backup",
    "create_directory_safe",
    "delete_directory_safe",
    "delete_file",
    "detect_line_endings",
    "edit_file",
    "fix_markdown",
    # Attributes
    "get_file_attributes",
    "get_file_attributes_tool",
    # Dates
    "get_file_dates",
    "get_file_dates_tool",
    # File Info
    "get_file_info",
    "get_file_info_tool",
    "handle_operation",
    "is_text_file",
    # Folder Operations
    "list_directory_contents",
    "list_directory_tool",
    "log_operation",
    "move_directory_safe",
    "move_file",
    "normalize_line_endings",
    "normalize_path",
    # File Operations
    "read_file",
    "register_edit_tools",
    "register_file_operations",
    "set_file_attributes",
    "set_file_attributes_tool",
    "set_file_dates",
    "set_file_dates_tool",
    "validate_file_path",
    "write_file",
]
