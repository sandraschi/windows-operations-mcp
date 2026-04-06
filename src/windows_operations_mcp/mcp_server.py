"""
Windows Operations MCP Server - FastMCP 3.2 SOTA Implementation

Main server module that registers all tools with FastMCP 3.2.
Provides Windows system operations through a standardized, agentic MCP interface.
"""

import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from windows_operations_mcp.logging_config import setup_logging, get_logger

# Initialize logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(level=log_level)
logger = get_logger(__name__)

try:
    from fastmcp import FastMCP
except ImportError as e:
    logger.error(f"Failed to import FastMCP 3.2+: {e}")
    sys.exit(1)

@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncGenerator[None, None]:
    """Manage server lifecycle: startup and shutdown."""
    logger.info("Initializing Windows Operations SOTA v14.0")
    try:
        yield
    finally:
        logger.info("Shutting down Windows Operations SOTA v14.0")

# Initialize FastMCP 3.2 instance
mcp = FastMCP(
    name="windows-operations-mcp",
    version="14.0.0",
    lifespan=lifespan,
    description="SOTA v14.0: Specialized Windows Control Plane & Data Surgery Hub"
)

def register_all_tools() -> None:
    """Register all portmanteau tool modules and advanced features."""
    try:
        logger.info("Starting SOTA v14.0 tool registration...")

        # Core Portmanteau Modules (SOTA v14.0 Modernized)
        portmanteau_tools = [
            "command_execution",
            "archive_management",
            "json_operations",
            "process_management",
            "windows_services",
            "system_management",
            "windows_event_logs",
            "windows_performance",
            "windows_permissions",
            "windows_registry",
            "windows_accounts",
            "windows_automation",
            "agentic_operations",
        ]

        # NOTE: file_operations and directory_operations are excluded to avoid 
        # redundancy with filesystem-mcp, as requested by the user.

        for tool_name in portmanteau_tools:
            module_path = f"windows_operations_mcp.tools.portmanteau.{tool_name}"
            register_func_name = f"register_{tool_name}"
            try:
                module = __import__(module_path, fromlist=[register_func_name])
                register_func = getattr(module, register_func_name)
                register_func(mcp)
                logger.debug(f"Registered: {tool_name}")
            except Exception as e:
                logger.warning(f"Failed to register '{tool_name}': {e}")

        # Register Skills & Prompts (New in SOTA v14.0)
        from .prompts import register_all_prompts
        register_all_prompts(mcp)

        logger.info("Tool registration completed successfully.")

    except Exception as e:
        logger.critical(f"Critical failure during tool registration: {e}")
        raise

def main() -> None:
    """Main entry point for the SOTA v14.0 server."""
    try:
        # Register tools
        register_all_tools()

        # Start the server using the unified 3.2 runner
        mcp.run()

    except Exception as e:
        logger.critical(f"Fatal error in MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

__all__ = ["mcp", "main"]
