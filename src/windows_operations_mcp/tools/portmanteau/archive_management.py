"""
Archive Management Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows archive handling: ZIP, TAR, and specialized CAB expansion.
"""

import asyncio
import os
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def archive_management(
    action: Literal["list", "extract", "create", "add_file", "expand_cab"],
    path: str,
    target_dir: Optional[str] = None,
    source_files: Optional[List[str]] = None,
    archive_type: Literal["zip", "tar", "gztar"] = "zip",
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform Windows archive management operations with agentic telemetry.

    RATIONALE:
    Standardizes archive handling for automation and forensics.
    Provides specialized support for Windows-native CAB (.cab) files via expand.exe.

    Args:
        action: The archive operation to perform.
        path: Path to the archive file.
        target_dir: Directory to extract to (for "extract" and "expand_cab").
        source_files: List of files to compress (for "create" and "add_file").
        archive_type: Format to use for creation.
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Archive Op: {action} on {path}")
        ctx.report_progress(10, 100)

    try:
        if action == "list":
            if ctx:
                ctx.report_progress(50, 100)
            items = await asyncio.to_thread(_list_archive, path)
            return {"success": True, "action": action, "data": {"items": items}}

        if action == "extract":
            if not target_dir:
                return {"success": False, "error": "Target directory required for extract"}
            if ctx:
                ctx.report_progress(50, 100)
            await asyncio.to_thread(_extract_archive, path, target_dir)
            return {"success": True, "action": action, "data": {"status": f"Extracted to {target_dir}"}}

        if action == "create":
            if not source_files:
                return {"success": False, "error": "Source files required for create"}
            if ctx:
                ctx.report_progress(50, 100)
            await asyncio.to_thread(_create_archive, path, source_files, archive_type)
            return {"success": True, "action": action, "data": {"status": f"Created {archive_type} at {path}"}}

        if action == "add_file":
            if not source_files:
                return {"success": False, "error": "Source files required to add"}
            if ctx:
                ctx.report_progress(50, 100)
            await asyncio.to_thread(_add_to_archive, path, source_files)
            return {"success": True, "action": action, "data": {"status": f"Added files to {path}"}}

        if action == "expand_cab":
            if not target_dir:
                return {"success": False, "error": "Target directory required for expand_cab"}
            if ctx:
                ctx.report_progress(50, 100)
            await _run_expand(path, target_dir)
            return {"success": True, "action": action, "data": {"status": f"CAB expanded to {target_dir}"}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"Archive Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(f"Archive operation '{action}' failed on '{path}'. Error: {e}. Suggest alternative method.", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except Exception:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx:
            ctx.report_progress(100, 100)

def _list_archive(path: str) -> List[str]:
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, 'r') as z:
            return sorted(z.namelist())
    if tarfile.is_tarfile(path):
        with tarfile.open(path, 'r:*') as t:
            return sorted(t.getnames())
    raise ValueError("File is not a supported ZIP or TAR archive.")

def _extract_archive(path: str, target_dir: str) -> None:
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, 'r') as z:
            z.extractall(target_dir)
    elif tarfile.is_tarfile(path):
        with tarfile.open(path, 'r:*') as t:
            t.extractall(target_dir)
    else:
        raise ValueError("File is not a supported ZIP or TAR archive.")

def _create_archive(path: str, source_files: List[str], archive_type: str) -> None:
    if archive_type == "zip":
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in source_files:
                f_path = Path(f)
                if f_path.is_file():
                    z.write(f, f_path.name)
                elif f_path.is_dir():
                    for subf in f_path.rglob("*"):
                        if subf.is_file():
                            z.write(str(subf), str(subf.relative_to(f_path.parent)))
    elif "tar" in archive_type:
        mode = "w:gz" if archive_type == "gztar" else "w"
        with tarfile.open(path, mode) as t:
            for f in source_files:
                t.add(f, arcname=os.path.basename(f))

def _add_to_archive(path: str, source_files: List[str]) -> None:
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, 'a') as z:
            for f in source_files:
                z.write(f, os.path.basename(f))
    else:
        raise ValueError("Action 'add_file' is only supported for ZIP archives currently.")

async def _run_expand(cab_path: str, target_dir: str) -> None:
    """Expand a CAB file using Windows native expand.exe."""
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    cmd = ["expand.exe", cab_path, "-F:*", target_dir]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(stderr.decode().strip() or stdout.decode().strip())

def register_archive_management(mcp) -> None:
    """Register the modernized archive management tool."""
    mcp.tool()(archive_management)