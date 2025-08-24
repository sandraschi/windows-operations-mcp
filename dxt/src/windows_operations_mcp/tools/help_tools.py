"""Enhanced help system for the Windows Operations MCP."""
from typing import Dict, List, Optional, Any
from textwrap import dedent

from ..logging_config import get_logger

logger = get_logger(__name__)

# Tool categories for organization
TOOL_CATEGORIES = {
    "powershell": "PowerShell and CMD command execution",
    "git": "Git version control operations", 
    "file": "File operations (read, write, search, etc.)",
    "system": "System information and management",
    "network": "Network-related operations",
    "process": "Process management",
    "archive": "Archive and compression operations",
    "help": "Help system"
}

def register_help_tools(mcp):
    """Register help tools with FastMCP."""
    
    @mcp.tool()
    def get_help(command: Optional[str] = None, category: Optional[str] = None, detail: int = 1) -> Dict[str, Any]:
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
            return {
                "status": "error",
                "message": f"Help system error: {str(e)}"
            }
    
    logger.info("help_tools_registered", tools=["get_help"])

def _get_command_help(command: str, detail: int) -> Dict[str, Any]:
    """Get detailed help for a specific command."""
    # This would normally query the tool registry, but for now return basic info
    known_commands = {
        "run_powershell_tool": {
            "description": "Execute PowerShell commands with reliable output capture and security checks.",
            "category": "powershell"
        },
        "run_cmd_tool": {
            "description": "Execute CMD commands with reliable output capture and security checks.", 
            "category": "powershell"
        },
        "get_system_info": {
            "description": "Get comprehensive system information including OS, hardware, and performance metrics.",
            "category": "system"
        },
        "health_check": {
            "description": "Check the health status and diagnostics of the Windows Operations MCP server.",
            "category": "system"
        },
        "test_port": {
            "description": "Test network port accessibility with detailed diagnostics.",
            "category": "network"
        },
        "get_process_list": {
            "description": "Get list of running processes with filtering options.",
            "category": "process"
        },
        "get_process_info": {
            "description": "Get detailed information about a specific process.",
            "category": "process"
        },
        "get_system_resources": {
            "description": "Get comprehensive system resource usage information.",
            "category": "process"
        },
        "get_help": {
            "description": "Get help about available commands and their usage.",
            "category": "help"
        }
    }
    
    if command not in known_commands:
        return {
            "status": "error",
            "message": f"Command '{command}' not found. Use 'get_help' to list available commands."
        }
    
    cmd_info = known_commands[command]
    
    if detail == 0:
        return {
            "status": "success", 
            "message": f"{command}: {cmd_info['description'].split('.')[0]}"
        }
    
    help_text = [
        f"Command: {command}",
        "=" * (8 + len(command)),
        "",
        cmd_info['description'],
        "",
        f"Category: {cmd_info['category']}",
        ""
    ]
    
    if detail > 1:
        help_text.extend([
            "Usage Examples:",
            f"  Use the '{command}' tool through the MCP interface",
            f"  Check tool parameters for specific options and requirements",
            ""
        ])
    
    return {
        "status": "success",
        "message": "\n".join(help_text).strip()
    }

def _list_commands(category: Optional[str], detail: int) -> Dict[str, Any]:
    """List all available commands, optionally filtered by category."""
    known_commands = {
        "run_powershell_tool": {"description": "Execute PowerShell commands with reliable output capture and security checks.", "category": "powershell"},
        "run_cmd_tool": {"description": "Execute CMD commands with reliable output capture and security checks.", "category": "powershell"},
        "get_system_info": {"description": "Get comprehensive system information including OS, hardware, and performance metrics.", "category": "system"},
        "health_check": {"description": "Check the health status and diagnostics of the Windows Operations MCP server.", "category": "system"},
        "test_port": {"description": "Test network port accessibility with detailed diagnostics.", "category": "network"},
        "get_process_list": {"description": "Get list of running processes with filtering options.", "category": "process"},
        "get_process_info": {"description": "Get detailed information about a specific process.", "category": "process"},
        "get_system_resources": {"description": "Get comprehensive system resource usage information.", "category": "process"},
        "get_help": {"description": "Get help about available commands and their usage.", "category": "help"}
    }
    
    # Categorize commands
    categorized = {}
    for cmd_name, cmd_info in known_commands.items():
        cat = cmd_info['category']
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append({
            'name': cmd_name,
            'description': cmd_info['description']
        })
    
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
                if detail > 0 and tool_info['description']:
                    result.append(f"    {tool_info['description']}")
                result.append("")
        
        if detail > 0:
            result.append("")
            result.append("Use 'get_help command=\"<command>\"' for more information about a specific command.")
    else:
        # Show all categories
        if category:
            result.append(f"Unknown category: {category}")
            result.append("")
            
        result.append("WINDOWS OPERATIONS MCP - AVAILABLE COMMANDS")
        result.append("=========================================")
        result.append("")
        
        for cat in sorted(categorized.keys()):
            tools = categorized[cat]
            if not tools:
                continue
                
            result.append(f"{cat.upper()} - {TOOL_CATEGORIES.get(cat, '')}")
            result.append("-" * (len(cat) + len(TOOL_CATEGORIES.get(cat, '')) + 3))
            
            for tool_info in tools:
                if detail == 0:
                    result.append(f"  {tool_info['name']}")
                else:
                    result.append(f"  {tool_info['name']}")
                    if detail > 0 and tool_info['description']:
                        result.append(f"    {tool_info['description']}")
                    result.append("")
            
            result.append("")
        
        if detail > 0:
            result.append("Use 'get_help command=\"<command>\"' for more information about a specific command.")
            result.append("Use 'get_help category=\"<category>\"' to list commands in a specific category.")
            result.append("Use 'get_help detail=2' for more detailed help.")
    
    return {
        "status": "success",
        "message": "\n".join(result).strip()
    }
