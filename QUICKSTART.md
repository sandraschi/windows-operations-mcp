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

### 3. Restart Claude Desktop

That's it! All tools are now available in Claude Desktop.

## 🎯 Try It Out - 3 Simple Examples

### Example 1: System Information
In Claude Desktop, try asking:
> "Get my system information"

Claude will use the `get_system_info` tool to show:
- Platform and Python version
- CPU and memory details
- Disk usage information

### Example 2: Create an Archive
Ask Claude:
> "Create a ZIP archive of my Documents folder at C:\Users\YourName\Documents and save it as backup.zip"

Claude will use the `create_archive` tool with smart exclusions (no .git, __pycache__, etc.)

### Example 3: Run PowerShell Command
Ask Claude:
> "Run a PowerShell command to show the 5 processes using the most memory"

Claude will use the `run_powershell` tool safely and show you the results.

## 📚 Available Tool Categories

### ✅ PowerShell & Command Execution
- `run_powershell` - Execute PowerShell commands
- `run_cmd` - Execute CMD commands

### ✅ File Operations
- `create_file`, `delete_file`, `move_file`, `copy_file`
- `get_file_info`, `get_file_dates`, `get_file_attributes`
- `edit_file_content` - Edit text files with backup

### ✅ System Tools
- `get_system_info` - Comprehensive system information
- `health_check` - Server diagnostics

### ✅ Network Tools
- `test_port` - Test TCP/UDP connectivity
- `resolve_dns` - DNS resolution

### ✅ Archive Management
- `create_archive` - Create ZIP/TAR archives
- `extract_archive` - Extract archives
- `list_archive` - List archive contents

### ✅ Git Integration
- `git_status` - Repository status
- `git_add` - Stage changes
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
