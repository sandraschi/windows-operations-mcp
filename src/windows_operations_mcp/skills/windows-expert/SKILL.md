---
name: windows-expert
description: Expert instructions for the Windows Operations MCP server, covering PowerShell best practices, diagnostic workflows, and error handling.
---

# Windows Operations Expert (SOTA v14.0)

This skill provides the theoretical and practical framework for executing high-integrity Windows system operations.

## ⚡ Core Philosophy
- **Industrial Reductionism**: All system states are observable data points.
- **PowerShell-First**: Favor PowerShell for all complex queries and administrative tasks due to its object-oriented nature.
- **Telemetry-Aware**: Always monitor `ctx.info` and `ctx.report_progress` during execution.

## 🛠️ Diagnostic Workflows

### 1. Process Anomalies
If a process is consuming excessive resources:
- Use `process_management` with `action="get_details"` to examine the thread count and memory working set.
- Check child processes via `process_management` with `action="list_tree"`.
- Use `ctx.sample()` to ask for advice if the process name is unknown.

### 2. Service Management
When troubleshooting a failed Windows service:
- Use `windows_services` with `action="get_status"`.
- Check the event log via `command_execution` using:
  `Get-WinEvent -FilterHashtable @{LogName='System'; ID=7036; ProviderName='Service Control Manager'} -MaxEvents 5`

### 3. File & Archive Ops
For large file operations:
- Always use `working_directory` to ensure relative paths are resolved correctly.
- Check archive integrity with `archive_management` with `action="test"` before extraction.

## ⚠️ Safety Protocols
- **Timeout Management**: Do not exceed 300s for any command execution.
- **Path Resolution**: Always use absolute paths unless `working_directory` is explicitly set and verified.
- **Zero Deletion Without Verification**: Never use `-Force` (Remove-Item) unless the target has been explicitly audited in the previous step.
