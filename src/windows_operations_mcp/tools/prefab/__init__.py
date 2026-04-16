"""
Prefab Tools Registry - SOTA v14.2.0
Wires prefab tools into the MCP server with app=True flag.
"""

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


def register_prefab_tools(mcp) -> None:
    """Register all Prefab UI tools. Called only when prefab-ui is installed."""
    from windows_operations_mcp.tools.prefab.system_cards import (
        process_list_card,
        system_health_card,
    )

    mcp.tool(app=True)(system_health_card)
    mcp.tool(app=True)(process_list_card)

    logger.info("Prefab tools registered: system_health_card, process_list_card")


__all__ = ["register_prefab_tools"]
