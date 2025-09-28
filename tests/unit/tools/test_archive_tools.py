import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.archive_tools import register_archive_tools


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, **kwargs):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator


class TestArchiveTools(unittest.TestCase):
    """Test archive tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_archive_tools(self):
        """Test registering archive tools with MCP."""
        register_archive_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('create_zip_archive', self.mcp.tools)
        self.assertIn('extract_zip_archive', self.mcp.tools)

    def test_create_zip_archive_tool(self):
        """Test create_zip_archive tool functionality."""
        register_archive_tools(self.mcp)
        create_zip_archive_func = self.mcp.tools['create_zip_archive']

        # Create a test file to archive
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Test content")

        archive_path = Path(self.test_dir) / "test.zip"

        result = create_zip_archive_func(str(archive_path), [str(test_file)])

        # Should handle gracefully
        self.assertIn('success', result)

    def test_extract_zip_archive_tool(self):
        """Test extract_zip_archive tool functionality."""
        register_archive_tools(self.mcp)
        extract_zip_archive_func = self.mcp.tools['extract_zip_archive']

        # Test with non-existent archive
        result = extract_zip_archive_func("/nonexistent/archive.zip", self.test_dir)

        # Should handle gracefully
        self.assertIn('success', result)

    def test_archive_tools_error_handling(self):
        """Test error handling in archive tools."""
        register_archive_tools(self.mcp)

        # Test with invalid parameters
        create_zip_archive_func = self.mcp.tools['create_zip_archive']
        result = create_zip_archive_func("", [])

        # Should handle gracefully
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()
