import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.windows_operations_mcp.mcp_server import mcp
from src.windows_operations_mcp.tools.help_tools import register_help_tools
from src.windows_operations_mcp.tools.system_tools import register_system_tools


class TestMCPServer(unittest.TestCase):
    """Test the MCP server core functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mcp_server_initialization(self):
        """Test that the MCP server initializes properly."""
        # This is a basic smoke test - the server should initialize without errors
        self.assertIsNotNone(mcp)

    def test_help_tools_registration(self):
        """Test that help tools can be registered."""
        # Register help tools
        register_help_tools(mcp)

        # The server should still be functional
        self.assertIsNotNone(mcp)

    def test_system_tools_registration(self):
        """Test that system tools can be registered."""
        # Register system tools
        register_system_tools(mcp)

        # The server should still be functional
        self.assertIsNotNone(mcp)

    def test_multiple_tool_registrations(self):
        """Test registering multiple tool sets."""
        # Register multiple tool sets
        register_help_tools(mcp)
        register_system_tools(mcp)

        # The server should still be functional
        self.assertIsNotNone(mcp)


if __name__ == "__main__":
    unittest.main()


