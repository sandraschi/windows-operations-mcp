"""
Windows Permissions - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_acl":
  winops_acl/get         - View ACL for a path
  winops_acl/grant       - Grant permissions to a user/group
  winops_acl/revoke      - Revoke permissions from a user/group
  winops_acl/inheritance - Enable or disable ACL inheritance
"""

import asyncio
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)


async def _icacls(*args: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        "icacls.exe",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode(errors="replace").strip())
    return stdout.decode(errors="replace").strip()


def register_windows_permissions(parent_mcp: FastMCP) -> None:
    """Mount atomic ACL tools under namespace 'winops_acl'."""
    ns = FastMCP(name="winops_acl")

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def get(
        path: Annotated[str, Field(description="File or directory path to inspect.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """View the ACL (Access Control List) for a file or directory.

        ## Return Format
        ```json
        {"success": bool, "path": str, "raw_acl": str}
        ```

        ## Examples
            get(path="C:\\\\Users\\\\Public")
        """
        try:
            return {"success": True, "path": path, "raw_acl": await _icacls(path)}
        except Exception as e:
            return fail_response(f"Operation failed: {e}", suggestions=["Verify path exists and is accessible."])

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def grant(
        path: Annotated[str, Field(description="File or directory path.")],
        user: Annotated[str, Field(description="Username or group to grant permission to.")],
        permission: Annotated[
            Literal["F", "M", "RX", "R", "W"],
            Field(description="F=Full, M=Modify, RX=Read+Execute, R=Read, W=Write."),
        ] = "R",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Grant a permission level to a user or group on a file or directory.

        ## Return Format
        ```json
        {"success": bool, "path": str, "user": str, "permission": str}
        ```

        ## Examples
            grant(path="D:\\\\data", user="jsmith", permission="M")
        """
        try:
            await _icacls(path, "/grant", f"{user}:{permission}")
            return {"success": True, "path": path, "user": user, "permission": permission}
        except Exception as e:
            return fail_response(f"Operation failed: {e}", suggestions=["Run as Administrator for system paths."])

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False)
    )
    async def revoke(
        path: Annotated[str, Field(description="File or directory path.")],
        user: Annotated[str, Field(description="Username or group to revoke.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Revoke all explicit permissions for a user or group on a file or directory.

        ## Return Format
        ```json
        {"success": bool, "path": str, "user": str}
        ```

        ## Examples
            revoke(path="D:\\\\data", user="jsmith")
        """
        try:
            await _icacls(path, "/remove", user)
            return {"success": True, "path": path, "user": user}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def inheritance(
        path: Annotated[str, Field(description="File or directory path.")],
        enable: Annotated[bool, Field(description="True to enable inheritance, False to disable.")] = True,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Enable or disable ACL inheritance on a file or directory.

        ## Return Format
        ```json
        {"success": bool, "path": str, "inheritance_enabled": bool}
        ```

        ## Examples
            inheritance(path="D:\\\\secure", enable=False)
        """
        try:
            flag = "/inheritance:e" if enable else "/inheritance:d"
            await _icacls(path, flag)
            return {"success": True, "path": path, "inheritance_enabled": enable}
        except Exception as e:
            return fail_response(f"Operation failed: {e}")

    parent_mcp.mount(ns, prefix="winops_acl")
    logger.info("Mounted atomic tools: winops_acl/get, /grant, /revoke, /inheritance")
