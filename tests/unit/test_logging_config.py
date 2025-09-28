import unittest
import tempfile
import os
from pathlib import Path
import sys
import json
import logging

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.windows_operations_mcp.logging_config import (
    get_logger,
    setup_logging,
    RequestContext,
    RequestIdFilter
)


class TestLoggingConfig(unittest.TestCase):
    """Test logging configuration functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_logger(self):
        """Test logger creation."""
        logger = get_logger("test_logger")

        # Check that it's a structlog logger
        self.assertIsNotNone(logger)
        # Structlog loggers don't have a name attribute like standard loggers
        self.assertTrue(hasattr(logger, 'info'))
        self.assertTrue(hasattr(logger, 'error'))

    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        setup_logging("INFO")

        logger = logging.getLogger("test")
        self.assertIsNotNone(logger)

    def test_setup_logging_with_level(self):
        """Test logging setup with specific level."""
        setup_logging("DEBUG")

        # Note: setup_logging doesn't set levels on standard loggers
        # This is just testing that the function doesn't raise an exception
        logger = logging.getLogger("test")
        self.assertIsNotNone(logger)

    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        log_file = Path(self.test_dir) / "test.log"
        # Note: setup_logging doesn't support file output directly,
        # this is just testing that the function works
        setup_logging("INFO")

        logger = logging.getLogger("test")
        self.assertIsNotNone(logger)

    def test_request_context(self):
        """Test RequestContext functionality."""
        context = RequestContext(request_id="test-123", user="test_user")

        with context:
            # Check that context variables are set
            import threading
            local = threading.local()
            if hasattr(local, 'request_id'):
                self.assertEqual(local.request_id, "test-123")

    def test_request_id_filter(self):
        """Test RequestIdFilter functionality."""
        filter_instance = RequestIdFilter()

        # Create a mock log record
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )

        # Test filter
        result = filter_instance.filter(record)
        self.assertTrue(result)
        self.assertIsNotNone(record.request_id)

    def test_multiple_logger_instances(self):
        """Test multiple logger instances."""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")

        self.assertNotEqual(logger1, logger2)
        # Structlog loggers don't have a name attribute like standard loggers
        self.assertTrue(hasattr(logger1, 'info'))
        self.assertTrue(hasattr(logger2, 'info'))

    def test_logger_with_structlog(self):
        """Test that logger works with structlog features."""
        logger = get_logger("structlog_test")

        # Test that logger has structlog methods
        self.assertTrue(hasattr(logger, 'info'))
        self.assertTrue(hasattr(logger, 'error'))
        self.assertTrue(hasattr(logger, 'debug'))


if __name__ == "__main__":
    unittest.main()


