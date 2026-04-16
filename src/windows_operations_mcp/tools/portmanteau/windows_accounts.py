"""
Windows Accounts Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides local user and group management for Windows system hardening.
"""

import asyncio
from typing import Any, Literal

from fastmcp import Context

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def windows_accounts(
    action: Literal[
        "list_users", "add_user", "remove_user", "set_password", "list_groups", "manage_group", "get_group_members"
    ],
    user: str | None = None,
    password: str | None = None,
    group: str | None = None,
    group_action: Literal["add", "remove"] = "add",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Perform Windows local account and group management with agentic telemetry.

    RATIONALE:
    Enables autonomous identity and access management (IAM) on local Windows systems.
    Uses 'net.exe' for industrial reliability and broad OS compatibility.

    Args:
        action: The account operation to perform.
        user: Target username.
        password: New password (for add_user or set_password).
        group: Target local group name.
        group_action: Action to perform on the group (target user is 'user').
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Accounts Op: {action} (User: {user}, Group: {group})")
        ctx.report_progress(10, 100)

    try:
        if action == "list_users":
            if ctx:
                ctx.report_progress(50, 100)
            users = await _run_net(["user"])
            return {"success": True, "action": action, "data": {"raw_users": users}}

        if action == "add_user":
            if not user or not password:
                return {"success": False, "error": "Username and password required for add_user"}
            if ctx:
                ctx.report_progress(50, 100)
            await _run_net(["user", user, password, "/add"])
            return {"success": True, "action": action, "data": {"status": f"User '{user}' added"}}

        if action == "remove_user":
            if not user:
                return {"success": False, "error": "Username required for remove_user"}
            if ctx:
                ctx.report_progress(50, 100)
            await _run_net(["user", user, "/delete"])
            return {"success": True, "action": action, "data": {"status": f"User '{user}' removed"}}

        if action == "set_password":
            if not user or not password:
                return {"success": False, "error": "Username and password required for set_password"}
            if ctx:
                ctx.report_progress(50, 100)
            await _run_net(["user", user, password])
            return {"success": True, "action": action, "data": {"status": f"Password for '{user}' updated"}}

        if action == "list_groups":
            if ctx:
                ctx.report_progress(50, 100)
            groups = await _run_net(["localgroup"])
            return {"success": True, "action": action, "data": {"raw_groups": groups}}

        if action == "manage_group":
            if not user or not group:
                return {"success": False, "error": "Username and group name required for manage_group"}
            if ctx:
                ctx.report_progress(50, 100)
            flag = f"/{group_action}"
            await _run_net(["localgroup", group, user, flag])
            return {
                "success": True,
                "action": action,
                "data": {"status": f"User '{user}' {group_action}ed to group '{group}'"},
            }

        if action == "get_group_members":
            if not group:
                return {"success": False, "error": "Group name required for get_group_members"}
            if ctx:
                ctx.report_progress(50, 100)

            output = await _run_net(["localgroup", group])

            # Parse members from net localgroup output
            # Format usually has "Members" header, then "---" separator, then names, then success message
            lines = output.splitlines()
            members = []
            parsing_members = False

            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                if line_stripped.startswith("---"):
                    parsing_members = True
                    continue
                if "The command completed successfully" in line_stripped:
                    break
                if parsing_members:
                    # Ignore lines that look like a footer or summary
                    if (
                        line_stripped
                        and not line_stripped.startswith("Alias name")
                        and not line_stripped.startswith("Comment")
                    ):
                        members.append(line_stripped)

            return {
                "success": True,
                "action": action,
                "data": {"group": group, "members": members, "raw_output": output},
            }

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"Accounts Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(
                    f"Windows local account operation '{action}' failed. Error: {e}. Suggest repair.", max_tokens=100
                )
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except Exception:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx:
            ctx.report_progress(100, 100)


async def _run_net(args: list[str]) -> str:
    """Run net.exe command asynchronously."""
    # Ensure all args are strings
    str_args = [str(a) for a in args]
    cmd = ["net.exe", *str_args]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(stderr.decode().strip() or stdout.decode().strip())
    return stdout.decode().strip()


def register_windows_accounts(mcp) -> None:
    """Register the modernized Windows accounts tool."""
    mcp.tool()(windows_accounts)
