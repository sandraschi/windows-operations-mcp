"""
WinOps - Simple wrapper tool for easy access to Windows Operations MCP.

Provides simple commands like "winops help" or "winops process list" instead of
complex tool names and action parameters.
"""

import logging
from typing import Any, Optional

from fastmcp import FastMCP

# Import the help function
from ..help_tools import get_help

logger = logging.getLogger(__name__)

# Command routing map: maps natural commands to (tool_name, action, params)
COMMAND_ROUTES = {
    # Help commands
    "help": ("system_management", "help", {}),
    "list": ("system_management", "help", {}),
    "tools": ("system_management", "help", {}),
    
    # Process commands
    "process list": ("process_management", "list", {}),
    "process info": ("process_management", "info", {}),
    "process resources": ("process_management", "resources", {}),
    
    # File commands
    "file read": ("file_operations", "read", {}),
    "file write": ("file_operations", "write", {}),
    "file delete": ("file_operations", "delete", {}),
    "file exists": ("file_operations", "exists", {}),
    "file info": ("file_operations", "info", {}),
    
    # Directory commands
    "dir list": ("directory_operations", "list", {}),
    "dir create": ("directory_operations", "create", {}),
    "dir delete": ("directory_operations", "delete", {}),
    
    # System commands (with short aliases)
    "system info": ("system_management", "info", {}),
    "system health": ("system_management", "health", {}),
    "info": ("system_management", "info", {}),
    "health": ("system_management", "health", {}),
    
    # Services commands
    "services list": ("windows_services", "list", {}),
    "services start": ("windows_services", "start", {}),
    "services stop": ("windows_services", "stop", {}),
    "services restart": ("windows_services", "restart", {}),
}


