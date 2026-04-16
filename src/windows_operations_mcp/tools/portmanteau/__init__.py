"""
Portmanteau tools for Windows Operations MCP.

These tools consolidate multiple related operations into single, action-based interfaces
following the virtualization-mcp pattern. This reduces the API surface from ~57 tools
to 15 portmanteau tools for better discoverability and maintainability.
"""

__all__ = [
    "agentic_operations",
    "archive_management",
    "command_execution",
    "directory_operations",
    "file_attributes",
    "file_editing",
    "file_operations",
    "git_operations",
    "json_operations",
    "media_metadata",
    "system_management",
    "windows_accounts",
    "windows_apps",
    "windows_automation",
    "windows_environment",
    "windows_network",
]
