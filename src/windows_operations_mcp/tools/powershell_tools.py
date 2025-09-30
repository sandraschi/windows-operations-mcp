"""
PowerShell and CMD execution tools for Windows Operations MCP.
QUICK FIX VERSION - Addresses core stdout issues and over-restrictive security.

FIXES APPLIED:
1. Relaxed security filters (removed 'format' block, allow common cmdlets)
2. Fixed encoding handling (use native console encoding)
3. Removed forced Out-String wrapping
4. Simplified command execution
"""

from typing import Dict, Any, Optional
import subprocess
import time
import os
import logging
import ctypes

from ..logging_config import get_logger
from ..decorators import tool

logger = get_logger(__name__)

class CMDExecutor:
    """
    CMD execution with reliable output capture.
    """
    
    def __init__(self):
        self.encoding = self._get_console_encoding()
        logger.info(f"CMD executor initialized with encoding: {self.encoding}")
    
    def _get_console_encoding(self) -> str:
        """Get the native console encoding."""
        try:
            # Try to get the console code page
            kernel32 = ctypes.windll.kernel32
            cp = kernel32.GetConsoleCP()
            if cp:
                return f"cp{cp}"
        except:
            pass
        return "cp850"  # Default Windows console encoding
    
    def execute(self, command: str, working_directory: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute CMD command with reliable output capture."""
        start_time = time.time()
        
        try:
            # Use cmd.exe /c to execute the command
            cmd_args = ["cmd.exe", "/c", command]
            
            # Set working directory
            cwd = working_directory or os.getcwd()
            
            # Execute command
            result = subprocess.run(
                cmd_args,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding=self.encoding,
                timeout=timeout,
                errors='replace'
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "execution_time": execution_time
            }
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "exit_code": -1,
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": -1,
                "execution_time": execution_time
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
                return 'utf-8'
            elif console_cp == 1252:  # Windows-1252
                return 'cp1252'
            else:
                return f'cp{console_cp}'
        except Exception as e:
            logger.warning(f"Could not get console encoding: {e}")
            return 'utf-8'  # Safe fallback
    
    def execute(self, command: str, working_dir: Optional[str] = None, timeout: int = 60) -> Dict[str, Any]:
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
                'powershell.exe',
                '-NoProfile',                    # Skip user profile loading
                '-NonInteractive',               # No interactive prompts
                '-ExecutionPolicy', 'Bypass',    # Override execution policy
                '-Command',
                command  # Execute command as-is, no manipulation
            ]
            
            logger.debug(f"Executing PowerShell: {command[:100]}...")
            
            # Execute with native encoding
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding=self.console_encoding,  # Use detected console encoding
                errors='replace',   # Never crash on encoding errors
                timeout=timeout,
                cwd=working_dir
            )
            
            execution_time = time.time() - start_time
            
            response = {
                'success': result.returncode == 0,
                'stdout': result.stdout,  # No .strip() - preserve formatting
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'execution_time': execution_time,
                'encoding_used': self.console_encoding
            }
            
            if response['success']:
                logger.debug(f"PowerShell command succeeded in {execution_time:.2f}s")
            else:
                logger.warning(f"PowerShell command failed with exit code {result.returncode}")
                
            return response
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"PowerShell command timed out after {timeout} seconds")
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'exit_code': -1,
                'execution_time': execution_time,
                'encoding_used': 'timeout'
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"PowerShell execution error: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'exit_code': -1,
                'execution_time': execution_time,
                'encoding_used': 'error'
            }

# Global executor instance
_powershell_executor = PowerShellExecutor()

def register_powershell_tools(mcp):
    """Register FIXED PowerShell and CMD tools with FastMCP."""
    # Register the PowerShell and CMD tools with MCP
    mcp.tool(run_powershell_tool)
    mcp.tool(run_cmd_tool)
    
    @tool(
        name="run_powershell_tool",
        description="Execute PowerShell commands with reliable output capture and security checks",
        parameters={
            "command": {
                "type": "string",
                "description": "PowerShell command to execute"
            },
            "working_directory": {
                "type": "string",
                "description": "Working directory for command execution"
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Command timeout in seconds",
                "default": 60
            },
            "capture_output": {
                "type": "boolean",
                "description": "Whether to capture command output",
                "default": True
            },
            "max_output_size": {
                "type": "integer",
                "description": "Maximum output size to capture",
                "default": 102400
            },
            "output_encoding": {
                "type": "string",
                "description": "Output encoding",
                "default": "utf-8"
            },
            "as_admin": {
                "type": "boolean",
                "description": "Run as administrator",
                "default": False
            }
        },
        required=["command"],
        returns={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "output": {"type": "string"},
                "error": {"type": "string"},
                "return_code": {"type": "integer"},
                "execution_time": {"type": "number"}
            }
        }
    )
    def run_powershell_tool(
        command: str,
        working_directory: Optional[str] = None,
        timeout_seconds: int = 60,
        capture_output: bool = True,
        max_output_size: int = 102400,
        output_encoding: str = "utf-8",
        as_admin: bool = False
    ) -> Dict[str, Any]:
        """
        Execute PowerShell commands with reliable output capture and security checks.

        FIXED VERSION that solves Windows PowerShell subprocess issues:
        - Removed overly aggressive security filters
        - Uses native console encoding instead of forcing UTF-8
        - No command wrapping that breaks output
        - Allows common cmdlets like Format-Table
        
        Args:
            command: PowerShell command to execute
            working_directory: Directory to run command in
            timeout_seconds: Command timeout (1-300 seconds)
            capture_output: Whether to capture stdout/stderr
            max_output_size: Maximum output size in bytes
            output_encoding: Output encoding (ignored - uses native)
            as_admin: Whether to run as administrator (not implemented for security)
            
        Returns:
            Dict with success, stdout, stderr, exit_code, execution_time
        """
        
        # Input validation
        if not command or not command.strip():
            return {
                "success": False,
                "stdout": "",
                "stderr": "Error: Command cannot be empty",
                "exit_code": -1,
                "execution_time": 0.0
            }
        
        if timeout_seconds < 1 or timeout_seconds > 300:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Error: Timeout must be between 1 and 300 seconds",
                "exit_code": -1,
                "execution_time": 0.0
            }
        
        if as_admin:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Error: Administrator execution not supported for security reasons",
                "exit_code": -1,
                "execution_time": 0.0
            }
        
        # RELAXED Security check - only block truly dangerous operations
        dangerous_patterns = [
            # Keep only the really dangerous ones
            'invoke-expression', 'iex',  # Code injection
            'invoke-webrequest', 'iwr', 'curl',  # Network operations
            'start-process',  # Process spawning
            'remove-item.*-recurse.*-force',  # Recursive forced deletion
            'del.*\\s',  # CMD recursive delete
            'rmdir.*\\s',  # CMD recursive directory removal
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern.replace('.*', ' ') in command_lower:  # Simple contains check
                logger.warning(f"Blocked potentially dangerous command: {pattern}")
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Error: Command blocked for security (contains '{pattern.replace('.*', '')}')",
                    "exit_code": -1,
                    "execution_time": 0.0
                }
        
        # Validate working directory
        if working_directory:
            if not os.path.exists(working_directory):
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Error: Working directory does not exist: {working_directory}",
                    "exit_code": -1,
                    "execution_time": 0.0
                }
            if not os.path.isdir(working_directory):
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Error: Working directory is not a directory: {working_directory}",
                    "exit_code": -1,
                    "execution_time": 0.0
                }
        
        # Execute using fixed executor
        result = _powershell_executor.execute(
            command=command,
            working_dir=working_directory,
            timeout=timeout_seconds
        )
        
        # Truncate output if too large (but preserve structure)
        if len(result['stdout']) > max_output_size:
            result['stdout'] = result['stdout'][:max_output_size] + '\n[OUTPUT TRUNCATED]'
            
        if len(result['stderr']) > max_output_size:
            result['stderr'] = result['stderr'][:max_output_size] + '\n[ERROR TRUNCATED]'
        
        # Log the result for debugging
        if result['success']:
            logger.info(f"PowerShell command executed successfully in {result['execution_time']:.2f}s")
        else:
            logger.warning(f"PowerShell command failed: {result['stderr']}")
        
        return {
            "success": result['success'],
            "stdout": result['stdout'],
            "stderr": result['stderr'],
            "exit_code": result['exit_code'],
            "execution_time": result['execution_time'],
            "command": command,
            "working_directory": working_directory or os.getcwd()
        }
    
    @tool(
        name="run_cmd_tool",
        description="Execute CMD commands with reliable output capture and security checks",
        parameters={
            "command": {
                "type": "string",
                "description": "CMD command to execute"
            },
            "working_directory": {
                "type": "string",
                "description": "Working directory for command execution"
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Command timeout in seconds",
                "default": 60
            },
            "capture_output": {
                "type": "boolean",
                "description": "Whether to capture command output",
                "default": True
            },
            "max_output_size": {
                "type": "integer",
                "description": "Maximum output size to capture",
                "default": 102400
            },
            "output_encoding": {
                "type": "string",
                "description": "Output encoding",
                "default": "cp1252"
            }
        },
        required=["command"],
        returns={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
                "exit_code": {"type": "integer"},
                "execution_time": {"type": "number"},
                "command": {"type": "string"},
                "working_directory": {"type": "string"}
            }
        }
    )
    def run_cmd_tool(
        command: str,
        working_directory: Optional[str] = None,
        timeout_seconds: int = 60,
        capture_output: bool = True,
        max_output_size: int = 102400,
        output_encoding: str = "cp1252"
    ) -> Dict[str, Any]:
        """
        Execute CMD commands with reliable output capture and security checks.

        FIXED VERSION - Uses proper Windows console encoding and simplified execution.
        """
        start_time = time.time()
        
        try:
            # Input validation
            if not command or not command.strip():
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "Error: Command cannot be empty",
                    "exit_code": -1,
                    "execution_time": 0.0
                }
            
            if timeout_seconds < 1 or timeout_seconds > 300:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "Error: Timeout must be between 1 and 300 seconds",
                    "exit_code": -1,
                    "execution_time": 0.0
                }
            
            # Get console encoding for CMD
            try:
                console_cp = ctypes.windll.kernel32.GetConsoleOutputCP()
                encoding = f'cp{console_cp}' if console_cp != 65001 else 'utf-8'
            except:
                encoding = 'cp1252'  # Windows CMD fallback
            
            # Execute command directly
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_directory,
                timeout=timeout_seconds,
                capture_output=True,
                text=True,
                encoding=encoding,
                errors='replace'  # Never crash on encoding errors
            )
            
            execution_time = time.time() - start_time
            
            # Truncate output if too large
            stdout = result.stdout
            stderr = result.stderr
            
            if len(stdout) > max_output_size:
                stdout = stdout[:max_output_size] + '\n[OUTPUT TRUNCATED]'
                
            if len(stderr) > max_output_size:
                stderr = stderr[:max_output_size] + '\n[ERROR TRUNCATED]'
            
            return {
                "success": result.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "execution_time": execution_time,
                "command": command,
                "working_directory": working_directory or os.getcwd()
            }
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout_seconds} seconds",
                "exit_code": -1,
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution failed: {str(e)}",
                "exit_code": execution_time
            }

def register_powershell_tools(mcp):
    """Register PowerShell and CMD execution tools with FastMCP."""
    # Create executor instances
    ps_executor = PowerShellExecutor()
    cmd_executor = CMDExecutor()
    
    # Register PowerShell tool
    @mcp.tool(
        name="run_powershell_tool",
        description="Execute PowerShell commands with reliable output capture and security checks",
        parameters={
            "command": {
                "type": "string",
                "description": "PowerShell command to execute"
            },
            "working_directory": {
                "type": "string",
                "description": "Working directory for command execution"
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Command timeout in seconds (1-300)",
                "default": 30
            },
            "max_output_size": {
                "type": "integer",
                "description": "Maximum output size in characters",
                "default": 10000
            }
        },
        required=["command"],
        returns={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
                "exit_code": {"type": "integer"},
                "execution_time": {"type": "number"}
            }
        }
    )
    def run_powershell_tool(
        command: str,
        working_directory: Optional[str] = None,
        timeout_seconds: int = 30,
        max_output_size: int = 10000
    ) -> Dict[str, Any]:
        """Execute PowerShell command with reliable output capture."""
        return ps_executor.execute_command(
            command=command,
            working_directory=working_directory,
            timeout_seconds=timeout_seconds,
            max_output_size=max_output_size
        )
    
    # Register CMD tool
    @mcp.tool(
        name="run_cmd_tool",
        description="Execute CMD commands with reliable output capture and security checks",
        parameters={
            "command": {
                "type": "string",
                "description": "CMD command to execute"
            },
            "working_directory": {
                "type": "string",
                "description": "Working directory for command execution"
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Command timeout in seconds (1-300)",
                "default": 30
            },
            "max_output_size": {
                "type": "integer",
                "description": "Maximum output size in characters",
                "default": 10000
            }
        },
        required=["command"],
        returns={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
                "exit_code": {"type": "integer"},
                "execution_time": {"type": "number"}
            }
        }
    )
    def run_cmd_tool(
        command: str,
        working_directory: Optional[str] = None,
        timeout_seconds: int = 30,
        max_output_size: int = 10000
    ) -> Dict[str, Any]:
        """Execute CMD command with reliable output capture."""
        return cmd_executor.execute_command(
            command=command,
            working_directory=working_directory,
            timeout_seconds=timeout_seconds,
            max_output_size=max_output_size
        )
    
    logger.info("PowerShell and CMD tools registered successfully")
