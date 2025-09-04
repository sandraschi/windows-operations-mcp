"""
Extended command execution utilities with advanced features.
"""

import asyncio
import json
import os
import platform
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Awaitable, cast

from .command_executor import CommandExecutor as BaseCommandExecutor, ProcessOutput
from ..logging_config import get_logger

logger = get_logger(__name__)

# Type aliases
OutputCallback = Callable[[str, str], Awaitable[None]]  # (output_type, data) -> None

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
    pid: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'success': self.success,
            'exit_code': self.exit_code,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'execution_time': self.execution_time,
            'command': self.command,
            'working_directory': self.working_directory,
            'pid': self.pid,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'error': self.error,
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandResult':
        """Create CommandResult from dictionary."""
        return cls(**data)


class ExtendedCommandExecutor(BaseCommandExecutor):
    """Extended command executor with advanced features."""
    
    @staticmethod
    async def execute_async(
        command: Union[str, List[str]],
        working_directory: Optional[str] = None,
        timeout_seconds: float = 60.0,
        env: Optional[Dict[str, str]] = None,
        shell: bool = False,
        capture_output: bool = True,
        encoding: str = 'utf-8',
        errors: str = 'replace',
        on_output: Optional[OutputCallback] = None,
        **kwargs
    ) -> CommandResult:
        """
        Asynchronously execute a command with real-time output streaming.
        
        Args:
            command: Command to execute (string or list of args)
            working_directory: Working directory for command
            timeout_seconds: Maximum execution time
            env: Environment variables
            shell: Use shell for execution
            capture_output: Whether to capture output
            encoding: Output encoding
            errors: How to handle encoding errors
            on_output: Callback for real-time output
            **kwargs: Additional subprocess.Popen arguments
            
        Returns:
            CommandResult with execution details
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
            
            # Prepare command
            if isinstance(command, str):
                cmd = command if shell else ['/bin/sh', '-c', command] if platform.system() != 'Windows' else ['cmd', '/c', command]
            else:
                cmd = command
            
            # Start process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=working_directory or os.getcwd(),
                env=process_env,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                shell=shell,
                **kwargs
            )
            
            # Process output
            if capture_output and process.stdout and process.stderr:
                # Create tasks for reading stdout and stderr
                read_stdout = process.stdout.read()
                read_stderr = process.stderr.read()
                
                # Wait for both to complete or timeout
                done, pending = await asyncio.wait(
                    [read_stdout, read_stderr],
                    timeout=timeout_seconds,
                    return_when=asyncio.ALL_COMPLETED
                )
                
                # Process results
                if read_stdout in done:
                    stdout_data = (await read_stdout).decode(encoding, errors).splitlines()
                    if on_output:
                        for line in stdout_data:
                            await on_output('stdout', line)
                
                if read_stderr in done:
                    stderr_data = (await read_stderr).decode(encoding, errors).splitlines()
                    if on_output:
                        for line in stderr_data:
                            await on_output('stderr', line)
                
                # Check for timeout
                if pending:
                    raise asyncio.TimeoutError(f"Command timed out after {timeout_seconds} seconds")
                
                # Wait for process to complete
                return_code = await asyncio.wait_for(process.wait(), timeout=timeout_seconds)
            else:
                # No output capture, just wait for process to complete
                return_code = await asyncio.wait_for(process.wait(), timeout=timeout_seconds)
            
            # Build result
            return CommandResult(
                success=return_code == 0,
                exit_code=return_code,
                stdout='\n'.join(stdout_data),
                stderr='\n'.join(stderr_data),
                execution_time=time.time() - start_time,
                command=command if isinstance(command, str) else ' '.join(command),
                working_directory=working_directory or os.getcwd(),
                pid=process.pid,
                start_time=start_time,
                end_time=time.time()
            )
            
        except asyncio.TimeoutError:
            if process:
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=5)
                except (ProcessLookupError, asyncio.TimeoutError):
                    if process.returncode is None:
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
            
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout='\n'.join(stdout_data),
                stderr=f'Command timed out after {timeout_seconds} seconds\n{"\n".join(stderr_data)}',
                execution_time=time.time() - start_time,
                command=command if isinstance(command, str) else ' '.join(command),
                working_directory=working_directory or os.getcwd(),
                error=f'Command timed out after {timeout_seconds} seconds',
                pid=process.pid if process else None,
                start_time=start_time,
                end_time=time.time()
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout='\n'.join(stdout_data),
                stderr=f'Error executing command: {str(e)}\n{"\n".join(stderr_data)}',
                execution_time=time.time() - start_time,
                command=command if isinstance(command, str) else ' '.join(command),
                working_directory=working_directory or os.getcwd(),
                error=str(e),
                pid=process.pid if process else None,
                start_time=start_time,
                end_time=time.time()
            )
    
    @staticmethod
    def execute_with_retry(
        command: Union[str, List[str]],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        **kwargs
    ) -> CommandResult:
        """
        Execute a command with automatic retries on failure.
        
        Args:
            command: Command to execute
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            backoff_factor: Multiplier for delay between retries
            **kwargs: Additional arguments for execute_async
            
        Returns:
            CommandResult of the last attempt
        """
        last_result = None
        current_delay = retry_delay
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                logger.warning(f"Retry {attempt}/{max_retries} after {current_delay:.1f}s")
                time.sleep(current_delay)
                current_delay *= backoff_factor
            
            last_result = asyncio.run(ExtendedCommandExecutor.execute_async(command, **kwargs))
            
            if last_result.success:
                return last_result
            
            logger.warning(f"Attempt {attempt + 1} failed with exit code {last_result.exit_code}")
        
        return last_result
    
    @staticmethod
    def execute_with_timeout_async(
        command: Union[str, List[str]],
        timeout_seconds: float,
        on_timeout: Optional[Callable[[], None]] = None,
        **kwargs
    ) -> CommandResult:
        """
        Execute a command with a timeout and optional timeout handler.
        
        Args:
            command: Command to execute
            timeout_seconds: Maximum execution time
            on_timeout: Callback to execute on timeout
            **kwargs: Additional arguments for execute_async
            
        Returns:
            CommandResult of the execution
        """
        try:
            return asyncio.run(
                asyncio.wait_for(
                    ExtendedCommandExecutor.execute_async(command, **kwargs),
                    timeout=timeout_seconds
                )
            )
        except asyncio.TimeoutError:
            if on_timeout:
                on_timeout()
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout='',
                stderr=f'Command timed out after {timeout_seconds} seconds',
                execution_time=timeout_seconds,
                command=command if isinstance(command, str) else ' '.join(command),
                working_directory=kwargs.get('working_directory', os.getcwd()),
                error=f'Command timed out after {timeout_seconds} seconds'
            )

    @classmethod
    async def execute_powershell_advanced(
        cls,
        script: str,
        working_directory: Optional[str] = None,
        timeout_seconds: int = 60,
        capture_output: bool = True,
        as_admin: bool = False,
        output_encoding: str = 'utf-8',
        convert_json: bool = True,
        **kwargs
    ) -> CommandResult:
        """
        Execute a PowerShell script with advanced features.
        
        Args:
            script: PowerShell script to execute
            working_directory: Working directory for the command
            timeout_seconds: Maximum execution time in seconds
            capture_output: Whether to capture command output
            as_admin: Run with elevated privileges (Windows only)
            output_encoding: Encoding for command output
            convert_json: Whether to automatically parse JSON output
            **kwargs: Additional arguments for command execution
            
        Returns:
            CommandResult with execution details and parsed JSON (if convert_json is True)
        """
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(suffix='.ps1', delete=False) as f:
            f.write(script.encode('utf-8'))
            temp_script_path = f.name
        
        try:
            # Build command
            if as_admin and platform.system() == 'Windows':
                command = [
                    'powershell.exe',
                    '-NoProfile',
                    '-ExecutionPolicy', 'Bypass',
                    '-File', temp_script_path
                ]
                
                # Use Start-Process with RunAs verb for elevation
                command_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in command)
                command = [
                    'powershell.exe',
                    '-NoProfile',
                    '-ExecutionPolicy', 'Bypass',
                    '-Command',
                    f'Start-Process -FilePath "{command[0]}" -ArgumentList {command[1:]} -Verb RunAs -Wait -PassThru | Select-Object ExitCode'
                ]
            else:
                command = [
                    'powershell.exe',
                    '-NoProfile',
                    '-ExecutionPolicy', 'Bypass',
                    '-File', temp_script_path
                ]
            
            # Execute with timeout
            result = await ExtendedCommandExecutor.execute_async(
                command=command,
                working_directory=working_directory,
                timeout_seconds=timeout_seconds,
                capture_output=capture_output,
                encoding=output_encoding,
                **kwargs
            )
            
            # Parse JSON output if requested
            if convert_json and capture_output and result.stdout.strip():
                try:
                    output = json.loads(result.stdout)
                    if isinstance(output, (dict, list)):
                        result.metadata = output
                except json.JSONDecodeError:
                    pass
            
            return result
            
        finally:
            try:
                os.unlink(temp_script_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary script: {e}")

# Example usage
async def example_usage():
    # Simple command execution
    result = await ExtendedCommandExecutor.execute_async(
        'echo Hello, World! && ping -n 3 localhost',
        on_output=lambda t, d: print(f"[{t.upper()}] {d}")
    )
    print(f"Exit code: {result.exit_code}")
    
    # PowerShell with JSON output (single line to avoid string issues)
    ps_script = "Get-Process | Select-Object -First 3 | Select-Object Name, Id, CPU, WorkingSet | ConvertTo-Json"
    
    result = await ExtendedCommandExecutor.execute_powershell_advanced(
        ps_script,
        on_output=lambda t, d: print(f"[{t.upper()}] {d}"),
        convert_json=True
    )
    
    if result.metadata:
        for process in result.metadata:
            print(f"Process: {process['Name']} (ID: {process['Id']})")

if __name__ == '__main__':
    asyncio.run(example_usage())
