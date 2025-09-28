import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.media_register import register_media_tools


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
            # Called as @mcp.tool
            self.tools[func.__name__] = func
            return func


class TestMediaTools(unittest.TestCase):
    """Test media tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_media_tools(self):
        """Test registering media tools with MCP."""
        register_media_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('get_media_metadata', self.mcp.tools)
        self.assertIn('update_media_metadata', self.mcp.tools)

    def test_get_media_metadata_tool(self):
        """Test get_media_metadata tool functionality."""
        register_media_tools(self.mcp)
        get_media_metadata_func = self.mcp.tools['get_media_metadata']

        # Test with non-existent file
        result = get_media_metadata_func("/nonexistent/file.jpg")

        # Should handle gracefully
        self.assertIn('success', result)

    def test_update_media_metadata_tool(self):
        """Test update_media_metadata tool functionality."""
        register_media_tools(self.mcp)
        update_media_metadata_func = self.mcp.tools['update_media_metadata']

        # Test with non-existent file
        result = update_media_metadata_func("/nonexistent/file.jpg", {})

        # Should handle gracefully
        self.assertIn('success', result)

    def test_media_tools_error_handling(self):
        """Test error handling in media tools."""
        register_media_tools(self.mcp)

        # Test with invalid parameters
        get_media_metadata_func = self.mcp.tools['get_media_metadata']
        result = get_media_metadata_func("")

        # Should handle gracefully
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()
