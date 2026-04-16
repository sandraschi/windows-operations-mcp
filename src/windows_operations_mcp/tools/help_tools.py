"""Enhanced help system for the Windows Operations MCP."""

from typing import Any

from ..decorators import tool
from ..logging_config import get_logger

logger = get_logger(__name__)

# Tool categories for organization
TOOL_CATEGORIES = {
    "command": "Command execution (PowerShell/CMD)",
    "file": "File operations (read, write, copy, move, delete, info, exists)",
    "directory": "Directory operations (create, delete, move, copy, list)",
    "attributes": "File attributes and dates",
    "editing": "File editing (edit, fix_markdown)",
    "archive": "Archive management (create, extract, list)",
    "json": "JSON operations (read, write, validate, format, convert, extract)",
    "media": "Media metadata (images, MP3)",
    "git": "Git operations (add, commit, push, status)",
    "process": "Process management (list, info, resources)",
    "services": "Windows Services (list, start, stop, restart)",
    "event_logs": "Windows Event Logs (query, export, clear, monitor)",
    "performance": "Windows Performance monitoring",
    "permissions": "Windows Permissions management",
    "system": "System management (info, health, test_port, help)",
    "agentic": "Agentic control and autonomous workflows (SEP-1577)",
}


@tool(
    name="get_help",
    description="Get help about available commands and their usage",
    parameters={
        "command": {
            "type": "string",
            "description": "Specific command to get detailed help for",
        },
        "category": {"type": "string", "description": "Filter tools by category"},
        "detail": {
            "type": "integer",
            "description": "Detail level (0=names only, 1=with descriptions, 2=verbose)",
            "default": 1,
        },
    },
    required=[],
    returns={
        "type": "object",
        "properties": {"status": {"type": "string"}, "message": {"type": "string"}},
    },
)
def get_help(command: str | None = None, category: str | None = None, detail: int = 1) -> dict[str, Any]:
    """
    Get help about available commands and their usage.

    This tool provides comprehensive help information about all available MCP tools,
    with support for filtering by category and adjustable detail levels.

    Args:
        command: Specific command to get detailed help for
        category: Filter tools by category
        detail: Detail level (0=names only, 1=with descriptions, 2=verbose)

    Returns:
        Dict containing help information and status
    """
    try:
        if command:
            return _get_command_help(command, detail)
        return _list_commands(category, detail)
    except Exception as e:
        logger.error(f"Help system error: {e}")
        return {"status": "error", "message": f"Help system error: {e!s}"}


def register_help_tools(mcp):
    """Register help tools with FastMCP."""
    # Register the get_help tool with MCP
    mcp.tool(get_help)

    logger.info("help_tools_registered", tools=["get_help"])


