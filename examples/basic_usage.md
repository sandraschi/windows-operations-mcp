# Basic Usage Examples

## Getting Started

### Server Health Check
```
# Check if the Windows Operations MCP server is working
health_check()

# Get comprehensive system information
get_system_info()
```

### Simple PowerShell Commands
```
# Get running processes
run_powershell("Get-Process | Select-Object Name, Id, CPU | Sort-Object CPU -Descending | Select-Object -First 10")

# Check disk space
run_powershell("Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace")

# Get Windows version information
run_powershell("Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, WindowsBuildLabEx")
```

### Simple CMD Commands
```
# List directory contents
run_cmd("dir C:\\Windows\\System32", working_directory="C:\\")

# Check network configuration
run_cmd("ipconfig /all")

# Get system information
run_cmd("systeminfo")
```

## File Operations

### Directory Listing
```
# List files in a directory
list_directory("C:\\temp")

# List with filtering
list_directory("C:\\logs", include_hidden=True, file_pattern="*.log", max_items=50)

# List specific file types
list_directory("C:\\projects", file_pattern="*.py")
```

### Reading Files
```
# Read a text file
read_file_content("C:\\temp\\config.txt")

# Read with specific encoding
read_file_content("C:\\logs\\app.log", encoding="utf-8", max_size_mb=5)

# Read configuration file
read_file_content("C:\\app\\settings.json")
```

### Writing Files
```
# Write simple text file
write_file_content("C:\\temp\\output.txt", "Hello World!")

# Write with backup
write_file_content("C:\\config\\app.conf", "new_setting=value", backup_existing=True)

# Write and create directories
write_file_content("C:\\new\\path\\file.txt", "content", create_directories=True)
```

## Network Testing

### Basic Connectivity
```
# Test HTTP connectivity
test_port("google.com", 80, protocol="tcp")

# Test HTTPS connectivity
test_port("github.com", 443, protocol="tcp")

# Test local service
test_port("localhost", 3306, protocol="tcp")
```

### Service Testing
```
# Test database connectivity
test_port("database.company.com", 5432, timeout_seconds=10)

# Test web server
test_port("webserver.local", 8080, protocol="tcp")

# Test UDP service
test_port("dns.server.com", 53, protocol="udp")
```

## Process Monitoring

### Process Lists
```
# Get all running processes
get_process_list()

# Filter by process name
get_process_list(filter_name="chrome", max_processes=20)

# Include system processes
get_process_list(include_system=True, max_processes=50)
```

### Process Details
```
# Get detailed info about a specific process
get_process_info(1234)  # Replace with actual PID

# Get system resource usage
get_system_resources()
```

## Common Workflows

### System Maintenance
```
# Check system health
health_check()
get_system_resources()

# Clean up temp files
list_directory("C:\\temp", file_pattern="*.tmp")
list_directory("C:\\Windows\\Temp")

# Check running services
run_powershell("Get-Service | Where-Object {$_.Status -eq 'Stopped'} | Select-Object Name, Status")
```

### Development Support
```
# Check development tools
run_powershell("python --version")
run_powershell("node --version")
run_powershell("git --version")

# Check project files
list_directory("C:\\projects\\myapp", file_pattern="*.py")
read_file_content("C:\\projects\\myapp\\requirements.txt")
```

### Log Analysis
```
# Find recent log files
list_directory("C:\\logs", file_pattern="*.log")

# Read error logs
read_file_content("C:\\logs\\error.log", max_size_mb=1)

# Search for specific errors
run_powershell("Select-String -Path 'C:\\logs\\*.log' -Pattern 'ERROR|FATAL'")
```

### Network Diagnostics
```
# Test internet connectivity
test_port("8.8.8.8", 53, protocol="udp")
test_port("google.com", 443, protocol="tcp")

# Check local services
test_port("localhost", 80, protocol="tcp")
test_port("localhost", 443, protocol="tcp")
test_port("localhost", 3306, protocol="tcp")

# Network configuration
run_cmd("ipconfig /all")
run_powershell("Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}")
```

## Error Handling Examples

### Safe File Operations
```
# Always check if file exists first
result = read_file_content("C:\\config\\app.conf")
if result["success"]:
    print("File content:", result["content"])
else:
    print("Error:", result["error"])
```

### Timeout Handling
```
# Use timeouts for potentially long operations
result = run_powershell("Get-Process", timeout_seconds=30)
if result["success"]:
    print("Command completed in", result["execution_time"], "seconds")
```

### Working Directory Management
```
# Use specific working directories
result = run_cmd("dir", working_directory="C:\\projects")
if result["success"]:
    print("Directory listing:", result["stdout"])
```

## Best Practices

### Security
- Never include credentials in commands
- Use read-only operations when possible
- Validate file paths before operations
- Be cautious with system-level commands

### Performance
- Use appropriate timeouts for operations
- Limit file size when reading large files
- Use specific working directories
- Monitor resource usage for long operations

### Error Handling
- Always check the "success" field in results
- Handle timeout scenarios appropriately
- Log errors for troubleshooting
- Provide meaningful error messages to users
