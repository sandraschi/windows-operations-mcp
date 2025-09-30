"""
Archive Tools for Windows Operations MCP

Provides functionality to work with various archive formats including ZIP and TAR.
"""
import os
import zipfile
import tarfile
import shutil
import fnmatch
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Set

from ..logging_config import get_logger
from ..decorators import tool

logger = get_logger(__name__)

class ArchiveError(Exception):
    """Base exception for archive operations."""
    pass

class UnsupportedFormatError(ArchiveError):
    """Raised when an unsupported archive format is encountered."""
    pass

def _get_archive_format(file_path: str) -> str:
    """Determine the archive format from file extension."""
    file_path = str(file_path).lower()
    if file_path.endswith('.zip'):
        return 'zip'
    elif file_path.endswith(('.tar.gz', '.tgz')):
        return 'tar.gz'
    elif file_path.endswith('.tar'):
        return 'tar'
    else:
        raise UnsupportedFormatError(f"Unsupported archive format: {file_path}")

def _should_exclude_path(file_path: str, exclude_patterns: List[str], base_path: str = "") -> bool:
    """
    Check if a file path should be excluded based on exclusion patterns.

    Args:
        file_path: The file path to check
        exclude_patterns: List of glob patterns to match against
        base_path: Base path for relative pattern matching

    Returns:
        True if the path should be excluded, False otherwise
    """
    if not exclude_patterns:
        return False

    # Convert to Path for easier manipulation
    path = Path(file_path)

    # Get relative path from base directory if provided
    if base_path:
        try:
            base = Path(base_path)
            rel_path = path.relative_to(base)
            path_str = str(rel_path).replace('\\', '/')
        except ValueError:
            # Path is not relative to base, use absolute path
            path_str = str(path).replace('\\', '/')
    else:
        path_str = str(path).replace('\\', '/')

    # Check against each exclusion pattern
    for pattern in exclude_patterns:
        # Convert pattern to use forward slashes for consistency
        pattern = pattern.replace('\\', '/')

        # Check if pattern matches
        if fnmatch.fnmatch(path_str, pattern):
            return True

        # Also check if pattern matches just the filename
        if fnmatch.fnmatch(path.name, pattern):
            return True

        # Check if pattern matches any parent directory
        for part in path.parts:
            if fnmatch.fnmatch(part, pattern):
                return True

    return False

def _load_gitignore_patterns(repo_path: str) -> List[str]:
    """
    Load .gitignore patterns from a repository.

    Args:
        repo_path: Path to the repository root

    Returns:
        List of gitignore patterns
    """
    gitignore_path = Path(repo_path) / '.gitignore'
    patterns = []

    if gitignore_path.exists():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            logger.warning(f"Failed to read .gitignore file: {e}")

    return patterns

def _get_default_exclusion_patterns() -> List[str]:
    """
    Get default exclusion patterns for common artifacts.

    Returns:
        List of default exclusion patterns
    """
    return [
        # Node.js
        'node_modules/',
        'node_modules/**',
        'npm-debug.log*',
        'yarn-debug.log*',
        'yarn-error.log*',

        # Python
        '__pycache__/',
        '__pycache__/**',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        'build/',
        'develop-eggs/',
        'dist/',
        'downloads/',
        'eggs/',
        '.eggs/',
        'lib/',
        'lib64/',
        'parts/',
        'sdist/',
        'var/',
        '*.egg-info/',
        '.installed.cfg',
        '*.egg',
        'MANIFEST',

        # Logs
        '*.log',
        'logs/',
        'logs/**',
        'log/',
        'log/**',
        '*.log.*',

        # Build artifacts
        'build/',
        'build/**',
        'dist/',
        'dist/**',
        'target/',
        'target/**',
        'out/',
        'out/**',
        'output/',
        'output/**',

        # IDE and editor files
        '.vscode/',
        '.vscode/**',
        '.idea/',
        '.idea/**',
        '*.swp',
        '*.swo',
        '*~',
        '.DS_Store',
        'Thumbs.db',

        # OS generated files
        '.DS_Store',
        '.DS_Store?',
        '._*',
        '.Spotlight-V100',
        '.Trashes',
        'ehthumbs.db',
        'Thumbs.db',

        # Temporary files
        '*.tmp',
        '*.temp',
        'tmp/',
        'tmp/**',
        'temp/',
        'temp/**',

        # Coverage and test artifacts
        '.coverage',
        'coverage.xml',
        '.tox/',
        '.tox/**',
        '.pytest_cache/',
        '.pytest_cache/**',
        'htmlcov/',
        'htmlcov/**',

        # Git
        '.git/',
        '.git/**',
        '.gitignore',
        '.gitattributes',
        '.gitmodules',

        # Docker
        'Dockerfile.*',
        'docker-compose*.yml',
        '.dockerignore',

        # CI/CD
        '.github/',
        '.github/**',
        '.gitlab-ci.yml',
        '.travis.yml',
        'Jenkinsfile',

        # Package managers
        'package-lock.json',
        'yarn.lock',
        'pnpm-lock.yaml',
        'composer.lock',
        'Gemfile.lock',
        'requirements.txt.lock',

        # Documentation builds
        'docs/_build/',
        'docs/_build/**',
        'site/',
        'site/**',
    ]

