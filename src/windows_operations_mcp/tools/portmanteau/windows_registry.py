"""
Windows Registry Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows Registry management with 'Safe Mode' auto-backups.
"""

import asyncio
import winreg
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

# Registry Hive Mapping
HIVES = {
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKU": winreg.HKEY_USERS,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
}

async def windows_registry(
    action: Literal["read", "write", "delete", "list_keys", "export", "import"],
    key_path: str,
    hive: Literal["HKLM", "HKCU", "HKU", "HKCR"] = "HKCU",
    value_name: Optional[str] = None,
    value_data: Optional[Any] = None,
    value_type: Literal["REG_SZ", "REG_DWORD", "REG_BINARY", "REG_EXPAND_SZ", "REG_MULTI_SZ"] = "REG_SZ",
    safe_mode: bool = True,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform Windows Registry operations with SOTA 'Safe Mode' auto-backups and telemetry.

    RATIONALE:
    Enables autonomous system configuration and hardening.
    'Safe Mode' ensures that keys are exported to a backup file before potentially destructive edits.

    Args:
        action: The registry operation to perform.
        key_path: Path within the hive (e.g., 'Software\\Microsoft\\Windows').
        hive: Registry hive to operate on.
        value_name: Name of the entry within the key.
        value_data: Data to write (for "write").
        value_type: Registry value type.
        safe_mode: If True, auto-exports the key before write/delete actions.
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Registry Op: {action} on {hive}\\{key_path}")
        ctx.report_progress(10, 100)

    try:
        hkey = HIVES.get(hive)
        if hkey is None:
            return {"success": False, "error": f"Invalid hive: {hive}"}

        # Safe Mode Trigger
        if safe_mode and action in ["write", "delete"]:
            if ctx:
                ctx.report_progress(20, 100)
            backup_path = await _auto_backup(hive, key_path, ctx)
            if ctx:
                ctx.info(f"Safe Mode: Created backup at {backup_path}")

        if action == "read":
            data, vtype = await asyncio.to_thread(_read_value, hkey, key_path, value_name)
            return {"success": True, "action": action, "data": {"value": data, "type": _vtype_name(vtype)}}

        if action == "write":
            vtype_const = getattr(winreg, value_type, winreg.REG_SZ)
            await asyncio.to_thread(_write_value, hkey, key_path, value_name, value_data, vtype_const)
            return {"success": True, "action": action, "data": {"status": "Written"}}

        if action == "delete":
            await asyncio.to_thread(_delete_registry, hkey, key_path, value_name)
            return {"success": True, "action": action, "data": {"status": "Deleted"}}

        if action == "list_keys":
            subkeys, values = await asyncio.to_thread(_list_registry, hkey, key_path)
            return {"success": True, "action": action, "data": {"subkeys": subkeys, "values": values}}

        if action == "export":
            path = await _run_reg(["export", f"{hive}\\{key_path}", value_data or "backup.reg"]) # value_data as path
            return {"success": True, "action": action, "data": {"export_path": path}}

        if action == "import":
            await _run_reg(["import", key_path]) # key_path as file path for import
            return {"success": True, "action": action, "data": {"status": "Imported"}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"Registry Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(f"Windows Registry operation '{action}' failed on '{hive}\\{key_path}'. Error: {e}. Suggest repair.", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except Exception:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

async def _auto_backup(hive: str, key_path: str, ctx: Optional[Context]) -> str:
    """Perform auto-backup of a registry key before modification."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path.cwd() / "backups" / "registry"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    sanitized_name = key_path.replace("\\", "_").replace("/", "_")[:128]
    backup_file = backup_dir / f"{timestamp}_{hive}_{sanitized_name}.reg"
    
    await _run_reg(["export", f"{hive}\\{key_path}", str(backup_file), "/y"])
    return str(backup_file)

async def _run_reg(args: List[str]) -> str:
    """Run reg.exe command asynchronously."""
    cmd = ["reg.exe"] + args
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        # Note: Exporting nested subkeys that don't exist yet might fail, which is okay for write ops.
        if "export" in args and "The system was unable to find the specified registry key" in stderr.decode():
            return "No existing key to backup"
        raise Exception(stderr.decode().strip() or stdout.decode().strip())
    return args[2] if len(args) > 2 else "Success"

def _read_value(hive_key, path, name):
    with winreg.OpenKey(hive_key, path, 0, winreg.KEY_READ) as key:
        return winreg.QueryValueEx(key, name)

def _write_value(hive_key, path, name, data, vtype):
    # Try to open, create if doesn't exist
    try:
        key = winreg.OpenKey(hive_key, path, 0, winreg.KEY_SET_VALUE)
    except FileNotFoundError:
        key = winreg.CreateKey(hive_key, path)
    
    with key:
        winreg.SetValueEx(key, name, 0, vtype, data)

def _delete_registry(hive_key, path, name=None):
    if name:
        with winreg.OpenKey(hive_key, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    else:
        winreg.DeleteKey(hive_key, path)

def _list_registry(hive_key, path):
    subkeys = []
    values = {}
    with winreg.OpenKey(hive_key, path, 0, winreg.KEY_READ) as key:
        # Enumerate subkeys
        try:
            i = 0
            while True:
                subkeys.append(winreg.EnumKey(key, i))
                i += 1
        except OSError:
            pass
        
        # Enumerate values
        try:
            i = 0
            while True:
                name, data, vtype = winreg.EnumValue(key, i)
                values[name] = {"data": data, "type": _vtype_name(vtype)}
                i += 1
        except OSError:
            pass
    return subkeys, values

def _vtype_name(vtype: int) -> str:
    for name in dir(winreg):
        if name.startswith("REG_") and getattr(winreg, name) == vtype:
            return name
    return str(vtype)

def register_windows_registry(mcp) -> None:
    """Register the modernized Windows registry tool."""
    mcp.tool()(windows_registry)
