import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
from windows_operations_mcp.mcp_server import register_all_tools
from windows_operations_mcp.__init__ import __version__


class TestMCPServer(unittest.TestCase):
    """Test MCP server functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mcp_server_creation(self):
        """Test MCP server creation."""
        # Test that register_all_tools can be called
        try:
            register_all_tools()
            self.assertTrue(True)  # Function exists and can be called
        except Exception as e:
            self.fail(f"register_all_tools failed: {e}")

    def test_mcp_server_initialization(self):
        """Test MCP server initialization."""
        # Test that register_all_tools function exists
        self.assertTrue(callable(register_all_tools))

    def test_version_constant(self):
        """Test version constant is defined."""
        self.assertIsNotNone(__version__)
        self.assertIsInstance(__version__, str)


class TestMainModule(unittest.TestCase):
    """Test main module functionality."""

    def test_main_import(self):
        """Test main module can be imported."""
        try:
            from windows_operations_mcp import main
            self.assertTrue(True)  # Import successful
        except ImportError:
            self.fail("Main module import failed")


if __name__ == "__main__":
    unittest.main()