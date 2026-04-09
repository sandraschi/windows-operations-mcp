"""
Resource Layer - SOTA v14.0 (FastMCP 3.2+)
Provides access to expert skills, workflows, and high-fidelity documentation as MCP resources.
"""

import os
from pathlib import Path
from fastmcp import FastMCP
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

def register_resources(mcp: FastMCP) -> None:
    """Register all system and expert resources."""
    
    # Path to the package root (where 'skills' and 'llms.txt' live)
    # Assuming this module is in src/windows_operations_mcp/
    package_root = Path(__file__).parent.parent.parent
    
    @mcp.resource("resource://windows/expert-skill")
    def get_expert_skill() -> str:
        """Get the SOTA Windows Expert skill instructions."""
        skill_path = package_root / "skills" / "windows-expert" / "SKILL.md"
        try:
            return skill_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read expert skill: {e}")
            return f"Error: Expert skill not found at {skill_path}"

    @mcp.resource("resource://windows/documentation/llms")
    def get_llms_txt() -> str:
        """Get the root llms.txt summary for the Windows Operations fleet."""
        docs_path = package_root / "llms.txt"
        try:
            return docs_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read llms.txt: {e}")
            return "Error: documentation summary not found."

    logger.info("Resource layer registered: expert-skill, documentation/llms")
