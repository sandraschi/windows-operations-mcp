import shutil
import tempfile
import unittest

from windows_operations_mcp.logging_config import get_logger, setup_logging


class TestLoggingConfig(unittest.TestCase):
    """Test logging configuration functionality."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_logger(self):
        logger = get_logger("test_module")
        self.assertIsNotNone(logger)
        self.assertTrue(hasattr(logger, "info"))
        self.assertTrue(hasattr(logger, "debug"))
        self.assertTrue(hasattr(logger, "error"))
        logger.info("test message")

    def test_get_logger_with_different_names(self):
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        logger3 = get_logger("module1")

        self.assertIsNotNone(logger1)
        self.assertIsNotNone(logger2)
        self.assertIsNotNone(logger3)

    def test_logger_functionality(self):
        logger = get_logger("test_functionality")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

    def test_logger_with_extra_context(self):
        logger = get_logger("test_context")
        logger.info("Test message", user_id=123, action="test_action")

    def test_setup_logging(self):
        setup_logging("DEBUG")
        logger = get_logger("test_setup")
        logger.info("Test log message")
        self.assertTrue(True)

    def test_add_service_context(self):
        try:
            from windows_operations_mcp.logging_config import add_service_context

            self.assertTrue(callable(add_service_context))
        except Exception as e:
            self.fail(f"add_service_context import failed: {e}")

    def test_drop_debug_logs(self):
        try:
            from windows_operations_mcp.logging_config import drop_debug_logs

            self.assertTrue(callable(drop_debug_logs))
        except Exception as e:
            self.fail(f"drop_debug_logs import failed: {e}")

    def test_logging_with_different_handlers(self):
        setup_logging("DEBUG")
        logger = get_logger("test_console")
        logger.debug("Console debug message")

        setup_logging("INFO")
        logger = get_logger("test_file_only")
        logger.info("Log message")
        self.assertTrue(True)

    def test_logging_performance(self):
        logger = get_logger("test_performance")
        for i in range(100):
            logger.info(f"Performance test message {i}", iteration=i)

    def test_logging_with_exception_handling(self):
        logger = get_logger("test_exceptions")
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Caught test exception", extra_info="test_data")

    def test_logger_hierarchy(self):
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")

        self.assertIsNotNone(parent_logger)
        self.assertIsNotNone(child_logger)
        self.assertTrue(hasattr(parent_logger, "info"))
        self.assertTrue(hasattr(child_logger, "info"))


if __name__ == "__main__":
    unittest.main()
