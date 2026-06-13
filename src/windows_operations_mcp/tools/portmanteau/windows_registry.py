"""
Windows Registry - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_reg":
  winops_reg/read       - Read a registry value
  winops_reg/write      - Write a registry value (auto-backup in safe_mode)
  winops_reg/delete     - Delete a value or key (auto-backup in safe_mode)
  winops_reg/list_keys  - List subkeys and values at a path
  winops_reg/export     - Export a key to .reg file
  winops_reg/import_reg - Import a .reg file
"""

import asyncio
import winreg
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)

HIVES = {
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKU": winreg.HKEY_USERS,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
}

HiveKey = Literal["HKLM", "HKCU", "HKU", "HKCR"]


async def _reg(*args: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        "reg.exe", *args,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        err = stderr.decode(errors="replace").strip()
        if "export" in args and "unable to find" in err.lower():
            return "no_existing_key"
        raise RuntimeError(err or stdout.decode(errors="replace").strip())
    return args[2] if len(args) > 2 else "ok"


async def _auto_backup(hive: str, key_path: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("D:/Dev/repos/temp/reg_backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    safe = key_path.replace("\\", "_").replace("/", "_")[:80]
    out = backup_dir / f"{ts}_{hive}_{safe}.reg"
    await _reg("export", f"{hive}\\{key_path}", str(out), "/y")
    return str(out)


def _vtype_name(vtype: int) -> str:
    for name in dir(winreg):
        if name.startswith("REG_") and getattr(winreg, name) == vtype:
            return name
    return str(vtype)


def _read_value_blocking(hkey, path: str, name: str | None):
    with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
        return winreg.QueryValueEx(key, name)


def _write_value_blocking(hkey, path: str, name: str, data: Any, vtype: int) -> None:
    try:
        key = winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE)
    except FileNotFoundError:
        key = winreg.CreateKey(hkey, path)
    with key:
        winreg.SetValueEx(key, name, 0, vtype, data)


def _delete_blocking(hkey, path: str, name: str | None) -> None:
    if name:
        with winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    else:
        winreg.DeleteKey(hkey, path)


def _list_blocking(hkey, path: str) -> tuple[list, dict]:
    subkeys, values = [], {}
    with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
        i = 0
        while True:
            try:
                subkeys.append(winreg.EnumKey(key, i))
                i += 1
            except OSError:
                break
        i = 0
        while True:
            try:
                n, d, t = winreg.EnumValue(key, i)
                values[n] = {"data": d, "type": _vtype_name(t)}
                i += 1
            except OSError:
                break
    return subkeys, values


def register_windows_registry(parent_mcp: FastMCP) -> None:
    """Mount atomic registry tools under namespace 'winops_reg'."""
    ns = FastMCP(name="winops_reg")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def read(
        hive: Annotated[HiveKey, Field(description="Registry hive.")] = "HKCU",
        key_path: Annotated[str, Field(description="Path within the hive (e.g. Software\\\\MyApp).")] = "",
        value_name: Annotated[str | None, Field(description="Value name to read (None for default).")] = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Read a Windows Registry value.

        ## Return Format
        ```json
        {"success": bool, "value": any, "type": str}
        ```

        ## Examples
            read(hive="HKCU", key_path="Software\\\\MyApp", value_name="InstallDir")
        """
        try:
            hkey = HIVES[hive]
            data, vtype = await asyncio.to_thread(_read_value_blocking, hkey, key_path, value_name)
            return {"success": True, "value": data, "type": _vtype_name(vtype)}
        except FileNotFoundError:
            return fail_response(f"Key or value not found: {hive}\\{key_path}",
                                 suggestions=["Use winops_reg/list_keys to browse available keys."])
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def write(
        key_path: Annotated[str, Field(description="Path within the hive.")],
        value_name: Annotated[str, Field(description="Value name to write.")],
        value_data: Annotated[Any, Field(description="Data to write.")],
        hive: Annotated[HiveKey, Field(description="Registry hive.")] = "HKCU",
        value_type: Annotated[
            Literal["REG_SZ", "REG_DWORD", "REG_BINARY", "REG_EXPAND_SZ", "REG_MULTI_SZ"],
            Field(description="Registry value type."),
        ] = "REG_SZ",
        safe_mode: Annotated[bool, Field(description="Auto-export key backup before writing.")] = True,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Write a Windows Registry value, optionally backing up the key first.

        ## Return Format
        ```json
        {"success": bool, "backup_path": str}  // backup_path only in safe_mode
        ```

        ## Examples
            write(key_path="Software\\\\MyApp", value_name="Debug", value_data=1, value_type="REG_DWORD")
        """
        try:
            backup_path = None
            if safe_mode:
                backup_path = await _auto_backup(hive, key_path)
            hkey = HIVES[hive]
            vtype_const = getattr(winreg, value_type, winreg.REG_SZ)
            await asyncio.to_thread(_write_value_blocking, hkey, key_path, value_name, value_data, vtype_const)
            result: dict[str, Any] = {"success": True}
            if backup_path:
                result["backup_path"] = backup_path
            return result
        except Exception as e:
            return fail_response(str(e), suggestions=["HKLM writes require Administrator elevation."])

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False))
    async def delete(
        hive: Annotated[HiveKey, Field(description="Registry hive.")] = "HKCU",
        key_path: Annotated[str, Field(description="Path within the hive.")] = "",
        value_name: Annotated[str | None, Field(description="Value name to delete (None deletes the whole key).")] = None,
        safe_mode: Annotated[bool, Field(description="Auto-export key backup before deleting.")] = True,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Delete a registry value or key. Backs up first if safe_mode=True.

        ## Return Format
        ```json
        {"success": bool, "backup_path": str}
        ```

        ## Examples
            delete(hive="HKCU", key_path="Software\\\\OldApp", value_name="Token")
        """
        try:
            backup_path = None
            if safe_mode:
                backup_path = await _auto_backup(hive, key_path)
            hkey = HIVES[hive]
            await asyncio.to_thread(_delete_blocking, hkey, key_path, value_name)
            result: dict[str, Any] = {"success": True}
            if backup_path:
                result["backup_path"] = backup_path
            return result
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def list_keys(
        hive: Annotated[HiveKey, Field(description="Registry hive.")] = "HKCU",
        key_path: Annotated[str, Field(description="Path within the hive.")] = "",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """List subkeys and values at a registry path.

        ## Return Format
        ```json
        {"success": bool, "subkeys": [str], "values": {str: {"data": any, "type": str}}}
        ```

        ## Examples
            list_keys(hive="HKCU", key_path="Software")
        """
        try:
            hkey = HIVES[hive]
            subkeys, values = await asyncio.to_thread(_list_blocking, hkey, key_path)
            return {"success": True, "subkeys": subkeys, "values": values}
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def export(
        key_path: Annotated[str, Field(description="Key path to export.")],
        output_path: Annotated[str, Field(description="Destination .reg file path.")],
        hive: Annotated[HiveKey, Field(description="Registry hive.")] = "HKCU",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Export a registry key to a .reg file.

        ## Return Format
        ```json
        {"success": bool, "output_path": str}
        ```

        ## Examples
            export(hive="HKCU", key_path="Software\\\\MyApp", output_path="D:\\\\backup\\\\myapp.reg")
        """
        try:
            await _reg("export", f"{hive}\\{key_path}", output_path, "/y")
            return {"success": True, "output_path": output_path}
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def import_reg(
        reg_file_path: Annotated[str, Field(description="Path to the .reg file to import.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Import a .reg file into the Windows Registry.

        ## Return Format
        ```json
        {"success": bool, "reg_file_path": str}
        ```

        ## Examples
            import_reg(reg_file_path="D:\\\\backup\\\\myapp.reg")
        """
        try:
            await _reg("import", reg_file_path)
            return {"success": True, "reg_file_path": reg_file_path}
        except Exception as e:
            return fail_response(str(e))

    parent_mcp.mount(ns, prefix="winops_reg")
    logger.info("Mounted atomic tools: winops_reg/read, /write, /delete, /list_keys, /export, /import_reg")
