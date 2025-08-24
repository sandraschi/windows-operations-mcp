"""
Pytest configuration and fixtures for Windows Operations MCP tests.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging for tests
import logging
logging.basicConfig(level=logging.INFO)

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture to get the path to the test data directory."""
    test_dir = Path(__file__).parent
    data_dir = test_dir / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    """Fixture to create a temporary directory for test files."""
    return tmp_path_factory.mktemp("test_files")

@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    """Set up a clean environment for each test."""
    # Clear any environment variables that might affect tests
    for key in list(os.environ.keys()):
        if key.startswith(('MCP_', 'WINDOWS_OPS_')):
            monkeypatch.delenv(key, raising=False)
    
    # Set up a clean environment
    monkeypatch.setenv('PYTHONPATH', str(Path(__file__).parent.parent))
    
    # Mock platform-specific modules if needed
    try:
        import win32api
    except ImportError:
        # Mock win32api for non-Windows platforms
        mock_win32 = MagicMock()
        sys.modules['win32api'] = mock_win32
        sys.modules['win32con'] = MagicMock()
        sys.modules['win32security'] = MagicMock()
        sys.modules['pywintypes'] = MagicMock()
        sys.modules['pythoncom'] = MagicMock()
    
    # Add any other environment setup needed for tests
    yield
    
    # Cleanup code if needed
    pass

# Common test utilities
class MockResponse:
    """Mock response object for testing."""
    
    def __init__(self, json_data, status_code=200, text=""):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text
    
    def json(self):
        return self.json_data

# Add any other common test utilities here
