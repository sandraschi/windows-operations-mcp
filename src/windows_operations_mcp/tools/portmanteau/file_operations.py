"""
File Operations - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_file":
  winops_file/read   - Read text content of a file
  winops_file/write  - Write text content to a file
  winops_file/delete - Delete a file or directory tree
  winops_file/move   - Move a file or directory
  winops_file/copy   - Copy a file or directory tree
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
                return {"success": False, "error": f"Not a file: {path}",
                        "suggestions": ["Verify the path exists and is a file, not a directory."]}
            content = await asyncio.to_thread(p.read_text, encoding)
            return {"success": True, "content": content, "size": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def write(
        path: Annotated[str, Field(description="Destination file path.")],
        content: Annotated[str, Field(description="Text content to write.")],
        overwrite: Annotated[bool, Field(description="Allow overwriting existing file.")] = False,
        create_dirs: Annotated[bool, Field(description="Create parent directories if missing.")] = True,
        encoding: Annotated[str, Field(description="Text encoding.")] = "utf-8",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Write text content to a file.

        ## Return Format
        ```json
        {"success": bool, "path": str, "bytes": int}
        ```

        ## Examples
            write(path="D:\\\\logs\\\\output.txt", content="hello", create_dirs=True)
        """
        try:
            p = Path(path).resolve()
            if p.exists() and not overwrite:
                return {"success": False, "error": "File exists and overwrite is False",
                        "suggestions": ["Pass overwrite=True to replace the existing file."]}
            if create_dirs:
                p.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(p.write_text, content, encoding)
            return {"success": True, "path": str(p), "bytes": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
                return {"success": False, "error": f"Path does not exist: {path}"}
            if p.is_file():
                await asyncio.to_thread(p.unlink)
            else:
                await asyncio.to_thread(shutil.rmtree, str(p))
            return {"success": True, "deleted": str(p)}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
                return {"success": False, "error": "Destination exists and overwrite is False"}
            await asyncio.to_thread(shutil.move, str(src), str(dst))
            return {"success": True, "from": str(src), "to": str(dst)}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
                return {"success": False, "error": "Destination exists and overwrite is False"}
            if src.is_dir():
                await asyncio.to_thread(shutil.copytree, str(src), str(dst), dirs_exist_ok=overwrite)
            else:
                await asyncio.to_thread(shutil.copy2, str(src), str(dst))
            return {"success": True, "from": str(src), "to": str(dst)}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
                return {"success": False, "error": f"Path does not exist: {path}"}
            st = p.stat()
            return {
                "success": True, "name": p.name, "path": str(p),
                "size": st.st_size, "created": st.st_ctime, "modified": st.st_mtime,
                "is_dir": p.is_dir(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    parent_mcp.mount(ns, prefix="winops_file")
    logger.info("Mounted atomic tools: winops_file/read, /write, /delete, /move, /copy, /info")
