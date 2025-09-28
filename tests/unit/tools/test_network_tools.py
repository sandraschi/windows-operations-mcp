import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.network_tools import register_network_tools


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, **kwargs):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator


class TestNetworkTools(unittest.TestCase):
    """Test network tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_network_tools(self):
        """Test registering network tools with MCP."""
        register_network_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('test_port', self.mcp.tools)
        self.assertIn('get_network_info', self.mcp.tools)

    def test_test_port_tool(self):
        """Test test_port tool functionality."""
        register_network_tools(self.mcp)
        test_port_func = self.mcp.tools['test_port']

        # Test with localhost (should be accessible)
        result = test_port_func("localhost", 80)

        self.assertIn('success', result)

    def test_get_network_info_tool(self):
        """Test get_network_info tool functionality."""
        register_network_tools(self.mcp)
        get_network_info_func = self.mcp.tools['get_network_info']

        result = get_network_info_func()

        self.assertIn('success', result)

    def test_network_tools_error_handling(self):
        """Test error handling in network tools."""
        register_network_tools(self.mcp)

        # Test with invalid hostname
        test_port_func = self.mcp.tools['test_port']
        result = test_port_func("invalid-hostname-that-does-not-exist", 80)

        # Should handle gracefully
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()