# Windows Operations MCP - Help Guide

## Overview

Windows Operations MCP provides **15 portmanteau tools** (consolidated from ~57 individual tools) for comprehensive Windows system management through the Model Context Protocol.

## Quick Start

All tools follow the same pattern: use the `action` parameter to specify which operation to perform.

```python
# Example: Execute PowerShell command
result = await command_execution(
    action="powershell",
    command="Get-Process | Select-Object -First 5"
)

# Example: List files
result = await file_operations(
    action="list",
    path="C:\\Users"
)
```

## Available Portmanteau Tools

### 1. **command_execution** - PowerShell/CMD Execution
**Main Value Proposition**: Reliable stdout/stderr capture (solves Claude Desktop PowerShell tool issues)

**Actions**: `powershell`, `cmd`

**Example**:
```python
result = await command_execution(
    action="powershell",
    command="Get-Process | Select-Object -First 5",
    timeout_seconds=30
)
```

### 2. **file_operations** - Basic File Operations
**Actions**: `read`, `write`, `delete`, `move`, `copy`, `info`, `exists`

**Example**:
```python
# Read file
result = await file_operations(action="read", path="C:\\file.txt")

# Write file
result = await file_operations(
    action="write",
    path="C:\\file.txt",
    content="Hello, World!"
)
```

### 3. **directory_operations** - Directory Management
**Actions**: `create`, `delete`, `move`, `copy`, `list`

**Example**:
```python
# List directory
result = await directory_operations(
    action="list",
    path="C:\\Users",
    include_hidden=False
)
```

### 4. **file_attributes** - File Attributes & Dates
**Actions**: `get_attributes`, `set_attributes`, `get_dates`, `set_dates`

**Example**:
```python
# Get file attributes
result = await file_attributes(
    action="get_attributes",
    file_path="C:\\file.txt"
)
```

### 5. **file_editing** - File Editing
**Actions**: `edit`, `fix_markdown`

**Example**:
```python
# Fix Markdown formatting
result = await file_editing(
    action="fix_markdown",
    file_path="C:\\readme.md"
)
```

### 6. **archive_management** - ZIP Operations
**Actions**: `create`, `extract`, `list`

**Example**:
```python
# Create archive
result = await archive_management(
    action="create",
    archive_path="C:\\backup.zip",
    source_paths=["C:\\project"],
    exclude_patterns=["*.pyc", "__pycache__"]
)
```

### 7. **json_operations** - JSON Tools
**Actions**: `read`, `write`, `validate`, `format`, `convert`, `extract`

**Example**:
```python
# Read JSON file
result = await json_operations(
    action="read",
    file_path="C:\\config.json"
)
```

### 8. **media_metadata** - Media Metadata
**Actions**: `get_media`, `update_media`, `get_image`, `update_image`, `get_mp3`, `update_mp3`

**Example**:
```python
# Get image metadata
result = await media_metadata(
    action="get_image",
    file_path="C:\\photo.jpg"
)
```

### 9. **git_operations** - Git Tools
**Actions**: `add`, `commit`, `push`, `status`

**Example**:
```python
# Commit changes
result = await git_operations(
    action="commit",
    message="Update documentation"
)
```

### 10. **process_management** - Process Tools
**Actions**: `list`, `info`, `resources`

**Example**:
```python
# List processes
result = await process_management(
    action="list",
    filter_name="python",
    max_processes=50
)
```

### 11. **windows_services** - Windows Services
**Actions**: `list`, `start`, `stop`, `restart`

**Example**:
```python
# Start service
result = await windows_services(
    action="start",
    service_name="Spooler"
)
```

### 12. **windows_event_logs** - Event Logs
**Actions**: `query`, `export`, `clear`, `monitor`

**Example**:
```python
# Query event log
result = await windows_event_logs(
    action="query",
    log_name="Application",
    max_events=50
)
```

### 13. **windows_performance** - Performance Monitoring
**Actions**: `get_counters`, `monitor`, `get_system`

**Example**:
```python
# Get performance counters
result = await windows_performance(
    action="get_counters",
    counter_names=["% Processor Time"],
    object_name="Processor"
)
```

### 14. **windows_permissions** - Permissions Management
**Actions**: `get_file`, `set_file`, `analyze_directory`, `fix`

**Example**:
```python
# Get file permissions
result = await windows_permissions(
    action="get_file",
    file_path="C:\\file.txt"
)
```

### 15. **system_management** - System Tools
**Actions**: `info`, `health`, `test_port`, `help`

**Example**:
```python
# Get system info
result = await system_management(
    action="info",
    detailed=True
)

# Get help
result = await system_management(
    action="help",
    command="file_operations",
    detail=2
)
```

## Common Patterns

### Error Handling
All tools return a consistent response format:
```python
{
    "success": bool,      # Operation succeeded
    "action": str,        # Action performed
    "data": dict,         # Result data
    "error": str          # Error message if failed
}
```

### Parameter Requirements
- **Required parameters** are specified in each tool's docstring
- **Optional parameters** have defaults and are clearly marked
- **Operation-specific parameters** are documented with "Required for: X operation"

### Type Hints
All parameters use clear type hints:
- `str | None` - Optional string
- `list[str]` - List of strings
- `int` - Integer
- `bool` - Boolean
- `Literal["action1", "action2"]` - Enum of allowed values

## Getting Help

### Via system_management Tool
```python
# List all commands
result = await system_management(action="help")

# Get help for specific command
result = await system_management(
    action="help",
    command="file_operations",
    detail=2
)

# Get help by category
result = await system_management(
    action="help",
    category="file",
    detail=1
)
```

### Help Detail Levels
- **detail=1** (default): Basic descriptions
- **detail=2**: Intermediate with examples
- **detail=3**: Advanced with full documentation

## Tool Categories

- **Command Execution**: PowerShell/CMD execution
- **File Operations**: Basic file/directory operations
- **File Management**: Attributes, editing, archiving
- **Data Formats**: JSON operations
- **Media**: Image/audio metadata
- **Version Control**: Git operations
- **System Monitoring**: Processes, performance, services
- **Windows-Specific**: Event logs, permissions, services
- **System Management**: Info, health, network, help

## Best Practices

1. **Always check `success` field** before using result data
2. **Use appropriate timeouts** for long-running operations
3. **Handle errors gracefully** - check error messages
4. **Use filters** to reduce result sizes (e.g., `max_processes`, `max_events`)
5. **Specify working directories** for file operations when needed

## Troubleshooting

### Tool Not Found
- Ensure the MCP server is running
- Check that portmanteau tools are registered (15 tools total)
- Verify FastMCP 2.12+ is installed

### Operation Failed
- Check the `error` field in the response
- Verify required parameters are provided
- Check file paths and permissions
- Review logs for detailed error information

### Performance Issues
- Use filters to limit result sizes
- Set appropriate timeouts
- Use `max_output_size` for command execution
- Monitor system resources with `process_management` and `windows_performance`

## Additional Resources

- **README.md**: Full project documentation
- **Tool Docstrings**: Comprehensive inline documentation in each tool
- **Examples**: See tool docstrings for usage examples
- **MCP Central Docs**: Standards and best practices

---

**Total Tools**: 15 portmanteau tools (replacing ~57 individual tools)  
**Status**: Production Ready  
**Version**: 0.2.0+

