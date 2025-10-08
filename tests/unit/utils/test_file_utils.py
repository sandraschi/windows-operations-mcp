import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
from windows_operations_mcp.utils.file_utils import (
    create_temp_file,
    safe_cleanup_file,
    validate_directory
)


class TestFileUtils(unittest.TestCase):
    """Test file utilities functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_temp_file(self):
        """Test create_temp_file function."""
        # Test creating temp file without content
        temp_path = create_temp_file(".txt")
        self.assertTrue(os.path.exists(temp_path))

        # Clean up
        os.unlink(temp_path)

        # Test creating temp file with content
        test_content = b"Hello, World!"
        temp_path = create_temp_file(".txt", test_content)
        self.assertTrue(os.path.exists(temp_path))

        with open(temp_path, 'rb') as f:
            content = f.read()
        self.assertEqual(content, test_content)

        # Clean up
        os.unlink(temp_path)

    def test_safe_cleanup_file(self):
        """Test safe_cleanup_file function."""
        # Test with existing file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("test content")

        result = safe_cleanup_file(str(test_file))
        self.assertTrue(result)
        self.assertFalse(test_file.exists())

        # Test with non-existent file
        result = safe_cleanup_file(str(test_file))
        self.assertTrue(result)

    def test_validate_directory(self):
        """Test validate_directory function."""
        # Test with valid directory
        valid, msg = validate_directory(self.test_dir)
        self.assertTrue(valid)
        self.assertEqual(msg, "")

        # Test with non-existent directory
        valid, msg = validate_directory("/nonexistent/directory")
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

        # Test with file instead of directory
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("test")
        valid, msg = validate_directory(str(test_file))
        self.assertFalse(valid)
        self.assertIn("not a directory", msg)


if __name__ == "__main__":
    unittest.main()