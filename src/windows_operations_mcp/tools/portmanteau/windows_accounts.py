"""
Windows Accounts - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_accounts":
  winops_accounts/list_users       - List local users
  winops_accounts/add_user         - Create a local user
  winops_accounts/remove_user      - Delete a local user
  winops_accounts/set_password     - Change a user's password
  winops_accounts/list_groups      - List local groups
  winops_accounts/group_members    - List members of a group
  winops_accounts/manage_group     - Add or remove a user from a group
"""

import asyncio
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def _net(args: list[str]) -> str:
    proc = await asyncio.create_subprocess_exec(
        "net.exe", *[str(a) for a in args],
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode(errors="replace").strip() or stdout.decode(errors="replace").strip())
    return stdout.decode(errors="replace").strip()


def register_windows_accounts(parent_mcp: FastMCP) -> None:
    """Mount atomic account management tools under namespace 'winops_accounts'."""
    ns = FastMCP(name="winops_accounts")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def list_users(ctx: Context | None = None) -> dict[str, Any]:
        """List local Windows user accounts.

        ## Return Format
        ```json
        {"success": bool, "raw_output": str}
        ```

        ## Examples
            list_users()
        """
        try:
            return {"success": True, "raw_output": await _net(["user"])}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def add_user(
        username: Annotated[str, Field(description="New user account name.")],
        password: Annotated[str, Field(description="Initial password.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Create a new local Windows user account.

        ## Return Format
        ```json
        {"success": bool, "username": str}
        ```

        ## Examples
            add_user(username="jsmith", password="P@ssw0rd!")
        """
        try:
            await _net(["user", username, password, "/add"])
            return {"success": True, "username": username}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Run as Administrator. Verify username does not already exist."]}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False))
    async def remove_user(
        username: Annotated[str, Field(description="User account name to delete.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Delete a local Windows user account.

        ## Return Format
        ```json
        {"success": bool, "username": str}
        ```

        ## Examples
            remove_user(username="jsmith")
        """
        try:
            await _net(["user", username, "/delete"])
            return {"success": True, "username": username}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Run as Administrator. Verify the user exists with list_users."]}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def set_password(
        username: Annotated[str, Field(description="Target user account.")],
        password: Annotated[str, Field(description="New password.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Set the password for a local Windows user account.

        ## Return Format
        ```json
        {"success": bool, "username": str}
        ```

        ## Examples
            set_password(username="jsmith", password="NewP@ss!")
        """
        try:
            await _net(["user", username, password])
            return {"success": True, "username": username}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def list_groups(ctx: Context | None = None) -> dict[str, Any]:
        """List local Windows groups.

        ## Return Format
        ```json
        {"success": bool, "raw_output": str}
        ```

        ## Examples
            list_groups()
        """
        try:
            return {"success": True, "raw_output": await _net(["localgroup"])}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def group_members(
        group: Annotated[str, Field(description="Local group name.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """List members of a local Windows group.

        ## Return Format
        ```json
        {"success": bool, "group": str, "members": [str]}
        ```

        ## Examples
            group_members(group="Administrators")
        """
        try:
            output = await _net(["localgroup", group])
            members = []
            parsing = False
            for line in output.splitlines():
                s = line.strip()
                if not s:
                    continue
                if s.startswith("---"):
                    parsing = True
                    continue
                if "The command completed successfully" in s:
                    break
                if parsing and s and not s.startswith(("Alias name", "Comment")):
                    members.append(s)
            return {"success": True, "group": group, "members": members}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Verify group name with list_groups."]}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def manage_group(
        group: Annotated[str, Field(description="Local group name.")],
        username: Annotated[str, Field(description="User to add or remove.")],
        action: Annotated[Literal["add", "remove"], Field(description="add or remove.")] = "add",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Add or remove a user from a local Windows group.

        ## Return Format
        ```json
        {"success": bool, "group": str, "username": str, "action": str}
        ```

        ## Examples
            manage_group(group="Administrators", username="jsmith", action="add")
            manage_group(group="Administrators", username="jsmith", action="remove")
        """
        try:
            await _net(["localgroup", group, username, f"/{action}"])
            return {"success": True, "group": group, "username": username, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "suggestions": ["Run as Administrator. Verify both user and group exist."]}

    parent_mcp.mount(ns, prefix="winops_accounts")
    logger.info("Mounted atomic tools: winops_accounts/list_users, /add_user, /remove_user, /set_password, /list_groups, /group_members, /manage_group")
