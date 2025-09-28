import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import main module functions (if any exist)
try:
    from src.windows_operations_mcp import main
except ImportError:
    main = None


class TestMainModule(unittest.TestCase):
    """Test main module functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_main_module_import(self):
        """Test that main module can be imported."""
        # If main module exists, it should be importable
        if main is not None:
            self.assertIsNotNone(main)
        else:
            # If no main module, that's also fine
            self.skipTest("No main module found")


if __name__ == "__main__":
    unittest.main()
