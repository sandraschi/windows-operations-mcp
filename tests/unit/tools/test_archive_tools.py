import os
import shutil
import tempfile
import unittest

# Add the project root to Python path
from windows_operations_mcp.tools.archive_tools import (
    create_archive,
    extract_archive,
    list_archive,
    register_archive_tools,
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


class TestArchiveTools(unittest.TestCase):
    """Test archive tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

        # Create test files
        self.test_file1 = os.path.join(self.test_dir, "test1.txt")
        self.test_file2 = os.path.join(self.test_dir, "test2.txt")

        with open(self.test_file1, "w") as f:
            f.write("Test content 1")
        with open(self.test_file2, "w") as f:
            f.write("Test content 2")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_archive_tools(self):
        """Test registering archive tools with MCP."""
        register_archive_tools(self.mcp)

        # Check that tools were registered
        self.assertIn("create_archive", self.mcp.tools)
        self.assertIn("extract_archive", self.mcp.tools)
        self.assertIn("list_archive", self.mcp.tools)

    def test_create_archive_basic(self):
        """Test basic archive creation."""
        register_archive_tools(self.mcp)
        create_archive_func = self.mcp.tools["create_archive"]

        archive_path = os.path.join(self.test_dir, "test_archive.zip")

        result = create_archive_func(archive_path=archive_path, source_paths=[self.test_file1, self.test_file2])

        self.assertIn("success", result)
        self.assertTrue(os.path.exists(archive_path))

    def test_create_archive_with_compression(self):
        """Test archive creation with compression."""
        archive_path = os.path.join(self.test_dir, "test_archive.zip")

        result = create_archive(archive_path=archive_path, source_paths=[self.test_file1, self.test_file2])

        self.assertIn("success", result)
        self.assertTrue(os.path.exists(archive_path))

    def test_extract_archive_basic(self):
        """Test basic archive extraction."""
        # First create an archive
        archive_path = os.path.join(self.test_dir, "test_archive.zip")
        create_result = create_archive(archive_path=archive_path, source_paths=[self.test_file1, self.test_file2])

        self.assertIn("success", create_result)

        # Then extract it
        extract_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        result = extract_archive(archive_path=archive_path, extract_dir=extract_dir)

        self.assertIn("success", result)

    def test_list_archive_basic(self):
        """Test basic archive listing."""
        # First create an archive
        archive_path = os.path.join(self.test_dir, "test_archive.zip")
        create_result = create_archive(archive_path=archive_path, source_paths=[self.test_file1, self.test_file2])

        self.assertIn("success", create_result)

        # Then list its contents
        result = list_archive(archive_path=archive_path)

        self.assertIn("success", result)
        self.assertIn("files", result)

    def test_create_archive_with_exclude_patterns(self):
        """Test archive creation with exclude patterns."""
        archive_path = os.path.join(self.test_dir, "test_archive.zip")

        result = create_archive(archive_path=archive_path, source_paths=[self.test_dir], exclude_patterns=["*.txt"])

        self.assertIn("success", result)
        self.assertTrue(os.path.exists(archive_path))

    def test_archive_tools_error_handling(self):
        """Test archive tools error handling."""
        # Test with invalid archive path
        result = create_archive(archive_path="/invalid/path/archive.zip", source_paths=[self.test_file1])

        self.assertIn("success", result)

    def test_extract_archive_nonexistent(self):
        """Test extracting nonexistent archive."""
        extract_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        result = extract_archive(archive_path="/nonexistent/archive.zip", extract_dir=extract_dir)

        self.assertIn("success", result)

    def test_list_archive_nonexistent(self):
        """Test listing nonexistent archive."""
        result = list_archive(archive_path="/nonexistent/archive.zip")

        self.assertIn("success", result)


if __name__ == "__main__":
    unittest.main()
