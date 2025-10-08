"""
Windows Operations MCP - Main entry point for MCPB packaging.

This module provides the main entry point for running the Windows Operations MCP server
when packaged as an MCPB extension. It ensures proper Python path resolution and
tool registration for MCPB runtime environments.
"""

import sys
import os
from pathlib import Path

# CRITICAL: Ensure proper Python path resolution for MCPB packaging
# This handles the path resolution issues in Claude Desktop extensions
PACKAGE_DIR = Path(__file__).parent.absolute()

# Add the package directory to Python path for proper module resolution
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

# Also add the src directory if it exists (for development)
src_dir = PACKAGE_DIR.parent
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Set environment variables for proper operation
os.environ.setdefault('PYTHONPATH', str(PACKAGE_DIR))
os.environ.setdefault('PYTHONUNBUFFERED', '1')

# Import and run the server
from .server import main

if __name__ == "__main__":
    main()
