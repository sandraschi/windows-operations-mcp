"""
Windows Operations MCP - FastMCP 2.12.3 Implementation

A comprehensive Windows system operations server for Claude Desktop.
Provides reliable PowerShell, CMD, file operations, and system monitoring.
"""

__version__ = "0.1.0"
__author__ = "Sandra"
__email__ = "sandra@example.com"

import os
import sys
from pathlib import Path

# Add the package directory to the Python path
PACKAGE_DIR = Path(__file__).parent.absolute()
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

# Import core components
from .mcp_server import mcp, register_all_tools
from .logging_config import setup_logging, get_logger

# Initialize logging with default configuration
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(level=log_level)
logger = get_logger(__name__)

# Export public API
__all__ = [
    "mcp",
    "register_all_tools",
    "get_logger",
    "logger"
]

# Log package initialization
logger.info(
    f"Windows Operations MCP v{__version__} initialized",
    log_level=log_level,
    python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    platform=sys.platform
)
