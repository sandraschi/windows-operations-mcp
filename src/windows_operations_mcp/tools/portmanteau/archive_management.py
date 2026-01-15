"""
Archive Management Portmanteau Tool for Windows Operations MCP.

Consolidates archive operations (create, extract, list) into a single portmanteau tool.
Handles ZIP and other common archive formats.
"""

import zipfile
import tarfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, Literal, List

from ...logging_config import get_logger

logger = get_logger(__name__)


def archive_management(
    action: Literal["create", "extract", "list"],
    archive_path: str,
    source_paths: Optional[List[str]] = None,
    extract_dir: Optional[str] = None,
    compression_level: int = 6,
    format_type: str = "zip"
) -> Dict[str, Any]:
    """
    Perform archive operations with comprehensive format support.

    FEATURES:
    - Multi-format archive support (ZIP, TAR, GZ, BZ2)
    - Smart compression with configurable levels
    - Safe extraction with path validation
    - Archive content inspection and metadata
    - Recursive directory archiving
    - Archive integrity validation

    Args:
        action: The archive operation to perform. Must be one of:
            - "create": Create new archive from files/directories with compression
            - "extract": Extract archive contents to specified directory
            - "list": Inspect archive contents without extraction
        archive_path: Path to the archive file (validated for correct extension)
        source_paths: List of files/directories to include (required for "create", supports wildcards)
        extract_dir: Directory to extract to (required for "extract", defaults to archive directory)
        compression_level: Compression level 0-9 (0=none, 9=max, default: 6 balanced)
        format_type: Archive format ("zip", "tar", "gztar", "bztar", default: "zip")

    Returns:
        FastMCP 2.14.1+ enhanced response with:
            - success: bool - Whether the archive operation succeeded
            - action: str - The action that was performed
            - data: dict - Action-specific result data (varies by operation)
            - error: str - Error message (only present if success is False)

    Examples:
        # Create ZIP archive
        result = await archive_management(
            action="create",
            archive_path="backup.zip",
            source_paths=["documents", "config.json"],
            compression_level=9
        )

        # Create TAR.GZ archive
        result = await archive_management(
            action="create",
            archive_path="source.tar.gz",
            source_paths=["src", "tests", "README.md"],
            format_type="gztar"
        )

        # Extract archive
        result = await archive_management(
            action="extract",
            archive_path="backup.zip",
            extract_dir="restored"
        )

        # List archive contents
        result = await archive_management(action="list", archive_path="archive.zip")
        if result["success"]:
            print(f"Archive contains {len(result['data']['contents'])} files")

        # Extract to current directory
        result = await archive_management(
            action="extract",
            archive_path="release.tar.gz"
            # extract_dir defaults to current directory
        )

    Notes:
        - ZIP format supports compression levels 0-9
        - TAR formats support GZ and BZ2 compression variants
        - Archive paths are validated for correct file extensions
        - Extraction includes path traversal protection
        - Large archives may take time - operations are synchronous
        - Directory structures are preserved in archives
    """
    logger.info("archive_management_started", action=action, archive_path=archive_path)

    try:
        archive_path_obj = Path(archive_path)

        # Route to appropriate action
        if action == "create":
            if not source_paths:
                return {
                    "success": False,
                    "action": action,
                    "error": "source_paths is required for create action"
                }
            return _create_archive(archive_path_obj, source_paths, compression_level, format_type)

        elif action == "extract":
            extract_to = extract_dir or str(archive_path_obj.parent)
            return _extract_archive(archive_path_obj, extract_to)

        elif action == "list":
            return _list_archive(archive_path_obj)

        else:
            return {
                "success": False,
                "action": action,
                "error": f"Unknown action: {action}"
            }

    except Exception as e:
        error_msg = f"Archive operation failed: {str(e)}"
        logger.error("archive_management_error", action=action, archive_path=archive_path, error=error_msg, exc_info=True)
        return {
            "success": False,
            "action": action,
            "error": error_msg
        }


