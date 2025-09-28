"""
File Operations Module

This package provides tools for file system operations including file attributes,
date manipulation, and file information retrieval.
"""

from .base import (
    FileOperationError,
    validate_file_path,
    normalize_path,
    log_operation,
    handle_operation
)

from .file_operations import (
    read_file,
    write_file,
    delete_file,
    move_file,
    copy_file
)

from .attributes import (
    get_file_attributes,
    set_file_attributes,
    get_file_attributes_tool,
    set_file_attributes_tool
)

from .dates import (
    get_file_dates,
    set_file_dates,
    get_file_dates_tool,
    set_file_dates_tool
)

from .info import (
    get_file_info,
    get_file_info_tool,
    list_directory_tool
)

from .folder_operations import (
    list_directory_contents,
    create_directory_safe,
    delete_directory_safe,
    move_directory_safe,
    copy_directory_safe
)

from .register import register_file_operations
from .edit import (
    EditError,
    BackupError,
    AtomicWriteError,
    is_text_file,
    create_backup,
    detect_line_endings,
    normalize_line_endings,
    atomic_write,
    edit_file,
    fix_markdown,
    register_edit_tools
)

# Export all public symbols
__all__ = [
    # Base
    'FileOperationError',
    'validate_file_path',
    'normalize_path',
    'log_operation',
    'handle_operation',
    
    # File Operations
    'read_file',
    'write_file',
    'delete_file',
    'move_file',
    'copy_file',
    
    # Attributes
    'get_file_attributes',
    'set_file_attributes',
    'get_file_attributes_tool',
    'set_file_attributes_tool',
    
    # Dates
    'get_file_dates',
    'set_file_dates',
    'get_file_dates_tool',
    'set_file_dates_tool',
    
    # File Info
    'get_file_info',
    'get_file_info_tool',
    'list_directory_tool',
    
    # Folder Operations
    'list_directory_contents',
    'create_directory_safe',
    'delete_directory_safe',
    'move_directory_safe',
    'copy_directory_safe',
    
    # Edit Tools
    'EditError',
    'BackupError',
    'AtomicWriteError',
    'is_text_file',
    'create_backup',
    'detect_line_endings',
    'normalize_line_endings',
    'atomic_write',
    'edit_file',
    'fix_markdown',
    'register_edit_tools'
]
