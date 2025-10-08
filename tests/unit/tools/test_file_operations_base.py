import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.file_operations.base import (
    validate_file_path,
    normalize_path,
    log_operation,
    handle_operation
)


class TestFileOperationsBase(unittest.TestCase):
    """Test file operations base utilities."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

        # Create test files
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("Test content for file operations")

        self.empty_file = os.path.join(self.test_dir, "empty.txt")
        with open(self.empty_file, 'w', encoding='utf-8') as f:
            f.write("")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_validate_file_path(self):
        """Test file path validation."""
        # Test valid file
        is_valid, error_msg = validate_file_path(self.test_file)
        self.assertTrue(is_valid)

        # Test invalid file
        is_valid, error_msg = validate_file_path("/nonexistent/file.txt")
        self.assertFalse(is_valid)

        # Test directory as file
        is_valid, error_msg = validate_file_path(self.test_dir)
        self.assertFalse(is_valid)

    def test_normalize_path(self):
        """Test path normalization."""
        normalized = normalize_path(self.test_file)
        self.assertIsInstance(normalized, Path)
        self.assertEqual(str(normalized), self.test_file)

    def test_log_operation_decorator(self):
        """Test log_operation decorator."""
        @log_operation("test_operation")
        def test_function():
            return {"result": "test"}

        result = test_function()
        self.assertEqual(result["result"], "test")

    def test_handle_operation_decorator(self):
        """Test handle_operation decorator."""
        @handle_operation("test_operation")
        def test_function():
            return {"result": "test"}

        result = test_function()
        self.assertEqual(result["result"], "test")

    def test_file_operations_edge_cases(self):
        """Test file operations with edge cases."""
        # Test with very long filename
        long_name = "a" * 200 + ".txt"
        long_file = os.path.join(self.test_dir, long_name)

        with open(long_file, 'w') as f:
            f.write("test")

        # Test path normalization with long filename
        normalized = normalize_path(long_file)
        self.assertIsInstance(normalized, Path)
        self.assertEqual(str(normalized), long_file)

        # Clean up
        os.remove(long_file)

    def test_file_operations_with_unicode(self):
        """Test file operations with Unicode content."""
        unicode_file = os.path.join(self.test_dir, "unicode.txt")
        unicode_content = "Hello 世界 🌍 café naïve"

        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write(unicode_content)

        # Test path validation with Unicode filename
        is_valid, error_msg = validate_file_path(unicode_file)
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main()