def _get_command_help(command: str, detail: int) -> dict[str, Any]:
    """Get detailed help for a specific portmanteau tool."""
    # Portmanteau tools (15 total, replacing ~57 individual tools)
    known_commands = {
        "command_execution": {
            "description": "Comprehensive command execution portmanteau tool with reliable stdout/stderr capture. Main value proposition: solves Claude Desktop PowerShell tool stdout/stderr capture issues. Actions: powershell, cmd",
            "category": "command",
            "actions": ["powershell", "cmd"],
        },
        "file_operations": {
            "description": "Comprehensive file operations portmanteau tool. Actions: read, write, delete, move, copy, info, exists",
            "category": "file",
            "actions": ["read", "write", "delete", "move", "copy", "info", "exists"],
        },
        "directory_operations": {
            "description": "Comprehensive directory operations portmanteau tool. Actions: create, delete, move, copy, list",
            "category": "directory",
            "actions": ["create", "delete", "move", "copy", "list"],
        },
        "file_attributes": {
            "description": "Comprehensive file attributes and dates portmanteau tool. Actions: get_attributes, set_attributes, get_dates, set_dates",
            "category": "attributes",
            "actions": ["get_attributes", "set_attributes", "get_dates", "set_dates"],
        },
        "file_editing": {
            "description": "Comprehensive file editing portmanteau tool. Actions: edit, fix_markdown",
            "category": "editing",
            "actions": ["edit", "fix_markdown"],
        },
        "archive_management": {
            "description": "Comprehensive archive management portmanteau tool. Actions: create, extract, list",
            "category": "archive",
            "actions": ["create", "extract", "list"],
        },
        "json_operations": {
            "description": "Comprehensive JSON operations portmanteau tool. Actions: read, write, validate, format, convert, extract",
            "category": "json",
            "actions": ["read", "write", "validate", "format", "convert", "extract"],
        },
        "media_metadata": {
            "description": "Comprehensive media metadata portmanteau tool. Actions: get_media, update_media, get_image, update_image, get_mp3, update_mp3",
            "category": "media",
            "actions": [
                "get_media",
                "update_media",
                "get_image",
                "update_image",
                "get_mp3",
                "update_mp3",
            ],
        },
        "git_operations": {
            "description": "Comprehensive Git operations portmanteau tool. Actions: add, commit, push, status",
            "category": "git",
            "actions": ["add", "commit", "push", "status"],
        },
        "process_management": {
            "description": "Comprehensive process management portmanteau tool. Actions: list, info, resources",
            "category": "process",
            "actions": ["list", "info", "resources"],
        },
        "windows_services": {
            "description": "Comprehensive Windows Services portmanteau tool. Actions: list, start, stop, restart",
            "category": "services",
            "actions": ["list", "start", "stop", "restart"],
        },
        "windows_event_logs": {
            "description": "Comprehensive Windows Event Logs portmanteau tool. Actions: query, export, clear, monitor",
            "category": "event_logs",
            "actions": ["query", "export", "clear", "monitor"],
        },
        "windows_performance": {
            "description": "Comprehensive Windows Performance portmanteau tool. Actions: get_counters, monitor, get_system",
            "category": "performance",
            "actions": ["get_counters", "monitor", "get_system"],
        },
        "windows_permissions": {
            "description": "Comprehensive Windows Permissions portmanteau tool. Actions: get_file, set_file, analyze_directory, fix",
            "category": "permissions",
            "actions": ["get_file", "set_file", "analyze_directory", "fix"],
        },
        "system_management": {
            "description": "Comprehensive system management portmanteau tool. Actions: info, health, test_port, help",
            "category": "system",
            "actions": ["info", "health", "test_port", "help"],
        },
        "agentic_operations": {
            "description": "Autonomous orchestration and agentic control portmanteau. Enables the LLM to plan and execute multi-step workflows. Actions: workflow, toggle_safety",
            "category": "agentic",
            "actions": ["workflow", "toggle_safety"],
        },
    }

    if command not in known_commands:
        return {
            "status": "error",
            "message": f"Tool '{command}' not found. Use 'winops(command=\"help\")' to list all 15 portmanteau tools.",
        }

    cmd_info = known_commands[command]

    if detail == 0:
        return {
            "status": "success",
            "message": f"{command}: {cmd_info['description'].split('.')[0]}",
        }

    help_text = [
        f"Tool: {command}",
        "=" * (6 + len(command)),
        "",
        cmd_info["description"],
        "",
        f"Category: {cmd_info['category']}",
        "",
    ]

    if "actions" in cmd_info:
        help_text.extend(
            [
                f"Available Actions: {', '.join(cmd_info['actions'])}",
                "",
                "Usage Pattern:",
                f'  result = await {command}(action="<action_name>", ...)',
                "",
            ]
        )

    if detail > 1:
        help_text.extend(
            [
                "Usage Examples:",
                "  # Basic usage - see tool docstring for full parameter details",
                f'  result = await {command}(action="{cmd_info["actions"][0] if "actions" in cmd_info else "action_name"}", ...)',
                "",
                "Note: All portmanteau tools follow the same pattern:",
                "  - Use 'action' parameter to specify which operation to perform",
                "  - Different actions require different parameters",
                "  - Check tool docstring for complete parameter documentation",
                "",
            ]
        )

        if command == "agentic_operations":
            help_text.extend(
                [
                    "Agentic Usage Examples:",
                    "  # Execute a complex workflow",
                    '  result = await agentic_operations(action="workflow", prompt="Analyze system health and fix common issues")',
                    "",
                    "  # Toggle safety guard for autonomous execution",
                    '  result = await agentic_operations(action="toggle_safety", enabled=True, reason="Autonomous maintenance task")',
                    "",
                    "SECURITY WARNING: Agentic tools allow autonomous actions. Use with caution.",
                    "",
                ]
            )

    return {"status": "success", "message": "\n".join(help_text).strip()}


