import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.git_tools import register_git_tools


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, **kwargs):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator


class TestGitTools(unittest.TestCase):
    """Test git tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_git_tools(self):
        """Test registering git tools with MCP."""
        register_git_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('git_status', self.mcp.tools)
        self.assertIn('git_log', self.mcp.tools)
        self.assertIn('git_add', self.mcp.tools)
        self.assertIn('git_commit', self.mcp.tools)

    def test_git_status_tool(self):
        """Test git_status tool functionality."""
        register_git_tools(self.mcp)
        git_status_func = self.mcp.tools['git_status']

        # Test in a directory that's not a git repo
        result = git_status_func()

        # Should handle gracefully
        self.assertIn('success', result)

    def test_git_tools_error_handling(self):
        """Test error handling in git tools."""
        register_git_tools(self.mcp)

        # Test with invalid parameters
        git_status_func = self.mcp.tools['git_status']
        result = git_status_func(invalid_param=True)

        # Should handle gracefully
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()
