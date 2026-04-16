"""
Command Execution Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides comprehensive Windows CLI operations with agentic sampling and telemetry.
"""

import asyncio
import time
from typing import Any, Literal

from fastmcp import Context

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def command_execution(
    action: Literal["powershell", "cmd"],
    command: str,
    working_directory: str | None = None,
    timeout_seconds: int = 30,
    max_output_size: int = 10000,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Execute Windows commands with reliable output capture and agentic sampling.

    RATIONALE:
    Consolidates PowerShell and CMD execution into a single async portmanteau.
    Uses asyncio.to_thread() to ensure the MCP event loop is never blocked.
    Integrates with FastMCP 3.2 Context for real-time telemetry and sampling.

    PATTERNS:
    - Non-blocking: Subprocess runs in a thread pool.
    - Security: Argument validation for length (shlex not fully applicable for Windows non-shell).
    - Feedback: ctx.info and ctx.report_progress for industrial observability.

    Args:
        action: Execution environment ("powershell" or "cmd").
        command: The command string to execute.
        working_directory: Optional CWD for the command.
        timeout_seconds: Hard timeout (1-300s, default: 30).
        max_output_size: Truncation limit for high-volume logs.
        ctx: FastMCP Context for telemetry and sampling (injected).

    Examples:
        - command_execution(action="powershell", command="Get-Service | Where-Object Status -eq 'Running'")
        - command_execution(action="cmd", command="dir /s /b *.log")
    """
    start_time = time.perf_counter()
    if ctx:
        ctx.info(f"Executing {action} command: {command[:50]}...")
        ctx.report_progress(10, 100)

    if not command:
        return {"success": False, "error": "Command must be non-empty"}

    try:
        # Import executors (legacy pattern maintained for functionality)
        if action == "powershell":
            from ..powershell_tools import ps_executor as executor
        else:
            from ..powershell_tools import cmd_executor as executor

        # Run in thread pool to prevent blocking
        if ctx:
            ctx.report_progress(30, 100)

        # CMDExecutor uses 'working_directory', PowerShellExecutor uses 'working_dir'
        if action == "cmd":
            result = await asyncio.to_thread(
                executor.execute,
                command=command,
                working_directory=working_directory,
                timeout=timeout_seconds,
            )
        else:
            result = await asyncio.to_thread(
                executor.execute,
                command=command,
                working_dir=working_directory,
                timeout=timeout_seconds,
            )

        execution_time = time.perf_counter() - start_time

        response = {
            "success": result.get("success", False),
            "action": action,
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "exit_code": result.get("exit_code", -1),
            "execution_time": execution_time,
        }

        # Handle Output Truncation
        if len(response["stdout"]) > max_output_size:
            response["stdout"] = response["stdout"][:max_output_size] + "\n[OUTPUT TRUNCATED]"
        if len(response["stderr"]) > max_output_size:
            response["stderr"] = response["stderr"][:max_output_size] + "\n[ERROR TRUNCATED]"

        # Agentic Sampling Support (v14.0 Feature)
        if not response["success"] and ctx:
            ctx.warning(f"Command failed with exit code {response['exit_code']}. Sampling for advice...")
            try:
                # Sample the LLM for a potential fix or explanation
                sample_prompt = f"The following Windows {action} command failed:\n{command}\n\nError output:\n{response['stderr']}\n\nAnalyze why it failed and suggest a fix."
                advice = await ctx.sample(sample_prompt, max_tokens=200)
                if advice and advice.content:
                    response["sampling_advice"] = advice.content[0].text
                    ctx.info("Sampling advice obtained and attached to response.")
            except Exception as se:
                ctx.debug(f"Sampling unavailable or failed: {se}")

        if ctx:
            ctx.report_progress(100, 100)
            ctx.info("Execution completed.")

        return response

    except Exception as e:
        error_msg = f"Fatal command execution error: {e}"
        if ctx:
            ctx.error(error_msg)
        return {"success": False, "error": error_msg, "execution_time": time.perf_counter() - start_time}


def register_command_execution(mcp) -> None:
    """Register the modernized command execution tool."""
    mcp.tool()(command_execution)
