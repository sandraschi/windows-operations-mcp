"""
File date operations module.

This module provides functionality for getting and setting file dates (created, modified, accessed).
"""

import os
import ctypes
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple

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
    _CreateFileW,
    _GetFileTime,
    _SetFileTime,
    _CloseHandle,
    FILETIME
)

def datetime_to_filetime(dt: datetime.datetime) -> int:
    """
    Convert a Python datetime to Windows FILETIME (100-nanosecond intervals since 1601-01-01).
    
    Args:
        dt: Datetime to convert
        
    Returns:
        Number of 100-nanosecond intervals since 1601-01-01
    """
    if dt.tzinfo is not None:
        # Convert to UTC if timezone-aware
        dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    
    # Convert to timestamp (seconds since 1970-01-01)
    timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    
    # Convert to 100-nanosecond intervals since 1601-01-01
    filetime = int(timestamp * 10_000_000) + 116444736000000000
    
    return filetime

def filetime_to_datetime(filetime: int) -> datetime.datetime:
    """
    Convert Windows FILETIME to Python datetime.
    
    Args:
        filetime: Number of 100-nanosecond intervals since 1601-01-01
        
    Returns:
        Datetime object
    """
    # Convert to seconds since 1970-01-01
    timestamp = (filetime - 116444736000000000) / 10_000_000
    
    # Convert to datetime (UTC)
    return datetime.datetime.utcfromtimestamp(timestamp)

@log_operation("get_file_dates")
@handle_operation()
def get_file_dates(file_path: Union[str, Path]) -> Dict[str, datetime.datetime]:
    """
    Get file dates (created, modified, accessed) for the specified file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with 'created', 'modified', and 'accessed' datetime objects
    """
    file_path = normalize_path(file_path)
    
    if not file_path.exists():
        raise FileOperationError(f"File not found: {file_path}")
    
    if os.name == 'nt':
        # Windows implementation using Win32 API for higher precision
        handle = _CreateFileW(
            str(file_path),
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            None
        )
        
        if handle == INVALID_HANDLE_VALUE:
            raise FileOperationError("Failed to open file for reading dates")
        
        try:
            created = FILETIME()
            modified = FILETIME()
            accessed = FILETIME()
            
            if not _GetFileTime(handle, ctypes.byref(created), 
                              ctypes.byref(accessed), ctypes.byref(modified)):
                raise FileOperationError("Failed to get file times")
            
            # Convert FILETIME to datetime
            created_ft = (created.dwHighDateTime << 32) | created.dwLowDateTime
            modified_ft = (modified.dwHighDateTime << 32) | modified.dwLowDateTime
            accessed_ft = (accessed.dwHighDateTime << 32) | accessed.dwLowDateTime
            
            return {
                'created': filetime_to_datetime(created_ft),
                'modified': filetime_to_datetime(modified_ft),
                'accessed': filetime_to_datetime(accessed_ft)
            }
            
        finally:
            _CloseHandle(handle)
    else:
        # Unix-like implementation using os.stat
        st = file_path.stat()
        
        return {
            'created': datetime.datetime.utcfromtimestamp(st.st_ctime),
            'modified': datetime.datetime.utcfromtimestamp(st.st_mtime),
            'accessed': datetime.datetime.utcfromtimestamp(st.st_atime)
        }

