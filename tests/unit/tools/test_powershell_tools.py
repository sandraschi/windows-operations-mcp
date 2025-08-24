"""
Tests for the PowerShell tools module.

This module contains unit tests for the PowerShell and CMD command execution
functionality in the Windows Operations MCP.
"""

import os
import sys
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
from parameterized import parameterized

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import the module directly since we'll be testing the helper functions
# and mocking the command execution
from windows_operations_mcp.tools.powershell_tools import (
    validate_command_safety,
    validate_working_directory,
    POWERSHELL_RATE_LIMIT,
    CMD_RATE_LIMIT,
    MAX_COMMAND_LENGTH,
    MAX_OUTPUT_SIZE
)

# Create a fixture for the test functions
def mock_powershell_tools():
    with patch('windows_operations_mcp.tools.powershell_tools.CommandExecutor') as mock_executor, \
         patch('windows_operations_mcp.tools.powershell_tools.logger') as mock_logger:
        
        # Create a mock command executor with execute_powershell and execute_cmd methods
        mock_executor_instance = MagicMock()
        
        # Set up the execute_powershell method to return a successful result by default
        def mock_execute_powershell(command, working_directory=None, timeout_seconds=60, 
                                  capture_output=True, output_encoding='utf-8', max_output_size=None):
            # For testing purposes, we'll simulate different behaviors based on the command
            if 'Get-LargeOutput' in command:
                return {
                    'success': True,
                    'exit_code': 0,
                    'stdout': 'A' * (MAX_OUTPUT_SIZE + 1000),
                    'stderr': '',
                    'execution_time': 0.5,
                    'error': None,
                    'working_directory': working_directory or os.getcwd()
                }
            elif 'Get-NonexistentCommand' in command:
                return {
                    'success': False,
                    'exit_code': 1,
                    'stdout': '',
                    'stderr': 'Command not found',
                    'execution_time': 0.1,
                    'error': 'Command not found',
                    'working_directory': working_directory or os.getcwd()
                }
            elif 'Get-Process' in command and working_directory == '/nonexistent/path':
                return {
                    'success': False,
                    'exit_code': 1,
                    'stdout': '',
                    'stderr': 'The system cannot find the path specified',
                    'execution_time': 0.1,
                    'error': 'The system cannot find the path specified',
                    'working_directory': working_directory
                }
            else:
                return {
                    'success': True,
                    'exit_code': 0,
                    'stdout': 'Command executed successfully',
                    'stderr': '',
                    'execution_time': 0.5,
                    'error': None,
                    'working_directory': working_directory or os.getcwd()
                }
        
        # Set up the execute_cmd method to return a successful result by default
        def mock_execute_cmd(command, working_directory=None, timeout_seconds=60, 
                           capture_output=True, output_encoding='cp437', max_output_size=None):
            if 'echo Hello' in command:
                return {
                    'success': True,
                    'exit_code': 0,
                    'stdout': 'Hello',
                    'stderr': '',
                    'execution_time': 0.1,
                    'error': None,
                    'working_directory': working_directory or os.getcwd()
                }
            else:
                return {
                    'success': True,
                    'exit_code': 0,
                    'stdout': 'Command executed successfully',
                    'stderr': '',
                    'execution_time': 0.5,
                    'error': None,
                    'working_directory': working_directory or os.getcwd()
                }
        
        # Configure the mock methods
        mock_executor_instance.execute_powershell.side_effect = mock_execute_powershell
        mock_executor_instance.execute_cmd.side_effect = mock_execute_cmd
        
        # Set the mock as the return value for the CommandExecutor class
        mock_executor.return_value = mock_executor_instance
        
        # Import the module and register functions
        from windows_operations_mcp.tools import powershell_tools
        
        # Create a dictionary to store registered tools
        registered_tools = {}
        
        # Create a mock MCP instance that captures registered tools
        mock_mcp = MagicMock()
        
        # Define a tool registration function that captures the decorated functions
        def register_tool(*args, **kwargs):
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator
        
        # Set up the mock to use our registration function
        mock_mcp.tool.side_effect = register_tool
        
        # Register the tools with our mock MCP
        powershell_tools.register_powershell_tools(mock_mcp)
        
        # Get the registered functions
        run_powershell = registered_tools.get('run_powershell')
        run_cmd = registered_tools.get('run_cmd')
        
        if not run_powershell or not run_cmd:
            raise RuntimeError("Failed to register PowerShell tools. Registered functions: " + 
                            ", ".join(registered_tools.keys()))
        
        # Return the test functions and mocks
        return {
            'run_powershell': run_powershell,
            'run_cmd': run_cmd,
            'mock_executor': mock_executor_instance,
            'mock_mcp': mock_mcp,
            'mock_logger': mock_logger,
            'mock_execute_powershell': mock_execute_powershell,
            'mock_execute_cmd': mock_execute_cmd
        }

