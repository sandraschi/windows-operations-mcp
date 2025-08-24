"""
Core file operations module.

This module provides basic file operations like create, delete, move, and copy.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from .base import (
    FileOperationError,
    validate_file_path,
    normalize_path,
    log_operation,
    handle_operation
)

@log_operation("create_file")
@handle_operation()
def create_file(
    path: str,
    content: str = "",
    overwrite: bool = False,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Create a new file with the specified content.
    
    Args:
        path: Path where the file should be created
        content: Content to write to the file
        overwrite: Whether to overwrite if file exists
        encoding: File encoding to use
        
    Returns:
        Dictionary with operation status and file info
    """
    path = normalize_path(path)
    
    if path.exists() and not overwrite:
        raise FileOperationError(f"File already exists: {path}")
    
    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file content
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)
    
    return {
        "path": str(path),
        "size": len(content),
        "created": True
    }

@log_operation("delete_file")
@handle_operation()
def delete_file(path: str) -> Dict[str, Any]:
    """
    Delete a file or directory.
    
    Args:
        path: Path to the file or directory to delete
        
    Returns:
        Dictionary with operation status
    """
    path = normalize_path(path)
    
    if not path.exists():
        raise FileOperationError(f"Path does not exist: {path}")
    
    if path.is_file() or path.is_symlink():
        path.unlink()
    else:
        shutil.rmtree(path)
    
    return {
        "path": str(path),
        "deleted": True
    }

@log_operation("move_file")
@handle_operation()
def move_file(
    source: str,
    destination: str,
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Move a file or directory to a new location.
    
    Args:
        source: Source path
        destination: Destination path
        overwrite: Whether to overwrite if destination exists
        
    Returns:
        Dictionary with operation status
    """
    source_path = normalize_path(source)
    dest_path = normalize_path(destination)
    
    if not source_path.exists():
        raise FileOperationError(f"Source does not exist: {source_path}")
    
    if dest_path.exists() and not overwrite:
        raise FileOperationError(f"Destination already exists: {dest_path}")
    
    # If destination is a directory, move into it
    if dest_path.is_dir():
        dest_path = dest_path / source_path.name
    
    # Create parent directories if they don't exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Perform the move
    source_path.replace(dest_path)
    
    return {
        "source": str(source_path),
        "destination": str(dest_path),
        "moved": True
    }

@log_operation("copy_file")
@handle_operation()
def copy_file(
    source: str,
    destination: str,
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Copy a file or directory to a new location.
    
    Args:
        source: Source path
        destination: Destination path
        overwrite: Whether to overwrite if destination exists
        
    Returns:
        Dictionary with operation status
    """
    source_path = normalize_path(source)
    dest_path = normalize_path(destination)
    
    if not source_path.exists():
        raise FileOperationError(f"Source does not exist: {source_path}")
    
    if dest_path.exists() and not overwrite:
        raise FileOperationError(f"Destination already exists: {dest_path}")
    
    # If destination is a directory, copy into it
    if dest_path.is_dir():
        dest_path = dest_path / source_path.name
    
    # Create parent directories if they don't exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Perform the copy
    if source_path.is_file() or source_path.is_symlink():
        shutil.copy2(source_path, dest_path)
    else:
        shutil.copytree(source_path, dest_path, dirs_exist_ok=overwrite)
    
    return {
        "source": str(source_path),
        "destination": str(dest_path),
        "copied": True
    }
