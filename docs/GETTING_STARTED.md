# Getting Started with Windows Operations MCP

This guide will help you quickly get up and running with the Windows Operations MCP.

## Table of Contents
1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Configuration](#configuration)
4. [Security Best Practices](#security-best-practices)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Topics](#advanced-topics)

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows operating system (recommended)
- Administrator privileges (for some operations)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/windows-operations-mcp.git
   cd windows-operations-mcp
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

4. **Verify installation**:
   ```bash
   windows-operations-mcp --version
   ```

## DXT Package Usage

### Installation

1. **Prerequisites**:
   - Python 3.8 or higher
   - DXT CLI tools installed
   - FastMCP 2.10.1 or higher

2. **Install the DXT package**:
   ```bash
   # Install the package in development mode
   pip install -e .
   ```

### Running the MCP Server

1. **Using DXT CLI**:
   ```bash
   # Build the DXT package
   dxt pack -o dist/windows-operations-mcp.dxt
   
   # Run the MCP server
   dxt run dist/windows-operations-mcp.dxt
   ```

2. **Configuration**:
   The server can be configured using environment variables or a `.env` file in the project root:
   ```env
   LOG_LEVEL=INFO
   MAX_WORKERS=5
   TEMP_DIR=C:\Temp\windows_operations_mcp
   ```

### Integration with Claude Desktop

1. **Install the DXT package** in Claude Desktop
2. **Configure** the MCP server settings through the Claude Desktop UI
3. **Use** the MCP tools directly in your Claude conversations

### Example Usage

```python
# Example of using the MCP client in your code
from fastmcp import MCPClient

# Initialize client with your MCP server URL
client = MCPClient("http://localhost:8080")

# Example: List running processes
processes = client.tools.list_processes()

# Example: Execute a command
result = client.tools.execute_command(
    command="Get-Process",
    shell="powershell",
    timeout=30
)

print(result.output)
result = client.run_tool("run_powershell", {"command": "Get-Process | Select-Object -First 5"})
print(result)

# List directory contents
dir_result = client.run_tool("list_directory", {"path": "C:\\temp"})
print(dir_result)
```

## Configuration

### Server Configuration

Create a `config.toml` file in the working directory:

```toml
[server]
host = "0.0.0.0"
port = 8080
log_level = "INFO"

[security]
enable_rate_limiting = true
max_requests_per_minute = 60
allowed_origins = ["http://localhost:3000"]

[paths]
workspace = "./workspace"
logs = "./logs"
```

### Environment Variables

You can also configure the server using environment variables:

```bash
# Server configuration
set MCP_HOST=0.0.0.0
set MCP_PORT=8080
set MCP_LOG_LEVEL=INFO

# Security settings
set MCP_ENABLE_RATE_LIMITING=true
set MCP_MAX_REQUESTS=60

# Paths
set MCP_WORKSPACE=./workspace
set MCP_LOGS=./logs
```

## Security Best Practices

### Authentication

```toml
[auth]
enabled = true
api_keys = ["your-secure-api-key"]
```

### Network Security
- Always run the server behind a reverse proxy (e.g., Nginx, Apache)
- Enable HTTPS with valid certificates
- Use a firewall to restrict access to the MCP port
- Regularly update dependencies

### Command Safety
- Never run untrusted commands
- Validate all input parameters
- Use the principle of least privilege

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Run the server as administrator
   - Check file and directory permissions

2. **Port Already in Use**
   ```bash
   netstat -ano | findstr :8080
   taskkill /PID <PID> /F
   ```

3. **Command Timeout**
   - Increase the timeout value
   - Check for long-running processes

### Logs

Logs are stored in the `logs` directory by default. Check them for detailed error information:

```bash
type logs\mcp.log
type logs\error.log
```

## Advanced Topics

### Custom Tools

1. Create a new Python file in `windows_operations_mcp/tools/`
2. Define your tool functions with the `@tool_decorator`
3. Register the tools in the module's `__init__.py`

### Monitoring

```bash
# Get system metrics
client.run_tool("get_system_metrics")

# Check service health
client.run_tool("health_check")
```

### Integration with Claude Desktop

1. Add the MCP server to your Claude Desktop configuration:
   ```json
   {
     "mcpServers": {
       "windows-ops": {
         "command": "windows-operations-mcp start --port 8080"
       }
     }
   }
   ```

2. Restart Claude Desktop
3. The tools will be available in the Claude interface

## Support

For help or to report issues, please [open an issue](https://github.com/your-org/windows-operations-mcp/issues).
