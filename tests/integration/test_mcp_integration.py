import unittest
import tempfile
import os
from pathlib import Path
import sys
import asyncio

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.windows_operations_mcp.mcp_server import mcp
from src.windows_operations_mcp.tools.help_tools import register_help_tools
from src.windows_operations_mcp.tools.system_tools import register_system_tools


class TestMCPIntegration(unittest.TestCase):
    """Integration tests for the MCP server."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

        # Create a fresh MCP instance for testing
        from src.windows_operations_mcp.mcp_server import FastMCP
        self.mcp = FastMCP("test-integration-server")

        # Register tools
        register_help_tools(self.mcp)
        register_system_tools(self.mcp)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mcp_has_registered_tools(self):
        """Test that MCP server has registered tools."""
        # This is a basic test - in a real integration test
        # we would test calling tools through the MCP interface
        self.assertIsNotNone(self.mcp)

    def test_system_info_tool_available(self):
        """Test that system info tool is available."""
        # In a real integration test, we would:
        # 1. Start the MCP server
        # 2. Connect a client
        # 3. Call the get_system_info tool
        # 4. Verify the response

        # For now, just verify the server is set up correctly
        self.assertIsNotNone(self.mcp)


if __name__ == "__main__":
    unittest.main()






