import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.utils.command_executor import (
    CommandExecutor,
    ProcessOutput
)
from src.windows_operations_mcp.utils.file_utils import (
    create_temp_file,
    safe_cleanup_file,
    validate_directory
)
from src.windows_operations_mcp.utils.common import (
    get_execution_result
)


class TestCommandExecutor(unittest.TestCase):
    """Test CommandExecutor functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.executor = CommandExecutor()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_cmd_execution_success(self):
        """Test successful CMD execution."""
        result = self.executor.execute_cmd("echo Hello World")
        
        self.assertTrue(result['success'])
        self.assertIn("Hello World", result['stdout'])
        self.assertEqual(result['exit_code'], 0)

    def test_cmd_execution_failure(self):
        """Test CMD execution failure."""
        result = self.executor.execute_cmd("nonexistent_command_12345")
        
        self.assertFalse(result['success'])
        self.assertNotEqual(result['exit_code'], 0)
        self.assertIn("not recognized", result['stderr'].lower())

    def test_powershell_execution_success(self):
        """Test successful PowerShell execution."""
        result = self.executor.execute_powershell("Write-Output 'Hello PowerShell'")
        
        self.assertTrue(result['success'])
        self.assertIn("Hello PowerShell", result['stdout'])
        self.assertEqual(result['exit_code'], 0)

    def test_powershell_execution_failure(self):
        """Test PowerShell execution failure."""
        result = self.executor.execute_powershell("Invalid-PowerShell-Command-12345")
        
        self.assertFalse(result['success'])
        self.assertNotEqual(result['exit_code'], 0)

    def test_execution_with_working_directory(self):
        """Test command execution with working directory."""
        result = self.executor.execute_cmd("cd", working_directory=self.test_dir)
        
        self.assertTrue(result['success'])
        self.assertIn(self.test_dir, result['stdout'])

    def test_execution_with_timeout(self):
        """Test command execution with timeout."""
        result = self.executor.execute_cmd("echo timeout_test", timeout=5)
        
        self.assertTrue(result['success'])

    def test_process_output_to_dict(self):
        """Test ProcessOutput to_dict conversion."""
        output = ProcessOutput(
            stdout="test output",
            stderr="",
            exit_code=0,
            execution_time=1.5
        )
        
        result_dict = output.to_dict()
        
        self.assertEqual(result_dict["stdout"], "test output")
        self.assertEqual(result_dict["exit_code"], 0)
        self.assertEqual(result_dict["execution_time"], 1.5)
        self.assertTrue(result_dict["success"])


class TestFileUtils(unittest.TestCase):
    """Test file utilities functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_temp_file(self):
        """Test temporary file creation."""
        temp_file = create_temp_file(suffix=".txt", content=b"test_content")

        self.assertTrue(os.path.exists(temp_file))

        with open(temp_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, "test_content")

        # Clean up
        safe_cleanup_file(temp_file)

    def test_safe_cleanup_file(self):
        """Test safe file cleanup."""
        temp_file = create_temp_file(suffix=".txt", content=b"test_content")

        self.assertTrue(os.path.exists(temp_file))

        safe_cleanup_file(temp_file)

        self.assertFalse(os.path.exists(temp_file))

    def test_safe_cleanup_nonexistent_file(self):
        """Test safe cleanup of nonexistent file."""
        # Should not raise an exception
        safe_cleanup_file("/nonexistent/file.txt")

    def test_validate_directory(self):
        """Test directory validation."""
        # Test valid directory
        result = validate_directory(self.test_dir)
        self.assertTrue(result[0])  # Returns (bool, str) tuple
        
        # Test nonexistent directory
        result = validate_directory("/nonexistent/directory")
        self.assertFalse(result[0])  # Returns (bool, str) tuple

    def test_validate_directory_with_creation(self):
        """Test directory validation with creation."""
        new_dir = os.path.join(self.test_dir, "new_subdir")
        
        # validate_directory doesn't have create parameter, so just test normal validation
        result = validate_directory(new_dir)
        self.assertFalse(result[0])  # Directory doesn't exist yet


class TestCommonUtils(unittest.TestCase):
    """Test common utilities functionality."""

    def test_get_execution_result_with_process_output(self):
        """Test get_execution_result with ProcessOutput."""
        from src.windows_operations_mcp.utils.command_executor import ProcessOutput
        
        process_output = ProcessOutput(
            stdout="test output",
            stderr="",
            exit_code=0,
            execution_time=1.5
        )

        result = get_execution_result(process_output)

        self.assertTrue(result['success'])
        self.assertEqual(result['stdout'], "test output")
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['execution_time'], 1.5)

    def test_get_execution_result_with_dict(self):
        """Test get_execution_result with dictionary."""
        dict_input = {
            'stdout': 'dict output',
            'stderr': '',
            'exit_code': 0,
            'execution_time': 2.0
        }

        result = get_execution_result(dict_input)

        self.assertTrue(result['success'])
        self.assertEqual(result['stdout'], "dict output")
        self.assertEqual(result['execution_time'], 2.0)

    def test_get_execution_result_with_invalid_input(self):
        """Test get_execution_result with invalid input."""
        result = get_execution_result("invalid_input")

        self.assertFalse(result['success'])
        self.assertIn('Unexpected output type', result['error'])

    def test_get_execution_result_with_error(self):
        """Test get_execution_result with error."""
        dict_input = {
            'stdout': '',
            'stderr': 'Error occurred',
            'exit_code': 1,
            'execution_time': 0.5,
            'error': 'Test error'
        }

        result = get_execution_result(dict_input)

        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Test error')
        self.assertEqual(result['exit_code'], 1)


if __name__ == "__main__":
    unittest.main()
