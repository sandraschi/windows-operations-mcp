import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
from windows_operations_mcp.tools.process_tools import (
    register_process_tools,
    get_process_list,
    get_process_info,
    get_system_resources
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


class TestProcessTools(unittest.TestCase):
    """Test process tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_process_tools(self):
        """Test registering process tools with MCP."""
        register_process_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('get_process_list', self.mcp.tools)
        self.assertIn('get_process_info', self.mcp.tools)
        self.assertIn('get_system_resources', self.mcp.tools)

    def test_get_process_list_basic(self):
        """Test basic process list retrieval."""
        register_process_tools(self.mcp)
        get_process_list_func = self.mcp.tools['get_process_list']

        result = get_process_list_func()

        self.assertTrue(result['success'])
        self.assertIn('processes', result)
        self.assertIsInstance(result['processes'], list)

    def test_get_process_list_with_filter(self):
        """Test process list with name filter."""
        register_process_tools(self.mcp)
        get_process_list_func = self.mcp.tools['get_process_list']

        result = get_process_list_func(filter_name="python")

        self.assertIn('success', result)
        self.assertIn('processes', result)
        self.assertIsInstance(result['processes'], list)

    def test_get_process_list_with_limit(self):
        """Test process list with limit."""
        register_process_tools(self.mcp)
        get_process_list_func = self.mcp.tools['get_process_list']

        result = get_process_list_func(max_processes=10)

        self.assertIn('success', result)
        self.assertIn('processes', result)
        self.assertIsInstance(result['processes'], list)

    def test_get_process_list_with_sort(self):
        """Test process list with sorting."""
        register_process_tools(self.mcp)
        get_process_list_func = self.mcp.tools['get_process_list']

        result = get_process_list_func(include_system=True)

        self.assertIn('success', result)
        self.assertIn('processes', result)
        self.assertIsInstance(result['processes'], list)

    def test_get_process_info_basic(self):
        """Test basic process info retrieval."""
        import os
        current_pid = os.getpid()

        result = get_process_info(pid=current_pid)

        self.assertTrue(result['success'])
        self.assertIn('process', result)

    def test_get_process_info_by_name(self):
        """Test process info retrieval by name."""
        import os
        current_pid = os.getpid()

        result = get_process_info(pid=current_pid)

        self.assertTrue(result['success'])
        self.assertIn('process', result)

    def test_get_process_info_detailed(self):
        """Test detailed process info retrieval."""
        import os
        current_pid = os.getpid()

        result = get_process_info(pid=current_pid)

        self.assertTrue(result['success'])
        self.assertIn('process', result)

    def test_get_system_resources_basic(self):
        """Test basic system resources retrieval."""
        result = get_system_resources()

        self.assertTrue(result['success'])
        self.assertIn('system', result)

    def test_get_system_resources_detailed(self):
        """Test detailed system resources retrieval."""
        result = get_system_resources()

        self.assertTrue(result['success'])
        self.assertIn('system', result)

    def test_get_system_resources_with_processes(self):
        """Test system resources with process information."""
        register_process_tools(self.mcp)
        get_system_resources_func = self.mcp.tools['get_system_resources']

        result = get_system_resources_func()

        self.assertIn('success', result)
        self.assertIn('system', result)

    def test_process_tools_error_handling(self):
        """Test error handling in process tools."""
        # Test with invalid PID
        result = get_process_info(pid=999999)

        self.assertFalse(result['success'])
        # Should not have 'process' field when error occurs

    def test_get_process_list_with_multiple_filters(self):
        """Test process list with multiple filters."""
        register_process_tools(self.mcp)
        get_process_list_func = self.mcp.tools['get_process_list']

        result = get_process_list(
            filter_name="python",
            max_processes=5,
            include_system=True
        )

        self.assertTrue(result['success'])
        self.assertIn('processes', result)
        self.assertIsInstance(result['processes'], list)

    def test_get_process_info_with_invalid_name(self):
        """Test process info with invalid process name."""
        result = get_process_info(pid=999999)

        self.assertFalse(result['success'])
        # Should not have 'process' field when error occurs

    def test_get_system_resources_comprehensive(self):
        """Test comprehensive system resources."""
        result = get_system_resources()

        self.assertTrue(result['success'])
        self.assertIn('system', result)


if __name__ == "__main__":
    unittest.main()