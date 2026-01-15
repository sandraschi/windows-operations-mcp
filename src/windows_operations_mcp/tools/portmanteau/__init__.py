"""
Portmanteau tools for Windows Operations MCP.

These tools consolidate multiple related operations into single, action-based interfaces
following the virtualization-mcp pattern. This reduces the API surface from ~57 tools
to 15 portmanteau tools for better discoverability and maintainability.
"""

__all__ = [
    "command_execution",
    "file_operations",
    "directory_operations",
    "file_attributes",
    "file_editing",
    "archive_management",
    "json_operations",
    "media_metadata",
    "git_operations",
    "process_management",
    "windows_services",
    "windows_event_logs",
    "windows_performance",
    "windows_permissions",
    "system_management",
]

