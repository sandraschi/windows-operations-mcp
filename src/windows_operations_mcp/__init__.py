"""
Windows Operations MCP - FastMCP 3.2 SOTA Implementation

Comprehensive Windows system operations server for Claude Desktop.
Full FastMCP 3.2 conformance: sampling, skills, prompts, prefab UI,
agentic workflows, SkillsDirectoryProvider.
"""

__version__ = "14.2.0"
__author__ = "Sandra Schipal"
__email__ = "sandra@schipal.at"

import os
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent.absolute()
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from .logging_config import get_logger, setup_logging  # noqa: E402
from .mcp_server import mcp, register_all_tools  # noqa: E402

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(level=log_level)
logger = get_logger(__name__)

__all__ = [
    "get_logger",
    "logger",
    "mcp",
    "register_all_tools",
]

logger.info(
    f"Windows Operations MCP v{__version__} initialized",
    log_level=log_level,
    python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    platform=sys.platform,
)
