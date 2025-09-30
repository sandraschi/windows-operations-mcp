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

    def test_test_port_tool(self):
        """Test test_port tool functionality."""
        register_network_tools(self.mcp)
        test_port_func = self.mcp.tools['test_port']

        # Test with localhost (should be accessible)
        result = test_port_func("localhost", 80)

        self.assertIn('success', result)

    def test_network_tools_error_handling(self):
        """Test error handling in network tools."""
        register_network_tools(self.mcp)
        test_port_func = self.mcp.tools['test_port']

        # Test with invalid parameters - should handle gracefully
        result = test_port_func(host="invalid_host", port=99999)

        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()