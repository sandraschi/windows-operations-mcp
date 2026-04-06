# Windows Operations MCP - Help Guide (SOTA v1.20.0-April-2026)

## Overview

Windows Operations MCP provides **10 core portmanteau tools** for comprehensive system management through the Model Context Protocol. The system is architecture-unified on ports **10748** (Backend) and **10749** (Fleet Dashboard).

## Quick Start

All tools follow the same pattern: use the `action` parameter to specify which operation to perform.

```python
# Example: PowerShell execution
result = await command_execution(
    action="powershell",
    command="Get-Service | Select-Object -First 5"
)

# Example: Process listing
result = await process_management(
    action="list",
    name_filter="python"
)
```

## Available Portmanteau Tools (10 Total)

### 1. **command_execution**
- **Actions**: `powershell`, `cmd`
- **Goal**: High-fidelity shell execution with reliable stdout/stderr capture.

### 2. **process_management**
- **Actions**: `list`, `info`, `resources`
- **Goal**: Real-time process monitoring and system resource utilization.

### 3. **system_management**
- **Actions**: `health`, `info`, `test_port`, `help`
- **Goal**: Diagnostics, system telemetry, and network testing.

### 4. **file_operations**
- **Actions**: `read`, `write`, `delete`, `move`, `copy`, `info`, `exists`
- **Goal**: Basic file management with integrated error handling.

### 5. **directory_operations**
- **Actions**: `create`, `delete`, `move`, `copy`, `list`
- **Goal**: Bulk directory management and tree traversal.

### 6. **archive_management**
- **Actions**: `create`, `extract`, `list`
- **Goal**: ZIP, TAR, GZ compression with intelligent exclusion support.

### 7. **json_operations**
- **Actions**: `read`, `write`, `validate`, `format`, `extract`
- **Goal**: High-speed JSON workloads and JSONPath extraction.

### 8. **windows_services**
- **Actions**: `list`, `start`, `stop`, `restart`
- **Goal**: System service lifecycle management.

### 9. **git_operations**
- **Actions**: `commit`, `push`, `status`
- **Goal**: Native Git synchronization for local repositories.

### 10. **agentic_operations**
- **Actions**: `workflow`, `toggle_safety`
- **Goal**: [SEP-1577] Autonomous mission management and safety orchestration.

---

## Response Format

All tools return a consistent response format:
```json
{
    "success": true,
    "action": "list",
    "data": { ... },
    "error": null
}
```

## Fleet Dashboard

Monitor real-time telemetry and execute tools with a premium visual interface at **http://localhost:10749**.

---

**Built with FastMCP 3.1.1**  
*January 2026 Fleet Standard v1.20.0*