def register_winops_tool(mcp: FastMCP) -> None:
    """Register the winops simple wrapper tool."""

    @mcp.tool()
    async def winops(
        command: str,
        tool_name: Optional[str] = None,
        category: Optional[str] = None,
        detail: int = 1,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Simple wrapper tool for Windows Operations MCP - easy access to common commands.
        
        PORTMANTEAU PATTERN RATIONALE:
        This tool provides a simple, user-friendly interface for common Windows Operations MCP
        commands. Instead of requiring users to remember complex tool names and action parameters,
        this tool allows natural language commands like "winops help" or "winops process list".
        This design:
        - Improves user experience with simple, memorable commands
        - Reduces cognitive load for common operations
        - Provides a single entry point for help and discovery
        - Follows FastMCP 2.12+ best practices for user-friendly interfaces
        
        Args:
            command (str): The command to execute. Required. Examples:
                - "help": Get help about tools
                - "process list": List running processes
                - "file read": Read a file
                - "services list": List Windows services
                - See COMMAND_ROUTES for all supported commands
            
            tool_name (str | None): Specific tool name to get help for. Optional.
                Used by: help command. Example: "file_operations", "command_execution"
            
            category (str | None): Filter tools by category. Optional.
                Used by: help command. Example: "file", "system", "command"
            
            detail (int): Help detail level. Optional. Default: 1
                Used by: help command. Valid: 1 (basic), 2 (intermediate), 3 (advanced)
            
            **kwargs: Additional parameters passed to the underlying tool.
                Example: For "process list", you can pass filter_name, max_processes, etc.
        
        Returns:
            Dict containing:
                - success (bool): Boolean indicating if command succeeded
                - command (str): The command that was executed
                - data (dict | Any): Command-specific result data
                - error (str): Error message if success is False
        
        Examples:
            # Get general help
            result = await winops(command="help")
            
            # List processes
            result = await winops(command="process list", filter_name="python")
            
            # List services
            result = await winops(command="services list")
            
            # Get system info
            result = await winops(command="system info", detailed=True)
        """
        try:
            command_lower = command.lower().strip()
            
            # Check if command is in routing map
            if command_lower in COMMAND_ROUTES:
                tool_name_route, action, default_params = COMMAND_ROUTES[command_lower]
                
                # Merge default params with kwargs
                params = {**default_params, **kwargs, "action": action}
                
                # Import and call the appropriate tool
                from importlib import import_module
                module_path = f"windows_operations_mcp.tools.portmanteau.{tool_name_route}"
                module = import_module(module_path)
                
                # Get the tool function (it's registered with @mcp.tool() so we need to find it)
                # Actually, we need to call the underlying function directly
                # Let's import the actual tool functions
                if tool_name_route == "system_management":
                    from ..portmanteau.system_management import register_system_management_tool
                    # We need to call the actual function, not the registration
                    # Let's import the functions directly
                    from ..system_tools import get_system_info, health_check
                    from ..network_tools import test_port
                    
                    if action == "help":
                        result = get_help(command=tool_name, category=category, detail=detail)
                        return {
                            "success": result.get("status") == "success",
                            "command": command,
                            "data": result,
                            "message": result.get("message", ""),
                        }
                    elif action == "info":
                        detailed = kwargs.get("detailed", False)
                        result = get_system_info(detailed=detailed)
                        return {"success": result.get("success", False), "command": command, "data": result}
                    elif action == "health":
                        result = health_check(
                            detailed=kwargs.get("detailed", False),
                            check_services=kwargs.get("check_services", True),
                            check_disk_space=kwargs.get("check_disk_space", True),
                            check_network=kwargs.get("check_network", True)
                        )
                        return {"success": result.get("success", False), "command": command, "data": result}
                
                elif tool_name_route == "process_management":
                    from ..process_tools import get_process_list, get_process_info, get_system_resources
                    
                    if action == "list":
                        result = get_process_list(
                            filter_name=kwargs.get("filter_name"),
                            include_system=kwargs.get("include_system", False),
                            max_processes=kwargs.get("max_processes", 100)
                        )
                        return {"success": True, "command": command, "data": result}
                    elif action == "info":
                        if "pid" not in kwargs:
                            return {"success": False, "command": command, "error": "pid is required for process info"}
                        result = get_process_info(pid=kwargs["pid"])
                        return {"success": True, "command": command, "data": result}
                    elif action == "resources":
                        result = get_system_resources()
                        return {"success": True, "command": command, "data": result}
                
                elif tool_name_route == "file_operations":
                    from ..file_operations import read_file, write_file, delete_file, get_file_info
                    from ..file_operations.info import file_exists
                    
                    if action == "read":
                        if "path" not in kwargs:
                            return {"success": False, "command": command, "error": "path is required for file read"}
                        result = read_file(
                            file_path=kwargs["path"],
                            encoding=kwargs.get("encoding", "utf-8"),
                            max_size=kwargs.get("max_size")
                        )
                        return {"success": True, "command": command, "data": result}
                    elif action == "write":
                        if "path" not in kwargs or "content" not in kwargs:
                            return {"success": False, "command": command, "error": "path and content are required for file write"}
                        result = write_file(
                            file_path=kwargs["path"],
                            content=kwargs["content"],
                            encoding=kwargs.get("encoding", "utf-8"),
                            overwrite=kwargs.get("overwrite", False)
                        )
                        return {"success": True, "command": command, "data": result}
                    elif action == "delete":
                        if "path" not in kwargs:
                            return {"success": False, "command": command, "error": "path is required for file delete"}
                        result = delete_file(file_path=kwargs["path"])
                        return {"success": True, "command": command, "data": result}
                    elif action == "exists":
                        if "path" not in kwargs:
                            return {"success": False, "command": command, "error": "path is required for file exists"}
                        exists = file_exists(kwargs["path"])
                        result = {"exists": exists, "path": kwargs["path"]}
                        return {"success": True, "command": command, "data": result}
                    elif action == "info":
                        if "path" not in kwargs:
                            return {"success": False, "command": command, "error": "path is required for file info"}
                        result = get_file_info(file_path=kwargs["path"])
                        return {"success": True, "command": command, "data": result}
                
                elif tool_name_route == "directory_operations":
                    from ..file_operations.folder_operations import list_directory_contents, create_directory_safe, delete_directory_safe
                    
                    if action == "list":
                        if "path" not in kwargs:
                            return {"success": False, "command": command, "error": "path is required for directory list"}
                        result = list_directory_contents(
                            directory_path=kwargs["path"],
                            include_hidden=kwargs.get("include_hidden", False),
                            pattern=kwargs.get("pattern")
                        )
                        return {"success": True, "command": command, "data": result}
                    elif action == "create":
                        if "path" not in kwargs:
                            return {"success": False, "command": command, "error": "path is required for directory create"}
                        result = create_directory_safe(
                            directory_path=kwargs["path"],
                            create_parents=kwargs.get("create_parents", True),
                            exist_ok=kwargs.get("exist_ok", True)
                        )
                        return {"success": True, "command": command, "data": result}
                    elif action == "delete":
                        if "path" not in kwargs:
                            return {"success": False, "command": command, "error": "path is required for directory delete"}
                        result = delete_directory_safe(
                            directory_path=kwargs["path"],
                            recursive=kwargs.get("recursive", False),
                            require_empty=kwargs.get("require_empty", True)
                        )
                        return {"success": True, "command": command, "data": result}
                
                elif tool_name_route == "windows_services":
                    from ..windows_services import list_windows_services, start_windows_service, stop_windows_service, restart_windows_service
                    
                    if action == "list":
                        result = list_windows_services(
                            filter_status=kwargs.get("filter_status", "all"),
                            filter_name=kwargs.get("filter_name"),
                            include_system_services=kwargs.get("include_system_services", True)
                        )
                        return {"success": True, "command": command, "data": result}
                    elif action == "start":
                        if "service_name" not in kwargs:
                            return {"success": False, "command": command, "error": "service_name is required for services start"}
                        result = start_windows_service(
                            service_name=kwargs["service_name"],
                            wait_timeout=kwargs.get("wait_timeout", 30)
                        )
                        return {"success": result.get("success", False), "command": command, "data": result}
                    elif action == "stop":
                        if "service_name" not in kwargs:
                            return {"success": False, "command": command, "error": "service_name is required for services stop"}
                        result = stop_windows_service(
                            service_name=kwargs["service_name"],
                            wait_timeout=kwargs.get("wait_timeout", 30)
                        )
                        return {"success": result.get("success", False), "command": command, "data": result}
                    elif action == "restart":
                        if "service_name" not in kwargs:
                            return {"success": False, "command": command, "error": "service_name is required for services restart"}
                        result = restart_windows_service(
                            service_name=kwargs["service_name"],
                            stop_timeout=kwargs.get("stop_timeout", 30),
                            start_timeout=kwargs.get("start_timeout", 30)
                        )
                        return {"success": result.get("success", False), "command": command, "data": result}
            
            # Fallback to help system for unknown commands
            if command_lower in ["help", "list", "tools"]:
                result = get_help(command=tool_name, category=category, detail=detail)
                return {
                    "success": result.get("status") == "success",
                    "command": command,
                    "data": result,
                    "message": result.get("message", ""),
                }
            
            # Unknown command
            available = ", ".join(sorted(COMMAND_ROUTES.keys()))
            return {
                "success": False,
                "command": command,
                "error": f"Unknown command '{command}'",
                "message": f"Supported commands: {available}\n\nUse 'winops(command=\"help\")' to see all available tools and actions."
            }
            
        except Exception as e:
            logger.error(f"Error in winops command '{command}': {e}", exc_info=True)
            return {
                "success": False,
                "command": command,
                "error": f"Failed to execute command '{command}': {str(e)}",
            }

