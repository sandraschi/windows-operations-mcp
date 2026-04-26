"""
PowerShell and CMD execution tools for Windows Operations MCP.
QUICK FIX VERSION - Addresses core stdout issues and over-restrictive security.

FIXES APPLIED:
1. Relaxed security filters (removed 'format' block, allow common cmdlets)
2. Fixed encoding handling (use native console encoding)
3. Removed forced Out-String wrapping
4. Simplified command execution
"""

import asyncio
import ctypes
import os
import subprocess
import time
from typing import Any

from ..logging_config import get_logger

logger = get_logger(__name__)


class CMDExecutor:
    """
    CMD execution with reliable output capture.

    FIX v14.2: cmd.exe was hanging due to console handle inheritance and missing
    no-interaction flags. Key changes:
    - CREATE_NO_WINDOW: detaches from parent console, prevents pipe deadlock
    - /Q flag: disables echo, avoids interactive prompts
    - stdin=DEVNULL: prevents cmd.exe blocking waiting for input
    - Explicit stdout/stderr PIPE instead of capture_output=True (same effect
      but more explicit and avoids any capture_output interaction with creationflags)
    """

    def __init__(self):
        self.encoding = self._get_console_encoding()
        logger.info(f"CMD executor initialized with encoding: {self.encoding}")

    def _get_console_encoding(self) -> str:
        """Get the native console encoding."""
        try:
            kernel32 = ctypes.windll.kernel32
            cp = kernel32.GetConsoleCP()
            if cp:
                return f"cp{cp}"
        except Exception:
            pass
        return "cp850"

    def execute(self, command: str, working_directory: str | None = None, timeout: int = 30) -> dict[str, Any]:
        """Execute CMD command with reliable non-blocking output capture."""
        start_time = time.time()

        try:
            # /Q: quiet mode (no echo), prevents interactive echo blocking
            cmd_args = ["cmd.exe", "/Q", "/c", command]

            cwd = working_directory or os.getcwd()

            result = subprocess.run(
                cmd_args,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,          # Never block waiting for input
                text=True,
                encoding=self.encoding,
                timeout=timeout,
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,  # Detach from console
            )

            execution_time = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "execution_time": execution_time,
            }

        except subprocess.TimeoutExpired as e:
            # Kill the process if timeout fires
            if e.output:
                partial_stdout = e.output.decode(self.encoding, errors="replace") if isinstance(e.output, bytes) else str(e.output)
            else:
                partial_stdout = ""
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": partial_stdout,
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
    Fixed PowerShell execution that solves the "no stdout" problem.

    Key fixes:
    1. Relaxed security filters - allow common PowerShell cmdlets
    2. Native encoding detection instead of forcing UTF-8
    3. Clean command execution without unnecessary wrapping
    """

    def __init__(self):
        self.console_encoding = self._get_console_encoding()
        logger.info(f"PowerShell executor initialized with encoding: {self.console_encoding}")

    def _get_console_encoding(self):
        """Get Windows console encoding reliably."""
        try:
            # Get the actual console codepage
            console_cp = ctypes.windll.kernel32.GetConsoleOutputCP()
            if console_cp == 65001:  # UTF-8
                return "utf-8"
            elif console_cp == 1252:  # Windows-1252
                return "cp1252"
            else:
                return f"cp{console_cp}"
        except Exception as e:
            logger.warning(f"Could not get console encoding: {e}")
            return "utf-8"  # Safe fallback

    def execute(self, command: str, working_dir: str | None = None, timeout: int = 60) -> dict[str, Any]:
        """
        Execute PowerShell command with reliable output capture.

        Args:
            command: PowerShell command to execute
            working_dir: Working directory (optional)
            timeout: Command timeout in seconds

        Returns:
            dict: {
                'success': bool,
                'stdout': str,
                'stderr': str,
                'exit_code': int,
                'execution_time': float,
                'encoding_used': str
            }
        """
        start_time = time.time()

        try:
            # Build clean PowerShell command - NO forced encoding, NO Out-String wrapping
            cmd = [
                "powershell.exe",
                "-NoProfile",  # Skip user profile loading
                "-NonInteractive",  # No interactive prompts
                "-ExecutionPolicy",
                "Bypass",  # Override execution policy
                "-Command",
                command,  # Execute command as-is, no manipulation
            ]

            logger.debug(f"Executing PowerShell: {command[:100]}...")

            # Execute with native encoding
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding=self.console_encoding,  # Use detected console encoding
                errors="replace",  # Never crash on encoding errors
                timeout=timeout,
                cwd=working_dir,
            )

            execution_time = time.time() - start_time

            response = {
                "success": result.returncode == 0,
                "stdout": result.stdout,  # No .strip() - preserve formatting
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "execution_time": execution_time,
                "encoding_used": self.console_encoding,
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
                "encoding_used": "timeout",
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
                "encoding_used": "error",
            }


# Module-level executor instances for import by portmanteau command_execution
ps_executor = PowerShellExecutor()
cmd_executor = CMDExecutor()


def register_powershell_tools(mcp):
    """Register PowerShell and CMD execution tools with FastMCP."""
    # Use module-level executor instances
    # (also available for import: from .powershell_tools import ps_executor, cmd_executor)

    # Register PowerShell tool
    @mcp.tool()
    async def run_powershell_tool(
        command: str, working_directory: str | None = None, timeout_seconds: int = 30, max_output_size: int = 10000
    ) -> dict[str, Any]:
        """Execute PowerShell command with reliable output capture."""
        return await asyncio.to_thread(
            ps_executor.execute,
            command=command,
            working_dir=working_directory,
            timeout=timeout_seconds,
        )

    @mcp.tool()
    async def run_cmd_tool(
        command: str, working_directory: str | None = None, timeout_seconds: int = 30, max_output_size: int = 10000
    ) -> dict[str, Any]:
        """Execute CMD command with reliable output capture."""
        return await asyncio.to_thread(
            cmd_executor.execute,
            command=command,
            working_directory=working_directory,
            timeout=timeout_seconds,
        )

    logger.info("PowerShell and CMD tools registered successfully")
