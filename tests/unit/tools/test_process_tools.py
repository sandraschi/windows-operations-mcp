import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.process_tools import register_process_tools


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, **kwargs):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator


class TestProcessTools(unittest.TestCase):
    """Test process tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_process_tools(self):
        """Test registering process tools with MCP."""
        register_process_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('get_process_list', self.mcp.tools)
        self.assertIn('get_process_info', self.mcp.tools)
        self.assertIn('get_system_resources', self.mcp.tools)

    def test_get_process_list_tool(self):
        """Test get_process_list tool functionality."""
        register_process_tools(self.mcp)
        get_process_list_func = self.mcp.tools['get_process_list']

        result = get_process_list_func()

        self.assertTrue(result['success'])
        self.assertIn('processes', result)

    def test_get_process_info_tool(self):
        """Test get_process_info tool functionality."""
        register_process_tools(self.mcp)
        get_process_info_func = self.mcp.tools['get_process_info']

        # Test with current process
        result = get_process_info_func(os.getpid())

        self.assertTrue(result['success'])
        self.assertIn('process', result)

    def test_get_system_resources_tool(self):
        """Test get_system_resources tool functionality."""
        register_process_tools(self.mcp)
        get_system_resources_func = self.mcp.tools['get_system_resources']

        result = get_system_resources_func()

        self.assertTrue(result['success'])
        self.assertIn('resources', result)

    def test_process_tools_error_handling(self):
        """Test error handling in process tools."""
        register_process_tools(self.mcp)

        # Test with invalid PID
        get_process_info_func = self.mcp.tools['get_process_info']
        result = get_process_info_func(999999)

        # Should handle gracefully
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()
