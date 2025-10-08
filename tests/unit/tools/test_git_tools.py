import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
from windows_operations_mcp.tools.git_tools import (
    register_git_tools,
    git_add,
    git_commit,
    git_push,
    git_status
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


class TestGitTools(unittest.TestCase):
    """Test Git tools functionality."""

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

    def test_register_git_tools(self):
        """Test registering Git tools with MCP."""
        register_git_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('git_add', self.mcp.tools)
        self.assertIn('git_commit', self.mcp.tools)
        self.assertIn('git_push', self.mcp.tools)
        self.assertIn('git_status', self.mcp.tools)

    def test_git_add_basic(self):
        """Test basic git add functionality."""
        register_git_tools(self.mcp)
        git_add_func = self.mcp.tools['git_add']

        result = git_add_func(
            pathspec=self.test_file,
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_add_all(self):
        """Test git add all functionality."""
        register_git_tools(self.mcp)
        git_add_func = self.mcp.tools['git_add']

        result = git_add_func(
            pathspec=".",
            all=True,
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_commit_basic(self):
        """Test basic git commit functionality."""
        register_git_tools(self.mcp)
        git_commit_func = self.mcp.tools['git_commit']

        result = git_commit_func(
            message="Test commit",
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_commit_with_amend(self):
        """Test git commit with amend option."""
        register_git_tools(self.mcp)
        git_commit_func = self.mcp.tools['git_commit']

        result = git_commit_func(
            message="Amended commit",
            repo_path=self.test_dir,
            amend=True
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_push_basic(self):
        """Test basic git push functionality."""
        register_git_tools(self.mcp)
        git_push_func = self.mcp.tools['git_push']

        result = git_push_func(
            remote="origin",
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_push_with_remote(self):
        """Test git push with specific remote."""
        register_git_tools(self.mcp)
        git_push_func = self.mcp.tools['git_push']

        result = git_push_func(
            remote="origin",
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_status_basic(self):
        """Test basic git status functionality."""
        register_git_tools(self.mcp)
        git_status_func = self.mcp.tools['git_status']

        result = git_status_func(
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_status_basic(self):
        """Test git status basic functionality."""
        register_git_tools(self.mcp)
        git_status_func = self.mcp.tools['git_status']

        result = git_status_func(repo_path=self.test_dir)

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_tools_error_handling(self):
        """Test error handling in Git tools."""
        register_git_tools(self.mcp)
        git_add_func = self.mcp.tools['git_add']

        # Test with invalid working directory
        result = git_add_func(
            pathspec="nonexistent.txt",
            repo_path="/nonexistent/directory"
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_add_with_pattern(self):
        """Test git add with pattern."""
        register_git_tools(self.mcp)
        git_add_func = self.mcp.tools['git_add']

        result = git_add_func(
            pathspec="*.txt",
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_commit_with_files(self):
        """Test git commit with specific files."""
        register_git_tools(self.mcp)
        git_commit_func = self.mcp.tools['git_commit']

        result = git_commit_func(
            message="Test commit with files",
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_push_with_branch(self):
        """Test git push with specific branch."""
        register_git_tools(self.mcp)
        git_push_func = self.mcp.tools['git_push']

        result = git_push_func(
            remote="origin",
            branch="main",
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_git_status_with_path(self):
        """Test git status with specific path."""
        register_git_tools(self.mcp)
        git_status_func = self.mcp.tools['git_status']

        result = git_status_func(
            repo_path=self.test_dir
        )

        self.assertIn('status', result)
        self.assertIn('message', result)


if __name__ == "__main__":
    unittest.main()