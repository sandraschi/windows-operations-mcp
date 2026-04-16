"""
Windows Environment Portmanteau - SOTA v14.1 (FastMCP 3.2+)
Provides persistent environment variable management with system-wide broadcasting.
"""

import asyncio
import ctypes
import winreg
from typing import Any, Literal

from fastmcp import Context

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

# Constants for broadcasting change
HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x001A
SMTO_ABORTIFHUNG = 0x0002


async def windows_environment(
    action: Literal["get", "set", "delete", "list"],
    name: str | None = None,
    value: str | None = None,
    scope: Literal["user", "system"] = "user",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Manage persistent Windows environment variables with system-wide broadcasting.

    RATIONALE:
    Standard 'set' or 'export' commands are session-only. This tool performs
    registry surgery to ensure variables persist across reboots and broadcasts
    a notification to other applications to update their environment.

    Args:
        action: The environment operation to perform.
        name: Name of the variable.
        value: Value to set (for "set").
        scope: Target scope (user or system).
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Env Op: {action} ({scope})")
        ctx.report_progress(10, 100)

    try:
        if action == "list":
            return await asyncio.to_thread(_list_env, scope)

        if action == "get":
            if not name:
                return {"success": False, "error": "name required"}
            val = await asyncio.to_thread(_get_env, scope, name)
            return {"success": True, "action": action, "data": {"name": name, "value": val}}

        if action == "set":
            if not name or value is None:
                return {"success": False, "error": "name and value required"}
            await asyncio.to_thread(_set_env, scope, name, value)
            if ctx:
                ctx.info("Broadcasting system-wide environment change...")
            await asyncio.to_thread(_broadcast_change)
            return {"success": True, "action": action, "data": {"name": name, "value": value}}

        if action == "delete":
            if not name:
                return {"success": False, "error": "name required"}
            await asyncio.to_thread(_delete_env, scope, name)
            await asyncio.to_thread(_broadcast_change)
            return {"success": True, "action": action, "data": {"name": name, "deleted": True}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"Environment Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(
                    f"Windows Environment operation '{action}' failed. Error: {e}. Suggest repair.", max_tokens=100
                )
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx:
            ctx.report_progress(100, 100)


def _get_key(scope, write=False):
    if scope == "system":
        key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        root = winreg.HKEY_LOCAL_MACHINE
    else:
        key_path = r"Environment"
        root = winreg.HKEY_CURRENT_USER

    access = winreg.KEY_READ
    if write:
        access |= winreg.KEY_WRITE
    return winreg.OpenKey(root, key_path, 0, access)


def _list_env(scope):
    with _get_key(scope) as key:
        vars = {}
        idx = 0
        while True:
            try:
                name, val, _ = winreg.EnumValue(key, idx)
                vars[name] = val
                idx += 1
            except OSError:
                break
        return {"success": True, "action": "list", "data": {"variables": vars, "count": len(vars)}}


def _get_env(scope, name):
    with _get_key(scope) as key:
        val, _ = winreg.QueryValueEx(key, name)
        return val


def _set_env(scope, name, value):
    with _get_key(scope, write=True) as key:
        # Use REG_EXPAND_SZ for Path-like variables, REG_SZ for others
        # Heuristic: if '%' in value, use expand
        type = winreg.REG_EXPAND_SZ if "%" in value else winreg.REG_SZ
        winreg.SetValueEx(key, name, 0, type, value)


def _delete_env(scope, name):
    with _get_key(scope, write=True) as key:
        winreg.DeleteValue(key, name)


def _broadcast_change():
    """Notify all windows that environment variables have changed."""
    # SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, u"Environment", SMTO_ABORTIFHUNG, 5000, pdwResult)
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(ctypes.c_size_t())
    )


def register_windows_environment(mcp) -> None:
    """Register the modernized Windows environment tool."""
    mcp.tool()(windows_environment)
