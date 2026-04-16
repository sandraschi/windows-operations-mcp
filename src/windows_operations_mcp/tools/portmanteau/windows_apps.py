"""
Windows Apps Portmanteau - SOTA v14.1 (FastMCP 3.2+)
Provides modern AppX and Windows Store package management.
"""

import asyncio
from typing import Any, Literal

from fastmcp import Context

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def windows_apps(
    action: Literal["list", "uninstall"],
    name_filter: str | None = None,
    package_name: str | None = None,
    all_users: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Manage modern Windows AppX and Store packages with PowerShell orchestration.

    RATIONALE:
    Modern Windows applications (AppX) cannot be managed via traditional 'net.exe'
    or basic registry surgery. This tool uses PowerShell to enable autonomous
    bloatware removal and package auditing.

    Args:
        action: The apps operation to perform.
        name_filter: Filter for listing (e.g. 'Xbox', 'Bing').
        package_name: Exact package name to uninstall.
        all_users: Perform action for all users (requires elevation).
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Apps Op: {action}")
        ctx.report_progress(10, 100)

    try:
        if action == "list":
            if ctx:
                ctx.report_progress(50, 100)
            ps_cmd = "Get-AppxPackage"
            if all_users:
                ps_cmd += " -AllUsers"
            if name_filter:
                ps_cmd += f" | Where-Object {{ $_.Name -like '*{name_filter}*' }}"
            ps_cmd += " | Select-Object Name, PackageFullName, Version, InstallLocation | ConvertTo-Json"

            output = await _run_ps(ps_cmd)
            return {"success": True, "action": action, "data": {"apps": output}}

        if action == "uninstall":
            if not package_name:
                return {"success": False, "error": "package_name required"}
            if ctx:
                ctx.warning(f"Uninstalling package: {package_name}...")
            ps_cmd = f"Remove-AppxPackage -Package '{package_name}'"
            if all_users:
                ps_cmd += " -AllUsers"
            await _run_ps(ps_cmd)
            return {"success": True, "action": action, "data": {"status": f"Package '{package_name}' uninstalled"}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"Apps Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(
                    f"Windows Apps operation '{action}' failed. Error: {e}. Suggest repair.", max_tokens=100
                )
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx:
            ctx.report_progress(100, 100)


async def _run_ps(command: str) -> Any:
    """Run a PowerShell command and return JSON output if possible."""
    cmd = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(stderr.decode().strip() or stdout.decode().strip())

    import json

    try:
        return json.loads(stdout.decode().strip())
    except:
        return stdout.decode().strip()


def register_windows_apps(mcp) -> None:
    """Register the modernized Windows apps tool."""
    mcp.tool()(windows_apps)
