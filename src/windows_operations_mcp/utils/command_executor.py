"""
Command execution utilities for PowerShell and CMD with RELIABLE output capture.

MAJOR FIX 2025-08-18: Replaced broken threading approach with subprocess.communicate()
for robust stdout/stderr capture. No more empty outputs or missed command results.
"""

import logging
import os
import platform
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# Import utility functions from the current package
from . import get_execution_result, validate_directory

logger = logging.getLogger(__name__)


@dataclass
class ProcessOutput:
    """Container for process output data."""

    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    error: str | None = None
    execution_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.exit_code == 0 and not self.error,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code or 0,
            "error": self.error,
            "execution_time": self.execution_time,
            "command": "",
            "working_directory": "",
        }


class CommandExecutor:
    """Handles command execution with RELIABLE output capture - FIXED VERSION."""

    DEFAULT_TIMEOUT = 3600  # 1 hour default timeout

    @classmethod
    def _execute_with_communicate(
        cls,
        process_args: list,
        command: str,
        working_directory: str,
        timeout_seconds: int,
        capture_output: bool,
        output_encoding: str,
        max_output_size: int,
        shell: bool = False,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        RELIABLE command execution using subprocess.communicate().

        This replaces the broken threading approach with the standard, proven
        method for capturing subprocess output.
        """
        start_time = time.time()

        # Normalize PATHEXT if the inherited environment is broken (see
        # tools/powershell_tools._sanitized_env for the full story).
        if env is None:
            env = dict(os.environ)
        if ".EXE" not in env.get("PATHEXT", "").upper():
            env["PATHEXT"] = ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC"

        try:
            # Create process with proper encoding setup
            process = subprocess.Popen(
                process_args,
                cwd=working_directory,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                stdin=subprocess.PIPE,
                text=True,  # CRITICAL: Enable text mode for proper encoding
                encoding=output_encoding,
                errors="replace",  # Handle encoding errors gracefully
                shell=shell,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0,
            )

            if not capture_output:
                # Just wait for completion without capturing output
                try:
                    exit_code = process.wait(timeout=timeout_seconds)
                    return get_execution_result(
                        success=exit_code == 0,
                        command=command,
                        exit_code=exit_code,
                        execution_time=time.time() - start_time,
                        working_directory=working_directory,
                    )
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()

                    return get_execution_result(
                        success=False,
                        command=command,
                        execution_time=time.time() - start_time,
                        error=f"Command timed out after {timeout_seconds} seconds",
                        working_directory=working_directory,
                    )

            # RELIABLE OUTPUT CAPTURE: Use communicate() - the standard approach
            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                exit_code = process.returncode

            except subprocess.TimeoutExpired:
                # Handle timeout gracefully
                logger.warning(f"Command timed out after {timeout_seconds} seconds: {command[:100]}")
                process.terminate()
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    try:
                        # CRITICAL: bounded — an unbounded communicate() here
                        # deadlocks until detached grandchildren holding
                        # inherited pipe handles exit (v15.1 wedge fix).
                        stdout, stderr = process.communicate(timeout=5)
                    except subprocess.TimeoutExpired:
                        stdout, stderr = "", ""

                return get_execution_result(
                    success=False,
                    command=command,
                    stdout=stdout or "",
                    stderr=stderr or "",
                    exit_code=-1,
                    execution_time=time.time() - start_time,
                    error=f"Command timed out after {timeout_seconds} seconds",
                    working_directory=working_directory,
                )

            # Handle output size limits
            stdout = stdout or ""
            stderr = stderr or ""
            total_output_size = len(stdout) + len(stderr)

            if max_output_size and total_output_size > max_output_size:
                # Truncate but don't fail - better to get partial output than none
                truncate_size = max_output_size // 2
                stdout = stdout[:truncate_size] + f"\n\n[TRUNCATED - Output too large ({total_output_size} bytes)]"
                stderr = stderr[:truncate_size] + "\n\n[TRUNCATED - Output too large]"
                logger.warning(f"Output truncated for command: {command[:100]} (size: {total_output_size} bytes)")

            execution_time = time.time() - start_time

            # Log successful execution with output stats
            logger.info(
                f"Command completed: exit_code={exit_code}, "
                f"stdout_len={len(stdout)}, stderr_len={len(stderr)}, "
                f"time={execution_time:.2f}s"
            )

            return get_execution_result(
                success=exit_code == 0,
                command=command,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time=execution_time,
                working_directory=working_directory,
            )

        except Exception as e:
            error_msg = f"Process execution failed: {e!s}"
            logger.error(f"{error_msg} - Command: {command[:100]}", exc_info=True)

            return get_execution_result(
                success=False,
                command=command,
                execution_time=time.time() - start_time,
                error=error_msg,
                working_directory=working_directory,
            )

    @classmethod
    def execute_powershell(
        cls,
        command: str,
        working_directory: str | None = None,
        timeout_seconds: int | None = None,
        capture_output: bool = True,
        output_encoding: str = "utf-8",
        max_output_size: int | None = 10 * 1024 * 1024,  # 10MB default
        output_callback: Callable[[str, str], None] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Execute PowerShell commands with RELIABLE output capture.

        FIXED: No more threading issues or empty stdout.
        Uses subprocess.communicate() for guaranteed output capture.
        """
        start_time = time.time()

        # Use default timeout if not specified
        if timeout_seconds is None:
            timeout_seconds = cls.DEFAULT_TIMEOUT

        # Validate and set working directory
        current_dir = os.getcwd()
        if working_directory:
            dir_validation = validate_directory(working_directory)
            if not dir_validation["valid"]:
                return get_execution_result(
                    success=False,
                    command=command,
                    execution_time=time.time() - start_time,
                    error=dir_validation["error"],
                )
            current_dir = working_directory

        logger.info(f"Executing PowerShell: {command[:100]}...")

        # Build PowerShell command with UTF-8 encoding enforcement
        # CRITICAL: Force UTF-8 output encoding to prevent character corruption
        ps_command = (
            f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            f"$OutputEncoding = [System.Text.Encoding]::UTF8; "
            f"{command}"
        )

        process_args = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-OutputEncoding",
            "UTF8",
            "-Command",
            ps_command,
        ]

        # Use the reliable execution method
        result = cls._execute_with_communicate(
            process_args=process_args,
            command=command,
            working_directory=current_dir,
            timeout_seconds=timeout_seconds,
            capture_output=capture_output,
            output_encoding=output_encoding,
            max_output_size=max_output_size or (10 * 1024 * 1024),
            shell=False,
            env=kwargs.get("env") or kwargs.get("environment"),
        )

        # Note: output_callback not supported in this simplified version
        # This is acceptable trade-off for reliability
        if output_callback:
            logger.warning("output_callback not supported in reliable execution mode")

        return result

    @classmethod
    def execute_cmd(
        cls,
        command: str,
        working_directory: str | None = None,
        timeout_seconds: int | None = None,
        capture_output: bool = True,
        output_encoding: str = "utf-8",
        max_output_size: int | None = 10 * 1024 * 1024,  # 10MB default
        output_callback: Callable[[str, str], None] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Execute CMD commands with RELIABLE output capture.

        FIXED: No more threading issues or empty stdout.
        Uses subprocess.communicate() for guaranteed output capture.
        """
        start_time = time.time()

        # Use default timeout if not specified
        if timeout_seconds is None:
            timeout_seconds = cls.DEFAULT_TIMEOUT

        # Validate and set working directory
        current_dir = os.getcwd()
        if working_directory:
            dir_validation = validate_directory(working_directory)
            if not dir_validation["valid"]:
                return get_execution_result(
                    success=False,
                    command=command,
                    execution_time=time.time() - start_time,
                    error=dir_validation["error"],
                )
            current_dir = working_directory

        logger.info(f"Executing CMD: {command[:100]}...")

        # Build CMD command with UTF-8 encoding (chcp 65001)
        # CRITICAL: Force UTF-8 codepage to prevent character corruption
        cmd_command = f"chcp 65001 >nul 2>&1 & {command}"

        process_args = ["cmd.exe", "/c", cmd_command]

        # Use the reliable execution method
        result = cls._execute_with_communicate(
            process_args=process_args,
            command=command,
            working_directory=current_dir,
            timeout_seconds=timeout_seconds,
            capture_output=capture_output,
            output_encoding=output_encoding,
            max_output_size=max_output_size or (10 * 1024 * 1024),
            shell=False,
            env=kwargs.get("env") or kwargs.get("environment"),
        )

        # Note: output_callback not supported in this simplified version
        if output_callback:
            logger.warning("output_callback not supported in reliable execution mode")

        return result

    # Legacy compatibility - keep old method names but redirect to new implementation
    @classmethod
    def _process_output(cls, *args, **kwargs):
        """Legacy method - replaced with reliable communicate() approach."""
        raise NotImplementedError(
            "Legacy _process_output method replaced. Use execute_powershell/execute_cmd directly."
        )

    @classmethod
    def _enqueue_output(cls, *args, **kwargs):
        """Legacy method - replaced with reliable communicate() approach."""
        raise NotImplementedError("Legacy _enqueue_output method replaced. Threading approach abandoned.")
