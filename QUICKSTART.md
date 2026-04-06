# 🚀 Quick Start Guide - Windows Operations MCP

Get up and running with Windows Operations MCP in 5 minutes!

## ⚡ Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install windows-operations-mcp
```

### Option 2: Install from Source
```bash
git clone https://github.com/sandraschi/windows-operations-mcp.git
cd windows-operations-mcp
pip install -e .
```

## 🔌 Claude Desktop Integration

### 1. Locate your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add this configuration:
```json
{
  "mcpServers": {
    "windows_operations_mcp": {
      "command": "python",
      "args": [
        "-m",
        "windows_operations_mcp.mcp_server"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 3. Start the Dashboard
Instead of just running the server, use the standardized SOTA startup script:

```powershell
./start.bat
```

This will:
1. Start the **Backend Bridge** (FastAPI) on port **10748**
2. Start the **SOTA Dashboard** (Vite) on port **10749**
3. Register the MCP server with Claude Desktop automatically

### 4. Restart Claude Desktop

That's it! All tools are now available in Claude Desktop.

## 🎯 Try It Out - 3 Simple Examples

**Note:** This MCP server uses portmanteau tools with action-based interfaces. Instead of individual tools like `get_system_info`, you now use consolidated tools like `system_management` with specific actions.

**Architecture Note:** Some tools (filesystem operations, git operations) may duplicate functionality from dedicated MCP repositories. These may be consolidated or removed in future updates for better ecosystem consistency.

**Version 0.3.0 Update:** All tools now use proper triple double quotes (`"""`) and follow FastMCP 2.14.1+ comprehensive documentation standards.

### Example 1: System Information
In Claude Desktop, try asking:
> "Get my system information"

Claude will use the `system_management` tool with the `info` action to show:
- Platform and Python version
- CPU and memory details
- Disk usage information

### Example 2: Create an Archive
Ask Claude:
> "Create a ZIP archive of my Documents folder at C:\Users\YourName\Documents and save it as backup.zip"

Claude will use the `archive_management` tool with the `create` action and smart exclusions (no .git, __pycache__, etc.)

### Example 3: Run PowerShell Command
Ask Claude:
> "Run a PowerShell command to show the 5 processes using the most memory"

Claude will use the `command_execution` tool with the `powershell` action safely and show you the results.

## 📚 Available Portmanteau Tools

### ✅ Command Execution (`command_execution`)
**Actions:** `powershell`, `cmd`
- Execute PowerShell and CMD commands with reliable output capture
- The main value proposition - reliable stdout/stderr handling

### ✅ File Operations (`file_operations`)
**Actions:** `read`, `write`, `delete`, `move`, `copy`, `list`, `info`, `exists`
- Core file operations with comprehensive error handling
- Includes directory listing and file information

### ✅ Directory Operations (`directory_operations`)
**Actions:** `create`, `delete`, `move`, `copy`, `list`
- Directory-specific operations separate from file operations
- Advanced directory management with safety checks

### ✅ Archive Management (`archive_management`)
**Actions:** `create`, `extract`, `list`
- ZIP and TAR archive handling
- Smart exclusions and format detection

### ✅ JSON Operations (`json_operations`)
**Actions:** `read`, `write`, `validate`, `format`, `convert`, `extract`
- Complete JSON file processing toolkit
- Validation, formatting, and extraction

### ✅ Git Operations (`git_operations`)
**Actions:** `add`, `commit`, `push`, `status`
- Git repository management
- Safe operations with error handling

### ✅ Process Management (`process_management`)
**Actions:** `list`, `info`, `resources`
- Process monitoring and system resources
- Real-time process information

### ✅ Windows Services (`windows_services`)
**Actions:** `list`, `start`, `stop`, `restart`
- Windows service management
- Safe service control with status monitoring

### ✅ System Management (`system_management`)
**Actions:** `info`, `health`, `test_port`, `help`
- System information, health checks, network testing
- Comprehensive system diagnostics
- `git_commit` - Create commits
- `git_push` - Push to remote

### ✅ Media Metadata
- `get_image_exif` - Read EXIF data from images
- `set_image_exif` - Write EXIF data
- `get_mp3_tags` - Read ID3 tags from MP3s
- `set_mp3_tags` - Write ID3 tags

## 🆘 Troubleshooting

### Issue: "Command not found: python"
**Solution**: Ensure Python is in your PATH. Try using `python3` or the full path:
```json
"command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
```

### Issue: "Module not found: windows_operations_mcp"
**Solution**: Install the package:
```bash
pip install windows-operations-mcp
```

### Issue: "Tools not appearing in Claude"
**Solution**:
1. Verify the config file is in the correct location
2. Check JSON syntax is valid (use a JSON validator)
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for errors

### Issue: "PowerShell commands fail"
**Solution**: Ensure PowerShell is installed and in PATH:
```bash
powershell -Command "Get-Host"
```

## 🔍 Testing Your Installation

### Test from Command Line
```bash
# Start the MCP server
python -m windows_operations_mcp.mcp_server

# In another terminal, send a test request
# (The server communicates via stdio protocol)
```

### Test with Python Script
```python
from windows_operations_mcp.tools.system_tools import get_system_info

# Get system information
result = get_system_info()
print(result)
```

## 📖 Next Steps

1. **Explore the Documentation**: Read [README.md](README.md) for comprehensive features
2. **Check Examples**: See [examples/](examples/) for real-world usage
3. **Run Tests**: `pytest tests/` to verify everything works
4. **Join Community**: [GitHub Discussions](https://github.com/sandraschi/windows-operations-mcp/discussions)

## 💡 Pro Tips

1. **Use Exclusion Patterns**: When creating archives, the tool automatically excludes `.git`, `__pycache__`, and other artifacts
2. **Safe Command Execution**: PowerShell commands run with timeout protection and error handling
3. **Atomic Operations**: File operations use atomic writes with automatic rollback on failure
4. **Structured Logging**: All operations are logged for debugging and audit trails

## 🎓 Learning Resources

- **Full Documentation**: [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)
- **API Reference**: [API Documentation](docs/API.md)
- **Video Tutorial**: [YouTube Walkthrough](#) *(coming soon)*
- **Blog Posts**: [Technical Articles](#) *(coming soon)*

---

**Ready to go? Start asking Claude to perform Windows operations!** 🚀
