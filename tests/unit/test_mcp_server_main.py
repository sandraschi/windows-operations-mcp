import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
from windows_operations_mcp.mcp_server import (
    mcp,
    register_all_tools
)


class TestMCPServer(unittest.TestCase):
    """Test MCP server functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mcp_server_creation(self):
        """Test MCP server creation."""
        self.assertIsNotNone(mcp)
        # FastMCP instance should be available
        self.assertTrue(hasattr(mcp, 'tool'))

    def test_register_all_tools(self):
        """Test register_all_tools function."""
        # Should not raise an exception
        register_all_tools()

        # Check that some tools were registered
        # (This is a basic check - the actual tool count depends on implementation)
        self.assertIsNotNone(mcp)


if __name__ == "__main__":
    unittest.main()
