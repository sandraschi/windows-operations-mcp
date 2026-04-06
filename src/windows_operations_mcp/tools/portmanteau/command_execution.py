"""
Command Execution Portmanteau Tool for Windows Operations MCP.

Consolidates PowerShell and CMD execution into a single async portmanteau tool.
Uses asyncio.to_thread() so subprocess.run() never blocks the MCP event loop.
"""

import asyncio
import logging
from typing import Any, Dict, Literal, Optional

from ...logging_config import get_logger

logger = get_logger(__name__)


async def command_execution(
    action: Literal["powershell", "cmd"],
    command: str,
    working_directory: Optional[str] = None,
    timeout_seconds: int = 30,
    max_output_size: int = 10000,
) -> Dict[str, Any]:
    """
    Execute Windows commands with reliable output capture.

    FEATURES:
    - Reliable stdout/stderr capture
    - PowerShell and CMD execution in single interface
    - Proper encoding handling (cp850 for CMD, UTF-8 for PowerShell)
    - Timeout and output size limits for safety
    - Structured error reporting with execution time
    - Non-blocking: subprocess runs in a thread pool, never freezes the MCP server

    Args:
        action: The command type to execute. Must be one of:
            - "powershell": Execute PowerShell command with full .NET access
            - "cmd": Execute CMD command for batch operations
        command: The command to execute (required, non-empty string)
        working_directory: Working directory for command execution (optional)
        timeout_seconds: Command timeout in seconds (1-300, default: 30)
        max_output_size: Maximum output size in characters (default: 10000)

    Returns:
        FastMCP 2.14.1+ enhanced response with:
            - success: bool
            - action: str
            - stdout: str
            - stderr: str
            - exit_code: int
            - execution_time: float

    Notes:
        - subprocess.run() is offloaded to asyncio.to_thread() — the event loop
          is never blocked regardless of how long the command takes.
    """
    logger.info("command_execution_started", action=action, command=command[:100])

    if not command or not isinstance(command, str):
        return {"success": False, "action": action,
                "error": "Command must be a non-empty string",
                "stdout": "", "stderr": "", "exit_code": -1, "execution_time": 0.0}

    if not (1 <= timeout_seconds <= 300):
        return {"success": False, "action": action,
                "error": "timeout_seconds must be between 1 and 300",
                "stdout": "", "stderr": "", "exit_code": -1, "execution_time": 0.0}

    try:
        if action == "powershell":
            try:
                from ..powershell_tools import ps_executor
            except ImportError:
                return {"success": False, "action": action,
                        "error": "PowerShell executor not available",
                        "stdout": "", "stderr": "", "exit_code": -1, "execution_time": 0.0}
            # Run blocking subprocess in thread pool — never blocks event loop
            result = await asyncio.to_thread(
                ps_executor.execute,
                command=command,
                working_dir=working_directory,
                timeout=timeout_seconds,
            )

        elif action == "cmd":
            try:
                from ..powershell_tools import cmd_executor
            except ImportError:
                return {"success": False, "action": action,
                        "error": "CMD executor not available",
                        "stdout": "", "stderr": "", "exit_code": -1, "execution_time": 0.0}
            result = await asyncio.to_thread(
                cmd_executor.execute,
                command=command,
                working_directory=working_directory,
                timeout=timeout_seconds,
            )

        else:
            return {"success": False, "action": action,
                    "error": f"Unknown action: {action}",
                    "stdout": "", "stderr": "", "exit_code": -1, "execution_time": 0.0}

        response = {
            "success": result.get("success", False),
            "action": action,
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "exit_code": result.get("exit_code", -1),
            "execution_time": result.get("execution_time", 0.0),
        }
        if len(response["stdout"]) > max_output_size:
            response["stdout"] = response["stdout"][:max_output_size] + "\n[OUTPUT TRUNCATED]"
        if len(response["stderr"]) > max_output_size:
            response["stderr"] = response["stderr"][:max_output_size] + "\n[ERROR TRUNCATED]"
        if not response["success"]:
            response["error"] = result.get("error", "Command execution failed")

        logger.info("command_execution_completed", action=action,
                    success=response["success"], exit_code=response["exit_code"])
        return response

    except Exception as exc:
        error_msg = f"Command execution failed: {exc}"
        logger.error("command_execution_error", action=action, error=error_msg, exc_info=True)
        return {"success": False, "action": action, "error": error_msg,
                "stdout": "", "stderr": "", "exit_code": -1, "execution_time": 0.0}


def register_command_execution(mcp) -> None:
    """Register the command execution portmanteau tool with FastMCP."""
    mcp.tool(command_execution)
