import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.file_operations.file_operations import (
    read_file,
    write_file,
    copy_file,
    move_file,
    delete_file
)


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, func=None, **kwargs):
        if func is not None:
            # Direct function registration: mcp.tool(function)
            self.tools[func.__name__] = func
            return func
        else:
            # Decorator pattern: @mcp.tool()
            def decorator(f):
                self.tools[f.__name__] = f
                return f
            return decorator


class TestFileOperations(unittest.TestCase):
    """Test file operations functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()
        
        # Create test file
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("Test content")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_file_operations(self):
        """Test registering file operations with MCP."""
        # Test that functions exist and are callable
        self.assertTrue(callable(read_file))
        self.assertTrue(callable(write_file))
        self.assertTrue(callable(copy_file))
        self.assertTrue(callable(move_file))
        self.assertTrue(callable(delete_file))

    def test_read_file_basic(self):
        """Test basic file reading."""
        result = read_file(path=self.test_file)

        self.assertIn('path', result)
        self.assertIn('content', result)
        self.assertIn('size', result)
        self.assertEqual(result['content'], "Test content")

    def test_write_file_basic(self):
        """Test basic file writing."""
        new_file = os.path.join(self.test_dir, "new_file.txt")
        result = write_file(
            path=new_file,
            content="New content"
        )

        self.assertIn('path', result)
        self.assertIn('size', result)
        self.assertIn('created', result)
        self.assertTrue(os.path.exists(new_file))

        # Verify content
        with open(new_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, "New content")

    def test_copy_file_basic(self):
        """Test basic file copying."""
        copy_path = os.path.join(self.test_dir, "copy.txt")
        result = copy_file(
            source=self.test_file,
            destination=copy_path
        )

        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(copy_path))

        # Verify content
        with open(copy_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, "Test content")

    def test_move_file_basic(self):
        """Test basic file moving."""
        move_path = os.path.join(self.test_dir, "moved.txt")
        result = move_file(
            source=self.test_file,
            destination=move_path
        )

        self.assertTrue(result['success'])
        self.assertFalse(os.path.exists(self.test_file))
        self.assertTrue(os.path.exists(move_path))

    def test_delete_file_basic(self):
        """Test basic file deletion."""
        result = delete_file(path=self.test_file)

        self.assertTrue(result['success'])
        self.assertFalse(os.path.exists(self.test_file))

    def test_read_file_nonexistent(self):
        """Test reading nonexistent file."""
        result = read_file(path="/nonexistent/file.txt")

        self.assertFalse(result['success'])

    def test_write_file_with_encoding(self):
        """Test file writing with encoding."""
        new_file = os.path.join(self.test_dir, "utf8_file.txt")
        result = write_file(
            path=new_file,
            content="UTF-8 content with émojis 🚀",
            encoding="utf-8"
        )

        self.assertIn('path', result)
        self.assertIn('size', result)
        self.assertIn('created', result)
        self.assertTrue(os.path.exists(new_file))

    def test_copy_file_overwrite(self):
        """Test file copying with overwrite."""
        # Create destination file first
        dest_file = os.path.join(self.test_dir, "destination.txt")
        write_file(path=dest_file, content="Original content")

        # Copy over it
        result = copy_file(
            source=self.test_file,
            destination=dest_file,
            overwrite=True
        )

        self.assertTrue(result['success'])

        # Verify content was overwritten
        with open(dest_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, "Test content")

    def test_file_operations_error_handling(self):
        """Test file operations error handling."""
        # Test deleting nonexistent file
        result = delete_file(path="/nonexistent/file.txt")

        self.assertFalse(result['success'])


if __name__ == "__main__":
    unittest.main()
