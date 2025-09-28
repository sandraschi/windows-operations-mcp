import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.file_operations import register_file_operations


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, func=None, name=None, **kwargs):
        """Mock FastMCP tool decorator."""
        if func is None:
            # Called as @mcp.tool(name="...")
            def decorator(f):
                tool_name = name or f.__name__
                self.tools[tool_name] = f
                return f
            return decorator
        else:
            # Called as @mcp.tool or mcp.tool(func)
            self.tools[func.__name__] = func
            return func


class TestFileOperations(unittest.TestCase):
    """Test file operations tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_file_operations(self):
        """Test registering file operations tools with MCP."""
        register_file_operations(self.mcp)

        # Check that tools were registered (just check a few key ones)
        self.assertIn('read_file', self.mcp.tools)
        self.assertIn('write_file', self.mcp.tools)
        self.assertIn('copy_file', self.mcp.tools)
        self.assertIn('move_file', self.mcp.tools)
        self.assertIn('delete_file', self.mcp.tools)

    def test_read_file_tool(self):
        """Test read_file tool functionality."""
        register_file_operations(self.mcp)
        read_file_func = self.mcp.tools['read_file']

        # Create a test file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Hello, World!")

        result = read_file_func(str(test_file))

        # Check that the function executed without error (the actual return format may vary)
        self.assertIsNotNone(result)
        self.assertIn('content', result)
        self.assertEqual(result['content'], "Hello, World!")

    def test_write_file_tool(self):
        """Test write_file tool functionality."""
        register_file_operations(self.mcp)
        write_file_func = self.mcp.tools['write_file']

        test_file = Path(self.test_dir) / "new_file.txt"

        result = write_file_func(str(test_file), "Test content")

        # Check that the function executed without error (the actual return format may vary)
        self.assertIsNotNone(result)
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "Test content")

    def test_file_operations_error_handling(self):
        """Test error handling in file operations."""
        register_file_operations(self.mcp)

        # Test reading non-existent file
        read_file_func = self.mcp.tools['read_file']
        result = read_file_func("/nonexistent/file.txt")

        self.assertFalse(result['success'])
        self.assertIn('error', result)


if __name__ == "__main__":
    unittest.main()
