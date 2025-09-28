"""
Windows Operations MCP Server - FastMCP 2.12.3 Implementation

Main server module that registers all tools with FastMCP 2.x.
Provides Windows system operations through a standardized MCP interface.
"""

import logging
import os
import sys
import traceback

# Configure logging before importing FastMCP to ensure proper initialization
from windows_operations_mcp.logging_config import setup_logging, get_logger

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
        fastmcp_version = getattr(fastmcp, '__version__', '2.0.0')  # Default to 2.0.0 if missing
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
        
        logger.info("Tool registration completed")
        
    except Exception as e:
        logger.critical("Error during tool registration", error=str(e))
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
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical("Fatal error in MCP server", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()

# Export the configured MCP instance and other public APIs
__all__ = [
    "mcp",
    "main"
]