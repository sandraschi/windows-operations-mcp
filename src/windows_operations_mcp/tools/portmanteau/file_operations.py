"""
File Operations - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_file":
  winops_file/read   - Read text content of a file
  winops_file/write  - Write text content to a file (with line_ending support)
  winops_file/edit   - Safe search/replace editing with atomic writes and backups
  winops_file/delete - Delete a file or directory tree
  winops_file/move   - Move a file or directory
  winops_file/copy   - Copy a file or directory tree
  winops_file/list   - List directory contents with filtering
  winops_file/info   - Get file/directory metadata
"""

import asyncio
import shutil
from pathlib import Path
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.tools.file_operations.edit import atomic_write, detect_line_endings
from windows_operations_mcp.tools.file_operations.folder_operations import list_directory_contents
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)


def register_file_operations(parent_mcp: FastMCP) -> None:
    """Mount atomic file operation tools under namespace 'winops_file'."""
    ns = FastMCP(name="winops_file")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def read(
        path: Annotated[str, Field(description="File path to read.")],
        encoding: Annotated[str, Field(description="Text encoding.")] = "utf-8",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Read the text content of a file.

        ## Return Format
        ```json
        {"success": bool, "content": str, "size": int}
        ```

        ## Examples
            read(path="D:\\\\config\\\\app.json")
        """
        try:
            p = Path(path).resolve()
            if not p.is_file():
                return fail_response(f"Not a file: {path}",
                        suggestions=["Verify the path exists and is a file, not a directory."])
            content = await asyncio.to_thread(p.read_text, encoding)
            return {"success": True, "content": content, "size": len(content)}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def write(
        path: Annotated[str, Field(description="Destination file path.")],
        content: Annotated[str, Field(description="Text content to write.")],
        overwrite: Annotated[bool, Field(description="Allow overwriting existing file.")] = False,
        create_dirs: Annotated[bool, Field(description="Create parent directories if missing.")] = True,
        encoding: Annotated[str, Field(description="Text encoding.")] = "utf-8",
        line_ending: Annotated[str | None, Field(description="Line ending: 'lf' (\\\\n), 'crlf' (\\\\r\\\\n), or null (auto-detect).")] = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Write text content to a file with line ending normalization.

        ## Return Format
        ```json
        {"success": bool, "path": str, "bytes": int, "line_ending": str}
        ```

        ## Examples
            write(path="D:\\\\logs\\\\output.txt", content="hello", create_dirs=True)
            write(path="/tmp/run.sh", content="echo hi", line_ending="lf")

        Notes:
         - line_ending='lf' writes Unix-style \\\\n (safe for .sh, .py used in containers)
         - line_ending='crlf' writes Windows-style \\\\r\\\\n (.bat, .ps1)
         - line_ending=None auto-detects from content (default \\\\n for new files)
        """
        try:
            p = Path(path).resolve()
            if p.exists() and not overwrite:
                return fail_response("File exists and overwrite is False",
                        suggestions=["Pass overwrite=True to replace the existing file."])
            if create_dirs:
                p.parent.mkdir(parents=True, exist_ok=True)

            # Map line_ending strings to actual chars
            le_map = {"lf": "\n", "crlf": "\r\n"}
            actual_le = le_map.get(line_ending) if line_ending else None
            await asyncio.to_thread(
                lambda: atomic_write(p, content, encoding=encoding, line_ending=actual_le, backup=False),
            )
            # Determine what line ending was actually used
            final_content = await asyncio.to_thread(p.read_text, encoding)
            detected_le = detect_line_endings(final_content)
            return {"success": True, "path": str(p), "bytes": len(final_content), "line_ending": repr(detected_le)}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def edit(
        path: Annotated[str, Field(description="File path to edit.")],
        old_string: Annotated[str, Field(description="String to find.")],
        new_string: Annotated[str, Field(description="String to replace with.")],
        encoding: Annotated[str, Field(description="Text encoding.")] = "utf-8",
        backup: Annotated[bool, Field(description="Create a .bak backup before editing.")] = True,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Replace a string in a text file with safe atomic write and optional backup.

        ## Return Format
        ```json
        {"success": bool, "modified": bool, "file": str, "backup": str|null}
        ```

        ## Examples
            edit(path="config.ini", old_string="debug=false", new_string="debug=true")
            edit(path="script.sh", old_string="set -e", new_string="set -ex")
        """
        try:
            p = Path(path).resolve()
            if not p.is_file():
                return fail_response(f"Not a file: {path}")
            original = await asyncio.to_thread(p.read_text, encoding)
            if old_string not in original:
                return fail_response("old_string not found in file",
                        suggestions=["Check for whitespace differences or trailing characters."])

            def replacer(content: str) -> str:
                return content.replace(old_string, new_string)

            modified = replacer(original)
            if modified == original:
                return {"success": True, "modified": False, "file": str(p), "backup": None}

            from windows_operations_mcp.tools.file_operations.edit import create_backup

            backup_path = None
            if backup:
                backup_path = await asyncio.to_thread(create_backup, p)

            await asyncio.to_thread(
                atomic_write, p, modified, encoding=encoding, backup=False,
            )
            return {"success": True, "modified": True, "file": str(p),
                    "backup": str(backup_path) if backup_path else None}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(name="list", annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def list_contents(
        path: Annotated[str, Field(description="Directory path to list.")],
        pattern: Annotated[str | None, Field(description="Optional glob pattern filter (e.g. '*.py').")] = None,
        include_hidden: Annotated[bool, Field(description="Include hidden files/folders.")] = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """List the contents of a directory with optional glob filtering.

        ## Return Format
        ```json
        {"success": bool, "path": str, "items": [...], "count": int}
        ```

        ## Examples
            list(path="D:\\\\projects")
            list(path=".", pattern="*.log", include_hidden=True)
        """
        try:
            result = await asyncio.to_thread(
                list_directory_contents, directory_path=path, include_hidden=include_hidden, pattern=pattern,
            )
            if not result.get("exists"):
                return fail_response(f"Directory not found: {path}")
            return {"success": True, "path": result["path"], "items": result["items"], "count": result["count"]}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False))
    async def delete(
        path: Annotated[str, Field(description="File or directory path to delete.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Delete a file or recursively delete a directory tree.

        ## Return Format
        ```json
        {"success": bool, "deleted": str}
        ```

        ## Examples
            delete(path="D:\\\\temp\\\\old_file.txt")

        Notes:
         - Directories are removed with shutil.rmtree (recursive, no confirmation).
        """
        try:
            p = Path(path).resolve()
            if not p.exists():
                return fail_response(f"Path does not exist: {path}")
            if p.is_file():
                await asyncio.to_thread(p.unlink)
            else:
                await asyncio.to_thread(shutil.rmtree, str(p))
            return {"success": True, "deleted": str(p)}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def move(
        path: Annotated[str, Field(description="Source file or directory path.")],
        destination: Annotated[str, Field(description="Destination path.")],
        overwrite: Annotated[bool, Field(description="Allow overwriting destination.")] = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Move a file or directory to a new location.

        ## Return Format
        ```json
        {"success": bool, "from": str, "to": str}
        ```

        ## Examples
            move(path="D:\\\\old\\\\file.txt", destination="D:\\\\new\\\\file.txt")
        """
        try:
            src, dst = Path(path).resolve(), Path(destination).resolve()
            if dst.exists() and not overwrite:
                return fail_response("Destination exists and overwrite is False")
            await asyncio.to_thread(shutil.move, str(src), str(dst))
            return {"success": True, "from": str(src), "to": str(dst)}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def copy(
        path: Annotated[str, Field(description="Source file or directory path.")],
        destination: Annotated[str, Field(description="Destination path.")],
        overwrite: Annotated[bool, Field(description="Allow overwriting destination.")] = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Copy a file or directory tree to a new location.

        ## Return Format
        ```json
        {"success": bool, "from": str, "to": str}
        ```

        ## Examples
            copy(path="D:\\\\docs\\\\report.pdf", destination="D:\\\\backup\\\\report.pdf")
        """
        try:
            src, dst = Path(path).resolve(), Path(destination).resolve()
            if dst.exists() and not overwrite:
                return fail_response("Destination exists and overwrite is False")
            if src.is_dir():
                await asyncio.to_thread(shutil.copytree, str(src), str(dst), dirs_exist_ok=overwrite)
            else:
                await asyncio.to_thread(shutil.copy2, str(src), str(dst))
            return {"success": True, "from": str(src), "to": str(dst)}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def info(
        path: Annotated[str, Field(description="File or directory path.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Get metadata (name, size, created, modified, is_dir) for a path.

        ## Return Format
        ```json
        {"success": bool, "name": str, "size": int, "created": float, "modified": float, "is_dir": bool}
        ```

        ## Examples
            info(path="D:\\\\data\\\\report.pdf")
        """
        try:
            p = Path(path).resolve()
            if not p.exists():
                return fail_response(f"Path does not exist: {path}")
            st = p.stat()
            return {
                "success": True, "name": p.name, "path": str(p),
                "size": st.st_size, "created": st.st_ctime, "modified": st.st_mtime,
                "is_dir": p.is_dir(),
            }
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    parent_mcp.mount(ns, prefix="winops_file")
    logger.info("Mounted atomic tools: winops_file/read, /write, /edit, /delete, /move, /copy, /list, /info")
