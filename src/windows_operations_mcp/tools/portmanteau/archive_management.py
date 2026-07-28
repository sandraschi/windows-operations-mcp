"""
Archive Management - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_archive":
  winops_archive/list       - List contents of a ZIP or TAR archive
  winops_archive/extract    - Extract a ZIP or TAR archive
  winops_archive/create     - Create a new ZIP or TAR archive
  winops_archive/add        - Add files to an existing ZIP archive
  winops_archive/expand_cab - Expand a Windows CAB file
"""

import asyncio
import os
import tarfile
import zipfile
from pathlib import Path
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)


def _list_blocking(path: str) -> list[str]:
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            return sorted(z.namelist())
    if tarfile.is_tarfile(path):
        with tarfile.open(path, "r:*") as t:
            return sorted(t.getnames())
    raise ValueError("Not a supported ZIP or TAR archive.")


def _extract_blocking(path: str, target_dir: str) -> None:
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            z.extractall(target_dir)
    elif tarfile.is_tarfile(path):
        with tarfile.open(path, "r:*") as t:
            t.extractall(target_dir)
    else:
        raise ValueError("Not a supported ZIP or TAR archive.")


def _create_blocking(path: str, source_files: list[str], archive_type: str) -> None:
    if archive_type == "zip":
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in source_files:
                fp = Path(f)
                if fp.is_file():
                    z.write(f, fp.name)
                elif fp.is_dir():
                    for sf in fp.rglob("*"):
                        if sf.is_file():
                            z.write(str(sf), str(sf.relative_to(fp.parent)))
    else:
        mode = "w:gz" if archive_type == "gztar" else "w"
        with tarfile.open(path, mode) as t:
            for f in source_files:
                t.add(f, arcname=os.path.basename(f))


def _add_blocking(path: str, source_files: list[str]) -> None:
    if not zipfile.is_zipfile(path):
        raise ValueError("add is only supported for ZIP archives.")
    with zipfile.ZipFile(path, "a") as z:
        for f in source_files:
            z.write(f, os.path.basename(f))


def register_archive_management(parent_mcp: FastMCP) -> None:
    """Mount atomic archive tools under namespace 'winops_archive'."""
    ns = FastMCP(name="winops_archive")

    @ns.tool(
        name="list",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    )
    async def list_contents(
        path: Annotated[str, Field(description="Path to ZIP or TAR archive.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """List the contents of a ZIP or TAR archive.

        ## Return Format
        ```json
        {"success": bool, "path": str, "items": [str], "count": int}
        ```

        ## Examples
            list(path="D:\\\\backups\\\\data.zip")
        """
        try:
            items = await asyncio.to_thread(_list_blocking, path)
            return {"success": True, "path": path, "items": items, "count": len(items)}
        except Exception as e:
            return fail_response(
                f"Operation failed: {e}",
                suggestions=["Ensure the file is a valid ZIP or TAR archive."],
            )

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def extract(
        path: Annotated[str, Field(description="Archive to extract.")],
        target_dir: Annotated[str, Field(description="Destination directory.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Extract a ZIP or TAR archive to a directory.

        ## Return Format
        ```json
        {"success": bool, "path": str, "target_dir": str}
        ```

        ## Examples
            extract(path="D:\\\\backups\\\\data.zip", target_dir="D:\\\\extracted")
        """
        try:
            await asyncio.to_thread(_extract_blocking, path, target_dir)
            return {"success": True, "path": path, "target_dir": target_dir}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def create(
        path: Annotated[str, Field(description="Output archive path.")],
        source_files: Annotated[list[str], Field(description="Files or directories to include.")],
        archive_type: Annotated[Literal["zip", "tar", "gztar"], Field(description="Archive format.")] = "zip",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Create a new ZIP or TAR archive from a list of files/directories.

        ## Return Format
        ```json
        {"success": bool, "path": str, "archive_type": str, "file_count": int}
        ```

        ## Examples
            create(path="D:\\\\backups\\\\logs.zip", source_files=["C:\\\\Logs\\\\app.log"])
        """
        try:
            await asyncio.to_thread(_create_blocking, path, source_files, archive_type)
            return {"success": True, "path": path, "archive_type": archive_type, "file_count": len(source_files)}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def add(
        path: Annotated[str, Field(description="Existing ZIP archive path.")],
        source_files: Annotated[list[str], Field(description="Files to add to the archive.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Add files to an existing ZIP archive.

        ## Return Format
        ```json
        {"success": bool, "path": str, "added": int}
        ```

        ## Examples
            add(path="D:\\\\backups\\\\data.zip", source_files=["D:\\\\new_file.txt"])

        Notes:
         - Only ZIP archives are supported for add. Use create for TAR.
        """
        try:
            await asyncio.to_thread(_add_blocking, path, source_files)
            return {"success": True, "path": path, "added": len(source_files)}
        except Exception as e:
            return fail_response(
                f"Operation failed: {e}",
                suggestions=["Only ZIP archives support add. Use create for TAR."],
            )

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def expand_cab(
        path: Annotated[str, Field(description="Path to the .cab file.")],
        target_dir: Annotated[str, Field(description="Destination directory.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Expand a Windows CAB archive using expand.exe.

        ## Return Format
        ```json
        {"success": bool, "path": str, "target_dir": str}
        ```

        ## Examples
            expand_cab(path="C:\\\\Windows\\\\system32\\\\cabinet.cab", target_dir="D:\\\\expanded")
        """
        try:
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            proc = await asyncio.create_subprocess_exec(
                "expand.exe",
                path,
                "-F:*",
                target_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(stderr.decode(errors="replace").strip())
            return {"success": True, "path": path, "target_dir": target_dir}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    parent_mcp.mount(ns, prefix="winops_archive")
    logger.info("Mounted atomic tools: winops_archive/list, /extract, /create, /add, /expand_cab")
