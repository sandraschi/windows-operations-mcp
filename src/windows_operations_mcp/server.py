"""
Windows Operations MCP Server - Main entry point for MCPB packaging.

This module provides the main MCP server instance and tool registration
for the Windows Operations MCP server when packaged as an MCPB extension.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging before importing FastMCP to ensure proper initialization
from .logging_config import setup_logging, get_logger

# Initialize logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(level=log_level)
logger = get_logger(__name__)

# Import FastMCP 2.12.0+ components
try:
    import fastmcp
    from fastmcp import FastMCP

    # Get version using __version__ attribute (standard Python practice)
    try:
        fastmcp_version = getattr(fastmcp, '__version__', '2.0.0')  # Default to 2.0.0 if missing
        logger.info(f"Using FastMCP version: {fastmcp_version}")
    except Exception as ve:
        logger.warning(f"Could not determine FastMCP version: {ve}")
        fastmcp_version = "2.0.0"  # Assume compatible version

except ImportError as e:
    logger.error(f"Failed to import FastMCP 2.12.0+: {e}")
    sys.exit(1)

except Exception as e:
    logger.error(f"Error initializing FastMCP: {e}")
    sys.exit(1)

# Initialize FastMCP instance
mcp = FastMCP(
    name="windows-operations-mcp",
    version="0.1.0"
)

# Register all tools using explicit registration functions
def register_all_tools() -> None:
    """Register all tool modules with the FastMCP instance."""
    try:
        logger.info("Starting tool registration...")

        # Import and register PowerShell tools
        try:
            from .tools.powershell_tools import register_powershell_tools
            register_powershell_tools(mcp)
            logger.info("Registered PowerShell tools")
        except Exception as e:
            logger.error(f"Failed to register PowerShell tools: {e}")

        # Import and register File tools from file_operations package
        try:
            from .tools.file_operations import register_file_operations
            register_file_operations(mcp)
            logger.info("Registered File tools")
        except Exception as e:
            logger.error(f"Failed to register File tools: {e}")

        # Import and register Network tools
        try:
            from .tools.network_tools import register_network_tools
            register_network_tools(mcp)
            logger.info("Registered Network tools")
        except Exception as e:
            logger.error(f"Failed to register Network tools: {e}")

        # Import and register System tools
        try:
            from .tools.system_tools import register_system_tools
            register_system_tools(mcp)
            logger.info("Registered System tools")
        except Exception as e:
            logger.error(f"Failed to register System tools: {e}")

        # Import and register Process tools
        try:
            from .tools.process_tools import register_process_tools
            register_process_tools(mcp)
            logger.info("Registered Process tools")
        except Exception as e:
            logger.error(f"Failed to register Process tools: {e}")

        # Import and register Git tools
        try:
            from .tools.git_tools import register_git_tools
            register_git_tools(mcp)
            logger.info("Registered Git tools")
        except Exception as e:
            logger.warning(f"Git tools not available or not converted: {e}")

        # Import and register JSON tools
        try:
            from .tools.json_register import register_json_tools
            register_json_tools(mcp)
            logger.info("Registered JSON tools")
        except Exception as e:
            logger.error(f"Failed to register JSON tools: {e}")

        # Import and register Media tools
        try:
            from .tools.media_register import register_media_tools
            register_media_tools(mcp)
            logger.info("Registered Media tools")
        except Exception as e:
            logger.error(f"Failed to register Media tools: {e}")

        # Import and register Help tools
        try:
            from .tools.help_tools import register_help_tools
            register_help_tools(mcp)
            logger.info("Registered Help tools")
        except Exception as e:
            logger.warning(f"Help tools not available or not converted: {e}")

        # Import and register Archive tools
        try:
            from .tools.archive_tools import register_archive_tools
            register_archive_tools(mcp)
            logger.info("Registered Archive tools")
        except Exception as e:
            logger.warning(f"Archive tools not available or not converted: {e}")

        # Import and register Windows Services tools
        try:
            from .tools.windows_services import register_windows_services_tools
            register_windows_services_tools(mcp)
            logger.info("Registered Windows Services tools")
        except Exception as e:
            logger.warning(f"Windows Services tools not available: {e}")

        # Import and register Windows Event Log tools
        try:
            from .tools.windows_event_logs import register_windows_event_log_tools
            register_windows_event_log_tools(mcp)
            logger.info("Registered Windows Event Log tools")
        except Exception as e:
            logger.warning(f"Windows Event Log tools not available: {e}")

        # Import and register Windows Performance tools
        try:
            from .tools.windows_performance import register_windows_performance_tools
            register_windows_performance_tools(mcp)
            logger.info("Registered Windows Performance tools")
        except Exception as e:
            logger.warning(f"Windows Performance tools not available: {e}")

        # Import and register Windows Permissions tools
        try:
            from .tools.windows_permissions import register_windows_permissions_tools
            register_windows_permissions_tools(mcp)
            logger.info("Registered Windows Permissions tools")
        except Exception as e:
            logger.warning(f"Windows Permissions tools not available: {e}")

        logger.info("Tool registration completed")

    except Exception as e:
        logger.critical("Error during tool registration", error=str(e))
        raise

# Register all tools
register_all_tools()

def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Windows Operations MCP Server")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.critical("MCP server crashed", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()

