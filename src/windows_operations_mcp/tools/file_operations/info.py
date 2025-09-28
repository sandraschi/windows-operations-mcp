"""
File information module.

This module provides functionality for getting detailed file information and directory listings.
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, BinaryIO

from .base import (
    FileOperationError,
    validate_file_path,
    normalize_path,
    log_operation,
    handle_operation
)
from . import attributes, dates

# Maximum file size to read for content hashing (10MB)
MAX_HASH_SIZE = 10 * 1024 * 1024

# Maximum number of items to return in directory listings
MAX_LIST_ITEMS = 1000

def calculate_file_hash(file_path: Path, algorithm: str = 'sha256', 
                      chunk_size: int = 65536) -> str:
    """
    Calculate a hash of the file's content.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
        chunk_size: Chunk size for reading the file
        
    Returns:
        Hex digest of the file's content
    """
    hash_func = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_func.update(chunk)
                
                # Don't hash more than MAX_HASH_SIZE
                if f.tell() > MAX_HASH_SIZE:
                    break
                    
        return hash_func.hexdigest()
    except (IOError, OSError) as e:
        raise FileOperationError(f"Failed to calculate hash: {str(e)}") from e

def get_mime_type(file_path: Path) -> str:
    """
    Get the MIME type of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string (e.g., 'text/plain')
    """
    # First try with Python's mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if not mime_type:
        # Fall back to common extensions not in mimetypes
        extension_map = {
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.yaml': 'application/x-yaml',
            '.yml': 'application/x-yaml',
            '.log': 'text/plain',
            '.env': 'text/plain',
            '.gitignore': 'text/plain',
            '.dockerignore': 'text/plain',
        }
        mime_type = extension_map.get(file_path.suffix.lower(), 'application/octet-stream')
    
    return mime_type

@log_operation("get_file_info")
@handle_operation("get_file_info")
def get_file_info(
    file_path: Union[str, Path],
    include_content: bool = False,
    include_metadata: bool = True,
    include_attributes: bool = True,
    include_dates: bool = True,
    include_hash: bool = False
) -> Dict[str, Any]:
    """
    Get detailed information about a file or directory.
    
    Args:
        file_path: Path to the file or directory
        include_content: Whether to include file content
        include_metadata: Whether to include file metadata
        include_attributes: Whether to include file attributes
        include_dates: Whether to include file dates
        include_hash: Whether to include file hash
        
    Returns:
        Dictionary with file/directory information
    """
    path = normalize_path(file_path)
    
    if not path.exists():
        raise FileOperationError(f"Path does not exist: {path}")
    
    info = {
        'path': str(path.absolute()),
        'name': path.name,
        'exists': True,
        'is_file': path.is_file(),
        'is_dir': path.is_dir(),
        'is_symlink': path.is_symlink(),
        'parent': str(path.parent.absolute())
    }
    
    # Add file metadata
    if include_metadata or include_hash:
        try:
            stat_info = path.stat()
            
            info.update({
                'size': stat_info.st_size,
                'inode': stat_info.st_ino,
                'device': stat_info.st_dev,
                'hard_links': stat_info.st_nlink,
                'user_id': stat_info.st_uid,
                'group_id': stat_info.st_gid,
                'mode': oct(stat_info.st_mode)[-4:],
                'mime_type': get_mime_type(path) if info['is_file'] else 'inode/directory'
            })
            
            # Calculate hash if requested
            if include_hash and info['is_file'] and info['size'] > 0:
                try:
                    info['hash'] = calculate_file_hash(path)
                except FileOperationError as e:
                    info['hash_error'] = str(e)
                    
        except (IOError, OSError) as e:
            info['metadata_error'] = str(e)
    
    # Add file attributes
    if include_attributes:
        try:
            info['attributes'] = attributes.get_file_attributes(path)
        except FileOperationError as e:
            info['attributes_error'] = str(e)
    
    # Add file dates
    if include_dates:
        try:
            file_dates = dates.get_file_dates(path)
            info.update({
                'created': file_dates['created'].isoformat(),
                'modified': file_dates['modified'].isoformat(),
                'accessed': file_dates['accessed'].isoformat()
            })
        except FileOperationError as e:
            info['dates_error'] = str(e)
    
    # Add file content if requested
    if include_content and info['is_file'] and info.get('size', 0) > 0:
        try:
            # Only read text files up to 1MB
            if info['size'] <= 1024 * 1024:  # 1MB
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        info['content'] = f.read()
                except UnicodeDecodeError:
                    # Fall back to binary if UTF-8 decoding fails
                    with open(path, 'rb') as f:
                        info['content_binary'] = True
                        info['content'] = f.read().decode('latin-1')
            else:
                info['content'] = None
                info['content_note'] = 'File too large to include content (limit: 1MB)'
        except (IOError, OSError) as e:
            info['content_error'] = str(e)
    
    return info

@log_operation("list_directory")
@handle_operation("get_file_info")
def list_directory(
    path: str,
    include_hidden: bool = False,
    include_system: bool = False,
    file_pattern: Optional[str] = None,
    max_items: int = MAX_LIST_ITEMS,
    include_stats: bool = False
) -> Dict[str, Any]:
    """
    List directory contents with filtering options.
    
    Args:
        path: Directory path to list
        include_hidden: Whether to include hidden files/directories
        include_system: Whether to include system files/directories
        file_pattern: Glob pattern to filter files
        max_items: Maximum number of items to return
        include_stats: Whether to include statistics about the directory
        
    Returns:
        Dictionary with directory contents and metadata
    """
    dir_path = normalize_path(path)
    
    if not dir_path.exists():
        raise FileOperationError(f"Directory does not exist: {path}")
    
    if not dir_path.is_dir():
        raise FileOperationError(f"Path is not a directory: {path}")
    
    items = []
    directories_count = 0
    files_count = 0
    total_size = 0
    
    # Compile pattern if provided
    import fnmatch
    pattern = file_pattern.lower() if file_pattern else None
    
    # Iterate through directory contents
    try:
        for item in dir_path.iterdir():
            try:
                # Skip hidden files/directories if not included
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                # Get item info
                item_info = {
                    'name': item.name,
                    'path': str(item.absolute()),
                    'is_dir': item.is_dir(),
                    'is_file': item.is_file(),
                    'is_symlink': item.is_symlink()
                }
                
                # Skip system files if not included
                if not include_system and item.is_file():
                    try:
                        attrs = attributes.get_file_attributes(item)
                        if attrs.get('system', False):
                            continue
                    except FileOperationError:
                        pass
                
                # Apply pattern filter
                if pattern and not fnmatch.fnmatch(item.name.lower(), pattern):
                    continue
                
                # Get additional stats if requested
                if include_stats or item.is_file():
                    try:
                        stat_info = item.stat()
                        
                        item_info.update({
                            'size': stat_info.st_size if item.is_file() else 0,
                            'created': stat_info.st_ctime,
                            'modified': stat_info.st_mtime,
                            'accessed': stat_info.st_atime
                        })
                        
                        if item.is_file():
                            total_size += stat_info.st_size
                            files_count += 1
                        else:
                            directories_count += 1
                            
                    except (IOError, OSError) as e:
                        item_info['error'] = str(e)
                
                items.append(item_info)
                
                # Limit number of items
                if len(items) >= max_items:
                    break
                    
            except (IOError, OSError) as e:
                # Skip files we can't access
                continue
    except (IOError, OSError) as e:
        raise FileOperationError(f"Failed to list directory: {str(e)}") from e
    
    # Sort items (directories first, then files, both alphabetically)
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    
    # Prepare result
    result = {
        'path': str(dir_path.absolute()),
        'items': items,
        'count': len(items),
        'directories': directories_count,
        'files': files_count,
        'total_size': total_size
    }
    
    # Add more stats if requested
    if include_stats:
        result.update({
            'size_on_disk': sum(item.get('size', 0) for item in items if item['is_file']),
            'last_modified': max(item.get('modified', 0) for item in items) if items else 0
        })
    
    return result

# MCP Tool Wrappers

def get_file_info_tool(
    file_path: str,
    include_content: bool = False,
    include_metadata: bool = True,
    include_attributes: bool = True
) -> Dict[str, Any]:
    """
    MCP tool wrapper for getting file information.
    
    Args:
        file_path: Path to the file or directory
        include_content: Whether to include file content
        include_metadata: Whether to include file metadata
        include_attributes: Whether to include file attributes
        
    Returns:
        Dictionary with file/directory information and operation status
    """
    try:
        info = get_file_info(
            file_path=file_path,
            include_content=include_content,
            include_metadata=include_metadata,
            include_attributes=include_attributes,
            include_dates=True,
            include_hash=include_metadata
        )
        
        return {
            "success": True,
            **info
        }
        
    except FileOperationError as e:
        return {
            "success": False,
            "error": str(e),
            "path": file_path
        }

def list_directory_tool(
    path: str,
    include_hidden: bool = False,
    include_system: bool = False,
    file_pattern: Optional[str] = None,
    max_items: int = 100,
    include_stats: bool = False
) -> Dict[str, Any]:
    """
    MCP tool wrapper for listing directory contents.
    
    Args:
        path: Directory path to list
        include_hidden: Whether to include hidden files/directories
        include_system: Whether to include system files/directories
        file_pattern: Glob pattern to filter files
        max_items: Maximum number of items to return (1-1000)
        include_stats: Whether to include statistics about the directory
        
    Returns:
        Dictionary with directory contents and operation status
    """
    # Validate max_items
    if not isinstance(max_items, int) or max_items < 1 or max_items > MAX_LIST_ITEMS:
        max_items = min(max(1, int(max_items or 100)), MAX_LIST_ITEMS)
    
    try:
        result = list_directory(
            path=path,
            include_hidden=include_hidden,
            include_system=include_system,
            file_pattern=file_pattern,
            max_items=max_items,
            include_stats=include_stats
        )
        
        return {
            "success": True,
            **result
        }
        
    except FileOperationError as e:
        return {
            "success": False,
            "error": str(e),
            "path": path
        }
