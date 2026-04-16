"""
Resource Layer - SOTA v14.2.0 (FastMCP 3.2+)

Exposes llms.txt as a resource for agent discoverability.
Note: skill:// URIs are now served by SkillsDirectoryProvider (mcp_server.py).
The legacy resource://windows/expert-skill is kept for backward compatibility.
"""

from pathlib import Path

from fastmcp import FastMCP

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

# Repo root: src/windows_operations_mcp/ -> ../../.. -> repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def register_resources(mcp: FastMCP) -> None:
    """Register static documentation resources."""

    @mcp.resource("resource://windows/documentation/llms")
    def get_llms_txt() -> str:
        """LLM-friendly summary of all tools and capabilities in this server."""
        docs_path = _REPO_ROOT / "llms.txt"
        try:
            return docs_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"llms.txt not found: {e}")
            return "windows-operations-mcp: llms.txt not found."

    @mcp.resource("resource://windows/documentation/llms-full")
    def get_llms_full_txt() -> str:
        """Full LLM corpus for windows-operations-mcp (llms-full.txt)."""
        docs_path = _REPO_ROOT / "llms-full.txt"
        try:
            return docs_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"llms-full.txt not found: {e}")
            return "windows-operations-mcp: llms-full.txt not found."

    @mcp.resource("resource://windows/expert-skill")
    def get_expert_skill_legacy() -> str:
        """[Legacy] SOTA Windows Expert skill instructions (use skill://windows-expert/SKILL.md instead)."""
        skill_path = _REPO_ROOT / "skills" / "windows-expert" / "SKILL.md"
        try:
            return skill_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Expert skill not found: {e}")
            return f"Error: skill not found at {skill_path}"

    logger.info("Resources registered: llms, llms-full, expert-skill (legacy)")


__all__ = ["register_resources"]
