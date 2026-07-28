"""
Windows Automation - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_auto":
  winops_auto/task_list    - List scheduled tasks
  winops_auto/task_create  - Create a scheduled task
  winops_auto/task_delete  - Delete a scheduled task
  winops_auto/task_run     - Trigger a scheduled task immediately
  winops_auto/wmi_query    - Query a WMI class
"""

import asyncio
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)


async def _run(cmd: list[str]) -> str:
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode(errors="replace").strip() or stdout.decode(errors="replace").strip())
    return stdout.decode(errors="replace").strip()


def register_windows_automation(parent_mcp: FastMCP) -> None:
    """Mount atomic automation tools under namespace 'winops_auto'."""
    ns = FastMCP(name="winops_auto")

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def task_list(ctx: Context | None = None) -> dict[str, Any]:
        """List all Windows Scheduled Tasks.

        ## Return Format
        ```json
        {"success": bool, "raw_tasks": str}
        ```

        ## Examples
            task_list()
        """
        try:
            return {"success": True, "raw_tasks": await _run(["schtasks.exe", "/query", "/fo", "LIST"])}
        except Exception as e:
            return fail_response(f"Scheduled task listing failed: {e}")

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def task_create(
        task_name: Annotated[str, Field(description="Unique task name.")],
        task_path: Annotated[str, Field(description="Full path to the executable.")],
        schedule: Annotated[
            Literal["MINUTE", "HOURLY", "DAILY", "WEEKLY", "MONTHLY", "ONCE", "ONLOGON", "ONIDLE", "ONEVENT"],
            Field(description="Task recurrence schedule."),
        ] = "DAILY",
        start_time: Annotated[str, Field(description="Start time in HH:mm format.")] = "12:00",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Create a Windows Scheduled Task.

        ## Return Format
        ```json
        {"success": bool, "task_name": str}
        ```

        ## Examples
            task_create(task_name="DailyBackup", task_path="C:\\\\scripts\\\\backup.bat", schedule="DAILY")
        """
        try:
            await _run(
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
            return {"success": True, "task_name": task_name}
        except Exception as e:
            return fail_response(
                f"Task creation failed: {e}", suggestions=["Run as Administrator. Verify task_path exists."]
            )

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False)
    )
    async def task_delete(
        task_name: Annotated[str, Field(description="Task name to delete.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Delete a Windows Scheduled Task.

        ## Return Format
        ```json
        {"success": bool, "task_name": str}
        ```

        ## Examples
            task_delete(task_name="DailyBackup")
        """
        try:
            await _run(["schtasks.exe", "/delete", "/tn", task_name, "/f"])
            return {"success": True, "task_name": task_name}
        except Exception as e:
            return fail_response(f"Task deletion failed: {e}", suggestions=["Verify task exists with task_list."])

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def task_run(
        task_name: Annotated[str, Field(description="Task name to trigger immediately.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Trigger a Windows Scheduled Task to run immediately.

        ## Return Format
        ```json
        {"success": bool, "task_name": str}
        ```

        ## Examples
            task_run(task_name="DailyBackup")
        """
        try:
            await _run(["schtasks.exe", "/run", "/tn", task_name])
            return {"success": True, "task_name": task_name}
        except Exception as e:
            return fail_response(f"Task run failed: {e}", suggestions=["Verify task exists with task_list."])

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def wmi_query(
        wmi_class: Annotated[
            str, Field(description="WMI class to query (e.g. Win32_Processor).")
        ] = "Win32_OperatingSystem",
        wmi_namespace: Annotated[str, Field(description="WMI namespace.")] = "root\\cimv2",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Query a WMI class and return the raw output.

        ## Return Format
        ```json
        {"success": bool, "wmi_class": str, "result": str}
        ```

        ## Examples
            wmi_query(wmi_class="Win32_Processor")
            wmi_query(wmi_class="Win32_BIOS")
        """
        try:
            result = await _run(["wmic.exe", f"/namespace:{wmi_namespace}", "path", wmi_class, "get", "/format:list"])
            return {"success": True, "wmi_class": wmi_class, "result": result}
        except Exception as e:
            return fail_response(
                f"WMI query failed: {e}",
                suggestions=["Verify wmi_class name. Try Win32_OperatingSystem for a basic test."],
            )

    parent_mcp.mount(ns, prefix="winops_auto")
    logger.info("Mounted atomic tools: winops_auto/task_list, /task_create, /task_delete, /task_run, /wmi_query")