def _list_commands(category: str | None, detail: int) -> dict[str, Any]:
    """List all available portmanteau tools, optionally filtered by category."""
    known_commands = {
        "command_execution": {
            "description": "Command execution (PowerShell/CMD) with reliable stdout/stderr capture",
            "category": "command",
            "actions": ["powershell", "cmd"],
        },
        "file_operations": {
            "description": "File operations (read, write, delete, move, copy, info, exists)",
            "category": "file",
            "actions": ["read", "write", "delete", "move", "copy", "info", "exists"],
        },
        "directory_operations": {
            "description": "Directory operations (create, delete, move, copy, list)",
            "category": "directory",
            "actions": ["create", "delete", "move", "copy", "list"],
        },
        "file_attributes": {
            "description": "File attributes and dates (get/set attributes, get/set dates)",
            "category": "attributes",
            "actions": ["get_attributes", "set_attributes", "get_dates", "set_dates"],
        },
        "file_editing": {
            "description": "File editing (edit, fix_markdown)",
            "category": "editing",
            "actions": ["edit", "fix_markdown"],
        },
        "archive_management": {
            "description": "Archive management (create, extract, list)",
            "category": "archive",
            "actions": ["create", "extract", "list"],
        },
        "json_operations": {
            "description": "JSON operations (read, write, validate, format, convert, extract)",
            "category": "json",
            "actions": ["read", "write", "validate", "format", "convert", "extract"],
        },
        "media_metadata": {
            "description": "Media metadata (get/update for media, images, MP3)",
            "category": "media",
            "actions": [
                "get_media",
                "update_media",
                "get_image",
                "update_image",
                "get_mp3",
                "update_mp3",
            ],
        },
        "git_operations": {
            "description": "Git operations (add, commit, push, status)",
            "category": "git",
            "actions": ["add", "commit", "push", "status"],
        },
        "process_management": {
            "description": "Process management (list, info, resources)",
            "category": "process",
            "actions": ["list", "info", "resources"],
        },
        "windows_services": {
            "description": "Windows Services (list, start, stop, restart)",
            "category": "services",
            "actions": ["list", "start", "stop", "restart"],
        },
        "windows_event_logs": {
            "description": "Windows Event Logs (query, export, clear, monitor)",
            "category": "event_logs",
            "actions": ["query", "export", "clear", "monitor"],
        },
        "windows_performance": {
            "description": "Windows Performance monitoring (counters, monitor, system)",
            "category": "performance",
            "actions": ["get_counters", "monitor", "get_system"],
        },
        "windows_permissions": {
            "description": "Windows Permissions (get/set file, analyze directory, fix)",
            "category": "permissions",
            "actions": ["get_file", "set_file", "analyze_directory", "fix"],
        },
        "system_management": {
            "description": "System management (info, health, test_port, help)",
            "category": "system",
            "actions": ["info", "health", "test_port", "help"],
        },
        "agentic_operations": {
            "description": "Agentic control and autonomous workflows (workflow, toggle_safety)",
            "category": "agentic",
            "actions": ["workflow", "toggle_safety"],
        },
    }

    # Categorize commands
    categorized = {}
    for cmd_name, cmd_info in known_commands.items():
        cat = cmd_info["category"]
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append({"name": cmd_name, "description": cmd_info["description"]})

    result = []

    if category and category.lower() in categorized:
        # Show only the specified category
        cat_name = category.lower()
        result.append(f"{cat_name.upper()} COMMANDS")
        result.append("=" * (len(cat_name) + 9))
        result.append(TOOL_CATEGORIES.get(cat_name, ""))
        result.append("")

        for tool_info in categorized[cat_name]:
            if detail == 0:
                result.append(f"  {tool_info['name']}")
            else:
                result.append(f"  {tool_info['name']}")
                if detail > 0 and tool_info["description"]:
                    result.append(f"    {tool_info['description']}")
                result.append("")

        if detail > 0:
            result.append("")
            result.append("For detailed help about a specific tool:")
            result.append("  winops(command='help', tool_name='<tool_name>', detail=2)")
    else:
        # Show all categories
        if category:
            result.append(f"Unknown category: {category}")
            result.append("")

        result.append("WINDOWS OPERATIONS MCP - PORTMANTEAU TOOLS")
        result.append("==========================================")
        result.append("")
        result.append("15 portmanteau tools (replacing ~57 individual tools)")
        result.append("All tools use the 'action' parameter to specify operations")
        result.append("")

        for cat in sorted(categorized.keys()):
            tools = categorized[cat]
            if not tools:
                continue

            result.append(f"{cat.upper()} - {TOOL_CATEGORIES.get(cat, '')}")
            result.append("-" * (len(cat) + len(TOOL_CATEGORIES.get(cat, "")) + 3))

            for tool_info in tools:
                if detail == 0:
                    result.append(f"  {tool_info['name']}")
                else:
                    result.append(f"  {tool_info['name']}")
                    if detail > 0 and tool_info["description"]:
                        result.append(f"    {tool_info['description']}")
                    if detail > 0 and "actions" in tool_info:
                        actions_str = ", ".join(tool_info["actions"])
                        result.append(f"    Actions: {actions_str}")
                    result.append("")

            result.append("")

        if detail > 0:
            result.append("Usage:")
            result.append("  Use 'winops' tool for easy access to help")
            result.append("  Example: winops(command='help', tool_name='file_operations', detail=2)")
            result.append("")
            result.append("For detailed help about a specific tool:")
            result.append("  winops(command='help', tool_name='<tool_name>', detail=2)")
            result.append("")
            result.append("To list tools by category:")
            result.append("  winops(command='help', category='<category>', detail=1)")
            result.append("")
            result.append("Quick commands:")
            result.append("  winops(command='help')        - List all tools")
            result.append("  winops(command='list')        - List all tools (alias)")
            result.append("  winops(command='tools')       - List all tools (alias)")

    return {"status": "success", "message": "\n".join(result).strip()}
