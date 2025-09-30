import unittest
import tempfile
import os
import shutil
import logging
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.logging_config import (
    get_logger,
    setup_logging,
    add_service_context,
    drop_debug_logs
)


class TestLoggingConfig(unittest.TestCase):
    """Test logging configuration functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_logger(self):
        """Test logger creation."""
        logger = get_logger("test_module")
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, logging.Logger)

    def test_get_logger_with_different_names(self):
        """Test logger creation with different module names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        logger3 = get_logger("module1")  # Same name should return same logger

        self.assertIsNotNone(logger1)
        self.assertIsNotNone(logger2)
        self.assertIsNotNone(logger3)
        self.assertIs(logger1, logger3)  # Same name should return same instance

    def test_logger_functionality(self):
        """Test logger basic functionality."""
        logger = get_logger("test_functionality")

        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

    def test_logger_with_extra_context(self):
        """Test logger with extra context."""
        logger = get_logger("test_context")

        # Test structured logging with extra fields
        logger.info("Test message", user_id=123, action="test_action")

    def test_setup_logging(self):
        """Test logging setup."""
        log_file = os.path.join(self.test_dir, "test.log")

        # Test setup with file logging
        setup_logging(log_level="INFO", log_file=log_file)

        logger = get_logger("test_setup")
        logger.info("Test log message")

        # Check that log file was created and contains the message
        self.assertTrue(os.path.exists(log_file))

        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn("Test log message", content)

    def test_add_service_context(self):
        """Test adding service context."""
        logger = get_logger("test_context")
        # Test that service context can be added
        try:
            add_service_context(logger)
            self.assertTrue(True)  # Function exists and doesn't error
        except Exception as e:
            self.fail(f"add_service_context failed: {e}")

    def test_drop_debug_logs(self):
        """Test dropping debug logs."""
        # Test that debug logs can be dropped
        try:
            drop_debug_logs()
            self.assertTrue(True)  # Function exists and doesn't error
        except Exception as e:
            self.fail(f"drop_debug_logs failed: {e}")

    def test_logging_with_different_handlers(self):
        """Test logging with different handler configurations."""
        # Test console logging
        setup_logging(log_level="DEBUG", console=True, log_file=None)

        logger = get_logger("test_console")
        logger.debug("Console debug message")

        # Test file-only logging
        log_file = os.path.join(self.test_dir, "file_only.log")
        setup_logging(log_level="INFO", console=False, log_file=log_file)

        logger = get_logger("test_file_only")
        logger.info("File-only log message")

        self.assertTrue(os.path.exists(log_file))

    def test_logging_performance(self):
        """Test logging performance with many messages."""
        logger = get_logger("test_performance")

        # Log many messages quickly
        for i in range(100):
            logger.info(f"Performance test message {i}", iteration=i)

        # Should not raise any exceptions

    def test_logging_with_exception_handling(self):
        """Test logging with exception handling."""
        logger = get_logger("test_exceptions")

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            logger.exception("Caught test exception", extra_info="test_data")

    def test_logger_hierarchy(self):
        """Test logger hierarchy and propagation."""
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")

        # Both should be valid loggers
        self.assertIsNotNone(parent_logger)
        self.assertIsNotNone(child_logger)

        # Child should inherit from parent
        self.assertTrue(child_logger.name.startswith(parent_logger.name))


if __name__ == "__main__":
    unittest.main()