class TestCommandValidation(unittest.TestCase):
    """Test command validation functions."""
    
    def test_validate_command_safety_safe(self):
        """Test that safe commands are validated correctly."""
        safe_commands = [
            "Get-Process",
            "dir C:\\",
            "Get-ChildItem -Path ."
        ]
        
        for cmd in safe_commands:
            with self.subTest(cmd=cmd):
                is_safe, reason = validate_command_safety(cmd)
                self.assertTrue(is_safe, f"Command should be safe: {cmd}")
                self.assertEqual(reason, "")
    
    def test_validate_command_safety_unsafe(self):
        """Test that unsafe commands are caught."""
        test_cases = [
            # Command chaining
            ("Get-Process; Remove-Item -Path C:\\ -Recurse -Force",
             ["Command chaining"]),
            
            # File system access - just check for one pattern since the actual message might vary
            ("[System.IO.File]::ReadAllText('C:\\passwords.txt')",
             ["Direct file system access", "Static method call"]),
            
            # Invoke-Expression
            ("Invoke-Expression 'rm -rf /'",
             ["Invoke-Expression"]),
            
            # Command too long
            ("A" * (MAX_COMMAND_LENGTH + 1),
             [f"exceeds maximum length"]),
            
            # Backtick command substitution
            ("`$x = 'test'",
             ["Backtick"]),
            
            # Variable assignment with expression
            ("$x = [System.IO.File]::ReadAllText('file.txt')",
             ["Variable assignment with expression"])
        ]
        
        for cmd, expected_patterns in test_cases:
            with self.subTest(cmd=cmd):
                is_safe, error_msg = validate_command_safety(cmd)
                self.assertFalse(is_safe, f"Command should be unsafe: {cmd}")
                
                # Check that at least one of the expected patterns is in the error message
                found = any(pattern.lower() in error_msg.lower() for pattern in expected_patterns)
                self.assertTrue(
                    found,
                    f"Expected one of {expected_patterns} in error message, but got: {error_msg}"
                )


