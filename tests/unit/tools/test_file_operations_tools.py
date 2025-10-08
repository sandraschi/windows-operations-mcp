import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
from windows_operations_mcp.tools.file_operations import register_file_operations


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, func=None, **kwargs):
        if func is not None:
            # Direct function registration: mcp.tool(function, name="custom_name")
            tool_name = kwargs.get('name', func.__name__)
            self.tools[tool_name] = func
            return func
        else:
            # Decorator pattern: @mcp.tool()
            def decorator(f):
                tool_name = kwargs.get('name', f.__name__)
                self.tools[tool_name] = f
                return f
            return decorator


class TestFileOperationsTools(unittest.TestCase):
    """Test file operations tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

        # Create test files
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("Test content")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_file_operations(self):
        """Test registering file operations tools with MCP."""
        register_file_operations(self.mcp)

        # Check that tools were registered
        self.assertIn('read_file', self.mcp.tools)
        self.assertIn('write_file', self.mcp.tools)
        self.assertIn('delete_file', self.mcp.tools)
        self.assertIn('move_file', self.mcp.tools)
        self.assertIn('copy_file', self.mcp.tools)
        self.assertIn('list_directory', self.mcp.tools)
        self.assertIn('create_directory', self.mcp.tools)
        self.assertIn('delete_directory', self.mcp.tools)
        self.assertIn('move_directory', self.mcp.tools)
        self.assertIn('copy_directory', self.mcp.tools)

    def test_read_file_basic(self):
        """Test basic file reading."""
        register_file_operations(self.mcp)
        read_file_func = self.mcp.tools['read_file']

        result = read_file_func(path=self.test_file)

        self.assertTrue(result['_metadata']['success'])
        self.assertIn('content', result)
        self.assertEqual(result['content'], "Test content")

    def test_read_file_with_encoding(self):
        """Test file reading with specific encoding."""
        register_file_operations(self.mcp)
        read_file_func = self.mcp.tools['read_file']

        result = read_file_func(path=self.test_file, encoding="utf-8")

        self.assertTrue(result['_metadata']['success'])
        self.assertIn('content', result)

    def test_write_file_basic(self):
        """Test basic file writing."""
        register_file_operations(self.mcp)
        write_file_func = self.mcp.tools['write_file']

        new_file = os.path.join(self.test_dir, "new_file.txt")
        result = write_file_func(
            path=new_file,
            content="New file content"
        )

        self.assertTrue(result['_metadata']['success'])
        self.assertTrue(os.path.exists(new_file))

    def test_write_file_with_overwrite(self):
        """Test file writing with overwrite."""
        register_file_operations(self.mcp)
        write_file_func = self.mcp.tools['write_file']

        result = write_file_func(
            path=self.test_file,
            content="Overwritten content",
            overwrite=True
        )

        self.assertTrue(result['_metadata']['success'])

    def test_delete_file_basic(self):
        """Test basic file deletion."""
        register_file_operations(self.mcp)
        delete_file_func = self.mcp.tools['delete_file']

        result = delete_file_func(path=self.test_file)

        self.assertTrue(result['success'])
        self.assertFalse(os.path.exists(self.test_file))

    def test_move_file_basic(self):
        """Test basic file moving."""
        register_file_operations(self.mcp)
        move_file_func = self.mcp.tools['move_file']

        new_location = os.path.join(self.test_dir, "moved_file.txt")
        result = move_file_func(
            source=self.test_file,
            destination=new_location
        )

        self.assertTrue(result['success'])
        self.assertFalse(os.path.exists(self.test_file))
        self.assertTrue(os.path.exists(new_location))

    def test_copy_file_basic(self):
        """Test basic file copying."""
        register_file_operations(self.mcp)
        copy_file_func = self.mcp.tools['copy_file']

        copy_location = os.path.join(self.test_dir, "copied_file.txt")
        result = copy_file_func(
            source=self.test_file,
            destination=copy_location
        )

        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(self.test_file))
        self.assertTrue(os.path.exists(copy_location))

    def test_list_directory_basic(self):
        """Test basic directory listing."""
        register_file_operations(self.mcp)
        list_directory_func = self.mcp.tools['list_directory']

        result = list_directory_func(directory_path=self.test_dir)

        self.assertTrue(result['success'])
        self.assertIn('items', result)
        self.assertIn('count', result)

    def test_list_directory_with_pattern(self):
        """Test directory listing with pattern."""
        register_file_operations(self.mcp)
        list_directory_func = self.mcp.tools['list_directory']

        result = list_directory_func(
            directory_path=self.test_dir,
            pattern="*.txt"
        )

        self.assertTrue(result['success'])
        self.assertIn('items', result)

    def test_create_directory_basic(self):
        """Test basic directory creation."""
        register_file_operations(self.mcp)
        create_directory_func = self.mcp.tools['create_directory']

        new_dir = os.path.join(self.test_dir, "new_directory")
        result = create_directory_func(directory_path=new_dir)

        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(new_dir))

    def test_create_directory_with_parents(self):
        """Test directory creation with parents."""
        register_file_operations(self.mcp)
        create_directory_func = self.mcp.tools['create_directory']

        new_dir = os.path.join(self.test_dir, "parent", "child")
        result = create_directory_func(
            directory_path=new_dir,
            create_parents=True
        )

        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(new_dir))

    def test_delete_directory_basic(self):
        """Test basic directory deletion."""
        register_file_operations(self.mcp)
        delete_directory_func = self.mcp.tools['delete_directory']

        # Create a directory to delete
        dir_to_delete = os.path.join(self.test_dir, "dir_to_delete")
        os.makedirs(dir_to_delete)

        result = delete_directory_func(directory_path=dir_to_delete)

        self.assertTrue(result['success'])
        self.assertFalse(os.path.exists(dir_to_delete))

    def test_move_directory_basic(self):
        """Test basic directory moving."""
        register_file_operations(self.mcp)
        move_directory_func = self.mcp.tools['move_directory']

        # Create a directory to move
        dir_to_move = os.path.join(self.test_dir, "dir_to_move")
        os.makedirs(dir_to_move)

        new_location = os.path.join(self.test_dir, "moved_dir")
        result = move_directory_func(
            source_path=dir_to_move,
            destination_path=new_location
        )

        self.assertTrue(result['success'])
        self.assertFalse(os.path.exists(dir_to_move))
        self.assertTrue(os.path.exists(new_location))

    def test_copy_directory_basic(self):
        """Test basic directory copying."""
        register_file_operations(self.mcp)
        copy_directory_func = self.mcp.tools['copy_directory']

        # Create a directory to copy
        dir_to_copy = os.path.join(self.test_dir, "dir_to_copy")
        os.makedirs(dir_to_copy)
        with open(os.path.join(dir_to_copy, "file.txt"), 'w') as f:
            f.write("Test")

        copy_location = os.path.join(self.test_dir, "copied_dir")
        result = copy_directory_func(
            source_path=dir_to_copy,
            destination_path=copy_location
        )

        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(dir_to_copy))
        self.assertTrue(os.path.exists(copy_location))

    def test_file_operations_error_handling(self):
        """Test error handling in file operations."""
        register_file_operations(self.mcp)
        read_file_func = self.mcp.tools['read_file']

        # Test with nonexistent file
        result = read_file_func(path="/nonexistent/file.txt")

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_write_file_without_overwrite(self):
        """Test file writing without overwrite on existing file."""
        register_file_operations(self.mcp)
        write_file_func = self.mcp.tools['write_file']

        result = write_file_func(
            path=self.test_file,
            content="New content",
            overwrite=False
        )

        # Should fail because file exists and overwrite=False
        self.assertFalse(result['success'])

    def test_delete_nonexistent_file(self):
        """Test deleting nonexistent file."""
        register_file_operations(self.mcp)
        delete_file_func = self.mcp.tools['delete_file']

        result = delete_file_func(path="/nonexistent/file.txt")

        self.assertFalse(result['success'])
        self.assertIn('error', result)


if __name__ == "__main__":
    unittest.main()
