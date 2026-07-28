"""
Windows Environment - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_env":
  winops_env/list   - List all environment variables for a scope
  winops_env/get    - Get a single variable
  winops_env/set    - Set a variable (persists to registry + broadcasts)
  winops_env/delete - Delete a variable
"""

import asyncio
import ctypes
import winreg
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)

HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x001A
SMTO_ABORTIFHUNG = 0x0002


def _get_key(scope: str, write: bool = False):
    if scope == "system":
        root = winreg.HKEY_LOCAL_MACHINE
        path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    else:
        root = winreg.HKEY_CURRENT_USER
        path = r"Environment"
    access = winreg.KEY_READ | (winreg.KEY_WRITE if write else 0)
    return winreg.OpenKey(root, path, 0, access)


def _list_env_blocking(scope: str) -> dict[str, Any]:
    with _get_key(scope) as key:
        variables = {}
        idx = 0
        while True:
            try:
                name, val, _ = winreg.EnumValue(key, idx)
                variables[name] = val
                idx += 1
            except OSError:
                break
        return {"success": True, "variables": variables, "count": len(variables)}


def _get_env_blocking(scope: str, name: str) -> str:
    with _get_key(scope) as key:
        val, _ = winreg.QueryValueEx(key, name)
        return val


def _set_env_blocking(scope: str, name: str, value: str) -> None:
    with _get_key(scope, write=True) as key:
        reg_type = winreg.REG_EXPAND_SZ if "%" in value else winreg.REG_SZ
        winreg.SetValueEx(key, name, 0, reg_type, value)


def _delete_env_blocking(scope: str, name: str) -> None:
    with _get_key(scope, write=True) as key:
        winreg.DeleteValue(key, name)


def _broadcast_change() -> None:
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST,
        WM_SETTINGCHANGE,
        0,
        "Environment",
        SMTO_ABORTIFHUNG,
        5000,
        ctypes.byref(ctypes.c_size_t()),
    )


def register_windows_environment(parent_mcp: FastMCP) -> None:
    """Mount atomic environment variable tools under namespace 'winops_env'."""
    ns = FastMCP(name="winops_env")

    @ns.tool(
        name="list",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    )
    async def list_env(
        scope: Annotated[Literal["user", "system"], Field(description="Registry scope.")] = "user",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """List all persistent Windows environment variables for user or system scope.

        ## Return Format
        ```json
        {"success": true, "variables": {str: str}, "count": int}
        ```

        ## Examples
            list(scope="user")
            list(scope="system")
        """
        try:
            return await asyncio.to_thread(_list_env_blocking, scope)
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def get(
        name: Annotated[str, Field(description="Variable name.")],
        scope: Annotated[Literal["user", "system"], Field(description="Registry scope.")] = "user",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Get the value of a persistent Windows environment variable.

        ## Return Format
        ```json
        {"success": bool, "name": str, "value": str}
        ```

        ## Examples
            get(name="PATH")
            get(name="JAVA_HOME", scope="system")
        """
        try:
            val = await asyncio.to_thread(_get_env_blocking, scope, name)
            return {"success": True, "name": name, "value": val}
        except FileNotFoundError:
            return fail_response(
                f"Variable '{name}' not found in {scope} scope",
                suggestions=["Use winops_env/list to see available variables."],
            )
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def set(
        name: Annotated[str, Field(description="Variable name.")],
        value: Annotated[str, Field(description="Value to persist.")],
        scope: Annotated[Literal["user", "system"], Field(description="Registry scope.")] = "user",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Set a persistent Windows environment variable via registry and broadcast the change.

        ## Return Format
        ```json
        {"success": bool, "name": str, "value": str, "scope": str}
        ```

        ## Examples
            set(name="MY_VAR", value="hello")
            set(name="JAVA_HOME", value="C:\\\\Java\\\\jdk21", scope="system")

        Notes:
         - Uses REG_EXPAND_SZ when value contains %; REG_SZ otherwise.
         - Broadcasts WM_SETTINGCHANGE so running applications see the change.
        """
        try:
            await asyncio.to_thread(_set_env_blocking, scope, name, value)
            await asyncio.to_thread(_broadcast_change)
            return {"success": True, "name": name, "value": value, "scope": scope}
        except Exception as e:
            return fail_response(str(e), suggestions=["System scope requires Administrator elevation."])

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False)
    )
    async def delete(
        name: Annotated[str, Field(description="Variable name to delete.")],
        scope: Annotated[Literal["user", "system"], Field(description="Registry scope.")] = "user",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Delete a persistent Windows environment variable.

        ## Return Format
        ```json
        {"success": bool, "name": str, "deleted": true}
        ```

        ## Examples
            delete(name="OLD_VAR")
        """
        try:
            await asyncio.to_thread(_delete_env_blocking, scope, name)
            await asyncio.to_thread(_broadcast_change)
            return {"success": True, "name": name, "deleted": True}
        except FileNotFoundError:
            return fail_response(
                f"Variable '{name}' not found", suggestions=["Use winops_env/list to verify the variable exists."]
            )
        except Exception as e:
            return fail_response(str(e))

    parent_mcp.mount(ns, prefix="winops_env")
    logger.info("Mounted atomic tools: winops_env/list, /get, /set, /delete")
