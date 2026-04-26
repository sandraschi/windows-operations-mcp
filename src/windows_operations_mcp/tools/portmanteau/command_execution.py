"""
Command Execution - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_cmd":
  winops_cmd/powershell  - Execute a PowerShell command
  winops_cmd/cmd         - Execute a CMD command
"""

import asyncio
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

_TIMEOUT_WARN_S = 10.0  # cap on ctx.sample() calls


def register_command_execution(parent_mcp: FastMCP) -> None:
    """Mount atomic command execution tools under namespace 'winops_cmd'."""
    ns = FastMCP(name="winops_cmd")

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def powershell(
        command: Annotated[str, Field(description="PowerShell command to execute.")],
        working_directory: Annotated[str | None, Field(description="Optional working directory.")] = None,
        timeout_seconds: Annotated[int, Field(description="Hard timeout 1-300s.", ge=1, le=300)] = 30,
        max_output_size: Annotated[int, Field(description="Truncate stdout/stderr at this many chars.")] = 10000,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Execute a PowerShell command and return stdout, stderr, exit_code, execution_time.

        ## Return Format
        ```json
        {
          "success": bool,
          "stdout": str,
          "stderr": str,
          "exit_code": int,
          "execution_time": float,
          "sampling_advice": str  // only on failure, if sampling succeeded
        }
        ```

        ## Examples
            powershell(command="Get-Service | Where-Object Status -eq 'Running'")
            powershell(command="Get-Process | Sort-Object CPU -Descending | Select -First 10")

        Notes:
         - Uses asyncio.to_thread — never blocks the event loop.
         - ctx.sample() capped at 10s to prevent hang on unsupported clients.
        """
        if not command:
            return {"success": False, "error": "command must be non-empty", "suggestions": ["Provide a PowerShell command string."]}

        if ctx:
            await ctx.info(f"PS> {command[:80]}")
            await ctx.report_progress(10, 100)

        from ..powershell_tools import ps_executor

        result = await asyncio.to_thread(
            ps_executor.execute,
            command=command,
            working_dir=working_directory,
            timeout=timeout_seconds,
        )

        if ctx:
            await ctx.report_progress(90, 100)

        response: dict[str, Any] = {
            "success": result.get("success", False),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "exit_code": result.get("exit_code", -1),
            "execution_time": result.get("execution_time", 0.0),
        }

        if len(response["stdout"]) > max_output_size:
            response["stdout"] = response["stdout"][:max_output_size] + "\n[OUTPUT TRUNCATED]"
        if len(response["stderr"]) > max_output_size:
            response["stderr"] = response["stderr"][:max_output_size] + "\n[ERROR TRUNCATED]"

        if not response["success"] and ctx:
            try:
                advice = await asyncio.wait_for(
                    ctx.sample(
                        f"PowerShell command failed:\n{command}\n\nError:\n{response['stderr']}\n\nAnalyze and suggest a fix.",
                        max_tokens=200,
                    ),
                    timeout=_TIMEOUT_WARN_S,
                )
                if advice and advice.content:
                    response["sampling_advice"] = advice.content[0].text
            except Exception:
                pass

        if ctx:
            await ctx.report_progress(100, 100)

        return response

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def cmd(
        command: Annotated[str, Field(description="CMD command to execute.")],
        working_directory: Annotated[str | None, Field(description="Optional working directory.")] = None,
        timeout_seconds: Annotated[int, Field(description="Hard timeout 1-300s.", ge=1, le=300)] = 30,
        max_output_size: Annotated[int, Field(description="Truncate stdout/stderr at this many chars.")] = 10000,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Execute a CMD (cmd.exe) command and return stdout, stderr, exit_code, execution_time.

        ## Return Format
        ```json
        {
          "success": bool,
          "stdout": str,
          "stderr": str,
          "exit_code": int,
          "execution_time": float,
          "sampling_advice": str  // only on failure, if sampling succeeded
        }
        ```

        ## Examples
            cmd(command="dir /s /b *.log", working_directory="C:\\Logs")
            cmd(command="ipconfig /all")

        Notes:
         - Uses asyncio.to_thread — never blocks the event loop.
         - ctx.sample() capped at 10s to prevent hang on unsupported clients.
        """
        if not command:
            return {"success": False, "error": "command must be non-empty", "suggestions": ["Provide a CMD command string."]}

        if ctx:
            await ctx.info(f"CMD> {command[:80]}")
            await ctx.report_progress(10, 100)

        from ..powershell_tools import cmd_executor

        result = await asyncio.to_thread(
            cmd_executor.execute,
            command=command,
            working_directory=working_directory,
            timeout=timeout_seconds,
        )

        if ctx:
            await ctx.report_progress(90, 100)

        response: dict[str, Any] = {
            "success": result.get("success", False),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "exit_code": result.get("exit_code", -1),
            "execution_time": result.get("execution_time", 0.0),
        }

        if len(response["stdout"]) > max_output_size:
            response["stdout"] = response["stdout"][:max_output_size] + "\n[OUTPUT TRUNCATED]"
        if len(response["stderr"]) > max_output_size:
            response["stderr"] = response["stderr"][:max_output_size] + "\n[ERROR TRUNCATED]"

        if not response["success"] and ctx:
            try:
                advice = await asyncio.wait_for(
                    ctx.sample(
                        f"CMD command failed:\n{command}\n\nError:\n{response['stderr']}\n\nAnalyze and suggest a fix.",
                        max_tokens=200,
                    ),
                    timeout=_TIMEOUT_WARN_S,
                )
                if advice and advice.content:
                    response["sampling_advice"] = advice.content[0].text
            except Exception:
                pass

        if ctx:
            await ctx.report_progress(100, 100)

        return response

    parent_mcp.mount(ns, prefix="winops_cmd")
    logger.info("Mounted atomic tools: winops_cmd/powershell, winops_cmd/cmd")
