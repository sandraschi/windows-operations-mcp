# Windows Operations MCP - Examples

This directory contains practical examples demonstrating how to use the Windows Operations MCP tools.

## 📋 Available Examples

### [01_system_info.py](01_system_info.py)
**System Information Query**

Learn how to retrieve comprehensive system information including:
- Operating system details
- Hardware configuration
- System health metrics (CPU, memory, disk)
- Uptime and performance data

```bash
python examples/01_system_info.py
```

### [02_archive_creation.py](02_archive_creation.py)
**Archive Management with Exclusions**

Demonstrates archive operations including:
- Creating ZIP archives with exclusion patterns
- Listing archive contents
- Extracting archives
- Smart exclusions (*.pyc, __pycache__, .git, etc.)

```bash
python examples/02_archive_creation.py
```

### [03_powershell_automation.py](03_powershell_automation.py)
**PowerShell Automation**

Shows how to execute PowerShell commands and scripts:
- Simple PowerShell commands
- Process management queries
- System information retrieval
- Script file execution
- Comparison with CMD commands

```bash
python examples/03_powershell_automation.py
```

### [04_service_management.py](04_service_management.py)
**Windows Service Management**

Demonstrates Windows service operations:
- Listing services by status (running, stopped)
- Filtering by start type (automatic, manual, disabled)
- Getting detailed service information
- Searching for specific services

```bash
python examples/04_service_management.py
```

**Note:** Service start/stop/restart requires administrator privileges.

### [05_event_log_query.py](05_event_log_query.py)
**Windows Event Log Querying**

Learn to query Windows Event Logs:
- Query System, Application, and Security logs
- Filter by event level (Error, Warning, Information)
- Time-based filtering
- Event ID specific queries
- List available event providers

```bash
python examples/05_event_log_query.py
```

**Note:** Querying Security logs may require administrator privileges.

## 🚀 Running Examples

### Prerequisites

1. **Install the package:**
   ```bash
   pip install -e .
   ```

2. **Or ensure src is in Python path:**
   ```bash
   # Examples already add ../src to path
   python examples/01_system_info.py
   ```

### Quick Start

Run all examples in sequence:

```bash
# Windows Command Prompt
for %f in (examples\*.py) do python %f

# PowerShell
Get-ChildItem examples\*.py | ForEach-Object { python $_.FullName }

# Git Bash / WSL
for example in examples/*.py; do python "$example"; done
```

## 📚 Learning Path

**Beginner:**
1. Start with `01_system_info.py` - Basic information retrieval
2. Try `03_powershell_automation.py` - Simple command execution

**Intermediate:**
3. Explore `02_archive_creation.py` - File operations
4. Learn `04_service_management.py` - Windows services

**Advanced:**
5. Master `05_event_log_query.py` - Event log analysis

## 🔧 Customization

Each example can be easily modified:

```python
# Customize system info output
system_info = get_system_info(detailed=True)

# Change archive exclusions
exclusions = ["*.log", "*.tmp", "cache/"]

# Adjust PowerShell timeout
result = run_powershell(command="Long-Running-Command", timeout=60)

# Filter services differently
services = list_windows_services(name_filter="sql")

# Query different event log
events = query_windows_event_log(log_name="Application", max_events=100)
```

## 💡 Tips & Best Practices

### Error Handling
All tools return a dict with `success` key:
```python
result = get_system_info()
if result.get("success"):
    # Process successful result
    info = result.get("system_info")
else:
    # Handle error
    print(f"Error: {result.get('error')}")
```

### Performance
- Use `max_results` to limit large queries
- Apply filters to reduce data processing
- Set appropriate timeouts for long-running commands

### Security
- Run with minimum required privileges
- Validate user inputs before passing to commands
- Use exclusion patterns to protect sensitive data
- Be cautious with PowerShell script execution

### Debugging
Set log level for detailed output:
```python
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
```

## 📖 Additional Resources

- **[Main Documentation](../docs/README.md)** - Complete documentation index
- **[Getting Started](../docs/mcp/GETTING_STARTED.md)** - Quick start guide
- **[API Reference](../docs/mcp/EXAMPLES.md)** - Detailed tool documentation
- **[Troubleshooting](../docs/mcp/TROUBLESHOOTING_FASTMCP_2.12.md)** - Common issues

## 🤝 Contributing Examples

Have a useful example? Contributions are welcome!

1. Fork the repository
2. Create your example file: `examples/XX_your_example.py`
3. Follow the existing format:
   - Clear docstring
   - Import statement handling
   - Comprehensive output
   - Error handling
4. Add to this README
5. Submit a pull request

## 🆘 Need Help?

- **Issues**: [GitHub Issues](https://github.com/sandraschi/windows-operations-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sandraschi/windows-operations-mcp/discussions)
- **Documentation**: Check the `docs/` directory

---

**Last Updated**: October 8, 2025  
**Version**: 0.2.0

