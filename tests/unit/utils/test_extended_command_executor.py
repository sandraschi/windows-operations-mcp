import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.utils.extended_command_executor import ExtendedCommandExecutor


class TestExtendedCommandExecutor(unittest.TestCase):
    """Test extended command executor functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_execute_with_output_callback(self):
        """Test command execution with output callback."""
        output_lines = []

        def capture_output(line, stream_type):
            output_lines.append((line, stream_type))

        result = ExtendedCommandExecutor.execute_cmd(
            "echo test",
            output_callback=capture_output
        )

        self.assertTrue(result['success'])
        self.assertGreater(len(output_lines), 0)

    def test_execute_with_timeout(self):
        """Test command execution with timeout."""
        # Use a very short timeout for a long-running command
        result = ExtendedCommandExecutor.execute_cmd(
            "timeout 10",
            timeout_seconds=2
        )

        # Should timeout and fail
        self.assertFalse(result['success'])
        self.assertEqual(result['exit_code'], 1)

    def test_execute_with_custom_encoding(self):
        """Test command execution with custom encoding."""
        result = ExtendedCommandExecutor.execute_cmd(
            "echo hello",
            output_encoding='utf-8'
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['stdout'].strip(), "hello")

    def test_execute_with_max_output_size(self):
        """Test command execution with max output size."""
        # Create a command that would produce a lot of output
        result = ExtendedCommandExecutor.execute_cmd(
            "for i in {1..1000}; do echo $i; done",
            max_output_size=1000  # 1KB limit
        )

        self.assertTrue(result['success'])
        # Output should be truncated if it exceeds the limit
        if len(result['stdout']) > 1000:
            self.assertIn("... (truncated)", result['stdout'])

    def test_execute_with_working_directory_validation(self):
        """Test command execution with working directory validation."""
        result = ExtendedCommandExecutor.execute_cmd(
            "echo hello",
            working_directory=self.test_dir
        )

        self.assertTrue(result['success'])

    def test_execute_powershell_with_complex_command(self):
        """Test PowerShell execution with complex command."""
        result = ExtendedCommandExecutor.execute_powershell(
            "Write-Output 'Complex PowerShell command with special chars: @#$%^&*()'"
        )

        self.assertTrue(result['success'])
        self.assertIn("Complex PowerShell command", result['stdout'])

    def test_execute_with_environment_variables(self):
        """Test command execution with environment variables."""
        # Set environment variable
        env = os.environ.copy()
        env['TEST_VAR'] = 'test_value'

        result = ExtendedCommandExecutor.execute_cmd(
            "echo %TEST_VAR%",
            environment=env
        )

        self.assertTrue(result['success'])
        self.assertIn("test_value", result['stdout'])

    def test_execute_with_error_handling(self):
        """Test command execution error handling."""
        result = ExtendedCommandExecutor.execute_cmd(
            "nonexistent_command_xyz"
        )

        self.assertFalse(result['success'])
        self.assertNotEqual(result['exit_code'], 0)
        self.assertIn("not recognized", result['stderr'].lower())

    def test_execute_with_large_output(self):
        """Test command execution with large output."""
        # Generate some output
        result = ExtendedCommandExecutor.execute_cmd(
            "for i in {1..50}; do echo \"Line $i with some content\"; done"
        )

        self.assertTrue(result['success'])
        self.assertGreater(len(result['stdout']), 100)

    def test_execute_multiple_commands(self):
        """Test executing multiple commands."""
        # Test command chaining (if supported)
        result = ExtendedCommandExecutor.execute_cmd(
            "echo first && echo second"
        )

        self.assertTrue(result['success'])
        # Should contain both outputs
        self.assertIn("first", result['stdout'])
        self.assertIn("second", result['stdout'])


if __name__ == "__main__":
    unittest.main()






