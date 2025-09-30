import unittest
import tempfile
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.help_tools import (
    register_help_tools
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

class TestHelpTools(unittest.TestCase):
    """Test help tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_help_tools(self):
        """Test registering help tools with MCP."""
        register_help_tools(self.mcp)

        # Check that get_help tool was registered
        self.assertIn('get_help', self.mcp.tools)

    def test_get_help_basic(self):
        """Test basic help retrieval."""
        register_help_tools(self.mcp)
        get_help_func = self.mcp.tools['get_help']

        result = get_help_func()

        self.assertEqual(result['status'], 'success')
        self.assertIn('message', result)

    def test_get_help_with_command(self):
        """Test help with specific command."""
        register_help_tools(self.mcp)
        get_help_func = self.mcp.tools['get_help']

        result = get_help_func(command="get_system_info")

        self.assertEqual(result['status'], 'success')
        self.assertIn('message', result)

    def test_get_help_with_category(self):
        """Test help for specific category."""
        register_help_tools(self.mcp)
        get_help_func = self.mcp.tools['get_help']

        result = get_help_func(category="system")

        self.assertEqual(result['status'], 'success')
        self.assertIn('message', result)

    def test_get_help_with_invalid_command(self):
        """Test help with invalid command."""
        register_help_tools(self.mcp)
        get_help_func = self.mcp.tools['get_help']

        result = get_help_func(command="nonexistent_command")

        self.assertEqual(result['status'], 'error')
        self.assertIn('not found', result['message'])


if __name__ == "__main__":
    unittest.main()


