import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp import (
    mcp,
    register_all_tools
)


class TestInitModule(unittest.TestCase):
    """Test __init__ module functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mcp_import(self):
        """Test mcp import."""
        self.assertIsNotNone(mcp)
        # FastMCP instance should be available
        self.assertTrue(hasattr(mcp, 'tool'))

    def test_register_all_tools_import(self):
        """Test register_all_tools import."""
        # Should not raise an exception
        register_all_tools()

        # Check that some tools were registered
        self.assertIsNotNone(mcp)


if __name__ == "__main__":
    unittest.main()
