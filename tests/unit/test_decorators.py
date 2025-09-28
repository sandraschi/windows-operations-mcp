import unittest
import tempfile
import time
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.windows_operations_mcp.decorators import (
    tool,
    validate_inputs,
    rate_limited,
    log_execution,
    RateLimiter,
    is_positive_number,
    is_valid_path,
    is_valid_port,
    is_safe_command
)


class TestDecorators(unittest.TestCase):
    """Test decorator functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_tool_decorator(self):
        """Test tool decorator."""

        @tool(name="test_tool", description="Test tool function")
        def test_function():
            return {"result": "success"}

        result = test_function()
        self.assertEqual(result["result"], "success")
        self.assertIn("_metadata", result)
        self.assertTrue(result["_metadata"]["success"])

    def test_validate_inputs_decorator(self):
        """Test validate inputs decorator."""

        @validate_inputs(is_positive_number)
        def test_function(value):
            return {"result": value * 2}

        result = test_function(5)
        self.assertEqual(result["result"], 10)

    def test_rate_limited_decorator(self):
        """Test rate limited decorator."""

        @rate_limited(max_calls=2, time_window=60)
        def test_function():
            return {"result": "success"}

        result1 = test_function()
        self.assertEqual(result1["result"], "success")

        result2 = test_function()
        self.assertEqual(result2["result"], "success")

    def test_log_execution_decorator(self):
        """Test log execution decorator."""

        @log_execution("test_execution")
        def test_function():
            return {"result": "success"}

        result = test_function()
        self.assertEqual(result["result"], "success")

    def test_rate_limiter_class(self):
        """Test RateLimiter class functionality."""

        limiter = RateLimiter(max_calls=2, time_window=1)
        allowed, wait_time = limiter.is_allowed("test_key")
        self.assertTrue(allowed)
        self.assertEqual(wait_time, 0.0)

        # Should allow second call
        allowed, wait_time = limiter.is_allowed("test_key")
        self.assertTrue(allowed)

        # Should deny third call
        allowed, wait_time = limiter.is_allowed("test_key")
        self.assertFalse(allowed)
        self.assertGreater(wait_time, 0)

    def test_validator_functions(self):
        """Test validator functions."""

        # Test is_positive_number
        valid, msg = is_positive_number(5)
        self.assertTrue(valid)
        self.assertEqual(msg, "")

        valid, msg = is_positive_number(-1)
        self.assertFalse(valid)
        self.assertIn("positive", msg)

        valid, msg = is_positive_number("not_a_number")
        self.assertFalse(valid)
        self.assertIn("number", msg)

    def test_is_valid_path_validator(self):
        """Test is_valid_path validator."""

        # Test with current directory (should exist)
        valid, msg = is_valid_path(".", check_readable=True)
        self.assertTrue(valid)
        self.assertEqual(msg, "")

        # Test with non-existent path
        valid, msg = is_valid_path("/nonexistent/path")
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

    def test_is_valid_port_validator(self):
        """Test is_valid_port validator."""

        valid, msg = is_valid_port(80)
        self.assertTrue(valid)
        self.assertEqual(msg, "")

        valid, msg = is_valid_port(70000)
        self.assertFalse(valid)
        self.assertIn("65535", msg)

        valid, msg = is_valid_port("not_a_number")
        self.assertFalse(valid)
        self.assertIn("integer", msg)

    def test_is_safe_command_validator(self):
        """Test is_safe_command validator."""

        valid, msg = is_safe_command("ls -la")
        self.assertTrue(valid)
        self.assertEqual(msg, "")

        valid, msg = is_safe_command("rm -rf /")
        self.assertFalse(valid)
        self.assertIn("Dangerous command detected", msg)

        valid, msg = is_safe_command("echo hello; rm file")
        self.assertFalse(valid)
        self.assertIn("Command chaining is not allowed", msg)


if __name__ == "__main__":
    unittest.main()