# Archive creation functions (defined before register function for proper imports)
@tool(
    name="create_archive",
    description="Create a new archive file containing the specified files and directories with optional exclusion patterns",
    parameters={
        "archive_path": {
            "type": "string",
            "description": "Path where the archive will be created"
        },
        "source_paths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of files/directories to include in the archive"
        },
        "compression_level": {
            "type": "integer",
            "description": "Compression level (0-9, where 0 is no compression and 9 is maximum compression)",
            "default": 6
        },
        "exclude_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of glob patterns to exclude from the archive"
        },
        "use_gitignore": {
            "type": "boolean",
            "description": "Automatically include .gitignore patterns from repository",
            "default": True
        },
        "use_default_exclusions": {
            "type": "boolean",
            "description": "Include default exclusion patterns for common artifacts",
            "default": True
        }
    },
    required=["archive_path", "source_paths"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "archive_path": {"type": "string"},
            "excluded_count": {"type": "integer"},
            "included_count": {"type": "integer"}
        }
    }
)
def create_archive(
    archive_path: str,
    source_paths: List[str],
    compression_level: int = 6,
    exclude_patterns: Optional[List[str]] = None,
    use_gitignore: bool = True,
    use_default_exclusions: bool = True
) -> Dict[str, Any]:
    """
    Create a new archive file containing the specified files and directories with exclusion support.

    Args:
        archive_path: Path where the archive will be created
        source_paths: List of files/directories to include in the archive
        compression_level: Compression level (0-9, where 0 is no compression and 9 is maximum compression)
        exclude_patterns: List of glob patterns to exclude from the archive
        use_gitignore: Whether to automatically include .gitignore patterns from repository
        use_default_exclusions: Whether to include default exclusion patterns for common artifacts

    Returns:
        dict: Dictionary with success status, message, path to created archive, and counts
    """
    try:
        archive_path = os.path.abspath(archive_path)
        archive_format = _get_archive_format(archive_path)

        # Build exclusion patterns
        all_exclusions = []

        # Add user-specified patterns
        if exclude_patterns:
            all_exclusions.extend(exclude_patterns)

        # Add default exclusions if requested
        if use_default_exclusions:
            all_exclusions.extend(_get_default_exclusion_patterns())

        # Try to detect repository root and add .gitignore patterns
        if use_gitignore:
            # Look for .git directory in source paths or parent directories
            repo_root = None
            for source_path in source_paths:
                source_abs = os.path.abspath(source_path)
                # Check if current path or any parent has .git
                current = Path(source_abs)
                for parent in [current] + list(current.parents):
                    if (parent / '.git').exists():
                        repo_root = str(parent)
                        break
                    if parent.parent == parent:  # Reached root
                        break

            if repo_root:
                gitignore_patterns = _load_gitignore_patterns(repo_root)
                all_exclusions.extend(gitignore_patterns)
                logger.info(f"Loaded {len(gitignore_patterns)} patterns from .gitignore")

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)

        if archive_format == 'zip':
            return _create_zip(archive_path, source_paths, compression_level, all_exclusions)
        elif archive_format in ('tar', 'tar.gz'):
            return _create_tar(archive_path, source_paths, compression_level, all_exclusions)
        else:
            return {"success": False, "message": f"Unsupported archive format: {archive_format}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to create archive: {str(e)}"}

