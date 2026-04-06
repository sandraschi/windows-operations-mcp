"""
Windows Permissions Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows ACL/Permission management with agentic telemetry.
"""

import asyncio
import subprocess
from typing import Any, Dict, List, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def windows_permissions(
    action: Literal["get", "grant", "revoke", "inheritance"],
    path: str,
    user: Optional[str] = None,
    permission: Optional[Literal["F", "M", "RX", "R", "W"]] = "R",
    enable_inheritance: bool = True,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform Windows Permission (ACL) operations with comprehensive error handling and agentic telemetry.

    RATIONALE:
    Consolidates ACL viewing, granting, revoking, and inheritance management into a single portmanteau.
    Uses 'icacls.exe' for industrial reliability on Windows.

    Args:
        action: The permission operation to perform.
        path: Target file or directory path.
        user: Target user or group (required for grant/revoke).
        permission: Permission level (F=Full, M=Modify, RX=Read/Exec, R=Read, W=Write).
        enable_inheritance: Whether to enable or disable inheritance (for "inheritance").
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Permissions Op: {action} on {path}")
        ctx.report_progress(10, 100)

    try:
        if action == "get":
            if ctx: ctx.report_progress(50, 100)
            result = await _run_icacls([path])
            return {"success": True, "action": action, "data": {"raw_acl": result}}

        if action == "grant":
            if not user: return {"success": False, "error": "User required for grant"}
            if ctx: ctx.report_progress(50, 100)
            await _run_icacls([path, "/grant", f"{user}:{permission}"])
            return {"success": True, "action": action, "data": {"granted": f"{user}:{permission}"}}

        if action == "revoke":
            if not user: return {"success": False, "error": "User required for revoke"}
            if ctx: ctx.report_progress(50, 100)
            await _run_icacls([path, "/remove", user])
            return {"success": True, "action": action, "data": {"revoked": user}}

        if action == "inheritance":
            flag = "/inheritance:e" if enable_inheritance else "/inheritance:d"
            if ctx: ctx.report_progress(50, 100)
            await _run_icacls([path, flag])
            return {"success": True, "action": action, "data": {"inheritance_enabled": enable_inheritance}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"Permissions Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(f"Windows Permissions operation '{action}' failed on '{path}'. Error: {e}. Suggest fix.", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except: pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

async def _run_icacls(args: List[str]) -> str:
    """Run icacls command asynchronously."""
    cmd = ["icacls.exe"] + args
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(stderr.decode().strip() or stdout.decode().strip())
    return stdout.decode().strip()

def register_windows_permissions(mcp) -> None:
    """Register the modernized Windows permissions tool."""
    mcp.tool()(windows_permissions)
