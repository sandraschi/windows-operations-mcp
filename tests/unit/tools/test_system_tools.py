import unittest
import tempfile
import os
from pathlib import Path
import sys
import json

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.system_tools import (
    register_system_tools
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

class TestSystemTools(unittest.TestCase):
    """Test system tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_system_tools(self):
        """Test registering system tools with MCP."""
        register_system_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('get_system_info', self.mcp.tools)
        self.assertIn('health_check', self.mcp.tools)

    def test_get_system_info_basic(self):
        """Test basic system info retrieval."""
        register_system_tools(self.mcp)
        get_system_info_func = self.mcp.tools['get_system_info']

        result = get_system_info_func()

        self.assertTrue(result['success'])
        self.assertIn('system', result)

    def test_health_check_basic(self):
        """Test basic health check."""
        register_system_tools(self.mcp)
        health_check_func = self.mcp.tools['health_check']

        result = health_check_func()

        self.assertTrue(result['success'])
        self.assertIn('status', result)
        self.assertIn('checks', result)

    def test_get_system_info_detailed(self):
        """Test detailed system info."""
        register_system_tools(self.mcp)
        get_system_info_func = self.mcp.tools['get_system_info']

        result = get_system_info_func(detailed=True)

        self.assertTrue(result['success'])
        self.assertIn('system', result)

    def test_health_check_comprehensive(self):
        """Test comprehensive health check."""
        register_system_tools(self.mcp)
        health_check_func = self.mcp.tools['health_check']

        result = health_check_func(detailed=True)

        self.assertTrue(result['success'])
        self.assertIn('status', result)
        self.assertIn('checks', result)

    def test_system_tools_error_handling(self):
        """Test error handling in system tools."""
        register_system_tools(self.mcp)

        # Test with invalid parameters - should handle gracefully
        get_system_info_func = self.mcp.tools['get_system_info']
        result = get_system_info_func(invalid_param=True)

        # Should handle gracefully
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()