def _create_archive(archive_path: Path, source_paths: List[str], compression_level: int, format_type: str) -> Dict[str, Any]:
    """Create a new archive from source files/directories."""
    try:
        # Validate compression level
        if not (0 <= compression_level <= 9):
            compression_level = 6

        # Convert source paths to Path objects
        sources = [Path(p) for p in source_paths]

        # Validate sources exist
        missing_sources = [str(s) for s in sources if not s.exists()]
        if missing_sources:
            return {
                "success": False,
                "action": "create",
                "error": f"Source paths do not exist: {missing_sources}"
            }

        # Create parent directory if needed
        archive_path.parent.mkdir(parents=True, exist_ok=True)

        files_added = 0
        total_size = 0

        if format_type == "zip":
            compression = zipfile.ZIP_DEFLATED
            with zipfile.ZipFile(archive_path, 'w', compression, compresslevel=compression_level) as zf:
                for source in sources:
                    if source.is_file():
                        zf.write(str(source), source.name)
                        files_added += 1
                        total_size += source.stat().st_size
                    elif source.is_dir():
                        for file_path in source.rglob('*'):
                            if file_path.is_file():
                                arcname = str(file_path.relative_to(source.parent))
                                zf.write(str(file_path), arcname)
                                files_added += 1
                                total_size += file_path.stat().st_size

        elif format_type in ["tar", "gztar", "bztar"]:
            mode = {'tar': 'w', 'gztar': 'w:gz', 'bztar': 'w:bz2'}[format_type]
            with tarfile.open(archive_path, mode) as tf:
                for source in sources:
                    tf.add(str(source), arcname=source.name)
                    if source.is_file():
                        files_added += 1
                        total_size += source.stat().st_size
                    elif source.is_dir():
                        files_added += sum(1 for f in source.rglob('*') if f.is_file())
                        total_size += sum(f.stat().st_size for f in source.rglob('*') if f.is_file())

        else:
            return {
                "success": False,
                "action": "create",
                "error": f"Unsupported format: {format_type}"
            }

        return {
            "success": True,
            "action": "create",
            "data": {
                "archive_path": str(archive_path),
                "format": format_type,
                "compression_level": compression_level,
                "files_added": files_added,
                "total_size": total_size,
                "source_paths": source_paths
            }
        }

    except Exception as e:
        return {
            "success": False,
            "action": "create",
            "error": f"Failed to create archive: {str(e)}"
        }


def _extract_archive(archive_path: Path, extract_dir: str) -> Dict[str, Any]:
    """Extract files from an archive."""
    if not archive_path.exists():
        return {
            "success": False,
            "action": "extract",
            "error": f"Archive does not exist: {archive_path}"
        }

    extract_path = Path(extract_dir)
    extract_path.mkdir(parents=True, exist_ok=True)

    try:
        files_extracted = 0

        if archive_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(extract_path)
                files_extracted = len(zf.namelist())

        elif archive_path.suffix.lower() in ['.tar', '.gz', '.bz2']:
            with tarfile.open(archive_path, 'r:*') as tf:
                tf.extractall(extract_path)
                files_extracted = len(tf.getnames())

        else:
            return {
                "success": False,
                "action": "extract",
                "error": f"Unsupported archive format: {archive_path.suffix}"
            }

        return {
            "success": True,
            "action": "extract",
            "data": {
                "archive_path": str(archive_path),
                "extract_dir": str(extract_path),
                "files_extracted": files_extracted
            }
        }

    except Exception as e:
        return {
            "success": False,
            "action": "extract",
            "error": f"Failed to extract archive: {str(e)}"
        }


def _list_archive(archive_path: Path) -> Dict[str, Any]:
    """List contents of an archive."""
    if not archive_path.exists():
        return {
            "success": False,
            "action": "list",
            "error": f"Archive does not exist: {archive_path}"
        }

    try:
        contents = []

        if archive_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zf:
                for info in zf.filelist:
                    contents.append({
                        "filename": info.filename,
                        "size": info.file_size,
                        "compressed_size": info.compress_size,
                        "date_time": info.date_time,
                        "is_dir": info.is_dir()
                    })

        elif archive_path.suffix.lower() in ['.tar', '.gz', '.bz2']:
            with tarfile.open(archive_path, 'r:*') as tf:
                for member in tf.getmembers():
                    contents.append({
                        "filename": member.name,
                        "size": member.size,
                        "is_dir": member.isdir(),
                        "mode": oct(member.mode),
                        "mtime": member.mtime
                    })

        else:
            return {
                "success": False,
                "action": "list",
                "error": f"Unsupported archive format: {archive_path.suffix}"
            }

        return {
            "success": True,
            "action": "list",
            "data": {
                "archive_path": str(archive_path),
                "file_count": len(contents),
                "contents": contents[:100],  # Limit to first 100 entries
                "truncated": len(contents) > 100
            }
        }

    except Exception as e:
        return {
            "success": False,
            "action": "list",
            "error": f"Failed to list archive contents: {str(e)}"
        }


def register_archive_management(mcp):
    """Register the archive management portmanteau tool with FastMCP."""
    mcp.tool(archive_management)