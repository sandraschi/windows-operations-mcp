import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.main import main
from src.windows_operations_mcp.__init__ import __version__


class TestMain(unittest.TestCase):
    """Test main module functionality."""

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        self.assertTrue(callable(main))

    def test_main_function_signature(self):
        """Test main function signature."""
        import inspect
        sig = inspect.signature(main)
        # Main function exists and is callable
        self.assertTrue(callable(main))
        self.assertIsNotNone(sig)

    def test_version_constant(self):
        """Test version constant is properly defined."""
        self.assertIsNotNone(__version__)
        self.assertIsInstance(__version__, str)
        # Should follow semantic versioning
        self.assertTrue(len(__version__.split('.')) >= 2)


class TestInitModule(unittest.TestCase):
    """Test __init__ module functionality."""

    def test_init_imports(self):
        """Test that __init__ imports work correctly."""
        from src.windows_operations_mcp import __init__ as init_module

        # Test that key attributes exist
        self.assertTrue(hasattr(init_module, '__version__'))

    def test_init_version_format(self):
        """Test version format in __init__."""
        from src.windows_operations_mcp import __init__ as init_module

        version = init_module.__version__
        self.assertIsInstance(version, str)
        # Should be semantic version format
        parts = version.split('.')
        self.assertTrue(len(parts) >= 2)
        for part in parts:
            self.assertTrue(part.isdigit())


if __name__ == "__main__":
    unittest.main()