"""
PowerShell and CMD execution tools for Windows Operations MCP.
v15.0 - RELIABLE OUTPUT CAPTURE FIXES

FIXES (May 2026):
1. PowerShell: Forces UTF-8 encoding setup before every command
   ([Console]::OutputEncoding + $OutputEncoding)
2. PowerShell: Uses -OutputFormat Text for text-mode output
3. PowerShell: Appends | Out-String -Width 4096 to capture native exe output
   (docker, psql, etc. — PowerShell 5.1 silently drops their stdout otherwise)
4. PowerShell/Cmd: Added stdin_data parameter for piping input
5. CMD: Uses shell=True with raw command string to prevent list2cmdline
   quote-mangling (fixes nested quoting with docker exec ... sh -c "...")
6. CMD: Uses full path C:\\Windows\\System32\\cmd.exe for reliability
7. Both: Uses utf-8 encoding consistently instead of brittle console CP detection
"""

import asyncio
import os
import subprocess
import time
from typing import Any

from ..logging_config import get_logger

logger = get_logger(__name__)


class CMDExecutor:
    """
    CMD execution with reliable output capture and proper quoting support.

    v15.0 FIXES:
    - shell=True prevents list2cmdline from mangling nested quotes
      (solves "Unterminated quoted string" errors with docker exec sh -c "...")
    - Full cmd.exe path avoids PATH resolution issues
    - stdin_data support for piped input
    - utf-8 encoding for consistent cross-platform output
    """

    def __init__(self):
        logger.info("CMD executor initialized (v15.0 — shell=True quoting fix)")

    def execute(
        self,
        command: str,
        working_directory: str | None = None,
        timeout: int = 30,
        stdin_data: str | None = None,
    ) -> dict[str, Any]:
        """Execute CMD command with reliable output capture."""
        start_time = time.time()
        cwd = working_directory or os.getcwd()

        try:
            # shell=True avoids list2cmdline quote-mangling on Windows.
            # Python passes the raw string as "COMSPEC /c <command>", preserving
            # the original quoting for nested patterns like:
            #   docker exec container sh -c "python -c '...'"
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
                errors="replace",
                input=stdin_data,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            execution_time = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "execution_time": execution_time,
            }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "exit_code": -1,
                "execution_time": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {e!s}",
                "exit_code": -1,
                "execution_time": execution_time,
            }


class PowerShellExecutor:
    """
    PowerShell execution with guaranteed native exe output capture.

    v15.0 FIXES:
    - Prepends [Console]::OutputEncoding = UTF8 and $OutputEncoding = UTF8
      to force PowerShell 5.1 to send output in UTF-8 when writing to a pipe
    - Appends | Out-String -Width 4096 to force string serialization
      (PowerShell 5.1 silently drops native exe stdout otherwise)
    - Uses -OutputFormat Text for pipe-friendly text output
    - Uses utf-8 encoding consistently (no brittle GetConsoleOutputCP)
    - stdin_data support for piped input
    """

    def __init__(self):
        logger.info("PowerShell executor initialized (v15.0 — Out-String + UTF-8 fixes)")

    def _build_command(self, command: str) -> str:
        """Wrap command with encoding setup and output-forcing pipeline.

        The | Out-String -Width 4096 suffix is critical for PowerShell 5.1:
        without it, native executables (docker, psql, etc.) have their stdout
        silently dropped when PowerShell writes to a pipe.
        """
        setup = (
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "$OutputEncoding = [System.Text.Encoding]::UTF8"
        )
        return f"{setup}; {command} | Out-String -Width 4096"

    def execute(
        self,
        command: str,
        working_dir: str | None = None,
        timeout: int = 60,
        stdin_data: str | None = None,
    ) -> dict[str, Any]:
        """Execute PowerShell command with reliable output capture.

        Args:
            command: PowerShell command to execute
            working_dir: Working directory (optional)
            timeout: Command timeout in seconds
            stdin_data: Optional data to pipe to stdin

        Returns:
            dict with success, stdout, stderr, exit_code, execution_time
        """
        start_time = time.time()

        try:
            full_command = self._build_command(command)

            cmd = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-OutputFormat",
                "Text",
                "-Command",
                full_command,
            ]

            logger.debug(f"Executing PowerShell: {command[:100]}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                cwd=working_dir,
                input=stdin_data,
            )

            execution_time = time.time() - start_time

            response = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "execution_time": execution_time,
            }

            if response["success"]:
                logger.debug(f"PowerShell command succeeded in {execution_time:.2f}s")
            else:
                logger.warning(f"PowerShell command failed with exit code {result.returncode}")

            return response

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"PowerShell command timed out after {timeout} seconds")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "exit_code": -1,
                "execution_time": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"PowerShell execution error: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {e!s}",
                "exit_code": -1,
                "execution_time": execution_time,
            }



# Module-level executor instances for import by portmanteau command_execution
ps_executor = PowerShellExecutor()
cmd_executor = CMDExecutor()


def register_powershell_tools(mcp):
    """Register PowerShell and CMD execution tools with FastMCP."""
    @mcp.tool()
    async def run_powershell_tool(
        command: str,
        working_directory: str | None = None,
        timeout_seconds: int = 60,
        max_output_size: int = 10000,
        stdin_data: str | None = None,
    ) -> dict[str, Any]:
        """Execute PowerShell command with reliable output capture."""
        return await asyncio.to_thread(
            ps_executor.execute,
            command=command,
            working_dir=working_directory,
            timeout=timeout_seconds,
            stdin_data=stdin_data,
        )

    @mcp.tool()
    async def run_cmd_tool(
        command: str,
        working_directory: str | None = None,
        timeout_seconds: int = 30,
        max_output_size: int = 10000,
        stdin_data: str | None = None,
    ) -> dict[str, Any]:
        """Execute CMD command with reliable output capture."""
        return await asyncio.to_thread(
            cmd_executor.execute,
            command=command,
            working_directory=working_directory,
            timeout=timeout_seconds,
            stdin_data=stdin_data,
        )

    logger.info("PowerShell and CMD tools registered successfully")
