import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.powershell_tools import register_powershell_tools


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, **kwargs):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator


class TestPowerShellTools(unittest.TestCase):
    """Test PowerShell tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_powershell_tools(self):
        """Test registering PowerShell tools with MCP."""
        register_powershell_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('run_powershell_tool', self.mcp.tools)
        self.assertIn('run_cmd_tool', self.mcp.tools)

    def test_run_powershell_tool(self):
        """Test run_powershell_tool functionality."""
        register_powershell_tools(self.mcp)
        run_powershell_func = self.mcp.tools['run_powershell_tool']

        # Test simple command
        result = run_powershell_func("echo 'Hello, World!'")

        self.assertTrue(result['success'])
        self.assertIn('output', result)

    def test_run_cmd_tool(self):
        """Test run_cmd_tool functionality."""
        register_powershell_tools(self.mcp)
        run_cmd_func = self.mcp.tools['run_cmd_tool']

        # Test simple command
        result = run_cmd_func("echo Hello, World!")

        self.assertTrue(result['success'])
        self.assertIn('output', result)

    def test_powershell_tools_error_handling(self):
        """Test error handling in PowerShell tools."""
        register_powershell_tools(self.mcp)

        # Test invalid PowerShell command
        run_powershell_func = self.mcp.tools['run_powershell_tool']
        result = run_powershell_func("invalid-command-that-does-not-exist")

        # Should handle gracefully
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()
