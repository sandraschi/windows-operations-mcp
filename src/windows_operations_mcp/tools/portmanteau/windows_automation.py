"""
Windows Automation Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides Scheduled Task management and deep WMI system introspection for Windows.
"""

import asyncio
from typing import Any, Literal

from fastmcp import Context

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def windows_automation(
    action: Literal["list_tasks", "create_task", "delete_task", "run_task", "wmi_query"],
    task_name: str | None = None,
    task_path: str | None = None,
    schedule: Literal[
        "MINUTE", "HOURLY", "DAILY", "WEEKLY", "MONTHLY", "ONCE", "ONLOGON", "ONIDLE", "ONEVENT"
    ] = "DAILY",
    start_time: str | None = "12:00",
    wmi_class: str | None = "Win32_OperatingSystem",
    wmi_namespace: str | None = "root\\cimv2",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Perform Windows Automation operations: Scheduled Tasks and WMI Queries.

    RATIONALE:
    Enables autonomous system orchestration and deep environment forensics.
    Uses 'schtasks.exe' and 'wmic.exe' for industrial reliability.

    Args:
        action: The automation operation to perform.
        task_name: Unique name for the scheduled task.
        task_path: Executable path for the scheduled task (for "create_task").
        schedule: Task frequency.
        start_time: Task start time (format HH:mm).
        wmi_class: Target WMI class (e.g., 'Win32_Processor', 'Win32_BIOS').
        wmi_namespace: WMI namespace for the query.
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Automation Op: {action}")
        ctx.report_progress(10, 100)

    try:
        if action == "list_tasks":
            if ctx:
                ctx.report_progress(50, 100)
            tasks = await _run_cmd(["schtasks.exe", "/query", "/fo", "LIST"])
            return {"success": True, "action": action, "data": {"raw_tasks": tasks}}

        if action == "create_task":
            if not task_name or not task_path:
                return {"success": False, "error": "Task name and path required for create_task"}
            if ctx:
                ctx.report_progress(50, 100)
            await _run_cmd(
                [
                    "schtasks.exe",
                    "/create",
                    "/tn",
                    task_name,
                    "/tr",
                    f'"{task_path}"',
                    "/sc",
                    schedule,
                    "/st",
                    start_time,
                    "/f",
                ]
            )
            return {"success": True, "action": action, "data": {"status": f"Task '{task_name}' created."}}

        if action == "delete_task":
            if not task_name:
                return {"success": False, "error": "Task name required for delete_task"}
            if ctx:
                ctx.report_progress(50, 100)
            await _run_cmd(["schtasks.exe", "/delete", "/tn", task_name, "/f"])
            return {"success": True, "action": action, "data": {"status": f"Task '{task_name}' deleted."}}

        if action == "run_task":
            if not task_name:
                return {"success": False, "error": "Task name required for run_task"}
            if ctx:
                ctx.report_progress(50, 100)
            await _run_cmd(["schtasks.exe", "/run", "/tn", task_name])
            return {"success": True, "action": action, "data": {"status": f"Task '{task_name}' triggered."}}

        if action == "wmi_query":
            if not wmi_class:
                return {"success": False, "error": "WMI class required for wmi_query"}
            if ctx:
                ctx.report_progress(50, 100)
            # Using wmic.exe for broad compatibility, but PowerShell Get-CimInstance is more modern.
            # We'll stick to native wmic for SOTA v14.0 industrial reliability.
            result = await _run_cmd(
                ["wmic.exe", f"/namespace:{wmi_namespace}", "path", wmi_class, "get", "/format:list"]
            )
            return {"success": True, "action": action, "data": {"wmi_result": result}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"Automation Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(
                    f"Windows Automation operation '{action}' failed. Error: {e}. Suggest fix.", max_tokens=100
                )
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx:
            ctx.report_progress(100, 100)


async def _run_cmd(cmd: list[str]) -> str:
    """Run a system command asynchronously."""
    # Ensure command string parts are properly handled
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(stderr.decode().strip() or stdout.decode().strip())
    return stdout.decode().strip()


def register_windows_automation(mcp) -> None:
    """Register the modernized Windows automation tool."""
    mcp.tool()(windows_automation)
