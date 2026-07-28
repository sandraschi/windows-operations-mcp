"""
Windows Apps - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_apps":
  winops_apps/list      - List AppX packages
  winops_apps/uninstall - Uninstall an AppX package
"""

import asyncio
import json
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)


async def _ps(command: str) -> Any:
    proc = await asyncio.create_subprocess_exec(
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode(errors="replace").strip())
    text = stdout.decode(errors="replace").strip()
    try:
        return json.loads(text)
    except Exception:
        return text


def register_windows_apps(parent_mcp: FastMCP) -> None:
    """Mount atomic AppX package tools under namespace 'winops_apps'."""
    ns = FastMCP(name="winops_apps")

    @ns.tool(
        name="list",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    )
    async def list_apps(
        name_filter: Annotated[str | None, Field(description="Substring filter on package name (e.g. 'Xbox').")] = None,
        all_users: Annotated[bool, Field(description="Include packages for all users (requires elevation).")] = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """List installed AppX/Windows Store packages.

        ## Return Format
        ```json
        {"success": bool, "apps": [...]}
        ```

        ## Examples
            list(name_filter="Xbox")
            list(all_users=True)
        """
        try:
            cmd = "Get-AppxPackage"
            if all_users:
                cmd += " -AllUsers"
            if name_filter:
                cmd += f" | Where-Object {{ $_.Name -like '*{name_filter}*' }}"
            cmd += " | Select-Object Name, PackageFullName, Version, InstallLocation | ConvertTo-Json"
            apps = await _ps(cmd)
            return {"success": True, "apps": apps}
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False)
    )
    async def uninstall(
        package_name: Annotated[str, Field(description="PackageFullName of the app to remove.")],
        all_users: Annotated[bool, Field(description="Remove for all users (requires elevation).")] = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Uninstall an AppX/Windows Store package by its PackageFullName.

        ## Return Format
        ```json
        {"success": bool, "package_name": str}
        ```

        ## Examples
            uninstall(package_name="Microsoft.XboxApp_48.49.31001.0_x64__8wekyb3d8bbwe")

        Notes:
         - Get PackageFullName from winops_apps/list.
         - Requires elevation for system/all-user packages.
        """
        try:
            cmd = f"Remove-AppxPackage -Package '{package_name}'"
            if all_users:
                cmd += " -AllUsers"
            await _ps(cmd)
            return {"success": True, "package_name": package_name}
        except Exception as e:
            return fail_response(
                str(e),
                suggestions=["Run as Administrator for system packages.", "Get PackageFullName from winops_apps/list."],
            )

    parent_mcp.mount(ns, prefix="winops_apps")
    logger.info("Mounted atomic tools: winops_apps/list, winops_apps/uninstall")
