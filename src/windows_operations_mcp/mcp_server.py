"""
Windows Operations MCP Server - FastMCP 3.2 SOTA Implementation

Main server module that registers all tools, prompts, resources, skills,
prefab tools, and agentic workflows with FastMCP 3.2.
"""

import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

from windows_operations_mcp.logging_config import get_logger, setup_logging

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
    logger.info("Initializing Windows Operations SOTA v14.2.0")
    try:
        yield
    finally:
        logger.info("Shutting down Windows Operations SOTA v14.2.0")


# Initialize FastMCP 3.2 instance
mcp = FastMCP(
    name="windows-operations-mcp",
    version="14.2.0",
    lifespan=lifespan,
    instructions="SOTA v14.2.0: Windows Control Plane & Data Surgery Hub — full FastMCP 3.2 conformance (sampling, skills, prompts, prefab)",
    strict_input_validation=True,
    mask_error_details=True,
    client_log_level="info",
)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "server": "windows-operations-mcp"})


def _register_skills_provider() -> None:
    """Register the SkillsDirectoryProvider for skill:// URI access."""
    try:
        from fastmcp.server.providers.skills import SkillsDirectoryProvider

        # skills/ is at repo root (two levels up from this file: src/windows_operations_mcp/)
        skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
        if skills_dir.is_dir():
            mcp.add_provider(SkillsDirectoryProvider(roots=[skills_dir]))
            logger.info(f"Skills provider registered: {skills_dir}")
        else:
            logger.warning(f"Skills dir not found at {skills_dir}, skipping provider")
    except ImportError:
        logger.warning("SkillsDirectoryProvider not available in this FastMCP build — skipping")
    except Exception as e:
        logger.warning(f"Skills provider registration failed: {e}")


def _register_prefab_tools() -> None:
    """Register Prefab UI tools (optional — requires [apps] extra)."""
    if os.getenv("WINOPS_PREFAB_APPS", "1") == "0":
        logger.info("WINOPS_PREFAB_APPS=0 — prefab tools disabled")
        return
    try:
        from windows_operations_mcp.tools.prefab import register_prefab_tools

        register_prefab_tools(mcp)
        logger.info("Prefab tools registered")
    except ImportError:
        logger.info("prefab-ui not installed (uv sync --extra apps) — prefab tools skipped")
    except Exception as e:
        logger.warning(f"Prefab tool registration failed: {e}")


def register_all_tools() -> None:
    """Register all portmanteau modules, prompts, resources, skills, and prefab tools."""
    try:
        logger.info("Starting SOTA v14.2 tool registration...")

        # Core Portmanteau Modules
        portmanteau_tools = [
            "command_execution",
            "container_execution",
            "archive_management",
            "json_operations",
            "process_management",
            "windows_services",
            "system_management",
            "windows_event_logs",
            "windows_performance",
            "windows_permissions",
            "windows_accounts",
            "windows_automation",
            "windows_network",
            "windows_environment",
            "windows_apps",
            "agentic_operations",
        ]

        for tool_name in portmanteau_tools:
            module_path = f"windows_operations_mcp.tools.portmanteau.{tool_name}"
            register_func_name = f"register_{tool_name}"
            try:
                module = __import__(module_path, fromlist=[register_func_name])
                register_func = getattr(module, register_func_name)
                register_func(mcp)
                logger.debug(f"Registered portmanteau: {tool_name}")
            except Exception as e:
                logger.warning(f"Failed to register '{tool_name}': {e}")

        # Prompts (FastMCP 3.2+)
        try:
            from .prompts import register_all_prompts

            register_all_prompts(mcp)
            logger.info("Prompts registered")
        except Exception as e:
            logger.warning(f"Prompt registration failed: {e}")

        # Resources (legacy resource:// URIs — kept for back-compat)
        try:
            from .resources import register_resources

            register_resources(mcp)
            logger.info("Resources registered")
        except Exception as e:
            logger.warning(f"Resource registration failed: {e}")

        # Skills Provider (FastMCP 3.2+ skill:// URIs)
        _register_skills_provider()

        # Prefab Tools (FastMCP 3.2+ / prefab-ui — optional [apps] extra)
        _register_prefab_tools()

        logger.info("Tool registration completed successfully.")

    except Exception as e:
        logger.critical(f"Critical failure during tool registration: {e}")
        raise


def main() -> None:
    """Main entry point."""
    # SOTA: Windows Binary Mode for clean JSON-RPC
    if os.name == "nt":
        import msvcrt

        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    try:
        register_all_tools()
        from .transport import run_server

        run_server(mcp, server_name="windows-operations-mcp")
    except Exception as e:
        logger.critical(f"Fatal error in MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

__all__ = ["main", "mcp"]
