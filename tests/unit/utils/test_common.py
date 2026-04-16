import tempfile
import unittest

# Add the project root to Python path
from windows_operations_mcp.utils.common import get_execution_result


class TestCommonUtils(unittest.TestCase):
    """Test common utilities functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_execution_result(self):
        """Test get_execution_result function."""
        from windows_operations_mcp.utils.command_executor import ProcessOutput

        # Test with ProcessOutput object
        process_output = ProcessOutput(stdout="test output", stderr="", exit_code=0, execution_time=1.5)

        result = get_execution_result(process_output)

        self.assertTrue(result["success"])
        self.assertEqual(result["stdout"], "test output")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["execution_time"], 1.5)

        # Test with dictionary
        dict_input = {"stdout": "dict output", "stderr": "", "exit_code": 0, "execution_time": 2.0}

        result = get_execution_result(dict_input)

        self.assertTrue(result["success"])
        self.assertEqual(result["stdout"], "dict output")
        self.assertEqual(result["execution_time"], 2.0)

        # Test with invalid input
        result = get_execution_result("invalid_input")

        self.assertFalse(result["success"])
        self.assertIn("Unexpected output type", result["error"])


if __name__ == "__main__":
    unittest.main()
