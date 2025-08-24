# Windows Operations MCP - Tool Reference

This document provides detailed documentation for all available tools in the Windows Operations MCP.

## Table of Contents

1. [Command Execution](#command-execution)
2. [File Operations](#file-operations)
3. [Network Tools](#network-tools)
4. [System Information](#system-information)
5. [Process Management](#process-management)
6. [Security Considerations](#security-considerations)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

## Command Execution

### `run_powershell`
Execute PowerShell commands with robust output capture.

**Parameters:**
- `command` (str): The PowerShell command to execute
- `working_directory` (str, optional): Working directory for the command
- `timeout_seconds` (int, default=30): Maximum execution time
- `capture_output` (bool, default=True): Whether to capture command output

**Returns:**
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "command output",
  "stderr": "",
  "execution_time_seconds": 0.123
}
```

**Example:**
```python
result = run_powershell("Get-Process | Select-Object -First 5")
```

### `run_cmd`
Execute CMD commands with reliable output capture.

**Parameters:**
- `command` (str): The CMD command to execute
- `working_directory` (str, optional): Working directory for the command
- `timeout_seconds` (int, default=30): Maximum execution time
- `capture_output` (bool, default=True): Whether to capture command output

**Returns:** Same as `run_powershell`

**Example:**
```python
result = run_cmd("dir /b", working_directory="C:\\Windows")
```

## File Operations

### `list_directory`
List contents of a directory with filtering options.

**Parameters:**
- `path` (str): Directory path
- `include_hidden` (bool, default=False): Include hidden files/directories
- `file_pattern` (str, optional): Filter files by glob pattern (e.g., "*.txt")
- `max_depth` (int, optional): Maximum directory depth to search

**Returns:**
```json
{
  "success": true,
  "path": "C:\\temp",
  "files": [
    {
      "name": "file.txt",
      "is_dir": false,
      "size_bytes": 1024,
      "modified_time": "2023-01-01T12:00:00"
    }
  ]
}
```

### `read_file_content`
Read file contents with encoding detection.

**Parameters:**
- `file_path` (str): Path to the file
- `encoding` (str, optional): Force specific encoding
- `max_size_mb` (int, default=10): Maximum file size in MB

**Returns:**
```json
{
  "success": true,
  "content": "file contents",
  "encoding": "utf-8",
  "size_bytes": 1024
}
```

### `write_file_content`
Write content to a file.

**Parameters:**
- `file_path` (str): Path to the file
- `content` (str): Content to write
- `encoding` (str, default="utf-8"): File encoding
- `backup_existing` (bool, default=False): Create backup if file exists

**Returns:**
```json
{
  "success": true,
  "file_path": "C:\\temp\\file.txt",
  "backup_created": false
}
```

## Network Tools

### `test_port`
Test network port accessibility.

**Parameters:**
- `host` (str): Hostname or IP address
- `port` (int): Port number (1-65535)
- `protocol` (str, default="tcp"): "tcp" or "udp"
- `timeout_seconds` (int, default=5): Connection timeout

**Returns:**
```json
{
  "success": true,
  "host": "example.com",
  "port": 80,
  "protocol": "tcp",
  "reachable": true,
  "response_time_ms": 15.5
}
```

## System Information

### `get_system_info`
Get comprehensive system information.

**Returns:**
```json
{
  "success": true,
  "system": {
    "os": "Windows 10",
    "hostname": "COMPUTER-NAME",
    "architecture": "64-bit"
  },
  "hardware": {
    "cpu_cores": 8,
    "total_memory_gb": 16.0,
    "disks": [
      {
        "device": "C:\\",
        "total_gb": 500.0,
        "used_gb": 250.0,
        "free_gb": 250.0
      }
    ]
  }
}
```

### `health_check`
Check system health and dependencies.

**Returns:**
```json
{
  "success": true,
  "status": "healthy",
  "checks": [
    {
      "name": "disk_space",
      "status": "ok",
      "message": "Sufficient disk space available"
    },
    {
      "name": "memory",
      "status": "warning",
      "message": "Memory usage at 85%"
    }
  ]
}
```

## Process Management

### `get_process_list`
List running processes.

**Parameters:**
- `name_filter` (str, optional): Filter processes by name
- `user` (str, optional): Filter processes by username

**Returns:**
```json
{
  "success": true,
  "processes": [
    {
      "pid": 1234,
      "name": "python.exe",
      "username": "user",
      "cpu_percent": 1.5,
      "memory_mb": 100.5
    }
  ]
}
```

### `get_process_info`
Get detailed information about a process.

**Parameters:**
- `pid` (int): Process ID

**Returns:**
```json
{
  "success": true,
  "pid": 1234,
  "name": "python.exe",
  "command_line": "python script.py",
  "status": "running",
  "cpu_percent": 1.5,
  "memory_mb": 100.5,
  "threads": 5,
  "create_time": "2023-01-01T12:00:00"
}
```

## Security Considerations

### Command Execution Safety
- All commands are executed with restricted permissions
- Command injection attempts are blocked
- Dangerous commands (e.g., `rm -rf /`) are prevented

### File Operations
- Path traversal attacks are prevented
- Symbolic links are resolved safely
- File permissions are respected

### Rate Limiting
- All operations are rate limited to prevent abuse
- Default limits:
  - 10 PowerShell commands per minute
  - 15 CMD commands per minute
  - 20 file operations per minute

## Error Handling

All tools return a standardized response format:

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ErrorType",
  "tool": "function_name",
  "timestamp": "2023-01-01T12:00:00",
  "execution_time_seconds": 0.123
}
```

Common error types:
- `ValidationError`: Invalid input parameters
- `PermissionError`: Insufficient permissions
- `TimeoutError`: Operation timed out
- `RateLimitError`: Rate limit exceeded
- `FileNotFoundError`: File or directory not found

## Rate Limiting

Rate limits are applied per client IP address. When a limit is exceeded:

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "error_type": "RateLimitError",
  "retry_after_seconds": 30,
  "max_calls": 10,
  "time_window_seconds": 60
}
```

Clients should implement exponential backoff when receiving rate limit errors.
