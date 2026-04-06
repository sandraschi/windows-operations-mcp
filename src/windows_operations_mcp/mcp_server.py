"""
Windows Operations MCP Server - FastMCP 2.12.3 Implementation

Main server module that registers all tools with FastMCP 2.x.
Provides Windows system operations through a standardized MCP interface.
"""

import os
import sys

# Configure logging before importing FastMCP to ensure proper initialization
from windows_operations_mcp.logging_config import setup_logging, get_logger
from .transport import run_server
# from .web import setup_webapp  # disabled - not needed for stdio transport

# Initialize logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(level=log_level)
logger = get_logger(__name__)

# Import FastMCP 2.12.3+ components
try:
    import fastmcp
    from fastmcp import FastMCP

    # Get version using __version__ attribute (standard Python practice)
    try:
        fastmcp_version = getattr(
            fastmcp, "__version__", "2.0.0"
        )  # Default to 2.0.0 if missing
        logger.info(f"Using FastMCP version: {fastmcp_version}")
    except Exception as ve:
        logger.warning(f"Could not determine FastMCP version: {ve}")
        fastmcp_version = "2.0.0"  # Assume compatible version

except ImportError as e:
    logger.error(f"Failed to import FastMCP 2.10+: {e}")
    sys.exit(1)

except Exception as e:
    logger.error(f"Error initializing FastMCP: {e}")
    sys.exit(1)

# Initialize FastMCP instance
mcp = FastMCP(name="windows-operations-mcp", version="0.1.0")

# Webapp bridge disabled - not needed for stdio transport (Claude Desktop)
# Mount API was changed in FastMCP 2.14.5+: mount(server, namespace) not mount(path, app)


# Register all tools using explicit registration functions
def register_all_tools() -> None:
    """Register all portmanteau tool modules with the FastMCP instance."""
    try:
        logger.info("Starting portmanteau tool registration...")

        # Register Portmanteau Tools - Core Windows Operations (9 tools)
        portmanteau_tools = [
            (
                "command_execution",
                "windows_operations_mcp.tools.portmanteau.command_execution",
                "register_command_execution",
            ),
            (
                "file_operations",
                "windows_operations_mcp.tools.portmanteau.file_operations",
                "register_file_operations",
            ),
            (
                "directory_operations",
                "windows_operations_mcp.tools.portmanteau.directory_operations",
                "register_directory_operations",
            ),
            (
                "archive_management",
                "windows_operations_mcp.tools.portmanteau.archive_management",
                "register_archive_management",
            ),
            (
                "json_operations",
                "windows_operations_mcp.tools.portmanteau.json_operations",
                "register_json_operations",
            ),
            (
                "git_operations",
                "windows_operations_mcp.tools.portmanteau.git_operations",
                "register_git_operations",
            ),
            (
                "process_management",
                "windows_operations_mcp.tools.portmanteau.process_management",
                "register_process_management",
            ),
            (
                "windows_services",
                "windows_operations_mcp.tools.portmanteau.windows_services",
                "register_windows_services",
            ),
            (
                "system_management",
                "windows_operations_mcp.tools.portmanteau.system_management",
                "register_system_management",
            ),
            (
                "agentic_operations",
                "windows_operations_mcp.tools.portmanteau.agentic_operations",
                "register_agentic_operations",
            ),
        ]

        registered_count = 0

        for tool_name, module_path, register_func_name in portmanteau_tools:
            try:
                # Dynamic import of portmanteau tool
                module = __import__(module_path, fromlist=[register_func_name])
                register_func = getattr(module, register_func_name)
                register_func(mcp)
                logger.info(f"Registered portmanteau tool: {tool_name}")
                registered_count += 1
            except Exception as e:
                logger.warning(
                    f"Failed to register portmanteau tool '{tool_name}': {e}"
                )

        logger.info(
            f"Portmanteau tool registration completed. Registered {registered_count} tools."
        )

    except Exception as e:
        logger.critical("Error during portmanteau tool registration", error=str(e))
        raise


# Main entry point
def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Windows Operations MCP server")

        # Register all tools
        register_all_tools()

        # Start the server with stdio transport
        logger.info("Starting MCP server with stdio transport")
        run_server(mcp, server_name="windows-operations-mcp")

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical("Fatal error in MCP server", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

# Export the configured MCP instance and other public APIs
__all__ = ["mcp", "main"]