@log_operation("set_file_dates")
@handle_operation()
def set_file_dates(
    file_path: Union[str, Path],
    created: Optional[datetime.datetime] = None,
    modified: Optional[datetime.datetime] = None,
    accessed: Optional[datetime.datetime] = None
) -> Dict[str, datetime.datetime]:
    """
    Set file dates (created, modified, accessed) for the specified file.
    
    Args:
        file_path: Path to the file
        created: New creation date (None to leave unchanged)
        modified: New modification date (None to leave unchanged)
        accessed: New access date (None to leave unchanged)
        
    Returns:
        Dictionary with updated file dates
    """
    file_path = normalize_path(file_path)
    
    if not file_path.exists():
        raise FileOperationError(f"File not found: {file_path}")
    
    if os.name == 'nt':
        # Windows implementation using Win32 API
        handle = _CreateFileW(
            str(file_path),
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            None
        )
        
        if handle == INVALID_HANDLE_VALUE:
            raise FileOperationError("Failed to open file for writing dates")
        
        try:
            # Get current times for any we're not changing
            current_created = FILETIME()
            current_modified = FILETIME()
            current_accessed = FILETIME()
            
            if not _GetFileTime(handle, ctypes.byref(current_created), 
                              ctypes.byref(current_accessed), 
                              ctypes.byref(current_modified)):
                raise FileOperationError("Failed to get current file times")
            
            # Convert input datetimes to FILETIME
            created_ft = FILETIME()
            modified_ft = FILETIME()
            accessed_ft = FILETIME()
            
            if created is not None:
                created_ft_val = datetime_to_filetime(created)
                created_ft.dwLowDateTime = created_ft_val & 0xFFFFFFFF
                created_ft.dwHighDateTime = (created_ft_val >> 32) & 0xFFFFFFFF
            else:
                created_ft = current_created
            
            if modified is not None:
                modified_ft_val = datetime_to_filetime(modified)
                modified_ft.dwLowDateTime = modified_ft_val & 0xFFFFFFFF
                modified_ft.dwHighDateTime = (modified_ft_val >> 32) & 0xFFFFFFFF
            else:
                modified_ft = current_modified
            
            if accessed is not None:
                accessed_ft_val = datetime_to_filetime(accessed)
                accessed_ft.dwLowDateTime = accessed_ft_val & 0xFFFFFFFF
                accessed_ft.dwHighDateTime = (accessed_ft_val >> 32) & 0xFFFFFFFF
            else:
                accessed_ft = current_accessed
            
            # Set the new file times
            if not _SetFileTime(handle, ctypes.byref(created_ft), 
                              ctypes.byref(accessed_ft), 
                              ctypes.byref(modified_ft)):
                raise FileOperationError("Failed to set file times")
            
            # Return the updated dates
            return get_file_dates(file_path)
            
        finally:
            _CloseHandle(handle)
    else:
        # Unix-like implementation using os.utime
        # Note: Can only set accessed and modified times on Unix
        if modified is not None or accessed is not None:
            # Convert to timestamps
            atime = accessed.timestamp() if accessed is not None else file_path.stat().st_atime
            mtime = modified.timestamp() if modified is not None else file_path.stat().st_mtime
            
            # Set the times
            os.utime(file_path, (atime, mtime))
        
        # Return the updated dates
        return get_file_dates(file_path)

# MCP Tool Wrappers

def get_file_dates_tool(file_path: str) -> Dict[str, Any]:
    """
    MCP tool wrapper for getting file dates.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file dates and operation status
    """
    try:
        dates = get_file_dates(file_path)
        return {
            "success": True,
            "path": file_path,
            "created": dates['created'].isoformat(),
            "modified": dates['modified'].isoformat(),
            "accessed": dates['accessed'].isoformat()
        }
    except FileOperationError as e:
        return {
            "success": False,
            "error": str(e),
            "path": file_path
        }

def set_file_dates_tool(
    file_path: str,
    created: Optional[str] = None,
    modified: Optional[str] = None,
    accessed: Optional[str] = None
) -> Dict[str, Any]:
    """
    MCP tool wrapper for setting file dates.
    
    Args:
        file_path: Path to the file
        created: New creation date (ISO format, None to leave unchanged)
        modified: New modification date (ISO format, None to leave unchanged)
        accessed: New access date (ISO format, None to leave unchanged)
        
    Returns:
        Dictionary with operation status and updated dates
    """
    def parse_datetime(dt_str: Optional[str]) -> Optional[datetime.datetime]:
        if not dt_str:
            return None
        try:
            # Handle timezone-aware and naive datetimes
            if 'T' in dt_str:
                if dt_str.endswith('Z'):
                    dt_str = dt_str[:-1] + '+00:00'
                return datetime.datetime.fromisoformat(dt_str)
            else:
                return datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError) as e:
            raise FileOperationError(f"Invalid date format: {dt_str}") from e
    
    try:
        # Parse input datetimes
        created_dt = parse_datetime(created)
        modified_dt = parse_datetime(modified)
        accessed_dt = parse_datetime(accessed)
        
        # Set the dates
        dates = set_file_dates(
            file_path,
            created=created_dt,
            modified=modified_dt,
            accessed=accessed_dt
        )
        
        # Format the response
        result = {
            "success": True,
            "path": file_path,
            "created": dates['created'].isoformat(),
            "modified": dates['modified'].isoformat(),
            "accessed": dates['accessed'].isoformat()
        }
        
        # Add a note if some dates couldn't be set (e.g., creation time on Unix)
        if os.name != 'nt' and created_dt is not None:
            result['note'] = "Creation time cannot be set on this platform"
            
        return result
        
    except FileOperationError as e:
        return {
            "success": False,
            "error": str(e),
            "path": file_path
        }
