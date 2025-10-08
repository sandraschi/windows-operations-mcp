import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
from windows_operations_mcp.utils.command_executor import (
    CommandExecutor,
    ProcessOutput
)


class TestCommandExecutor(unittest.TestCase):
    """Test command executor functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_command_executor_initialization(self):
        """Test CommandExecutor initialization."""
        executor = CommandExecutor()

        self.assertIsNotNone(executor)
        self.assertIsInstance(executor, CommandExecutor)

    def test_process_output_creation(self):
        """Test ProcessOutput creation."""
        result = ProcessOutput(
            stdout="test output",
            stderr="",
            exit_code=0,
            execution_time=1.0
        )

        self.assertEqual(result.stdout, "test output")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.execution_time, 1.0)

        # Test to_dict method
        result_dict = result.to_dict()
        self.assertTrue(result_dict['success'])
        self.assertEqual(result_dict['stdout'], "test output")

    def test_command_executor_simple_command(self):
        """Test executing a simple command."""
        result = CommandExecutor.execute_cmd("echo 'Hello, World!'")

        self.assertTrue(result['success'])
        self.assertIn("Hello, World!", result['stdout'])

    def test_command_executor_error_handling(self):
        """Test error handling in command execution."""
        # Test with non-existent command
        result = CommandExecutor.execute_cmd("nonexistent_command")

        self.assertFalse(result['success'])
        self.assertNotEqual(result['exit_code'], 0)


if __name__ == "__main__":
    unittest.main()