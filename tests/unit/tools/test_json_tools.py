import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.json_register import register_json_tools


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


class TestJsonTools(unittest.TestCase):
    """Test JSON tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_json_tools(self):
        """Test registering JSON tools with MCP."""
        register_json_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('validate_json', self.mcp.tools)
        self.assertIn('format_json', self.mcp.tools)
        self.assertIn('minify_json', self.mcp.tools)

    def test_validate_json_tool(self):
        """Test validate_json tool functionality."""
        register_json_tools(self.mcp)
        validate_json_func = self.mcp.tools['validate_json']

        # Test with valid JSON
        valid_json = '{"name": "test", "value": 123}'
        result = validate_json_func(valid_json)

        self.assertIn('success', result)

        # Test with invalid JSON
        invalid_json = '{"name": "test", "value": }'
        result = validate_json_func(invalid_json)

        self.assertIn('success', result)

    def test_format_json_tool(self):
        """Test format_json tool functionality."""
        register_json_tools(self.mcp)
        format_json_func = self.mcp.tools['format_json']

        # Test with valid JSON
        json_content = '{"name":"test","value":123}'
        result = format_json_func(json_content)

        self.assertIn('success', result)

    def test_json_tools_error_handling(self):
        """Test error handling in JSON tools."""
        register_json_tools(self.mcp)

        # Test with invalid parameters
        validate_json_func = self.mcp.tools['validate_json']
        result = validate_json_func("")

        # Should handle gracefully
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()