@tool(
    name="extract_archive",
    description="Extract files from an archive to the specified directory",
    parameters={
        "archive_path": {
            "type": "string",
            "description": "Path to the archive file"
        },
        "extract_dir": {
            "type": "string",
            "description": "Directory where files will be extracted"
        },
        "members": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optional list of files to extract (default: all files)"
        }
    },
    required=["archive_path", "extract_dir"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "extracted_files": {"type": "array", "items": {"type": "string"}}
        }
    }
)
def extract_archive(
    archive_path: str,
    extract_dir: str,
    members: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Extract files from an archive to the specified directory.

    Args:
        archive_path: Path to the archive file
        extract_dir: Directory where files will be extracted
        members: Optional list of files to extract (default: all files)

    Returns:
        dict: Dictionary with success status and extraction details
    """
    try:
        archive_path = os.path.abspath(archive_path)
        extract_dir = os.path.abspath(extract_dir)
        archive_format = _get_archive_format(archive_path)

        # Ensure extraction directory exists
        os.makedirs(extract_dir, exist_ok=True)

        if archive_format == 'zip':
            return _extract_zip(archive_path, extract_dir, members)
        elif archive_format in ('tar', 'tar.gz'):
            return _extract_tar(archive_path, extract_dir, members)
        else:
            return {"success": False, "message": f"Unsupported archive format: {archive_format}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to extract archive: {str(e)}"}

@tool(
    name="list_archive",
    description="List the contents of an archive file",
    parameters={
        "archive_path": {
            "type": "string",
            "description": "Path to the archive file"
        }
    },
    required=["archive_path"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "files": {"type": "array", "items": {"type": "string"}}
        }
    }
)
def list_archive(archive_path: str) -> Dict[str, Any]:
    """
    List the contents of an archive file.

    Args:
        archive_path: Path to the archive file

    Returns:
        dict: Dictionary with success status, message, and list of files in the archive
    """
    try:
        archive_path = os.path.abspath(archive_path)
        archive_format = _get_archive_format(archive_path)

        if archive_format == 'zip':
            return _list_zip(archive_path)
        elif archive_format in ('tar', 'tar.gz'):
            return _list_tar(archive_path)
        else:
            return {"success": False, "message": f"Unsupported archive format: {archive_format}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to list archive contents: {str(e)}"}

@tool(
    name="create_archive",
    description="Create a new archive file containing the specified files and directories with optional exclusion patterns",
    parameters={
        "archive_path": {
            "type": "string",
            "description": "Path where the archive will be created"
        },
        "source_paths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of files/directories to include in the archive"
        },
        "compression_level": {
            "type": "integer",
            "description": "Compression level (0-9, where 0 is no compression and 9 is maximum compression)",
            "default": 6
        },
        "exclude_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of glob patterns to exclude from the archive"
        },
        "use_gitignore": {
            "type": "boolean",
            "description": "Automatically include .gitignore patterns from repository",
            "default": True
        },
        "use_default_exclusions": {
            "type": "boolean",
            "description": "Include default exclusion patterns for common artifacts",
            "default": True
        }
    },
    required=["archive_path", "source_paths"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "archive_path": {"type": "string"},
            "excluded_count": {"type": "integer"},
            "included_count": {"type": "integer"}
        }
    }
)
def create_archive(
    archive_path: str,
    source_paths: List[str],
    compression_level: int = 6,
    exclude_patterns: Optional[List[str]] = None,
    use_gitignore: bool = True,
    use_default_exclusions: bool = True
) -> Dict[str, Any]:
    """
    Create a new archive file containing the specified files and directories with exclusion support.

    Args:
        archive_path: Path where the archive will be created
        source_paths: List of files/directories to include in the archive
        compression_level: Compression level (0-9, where 0 is no compression and 9 is maximum compression)
        exclude_patterns: List of glob patterns to exclude from the archive
        use_gitignore: Whether to automatically include .gitignore patterns from repository
        use_default_exclusions: Whether to include default exclusion patterns for common artifacts

    Returns:
        dict: Dictionary with success status, message, path to created archive, and counts
    """
    try:
        archive_path = os.path.abspath(archive_path)
        archive_format = _get_archive_format(archive_path)

        # Build exclusion patterns
        all_exclusions = []

        # Add user-specified patterns
        if exclude_patterns:
            all_exclusions.extend(exclude_patterns)

        # Add default exclusions if requested
        if use_default_exclusions:
            all_exclusions.extend(_get_default_exclusion_patterns())

        # Try to detect repository root and add .gitignore patterns
        if use_gitignore:
            # Look for .git directory in source paths or parent directories
            repo_root = None
            for source_path in source_paths:
                source_abs = os.path.abspath(source_path)
                # Check if current path or any parent has .git
                current = Path(source_abs)
                for parent in [current] + list(current.parents):
                    if (parent / '.git').exists():
                        repo_root = str(parent)
                        break
                    if parent.parent == parent:  # Reached root
                        break

            if repo_root:
                gitignore_patterns = _load_gitignore_patterns(repo_root)
                all_exclusions.extend(gitignore_patterns)
                logger.info(f"Loaded {len(gitignore_patterns)} patterns from .gitignore")

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)

        if archive_format == 'zip':
            return _create_zip(archive_path, source_paths, compression_level, all_exclusions)
        elif archive_format in ('tar', 'tar.gz'):
            return _create_tar(archive_path, source_paths, compression_level, all_exclusions)
        else:
            return {"success": False, "message": f"Unsupported archive format: {archive_format}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to create archive: {str(e)}"}

@tool(
    name="extract_archive",
    description="Extract files from an archive to the specified directory",
    parameters={
        "archive_path": {
            "type": "string",
            "description": "Path to the archive file"
        },
        "extract_dir": {
            "type": "string",
            "description": "Directory where files will be extracted"
        },
        "members": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optional list of files to extract (default: all files)"
        }
    },
    required=["archive_path", "extract_dir"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "extracted_files": {"type": "array", "items": {"type": "string"}}
        }
    }
)
def extract_archive(
    archive_path: str,
    extract_dir: str,
    members: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Extract files from an archive to the specified directory.

    Args:
        archive_path: Path to the archive file
        extract_dir: Directory where files will be extracted
        members: Optional list of files to extract (default: all files)

    Returns:
        dict: Dictionary with success status, message, and list of extracted files
    """
    try:
        archive_path = os.path.abspath(archive_path)
        extract_dir = os.path.abspath(extract_dir)
        archive_format = _get_archive_format(archive_path)
        
        # Ensure extract directory exists
        os.makedirs(extract_dir, exist_ok=True)
        
        if archive_format == 'zip':
            return _extract_zip(archive_path, extract_dir, members)
        elif archive_format in ('tar', 'tar.gz'):
            return _extract_tar(archive_path, extract_dir, members)
        else:
            return {"success": False, "message": f"Unsupported archive format: {archive_format}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to extract archive: {str(e)}"}

@tool(
    name="list_archive",
    description="List the contents of an archive file",
    parameters={
        "archive_path": {
            "type": "string",
            "description": "Path to the archive file"
        }
    },
    required=["archive_path"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "files": {"type": "array", "items": {"type": "string"}}
        }
    }
)
def list_archive(archive_path: str) -> Dict[str, Any]:
    """
    List the contents of an archive file.

    Args:
        archive_path: Path to the archive file

    Returns:
        dict: Dictionary with success status, message, and list of files in the archive
    """
    try:
        archive_path = os.path.abspath(archive_path)
        archive_format = _get_archive_format(archive_path)
        
        if archive_format == 'zip':
            return _list_zip(archive_path)
        elif archive_format in ('tar', 'tar.gz'):
            return _list_tar(archive_path)
        else:
            return {"success": False, "message": f"Unsupported archive format: {archive_format}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to list archive contents: {str(e)}"}

