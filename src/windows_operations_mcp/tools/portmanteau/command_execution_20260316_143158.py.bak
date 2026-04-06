"""
Command Execution Portmanteau Tool for Windows Operations MCP.

Consolidates PowerShell and CMD execution tools into a single portmanteau tool.
This is the highest priority tool as it provides the core value proposition:
reliable stdout/stderr capture for Windows command execution.
"""

import logging
from typing import Dict, Any, Optional, Literal

from ...logging_config import get_logger

logger = get_logger(__name__)


def command_execution(
    action: Literal["powershell", "cmd"],
    command: str,
    working_directory: Optional[str] = None,
    timeout_seconds: int = 30,
    max_output_size: int = 10000
) -> Dict[str, Any]:
    """
    Execute Windows commands with reliable output capture.

    FEATURES:
    - Reliable stdout/stderr capture (the main reason this exists!)
    - PowerShell and CMD execution in single interface
    - Proper encoding handling (cp850 for CMD, UTF-8 for PowerShell)
    - Timeout and output size limits for safety
    - Structured error reporting with execution time

    Args:
        action: The command type to execute. Must be one of:
            - "powershell": Execute PowerShell command with full .NET access
            - "cmd": Execute CMD command for batch operations
        command: The command to execute (required, non-empty string)
        working_directory: Working directory for command execution (optional, uses current if None)
        timeout_seconds: Command timeout in seconds (1-300, default: 30)
        max_output_size: Maximum output size in characters (default: 10000, prevents memory issues)

    Returns:
        FastMCP 2.14.1+ enhanced response with:
            - success: bool - Whether the command executed successfully
            - action: str - The action that was performed
            - stdout: str - Command standard output (if successful)
            - stderr: str - Command standard error (if any errors occurred)
            - exit_code: int - Command exit code (0 = success)
            - execution_time: float - Time taken to execute in seconds
            - error: str - Error message (only present if success is False)

    Examples:
        # Execute PowerShell command
        result = await command_execution(action="powershell", command="Get-Process")
        if result["success"]:
            print(f"Found {len(result['stdout'].splitlines())} processes")

        # Execute CMD command with timeout
        result = await command_execution(
            action="cmd",
            command="dir C:\\",
            timeout_seconds=10
        )

        # Execute in specific directory
        result = await command_execution(
            action="powershell",
            command="Get-ChildItem",
            working_directory="C:\\Users\\MyUser"
        )

    Notes:
        - PowerShell commands have access to full .NET framework
        - CMD commands use Windows console encoding (cp850)
        - Commands are executed synchronously with timeout protection
        - Large output may be truncated based on max_output_size
        - Working directory is validated before execution
    """
    logger.info("command_execution_started", action=action, command=command[:100])

    try:
        # Validate inputs
        if not command or not isinstance(command, str):
            return {
                "success": False,
                "action": action,
                "error": "Command must be a non-empty string"
            }

        if timeout_seconds < 1 or timeout_seconds > 300:
            return {
                "success": False,
                "action": action,
                "error": "timeout_seconds must be between 1 and 300"
            }

        # Route to appropriate executor based on action
        if action == "powershell":
            # Import PowerShell executor
            try:
                from ..powershell_tools import ps_executor
                result = ps_executor.execute_command(
                    command=command,
                    working_directory=working_directory,
                    timeout_seconds=timeout_seconds,
                    max_output_size=max_output_size
                )
            except ImportError:
                return {
                    "success": False,
                    "action": action,
                    "error": "PowerShell executor not available"
                }

        elif action == "cmd":
            # Import CMD executor
            try:
                from ..powershell_tools import cmd_executor
                result = cmd_executor.execute_command(
                    command=command,
                    working_directory=working_directory,
                    timeout_seconds=timeout_seconds,
                    max_output_size=max_output_size
                )
            except ImportError:
                return {
                    "success": False,
                    "action": action,
                    "error": "CMD executor not available"
                }

        else:
            return {
                "success": False,
                "action": action,
                "error": f"Unknown action: {action}"
            }

        # Standardize response format
        response = {
            "success": result.get("success", False),
            "action": action,
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "exit_code": result.get("exit_code", -1),
            "execution_time": result.get("execution_time", 0.0)
        }

        if not response["success"]:
            response["error"] = result.get("error", "Command execution failed")

        logger.info("command_execution_completed", action=action, success=response["success"], exit_code=response["exit_code"])
        return response

    except Exception as e:
        error_msg = f"Command execution failed: {str(e)}"
        logger.error("command_execution_error", action=action, error=error_msg, exc_info=True)
        return {
            "success": False,
            "action": action,
            "error": error_msg,
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "execution_time": 0.0
        }


def register_command_execution(mcp):
    """Register the command execution portmanteau tool with FastMCP."""
    mcp.tool(command_execution)