import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
# Import all main modules for comprehensive testing
from windows_operations_mcp import decorators, logging_config, utils, __init__
from windows_operations_mcp.tools import (
    system_tools, help_tools, network_tools, git_tools,
    process_tools, archive_tools
)
from windows_operations_mcp.tools.file_operations import file_operations


class TestComprehensive(unittest.TestCase):
    """Comprehensive test covering all major modules."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_decorators_functionality(self):
        """Test all decorator functions."""
        from windows_operations_mcp.decorators import (
            tool, validate_inputs, rate_limited, log_execution,
            is_positive_number, is_valid_path, is_valid_port, is_safe_command
        )

        # Test validation functions
        self.assertTrue(is_positive_number(5)[0])
        self.assertFalse(is_positive_number(-1)[0])

        self.assertTrue(is_valid_path(self.test_dir)[0])
        self.assertFalse(is_valid_path("/nonexistent")[0])

        self.assertTrue(is_valid_port(8080)[0])
        self.assertFalse(is_valid_port(99999)[0])

        self.assertTrue(is_safe_command("echo hello")[0])
        self.assertFalse(is_safe_command("rm -rf /")[0])

        # Test decorators
        @tool(name="test_tool", description="Test", parameters={}, required=[], returns={})
        @log_execution()
        def test_function():
            return {"result": "test"}

        result = test_function()
        self.assertEqual(result["result"], "test")

    def test_logging_config_functionality(self):
        """Test logging configuration."""
        logger = logging_config.get_logger("test_module")
        self.assertIsNotNone(logger)

        # Test logging works
        logger.info("Test message")
        logger.warning("Test warning")

    def test_utils_functionality(self):
        """Test utility functions."""
        from windows_operations_mcp.utils.common import get_execution_result
        from windows_operations_mcp.utils.file_utils import create_temp_file, safe_cleanup_file

        # Test execution result processing
        test_result = {
            'success': True,
            'stdout': 'test output',
            'stderr': '',
            'exit_code': 0,
            'execution_time': 1.5
        }

        result = get_execution_result(test_result)
        self.assertTrue(result['success'])
        self.assertEqual(result['stdout'], 'test output')

        # Test file utilities
        temp_file = create_temp_file(suffix=".txt", content=b"test content")
        self.assertTrue(os.path.exists(temp_file))

        safe_cleanup_file(temp_file)
        self.assertFalse(os.path.exists(temp_file))

    def test_system_tools_functionality(self):
        """Test system tools."""
        result = system_tools.get_system_info()
        self.assertTrue(result['success'])
        self.assertIn('system', result)

        result = system_tools.health_check()
        self.assertTrue(result['success'])
        self.assertIn('status', result)

    def test_help_tools_functionality(self):
        """Test help tools."""
        result = help_tools.get_help()
        self.assertIn('status', result)
        self.assertIn('message', result)

        result = help_tools.get_help(command="get_system_info")
        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_network_tools_functionality(self):
        """Test network tools."""
        result = network_tools.test_port(host="127.0.0.1", port=80, timeout_seconds=1)
        self.assertIn('success', result)
        self.assertIn('status', result)
        self.assertIn('connect_time', result)

    def test_git_tools_functionality(self):
        """Test git tools."""
        # Test with non-git directory (should handle gracefully)
        result = git_tools.git_status(repo_path=self.test_dir)
        self.assertIn('status', result)
        self.assertIn('message', result)

    def test_process_tools_functionality(self):
        """Test process tools."""
        result = process_tools.get_process_list(max_processes=5)
        self.assertTrue(result['success'])
        self.assertIn('processes', result)
        self.assertIsInstance(result['processes'], list)

        # Test with current process
        import os
        result = process_tools.get_process_info(pid=os.getpid())
        self.assertTrue(result['success'])
        self.assertIn('process', result)

    def test_archive_tools_functionality(self):
        """Test archive tools."""
        # Create test files
        test_file1 = os.path.join(self.test_dir, "test1.txt")
        test_file2 = os.path.join(self.test_dir, "test2.txt")

        with open(test_file1, 'w') as f:
            f.write("Test content 1")
        with open(test_file2, 'w') as f:
            f.write("Test content 2")

        # Test archive creation
        archive_path = os.path.join(self.test_dir, "test.zip")
        result = archive_tools.create_archive(
            archive_path=archive_path,
            source_paths=[test_file1, test_file2]
        )
        self.assertIn('success', result)
        self.assertTrue(os.path.exists(archive_path))

        # Test archive listing
        result = archive_tools.list_archive(archive_path=archive_path)
        self.assertIn('success', result)
        self.assertIn('files', result)

    def test_file_operations_functionality(self):
        """Test file operations."""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")

        # Test file reading
        result = file_operations.read_file(path=test_file)
        self.assertIn('path', result)
        self.assertIn('content', result)
        self.assertEqual(result['content'], "Test content")

        # Test file writing
        new_file = os.path.join(self.test_dir, "new.txt")
        result = file_operations.write_file(
            path=new_file,
            content="New content"
        )
        self.assertIn('path', result)
        self.assertIn('size', result)
        self.assertIn('created', result)
        self.assertTrue(os.path.exists(new_file))

        # Test file copying
        copy_file = os.path.join(self.test_dir, "copy.txt")
        result = file_operations.copy_file(
            source=test_file,
            destination=copy_file
        )
        self.assertIn('success', result)
        self.assertTrue(os.path.exists(copy_file))

        # Test file deletion
        result = file_operations.delete_file(path=test_file)
        self.assertIn('success', result)
        self.assertFalse(os.path.exists(test_file))

    def test_module_imports(self):
        """Test that all modules can be imported."""
        # Test that all main modules are importable
        modules = [
            'src.windows_operations_mcp.decorators',
            'src.windows_operations_mcp.logging_config',
            'src.windows_operations_mcp.utils',
            'src.windows_operations_mcp.tools.system_tools',
            'src.windows_operations_mcp.tools.help_tools',
            'src.windows_operations_mcp.tools.network_tools',
            'src.windows_operations_mcp.tools.git_tools',
            'src.windows_operations_mcp.tools.process_tools',
            'src.windows_operations_mcp.tools.archive_tools',
            'src.windows_operations_mcp.tools.file_operations.file_operations',
        ]

        for module_name in modules:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")

    def test_function_callability(self):
        """Test that key functions are callable."""
        functions = [
            decorators.tool,
            decorators.validate_inputs,
            decorators.rate_limited,
            decorators.log_execution,
            logging_config.get_logger,
            system_tools.get_system_info,
            system_tools.health_check,
            help_tools.get_help,
            network_tools.test_port,
            git_tools.git_status,
            process_tools.get_process_list,
            process_tools.get_process_info,
            archive_tools.create_archive,
            archive_tools.list_archive,
            file_operations.read_file,
            file_operations.write_file,
        ]

        for func in functions:
            self.assertTrue(callable(func), f"{func} is not callable")

    def test_error_handling(self):
        """Test error handling across modules."""
        # Test system tools error handling
        result = system_tools.get_system_info(invalid_param=True)
        self.assertIn('success', result)  # Should handle gracefully

        # Test process tools error handling
        result = process_tools.get_process_info(pid=999999)
        self.assertFalse(result['success'])

        # Test file operations error handling
        result = file_operations.read_file(path="/nonexistent/file.txt")
        self.assertIn('error', result)  # Should return error in result

        # Test archive tools error handling
        result = archive_tools.list_archive(archive_path="/nonexistent/archive.zip")
        self.assertIn('success', result)


if __name__ == "__main__":
    unittest.main()