def register_archive_tools(mcp):
    """Register archive tools with FastMCP."""
    mcp.tool(create_archive)
    mcp.tool(extract_archive)
    mcp.tool(list_archive)
    
    logger.info("archive_tools_registered", tools=["create_archive", "extract_archive", "list_archive"])

def _create_zip(archive_path: str, source_paths: List[str], compression_level: int, exclude_patterns: List[str]) -> Dict[str, Any]:
    """Create a ZIP archive with exclusion support."""
    try:
        included_count = 0
        excluded_count = 0

        with zipfile.ZipFile(
            archive_path,
            'w',
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=compression_level
        ) as zipf:
            for source_path in source_paths:
                source_path = os.path.abspath(source_path)
                if os.path.isdir(source_path):
                    for root, dirs, files in os.walk(source_path):
                        # Filter out excluded directories
                        dirs[:] = [d for d in dirs if not _should_exclude_path(
                            os.path.join(root, d), exclude_patterns, source_path
                        )]

                        for file in files:
                            file_path = os.path.join(root, file)

                            # Check if file should be excluded
                            if _should_exclude_path(file_path, exclude_patterns, source_path):
                                excluded_count += 1
                                logger.debug(f"Excluding file: {file_path}")
                                continue

                            arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                            zipf.write(file_path, arcname=arcname)
                            included_count += 1
                else:
                    # Check if single file should be excluded
                    if _should_exclude_path(source_path, exclude_patterns, os.path.dirname(source_path)):
                        excluded_count += 1
                        logger.debug(f"Excluding file: {source_path}")
                        continue

                    zipf.write(source_path, arcname=os.path.basename(source_path))
                    included_count += 1

        return {
            "success": True,
            "message": f"Successfully created ZIP archive: {archive_path}",
            "archive_path": archive_path,
            "excluded_count": excluded_count,
            "included_count": included_count
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to create ZIP archive: {str(e)}"}

def _create_tar(archive_path: str, source_paths: List[str], compression_level: int, exclude_patterns: List[str]) -> Dict[str, Any]:
    """Create a TAR or TAR.GZ archive with exclusion support."""
    try:
        mode = 'w:gz' if archive_path.endswith(('.tar.gz', '.tgz')) else 'w'
        included_count = 0
        excluded_count = 0

        with tarfile.open(archive_path, mode) as tar:
            for source_path in source_paths:
                source_path = os.path.abspath(source_path)

                # For tar, we need to manually filter files since tarfile.add() doesn't support exclusions
                if os.path.isdir(source_path):
                    for root, dirs, files in os.walk(source_path):
                        # Filter out excluded directories
                        dirs[:] = [d for d in dirs if not _should_exclude_path(
                            os.path.join(root, d), exclude_patterns, source_path
                        )]

                        for file in files:
                            file_path = os.path.join(root, file)

                            # Check if file should be excluded
                            if _should_exclude_path(file_path, exclude_patterns, source_path):
                                excluded_count += 1
                                logger.debug(f"Excluding file: {file_path}")
                                continue

                            arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                            tar.add(file_path, arcname=arcname)
                            included_count += 1
                else:
                    # Check if single file should be excluded
                    if _should_exclude_path(source_path, exclude_patterns, os.path.dirname(source_path)):
                        excluded_count += 1
                        logger.debug(f"Excluding file: {source_path}")
                        continue

                    tar.add(source_path, arcname=os.path.basename(source_path))
                    included_count += 1

        return {
            "success": True,
            "message": f"Successfully created TAR archive: {archive_path}",
            "archive_path": archive_path,
            "excluded_count": excluded_count,
            "included_count": included_count
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to create TAR archive: {str(e)}"}

def _extract_zip(archive_path: str, extract_dir: str, members: Optional[List[str]]) -> Dict[str, Any]:
    """Extract files from a ZIP archive."""
    try:
        extracted_files = []
        
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            file_list = members if members else zipf.namelist()
            
            for member in file_list:
                try:
                    zipf.extract(member, extract_dir)
                    extracted_files.append(os.path.join(extract_dir, member))
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Failed to extract {member}: {str(e)}",
                        "extracted_files": extracted_files
                    }
        
        return {
            "success": True,
            "message": f"Successfully extracted {len(extracted_files)} files to {extract_dir}",
            "extracted_files": extracted_files
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to extract ZIP archive: {str(e)}",
            "extracted_files": []
        }

def _extract_tar(archive_path: str, extract_dir: str, members: Optional[List[str]]) -> Dict[str, Any]:
    """Extract files from a TAR or TAR.GZ archive."""
    try:
        extracted_files = []
        mode = 'r:gz' if archive_path.endswith(('.tar.gz', '.tgz')) else 'r'
        
        with tarfile.open(archive_path, mode) as tar:
            if members:
                members_to_extract = []
                for member in members:
                    try:
                        members_to_extract.append(tar.getmember(member))
                    except KeyError:
                        return {
                            "success": False,
                            "message": f"Member not found in archive: {member}",
                            "extracted_files": extracted_files
                        }
            else:
                members_to_extract = tar.getmembers()
            
            for member in members_to_extract:
                try:
                    tar.extract(member, extract_dir)
                    extracted_files.append(os.path.join(extract_dir, member.name))
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Failed to extract {member.name}: {str(e)}",
                        "extracted_files": extracted_files
                    }
        
        return {
            "success": True,
            "message": f"Successfully extracted {len(extracted_files)} files to {extract_dir}",
            "extracted_files": extracted_files
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to extract TAR archive: {str(e)}",
            "extracted_files": []
        }

def _list_zip(archive_path: str) -> Dict[str, Any]:
    """List contents of a ZIP archive."""
    try:
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            file_list = zipf.namelist()
            
            return {
                "success": True,
                "message": f"Found {len(file_list)} files in {archive_path}",
                "files": file_list
            }
    except zipfile.BadZipFile as e:
        return {"success": False, "message": f"Bad ZIP file: {str(e)}"}

def _list_tar(archive_path: str) -> Dict[str, Any]:
    """List contents of a TAR or TAR.GZ archive."""
    try:
        mode = 'r:gz' if archive_path.endswith(('.tar.gz', '.tgz')) else 'r'
        
        with tarfile.open(archive_path, mode) as tar:
            file_list = [member.name for member in tar.getmembers()]
            
            return {
                "success": True,
                "message": f"Found {len(file_list)} files in {archive_path}",
                "files": file_list
            }
    except tarfile.TarError as e:
        return {"success": False, "message": f"Error reading TAR archive: {str(e)}"}