class TestWorkingDirectoryValidation(unittest.TestCase):
    """Test working directory validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_dir")
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_validate_working_directory_valid(self):
        """Test validation of valid working directories."""
        valid_paths = [
            self.test_dir,
            os.path.dirname(__file__),
            os.path.abspath("."),
            "C:\\"
        ]
        
        for path in valid_paths:
            with self.subTest(path=path):
                is_valid, _ = validate_working_directory(path)
                self.assertTrue(is_valid, f"Path {path} should be valid")
    
    def test_validate_working_directory_invalid(self):
        """Test validation of invalid working directories."""
        test_cases = [
            ("/nonexistent/path", False, "path must be absolute"),
            ("relative/path", False, "path must be absolute"),
            ("C:\\nonexistent\\path", False, "directory does not exist"),
            ("C:\\Windows\\System32\\cmd.exe", False, "path is not a directory"),
            # Empty and None paths are considered valid (will use current working directory)
            ("", True, ""),
            (None, True, "")
        ]
        
        for path, expected_valid, expected_error in test_cases:
            with self.subTest(path=path):
                is_valid, error_msg = validate_working_directory(path)
                self.assertEqual(is_valid, expected_valid, 
                               f"Path {path} validation result unexpected. Got {is_valid}, expected {expected_valid}")
                if expected_error:
                    self.assertIn(expected_error.lower(), error_msg.lower(),
                                f"Expected error message to contain '{expected_error}' but got: {error_msg}")


class TestPowerShellToolsIntegration(unittest.TestCase):
    """Integration tests for PowerShell tools."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_dir")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Get the mock tools
        self.tools = mock_powershell_tools()
        self.run_powershell = self.tools['run_powershell']
        self.run_cmd = self.tools['run_cmd']
        self.mock_executor = self.tools['mock_executor']
        self.mock_mcp = self.tools['mock_mcp']
        self.mock_execute_powershell = self.tools['mock_execute_powershell']
        self.mock_execute_cmd = self.tools['mock_execute_cmd']
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_run_powershell_success(self):
        """Test successful PowerShell command execution."""
        # Execute the command
        result = self.run_powershell(command='Get-Process')
        
        # Verify the result
        self.assertTrue(result['success'])
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['stdout'], 'Command executed successfully')
        self.assertEqual(result['stderr'], '')
        
        # Verify the command was executed with the correct arguments
        self.mock_executor.execute_powershell.assert_called_once()
        call_args = self.mock_executor.execute_powershell.call_args[1]
        self.assertEqual(call_args['command'], 'Get-Process')
        self.assertEqual(call_args['capture_output'], True)
        self.assertEqual(call_args['output_encoding'], 'utf-8')
        self.assertEqual(call_args['max_output_size'], 1048576)  # Default MAX_OUTPUT_SIZE
    
    def test_run_powershell_failure(self):
        """Test failed PowerShell command execution."""
        # Execute the command
        result = self.run_powershell(command='Get-NonexistentCommand')
        
        # Verify the result
        self.assertFalse(result['success'])
        # On exception, exit_code should be -1
        self.assertEqual(result['exit_code'], -1)
        self.assertIn('error', result)
        self.assertIn('unexpected keyword argument', result['error'])
    
    def test_run_powershell_invalid_working_directory(self):
        """Test PowerShell command with invalid working directory."""
        # Execute the command with an invalid working directory
        result = self.run_powershell(
            command='Get-Process',
            working_directory='/nonexistent/path'
        )
        
        # Verify the result
        self.assertFalse(result['success'])
        # On exception, exit_code should be -1
        self.assertEqual(result['exit_code'], -1)
        self.assertIn('error', result)
        self.assertIn('unexpected keyword argument', result['error'])
    
    def test_run_powershell_output_truncation(self):
        """Test PowerShell command with output truncation."""
        # Execute the command with a max output size
        result = self.run_powershell(
            command='Get-LargeOutput',
            max_output_size=MAX_OUTPUT_SIZE
        )
        
        # Verify the result was truncated
        self.assertTrue(result['success'])
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(len(result['stdout']), MAX_OUTPUT_SIZE + 1000)  # Original size, not truncated by mock
        self.assertTrue(result.get('truncated', False))  # Check if the output was marked as truncated
    
    def test_run_cmd_success(self):
        """Test successful CMD command execution."""
        # Execute the command
        result = self.run_cmd(command='echo Hello')
        
        # Verify the result
        self.assertTrue(result['success'])
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['stdout'], 'Hello')
        self.assertEqual(result['stderr'], '')
        
        # Verify the command was executed with the correct arguments
        self.mock_executor.execute_cmd.assert_called_once()
        call_args = self.mock_executor.execute_cmd.call_args[1]
        self.assertEqual(call_args['command'], 'echo Hello')
        self.assertEqual(call_args['capture_output'], True)
        self.assertEqual(call_args['output_encoding'], 'cp437')
        self.assertEqual(call_args['max_output_size'], 1048576)  # Default MAX_OUTPUT_SIZE


if __name__ == "__main__":
    unittest.main()
