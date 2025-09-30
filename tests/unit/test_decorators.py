import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.decorators import (
    tool,
    validate_inputs,
    rate_limited,
    log_execution,
    is_positive_number,
    is_valid_path,
    is_valid_port,
    is_safe_command
)
from src.windows_operations_mcp.logging_config import get_logger


class TestDecorators(unittest.TestCase):
    """Test decorator functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_tool_decorator(self):
        """Test @tool decorator."""
        @tool(
            name="test_tool",
            description="Test tool for decorator testing",
            parameters={
                "param1": {
                    "type": "string",
                    "description": "Test parameter"
                }
            },
            required=["param1"],
            returns={
                "type": "object",
                "properties": {
                    "result": {"type": "string"}
                }
            }
        )
        def test_function(param1: str):
            return {"result": f"Hello {param1}"}

        # Test that the decorator preserves function functionality
        result = test_function("World")
        self.assertEqual(result["result"], "Hello World")

    def test_validate_inputs_decorator(self):
        """Test @validate_inputs decorator."""
        @validate_inputs(is_positive_number)
        def test_validated_operation(param1: int):
            return {"result": param1}

        result = test_validated_operation(5)
        self.assertEqual(result["result"], 5)

    def test_rate_limited_decorator(self):
        """Test @rate_limited decorator."""
        @rate_limited(max_calls=60, time_window=60)
        def test_rate_limited_operation():
            return {"result": "rate_limited"}

        result = test_rate_limited_operation()
        self.assertEqual(result["result"], "rate_limited")

    def test_log_execution_decorator(self):
        """Test @log_execution decorator."""
        @log_execution()
        def test_execution_logged_operation():
            return {"result": "execution_logged"}

        result = test_execution_logged_operation()
        self.assertEqual(result["result"], "execution_logged")

    def test_validation_functions(self):
        """Test validation helper functions."""
        # Test is_positive_number
        valid, msg = is_positive_number(5)
        self.assertTrue(valid)
        
        valid, msg = is_positive_number(-1)
        self.assertFalse(valid)

        # Test is_valid_path
        valid, msg = is_valid_path(self.test_dir)
        self.assertTrue(valid)
        
        valid, msg = is_valid_path("/nonexistent/path")
        self.assertFalse(valid)

        # Test is_valid_port
        valid, msg = is_valid_port(8080)
        self.assertTrue(valid)
        
        valid, msg = is_valid_port(99999)
        self.assertFalse(valid)

        # Test is_safe_command
        valid, msg = is_safe_command("echo hello")
        self.assertTrue(valid)
        
        valid, msg = is_safe_command("rm -rf /")
        self.assertFalse(valid)

    def test_nested_decorators(self):
        """Test multiple decorators working together."""
        @tool(
            name="nested_test",
            description="Test nested decorators",
            parameters={},
            required=[],
            returns={"type": "object"}
        )
        @log_execution()
        def nested_test_function(param1: int):
            return {"success": True, "value": param1}

        result = nested_test_function(5)
        self.assertTrue(result["success"])
        self.assertEqual(result["value"], 5)


class TestLoggingConfig(unittest.TestCase):
    """Test logging configuration."""

    def test_get_logger(self):
        """Test logger creation."""
        logger = get_logger("test_module")
        self.assertIsNotNone(logger)

    def test_logger_functionality(self):
        """Test logger basic functionality."""
        logger = get_logger("test_module")
        
        # Test that logger can be called without errors
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

    def test_logger_with_context(self):
        """Test logger with structured context."""
        logger = get_logger("test_module")
        
        # Test structured logging
        logger.info("Test message", extra_data="test_value")
        logger.error("Test error", error_code=500)


if __name__ == "__main__":
    unittest.main()