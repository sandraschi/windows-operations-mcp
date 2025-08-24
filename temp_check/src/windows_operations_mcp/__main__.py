"""
Windows Operations MCP - Command Line Interface

Entry point for the Windows Operations MCP server.
FIXED: Claude Desktop event loop compatibility
"""

import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

# Configure logging before other imports to ensure proper initialization
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

# Add the package directory to the Python path
PACKAGE_DIR = Path(__file__).parent.absolute()
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

# Now import the rest of the application
from . import __version__, logger
from .mcp_server import mcp, register_all_tools


def print_help() -> None:
    """Print help message."""
    print("""Windows Operations MCP - Windows system operations for Claude Desktop

Usage:
  windows-operations-mcp           Run the MCP server (default)
  windows-operations-mcp run       Run the MCP server
  windows-operations-mcp help      Show this help message

Available Tools:
   run_powershell      - Execute PowerShell commands with reliable output capture
   run_cmd            - Execute CMD commands with reliable output capture  
   list_directory     - List directory contents with filtering options
   read_file_content  - Read file contents with encoding handling
   write_file_content - Write file contents with encoding handling
   test_port          - Test network port accessibility
   get_process_list   - List running processes (requires psutil)
   get_system_info    - Get comprehensive system information
   health_check       - Server health status and diagnostics

Configure in Claude Desktop:
Add to claude_desktop_config.json under mcpServers:
  "windows-operations-mcp": {
    "command": "python",
    "args": ["-m", "windows_operations_mcp"],
    "cwd": "D:/Dev/repos/windows-operations-mcp"
  }
""")


def main() -> None:
    """
    Main entry point for the Windows Operations MCP CLI.
    
    Handles command line arguments and starts the appropriate action.
    """
    try:
        # Handle command line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            if command in ("-h", "--help", "help"):
                print_help()
                return 0
            elif command == "version" or command == "-v" or command == "--version":
                print(f"Windows Operations MCP v{__version__}")
                return 0
            elif command != "run":
                print(f"Unknown command: {command}", file=sys.stderr)
                print_help()
                return 1
        
        # Default action: run the server
        logger.info(
            "Starting Windows Operations MCP Server",
            version=__version__,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            platform=sys.platform
        )
        
        # Register all tools before starting the server
        register_all_tools()
        
        # Start the MCP server with stdio transport
        mcp.run(transport="stdio")
        
        logger.info("Windows Operations MCP Server stopped gracefully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        return 0
        
    except Exception as e:
        logger.critical(
            "Fatal error in Windows Operations MCP Server",
            error=str(e),
            exc_info=True
        )
        return 1


if __name__ == "__main__":
    main()
