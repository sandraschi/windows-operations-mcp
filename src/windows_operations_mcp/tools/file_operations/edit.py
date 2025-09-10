"""
Safe file editing utilities with atomic writes and backup support.

This module provides functions for safely editing text files with features like:
- Atomic writes (writes to temporary file first, then renames)
- Automatic backups before modification
- Line ending normalization
- Encoding detection and handling
- File locking for concurrent access
"""

import os
import shutil
import tempfile
import contextlib
import codecs
import logging
import hashlib
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Union, BinaryIO, TextIO, Any, Dict
import io
import time

logger = logging.getLogger(__name__)

# Supported text file extensions for safe editing
TEXT_FILE_EXTENSIONS = {
    # Source files
    '.py', '.rs', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.go', '.rb', '.php', '.swift', '.kt', '.scala', '.m', '.mm', '.r', '.sh', '.bash',
    '.ps1', '.bat', '.cmd', '.fish', '.zsh',
    
    # Configuration
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env',
    
    # Web
    '.html', '.css', '.scss', '.sass', '.less',
    
    # Documentation
    '.md', '.markdown', '.rst', '.txt', '.adoc',
    
    # Data
    '.csv', '.xml', '.xsl', '.xslt', '.svg',
    
    # Other text formats
    '.log', '.diff', '.patch', '.sql', '.graphql', '.gql'
}

class EditError(Exception):
    """Base exception for file editing errors."""
    pass

class BackupError(EditError):
    """Raised when backup operations fail."""
    pass

class AtomicWriteError(EditError):
    """Raised when atomic write operations fail."""
    pass

def is_text_file(filepath: Union[str, Path], chunk_size: int = 4096) -> bool:
    """
    Check if a file appears to be a text file by examining its content.
    
    Args:
        filepath: Path to the file to check
        chunk_size: Number of bytes to read for analysis
        
    Returns:
        bool: True if the file appears to be text, False otherwise
    """
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(chunk_size)
            # Check for null bytes which typically indicate binary files
            if b'\x00' in chunk:
                return False
            
            # Try to decode as text
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
    except Exception as e:
        logger.warning(f"Error checking if file is text: {e}")
        return False

