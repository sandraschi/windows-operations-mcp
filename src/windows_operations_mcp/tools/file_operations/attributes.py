"""
File attributes module.

This module provides functionality for getting and setting file attributes.
"""

import os
import ctypes
import stat
from pathlib import Path
from typing import Dict, Any, Optional, Union, cast

from .base import (
    FileOperationError,
    validate_file_path,
    normalize_path,
    log_operation,
    handle_operation,
    GENERIC_READ,
    GENERIC_WRITE,
    FILE_SHARE_READ,
    FILE_SHARE_WRITE,
    FILE_ATTRIBUTE_NORMAL,
    OPEN_EXISTING,
    INVALID_HANDLE_VALUE,
    FILE_ATTRIBUTE_READONLY,
    FILE_ATTRIBUTE_HIDDEN,
    FILE_ATTRIBUTE_SYSTEM,
    FILE_ATTRIBUTE_ARCHIVE,
    FILE_ATTRIBUTE_NORMAL,
    FILE_ATTRIBUTE_TEMPORARY,
    FILE_ATTRIBUTE_OFFLINE,
    FILE_ATTRIBUTE_ENCRYPTED,
    _CreateFileW,
    _GetFileAttributesW,
    _SetFileAttributesW,
    _CloseHandle
)

# Map of attribute names to Windows attribute constants
ATTRIBUTE_MAP = {
    'readonly': FILE_ATTRIBUTE_READONLY,
    'hidden': FILE_ATTRIBUTE_HIDDEN,
    'system': FILE_ATTRIBUTE_SYSTEM,
    'archive': FILE_ATTRIBUTE_ARCHIVE,
    'temporary': FILE_ATTRIBUTE_TEMPORARY,
    'offline': FILE_ATTRIBUTE_OFFLINE,
    'encrypted': FILE_ATTRIBUTE_ENCRYPTED
}

@log_operation("get_file_attributes")
@handle_operation("get_file_attributes")
def get_file_attributes(file_path: Union[str, Path]) -> Dict[str, bool]:
    """
    Get file attributes for the specified file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary of attribute names and their values
    """
    file_path = normalize_path(file_path)
    
    if not file_path.exists():
        raise FileOperationError(f"File not found: {file_path}")
    
    attributes = {}
    
    if os.name == 'nt':
        # Windows implementation using Win32 API
        attrs = _GetFileAttributesW(str(file_path))
        
        for name, flag in ATTRIBUTE_MAP.items():
            attributes[name] = bool(attrs & flag)
    else:
        # Unix-like implementation using stat
        st = file_path.stat()
        
        # Map stat attributes to our attribute names
        attributes.update({
            'readonly': not bool(st.st_mode & 0o222),  # Not writable by owner
            'hidden': file_path.name.startswith('.'),   # Hidden files start with .
            'system': False,  # No direct equivalent on Unix
            'archive': False,  # No direct equivalent on Unix
            'temporary': False,  # No direct equivalent on Unix
            'offline': False,  # No direct equivalent on Unix
            'encrypted': False  # No direct equivalent without checking encryption
        })
    
    # Add some additional useful attributes
    attributes.update({
        'exists': True,
        'is_file': file_path.is_file(),
        'is_dir': file_path.is_dir(),
        'is_symlink': file_path.is_symlink(),
        'size': file_path.stat().st_size if file_path.is_file() else 0
    })
    
    return attributes

@log_operation("set_file_attributes")
@handle_operation("get_file_attributes")
def set_file_attributes(
    file_path: Union[str, Path],
    attributes: Dict[str, bool]
) -> Dict[str, Any]:
    """
    Set file attributes for the specified file.
    
    Args:
        file_path: Path to the file
        attributes: Dictionary of attributes to set
        
    Returns:
        Dictionary with operation status and updated attributes
    """
    file_path = normalize_path(file_path)
    
    if not file_path.exists():
        raise FileOperationError(f"File not found: {file_path}")
    
    if os.name == 'nt':
        # Windows implementation using Win32 API
        current_attrs = _GetFileAttributesW(str(file_path))
        
        # Update attributes based on the provided values
        for name, value in attributes.items():
            if name in ATTRIBUTE_MAP:
                if value:
                    current_attrs |= ATTRIBUTE_MAP[name]
                else:
                    current_attrs &= ~ATTRIBUTE_MAP[name]
        
        # Apply the new attributes
        if not _SetFileAttributesW(str(file_path), current_attrs):
            raise FileOperationError("Failed to set file attributes")
    else:
        # Unix-like implementation using chmod
        if 'readonly' in attributes:
            st = file_path.stat()
            mode = st.st_mode
            
            if attributes['readonly']:
                # Remove write permissions for all
                mode &= ~0o222
            else:
                # Add write permissions for owner
                mode |= 0o200
            
            file_path.chmod(mode)
        
        # Handle hidden files (prefix with .)
        if 'hidden' in attributes and attributes['hidden'] != file_path.name.startswith('.'):
            if attributes['hidden']:
                new_path = file_path.parent / ('.' + file_path.name)
            else:
                new_path = file_path.parent / file_path.name.lstrip('.')
            
            if new_path != file_path:
                file_path.rename(new_path)
                file_path = new_path
    
    # Return the updated attributes
    updated_attrs = get_file_attributes(file_path)
    updated_attrs['path'] = str(file_path)
    
    return updated_attrs

# MCP Tool Wrappers

def get_file_attributes_tool(file_path: str) -> Dict[str, Any]:
    """
    MCP tool wrapper for getting file attributes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file attributes and operation status
    """
    try:
        attrs = get_file_attributes(file_path)
        return {
            "success": True,
            "path": file_path,
            "attributes": attrs
        }
    except FileOperationError as e:
        return {
            "success": False,
            "error": str(e),
            "path": file_path
        }

def set_file_attributes_tool(
    file_path: str,
    attributes: Dict[str, bool]
) -> Dict[str, Any]:
    """
    MCP tool wrapper for setting file attributes.
    
    Args:
        file_path: Path to the file
        attributes: Dictionary of attributes to set
        
    Returns:
        Dictionary with operation status and updated attributes
    """
    try:
        result = set_file_attributes(file_path, attributes)
        result["success"] = True
        return result
    except FileOperationError as e:
        return {
            "success": False,
            "error": str(e),
            "path": file_path
        }
