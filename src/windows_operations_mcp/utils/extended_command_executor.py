"""
Extended command execution utilities with advanced features.
"""

import asyncio
import json
import os
import platform
import subprocess
import tempfile
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from ..logging_config import get_logger
from .command_executor import CommandExecutor as BaseCommandExecutor

logger = get_logger(__name__)

# Type aliases
OutputCallback = Callable[[str, str], Awaitable[None]]  # (data, stream_type) -> None


@dataclass
class CommandResult:
    """Structured result of command execution."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    command: str
    working_directory: str
    pid: int | None = None
    start_time: float | None = None
    end_time: float | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "execution_time": self.execution_time,
            "command": self.command,
            "working_directory": self.working_directory,
            "pid": self.pid,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error": self.error,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommandResult":
        """Create CommandResult from dictionary."""
        return cls(**data)


class ExtendedCommandExecutor(BaseCommandExecutor):
    """Extended command executor with advanced features."""

    @classmethod
    def execute_cmd(cls, command: str, **kwargs) -> dict[str, Any]:
        """
        Synchronous wrapper that supports output callbacks and advanced features
        by running the async execution engine.
        """
        # If there is a callback, we MUST use execute_async to get real-time results
        if kwargs.get("output_callback"):
            # Convert sync callback to async if needed
            sync_callback = kwargs.get("output_callback")

            async def wrapped_callback(data, stream):
                sync_callback(data, stream)

            kwargs["on_output"] = wrapped_callback
            del kwargs["output_callback"]

            result = asyncio.run(cls.execute_async(command, **kwargs))
            return result.to_dict()

        # Otherwise use the base implementation for speed/simplicity
        result = BaseCommandExecutor.execute_cmd(command, **kwargs)
        return result if isinstance(result, dict) else result.to_dict()

    @classmethod
    def execute_powershell(cls, command: str, **kwargs) -> dict[str, Any]:
        """Synchronous PowerShell wrapper."""
        # Escape double quotes for the command wrapper
        escaped_command = command.replace('"', '\\"')
        ps_command = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "{escaped_command}"'
        return cls.execute_cmd(ps_command, **kwargs)

    @staticmethod
    async def execute_async(
        command: str | list[str],
        working_directory: str | None = None,
        timeout_seconds: float = 60.0,
        env: dict[str, str] | None = None,
        shell: bool = False,
        capture_output: bool = True,
        encoding: str = "utf-8",
        errors: str = "replace",
        on_output: OutputCallback | None = None,
        **kwargs,
    ) -> CommandResult:
        """
        Asynchronously execute a command with real-time output streaming.
        """
        start_time = time.time()
        process = None
        stdout_data = []
        stderr_data = []

        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            elif kwargs.get("environment"):
                process_env.update(kwargs.get("environment"))

            # Prepare command
            if isinstance(command, str):
                if platform.system() == "Windows":
                    cmd = ["cmd", "/c", command]
                else:
                    cmd = ["/bin/sh", "-c", command]
            else:
                cmd = command

            # Start process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=working_directory or os.getcwd(),
                env=process_env,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0,
                **{k: v for k, v in kwargs.items() if k not in ["environment", "on_output"]},
            )

            # Process output
            if capture_output and process.stdout and process.stderr:

                async def read_stream(stream, stream_type):
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        decoded_line = line.decode(encoding, errors).rstrip()
                        if stream_type == "stdout":
                            stdout_data.append(decoded_line)
                        else:
                            stderr_data.append(decoded_line)

                        if on_output:
                            await on_output(decoded_line, stream_type)

                # Wait for both streams and completion
                try:
                    await asyncio.wait_for(
                        asyncio.gather(read_stream(process.stdout, "stdout"), read_stream(process.stderr, "stderr")),
                        timeout=timeout_seconds,
                    )
                except TimeoutError:
                    raise TimeoutError(f"Stream reading timed out after {timeout_seconds}s")

                return_code = await asyncio.wait_for(process.wait(), timeout=5)
            else:
                return_code = await asyncio.wait_for(process.wait(), timeout=timeout_seconds)

            return CommandResult(
                success=return_code == 0,
                exit_code=return_code if return_code is not None else -1,
                stdout="\n".join(stdout_data),
                stderr="\n".join(stderr_data),
                execution_time=time.time() - start_time,
                command=command if isinstance(command, str) else " ".join(command),
                working_directory=working_directory or os.getcwd(),
                pid=process.pid,
                start_time=start_time,
                end_time=time.time(),
            )

        except TimeoutError:
            if process:
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=5)
                except:
                    if process.returncode is None:
                        try:
                            process.kill()
                        except:
                            pass

            return CommandResult(
                success=False,
                exit_code=1,  # Match legacy test expectation for timeout
                stdout="\n".join(stdout_data),
                stderr=f"Command timed out after {timeout_seconds} seconds\n" + "\n".join(stderr_data),
                execution_time=time.time() - start_time,
                command=str(command),
                working_directory=working_directory or os.getcwd(),
                error=f"Command timed out after {timeout_seconds} seconds",
                pid=process.pid if process else None,
            )

        except Exception as e:
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="\n".join(stdout_data),
                stderr=str(e),
                execution_time=time.time() - start_time,
                command=str(command),
                working_directory=working_directory or os.getcwd(),
                error=str(e),
            )

    @staticmethod
    def execute_with_retry(command: str | list[str], max_retries: int = 3, **kwargs) -> CommandResult:
        """Execute with automatic retries."""
        last_result = None
        for attempt in range(max_retries + 1):
            last_result = asyncio.run(ExtendedCommandExecutor.execute_async(command, **kwargs))
            if last_result.success:
                return last_result
            if attempt < max_retries:
                time.sleep(1.0 * (2**attempt))
        return last_result

    @classmethod
    async def execute_powershell_advanced(
        cls,
        script: str,
        working_directory: str | None = None,
        timeout_seconds: int = 60,
        capture_output: bool = True,
        as_admin: bool = False,
        output_encoding: str = "utf-8",
        convert_json: bool = True,
        **kwargs,
    ) -> CommandResult:
        """Execute PowerShell script with elevation and JSON support."""
        with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False, mode="w", encoding="utf-8") as f:
            f.write(script)
            temp_path = f.name

        try:
            if as_admin and platform.system() == "Windows":
                cmd = [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    f'Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File {temp_path}" -Verb RunAs -Wait',
                ]
            else:
                cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", temp_path]

            result = await cls.execute_async(
                cmd,
                working_directory=working_directory,
                timeout_seconds=timeout_seconds,
                capture_output=capture_output,
                encoding=output_encoding,
                **kwargs,
            )

            if convert_json and result.success and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    result.metadata = data
                    # If JSON follows standard tool result format, unpack it
                    if isinstance(data, dict) and "success" in data:
                        result.success = data.get("success", result.success)
                        result.stdout = data.get("stdout", result.stdout)
                        result.stderr = data.get("stderr", result.stderr)
                except:
                    pass

            return result
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass


if __name__ == "__main__":
    # Simple self-test
    ExtendedCommandExecutor.execute_cmd("echo Hello")