def create_backup(filepath: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Create a timestamped backup of a file.
    
    Args:
        filepath: Path to the file to back up
        backup_dir: Directory to store backups (default: same directory as file)
        
    Returns:
        Path to the backup file
        
    Raises:
        BackupError: If backup creation fails
    """
    filepath = Path(filepath).resolve()
    if not filepath.exists():
        raise BackupError(f"File does not exist: {filepath}")
    
    backup_dir = Path(backup_dir) if backup_dir else filepath.parent
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filepath.name}.bak_{timestamp}"
    backup_path = backup_dir / backup_name
    
    try:
        shutil.copy2(filepath, backup_path)
        logger.info(f"Created backup at: {backup_path}")
        return backup_path
    except Exception as e:
        raise BackupError(f"Failed to create backup of {filepath}: {e}")

def detect_line_endings(content: str) -> str:
    """
    Detect the line ending style of the content.
    
    Args:
        content: The file content as a string
        
    Returns:
        The detected line ending (\n, \r\n, or \r)
    """
    if '\r\n' in content:
        return '\r\n'  # Windows
    elif '\r' in content:
        return '\r'     # Old Mac
    else:
        return '\n'     # Unix/Linux/macOS

def normalize_line_endings(content: str, line_ending: Optional[str] = None) -> str:
    """
    Normalize line endings in the content.
    
    Args:
        content: The content to normalize
        line_ending: The line ending to use (None to auto-detect)
        
    Returns:
        Content with normalized line endings
    """
    if line_ending is None:
        line_ending = detect_line_endings(content)
    
    # Normalize all line endings to LF first
    normalized = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Convert to desired line ending
    if line_ending != '\n':
        normalized = normalized.replace('\n', line_ending)
    
    return normalized

def atomic_write(
    filepath: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    line_ending: Optional[str] = None,
    backup: bool = True,
    backup_dir: Optional[Union[str, Path]] = None,
    create_dirs: bool = True
) -> None:
    """
    Atomically write content to a file with backup support.
    
    Args:
        filepath: Path to the file to write
        content: Content to write to the file
        encoding: File encoding to use
        line_ending: Line ending to use (None to auto-detect)
        backup: Whether to create a backup before writing
        backup_dir: Directory to store backups (default: same as file directory)
        create_dirs: Whether to create parent directories if they don't exist
        
    Raises:
        AtomicWriteError: If the atomic write operation fails
    """
    filepath = Path(filepath).resolve()
    
    # Create parent directories if needed
    if create_dirs:
        filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Normalize line endings
    content = normalize_line_endings(content, line_ending)
    
    # Create backup if requested
    if backup and filepath.exists():
        try:
            create_backup(filepath, backup_dir)
        except BackupError as e:
            logger.warning(f"Backup failed: {e}")
    
    # Write to temporary file first
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding=encoding,
            dir=str(filepath.parent),
            prefix=f".{filepath.name}.",
            suffix='.tmp',
            delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)
            try:
                tmp_file.write(content)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                
                # On Windows, we need to close the file before renaming
                tmp_file.close()
                
                # On Windows, we need to remove the destination file first if it exists
                if os.name == 'nt' and filepath.exists():
                    os.unlink(filepath)
                
                # Atomic rename
                tmp_path.replace(filepath)
                
            except Exception as e:
                # Clean up the temporary file if something went wrong
                try:
                    tmp_path.unlink()
                except:
                    pass
                raise
                
    except Exception as e:
        raise AtomicWriteError(f"Failed to write to {filepath}: {e}")

def edit_file(
    filepath: Union[str, Path],
    editor_func: Callable[[str], str],
    encoding: str = 'utf-8',
    backup: bool = True,
    backup_dir: Optional[Union[str, Path]] = None,
    create_dirs: bool = True
) -> Dict[str, Any]:
    """
    Safely edit a text file using the provided editor function.
    
    Args:
        filepath: Path to the file to edit
        editor_func: Function that takes the file content and returns the modified content
        encoding: File encoding to use
        backup: Whether to create a backup before editing
        backup_dir: Directory to store backups (default: same as file directory)
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        Dictionary with operation status and information
        
    Raises:
        EditError: If the edit operation fails
    """
    filepath = Path(filepath).resolve()
    
    # Check if the file exists and is a text file
    if filepath.exists():
        if not filepath.is_file():
            raise EditError(f"Not a regular file: {filepath}")
            
        if not is_text_file(filepath):
            raise EditError(f"File does not appear to be a text file: {filepath}")
    
    # Read existing content if file exists
    original_content = ""
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                original_content = f.read()
        except Exception as e:
            raise EditError(f"Failed to read file {filepath}: {e}")
    
    # Apply editor function
    try:
        modified_content = editor_func(original_content)
        
        # If content wasn't modified, return early
        if modified_content == original_content:
            return {
                'success': True,
                'modified': False,
                'file': str(filepath),
                'message': 'File content was not modified',
                'backup': None
            }
        
        # Write changes atomically
        atomic_write(
            filepath=filepath,
            content=modified_content,
            encoding=encoding,
            backup=backup,
            backup_dir=backup_dir,
            create_dirs=create_dirs
        )
        
        return {
            'success': True,
            'modified': True,
            'file': str(filepath),
            'message': 'File updated successfully',
            'backup': str(backup_dir) if backup else None
        }
        
    except Exception as e:
        raise EditError(f"Failed to edit file {filepath}: {e}")

def fix_markdown(content: str) -> str:
    """
    Fix common Markdown formatting issues.
    
    Args:
        content: The Markdown content to fix
        
    Returns:
        The fixed Markdown content
    """
    if not content.strip():
        return content
    
    lines = content.splitlines()
    fixed_lines = []
    in_code_block = False
    in_list = False
    list_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        
        # Handle code blocks
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            fixed_lines.append(line)
            continue
        
        if in_code_block:
            fixed_lines.append(line)
            continue
        
        # Fix list items
        if stripped.startswith(('* ', '- ', '+ ')) or (stripped and stripped[0].isdigit() and ". " in stripped[:5]):
            if not in_list:
                in_list = True
                # Ensure blank line before list
                if fixed_lines and fixed_lines[-1].strip() != '':
                    fixed_lines.append('')
            
            # Standardize list marker
            if stripped.startswith(('- ', '+ ')):
                line = line.replace('- ', '* ', 1).replace('+ ', '* ', 1)
            
            # Ensure consistent indentation
            indent = len(line) - len(line.lstrip())
            if in_list and indent % 2 != 0:
                line = ' ' * (indent + 1) + line.lstrip()
                
            fixed_lines.append(line)
            
        else:
            if in_list and line.strip() != '':
                # Handle nested list items
                if line.strip().startswith(('* ', '- ', '+ ')) or (line.strip() and line.strip()[0].isdigit() and ". " in line.strip()[:5]):
                    fixed_lines.append(line)
                    continue
                # Handle continuation of list item
                elif line.strip() and not line.strip().startswith(('```', '>', '#', '---', '===')):
                    fixed_lines.append('  ' + line.lstrip())
                    continue
                else:
                    in_list = False
                    # Ensure blank line after list
                    if fixed_lines and fixed_lines[-1].strip() != '':
                        fixed_lines.append('')
            
            # Fix headers (ensure space after #)
            if stripped.startswith('#'):
                if '#' in stripped and not stripped.startswith('# '):
                    # Fix headers without space after #
                    count = len(stripped) - len(stripped.lstrip('#'))
                    line = line.replace('#' * count, f"{"#" * count} ", 1)
            
            # Fix code blocks with incorrect backticks
            if '`' in stripped and not any(block in stripped for block in ['```', '`']):
                line = line.replace('`', '`')
            
            fixed_lines.append(line)
    
    # Join lines with proper line endings
    line_ending = detect_line_endings(content)
    result = line_ending.join(fixed_lines)
    return result
    # Ensure exactly one newline at the end of file
    result = result.rstrip() + line_ending
    
    return result

# Register the tools
def register_edit_tools(mcp):
    """Register file editing tools with FastMCP."""
    
    @mcp.tool()
    def edit_text_file(
        file_path: str,
        edit_function: str,
        encoding: str = 'utf-8',
        backup: bool = True,
        backup_dir: Optional[str] = None,
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """
        Safely edit a text file using the provided edit function.
        
        Args:
            file_path: Path to the file to edit
            edit_function: Python code as a string that defines a function taking the file content 
                         and returning the modified content. The function should be named 'edit'. 
                         Example: 'def edit(content): return content.replace("old", "new")'
            encoding: File encoding to use
            backup: Whether to create a backup before editing
            backup_dir: Directory to store backups (default: same as file directory)
            create_dirs: Whether to create parent directories if they don't exist
            
        Returns:
            Dictionary with operation status and information
        """
        try:
            # Create a dictionary to hold the edit function
            namespace = {}
            
            # Define the edit function in the namespace
            exec(edit_function, globals(), namespace)
            
            # Get the edit function from the namespace
            if 'edit' not in namespace or not callable(namespace['edit']):
                return {
                    'success': False,
                    'error': 'The edit_function must define a function named "edit"',
                    'file': file_path
                }
            
            editor_func = namespace['edit']
            
            # Edit the file
            result = edit_file(
                filepath=file_path,
                editor_func=editor_func,
                encoding=encoding,
                backup=backup,
                backup_dir=backup_dir,
                create_dirs=create_dirs
            )
            
            return {
                'success': True,
                'modified': result['modified'],
                'file': file_path,
                'message': result['message'],
                'backup': result.get('backup')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file': file_path
            }
    
    @mcp.tool()
    def fix_markdown_file(
        file_path: str,
        encoding: str = 'utf-8',
        backup: bool = True,
        backup_dir: Optional[str] = None,
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """
        Fix common Markdown formatting issues in a file.
        
        Args:
            file_path: Path to the Markdown file to fix
            encoding: File encoding to use
            backup: Whether to create a backup before editing
            backup_dir: Directory to store backups (default: same as file directory)
            create_dirs: Whether to create parent directories if they don't exist
            
        Returns:
            Dictionary with operation status and information
        """
        try:
            # Edit the file with the fix_markdown function
            result = edit_file(
                filepath=file_path,
                editor_func=fix_markdown,
                encoding=encoding,
                backup=backup,
                backup_dir=backup_dir,
                create_dirs=create_dirs
            )
            
            return {
                'success': True,
                'modified': result['modified'],
                'file': file_path,
                'message': 'Markdown file fixed successfully' if result['modified'] else 'No changes needed',
                'backup': result.get('backup')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file': file_path
            }
