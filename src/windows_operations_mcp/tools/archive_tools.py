"""
Archive Tools for Windows Operations MCP

Provides functionality to work with various archive formats including ZIP and TAR.
"""
import os
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

from ..logging_config import get_logger

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

def register_archive_tools(mcp):
    """Register archive tools with FastMCP."""
    
    @mcp.tool()
    def create_archive(
        archive_path: str,
        source_paths: List[str],
        compression_level: int = 6
    ) -> Dict[str, Any]:
        """
        Create a new archive file containing the specified files and directories.
        
        Args:
            archive_path: Path where the archive will be created
            source_paths: List of files/directories to include in the archive
            compression_level: Compression level (0-9, where 0 is no compression and 9 is maximum compression)
            
        Returns:
            dict: Dictionary with success status, message, and path to created archive
        """
        try:
            archive_path = os.path.abspath(archive_path)
            archive_format = _get_archive_format(archive_path)
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            
            if archive_format == 'zip':
                return _create_zip(archive_path, source_paths, compression_level)
            elif archive_format in ('tar', 'tar.gz'):
                return _create_tar(archive_path, source_paths, compression_level)
            else:
                return {"success": False, "message": f"Unsupported archive format: {archive_format}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to create archive: {str(e)}"}

    @mcp.tool()
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

    @mcp.tool()
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
    
    logger.info("archive_tools_registered", tools=["create_archive", "extract_archive", "list_archive"])

def _create_zip(archive_path: str, source_paths: List[str], compression_level: int) -> Dict[str, Any]:
    """Create a ZIP archive."""
    try:
        with zipfile.ZipFile(
            archive_path,
            'w',
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=compression_level
        ) as zipf:
            for source_path in source_paths:
                source_path = os.path.abspath(source_path)
                if os.path.isdir(source_path):
                    for root, _, files in os.walk(source_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                            zipf.write(file_path, arcname=arcname)
                else:
                    zipf.write(source_path, arcname=os.path.basename(source_path))
        
        return {
            "success": True,
            "message": f"Successfully created ZIP archive: {archive_path}",
            "archive_path": archive_path
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to create ZIP archive: {str(e)}"}

def _create_tar(archive_path: str, source_paths: List[str], compression_level: int) -> Dict[str, Any]:
    """Create a TAR or TAR.GZ archive."""
    try:
        mode = 'w:gz' if archive_path.endswith(('.tar.gz', '.tgz')) else 'w'
        
        with tarfile.open(archive_path, mode) as tar:
            for source_path in source_paths:
                source_path = os.path.abspath(source_path)
                if os.path.isdir(source_path):
                    tar.add(source_path, arcname=os.path.basename(source_path))
                else:
                    tar.add(source_path, arcname=os.path.basename(source_path))
        
        return {
            "success": True,
            "message": f"Successfully created TAR archive: {archive_path}",
            "archive_path": archive_path
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
