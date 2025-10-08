# Windows Operations MCP

[![FastMCP](https://img.shields.io/badge/FastMCP-2.12.3-blue)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![MCPB](https://img.shields.io/badge/MCPB-v0.2-green)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green)](REPOSITORY_STATUS_REPORT.md)

A comprehensive Windows system operations MCP server implementing the FastMCP 2.12.3 protocol with full MCPB (MCP Bundle) packaging support.

## ✨ What's New (October 2025)

- **✅ MCPB Migration Complete**: Fully migrated from DXT to MCPB packaging
- **✅ Enhanced Test Coverage**: 16+ test modules with comprehensive coverage
- **✅ GitHub Actions CI/CD**: Automated builds and testing
- **✅ Improved Tools**: Enhanced JSON and media metadata tools
- **✅ Better Error Handling**: Improved command execution and error reporting
- **✅ PowerShell Build Automation**: One-command package building
- **✅ Production Ready**: Validated, tested, and ready for deployment

## 🚨 IMPORTANT: MCPB Migration Complete

This repository has been fully migrated from DXT to MCPB (MCP Bundle) standards as of **October 2025**. All tooling, configuration, and packaging now follows the latest MCPB specifications with FastMCP 2.12.3 compatibility.

### Migration Summary

| Component | Old (DXT) | New (MCPB) | Status |
|-----------|-----------|------------|--------|
| **CLI Tool** | `dxt` commands | `mcpb` commands | ✅ Migrated |
| **Config File** | `dxt.json` | `mcpb.json` | ✅ Migrated |
| **Manifest** | `dxt_manifest.json` | `mcpb/manifest.json` | ✅ Migrated |
| **Package Format** | `.dxt` packages | `.mcpb` packages | ✅ Migrated |
| **Documentation** | DXT guides | MCPB guides | ✅ Migrated |
| **Build Scripts** | Manual build | PowerShell automation | ✅ Migrated |
| **CI/CD** | None | GitHub Actions | ✅ Added |

## 🚀 Key Features

### ✅ MCPB Packaging & Distribution
- **Full MCPB compliance** with proper manifest structure (v0.2 format)
- **Automated AI-generated manifests** for optimal configuration
- **PowerShell build automation** with validation and signing support
- **GitHub Actions CI/CD** for automated package building
- **Comprehensive exclusion patterns** for clean repository archiving
- **Production-ready packaging** validated and tested

### ✅ Windows System Operations
- **Windows Services Management**: Start, stop, restart, list services with filtering
- **Windows Event Log Tools**: Query, export, monitor, and clear event logs
- **Windows Performance Monitoring**: Real-time performance counters and system metrics
- **Windows Permissions Management**: File/directory permissions analysis and modification

### ✅ Core Operations
- **PowerShell & CMD Execution**: Reliable command execution with output capture and error handling
- **File Operations**: Create, read, write, move, copy files and directories with comprehensive error handling
- **Archive Management**: Create/extract ZIP archives with intelligent exclusion patterns
- **JSON Tools**: Parse, validate, format, and query JSON files with JSONPath support
- **Media Metadata**: Extract metadata from images, audio, and video files
- **System Information**: Comprehensive OS, hardware, and environment reporting
- **Health Monitoring**: Built-in health checks and diagnostic tools

## 🏗️ Installation

### Option 1: MCPB Package (Recommended)

1. **Download the latest release** from the [GitHub Releases](https://github.com/sandraschi/windows-operations-mcp/releases) page
2. **Drag the `.mcpb` file** to Claude Desktop for automatic installation
3. **Follow the configuration prompts** to set up your preferences
4. **Restart Claude Desktop** to complete the installation

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/sandraschi/windows-operations-mcp.git
cd windows-operations-mcp

# Install Python dependencies
pip install -r requirements.txt

# Install as editable package
pip install -e .

# Configure for Claude Desktop
# Add to claude_desktop_config.json:
{
  "mcpServers": {
    "windows-operations": {
    "command": "python",
      "args": ["-m", "windows_operations_mcp"],
      "cwd": "src"
    }
  }
}
```

## 🛠️ Development & Building

### Prerequisites

```bash
# Install MCPB CLI (official toolchain)
npm install -g @anthropic-ai/mcpb

# Install Python dependencies (EXACT VERSIONS)
pip install "fastmcp>=2.12.0,<3.0.0"
pip install -r requirements.txt
```

### Repository Structure

```
windows-operations-mcp/
├── mcpb/                          # MCPB configuration and manifest
│   ├── manifest.json              # AI-generated runtime configuration
│   └── assets/                    # Icons, screenshots
├── src/                           # Python source code
│   └── windows_operations_mcp/    # Main Python package
│       ├── __init__.py
│       ├── server.py              # Main server entry point
│       └── tools/                 # Tool modules
├── scripts/                       # Build and utility scripts
│   └── build-mcp-package.ps1     # MCPB package builder
├── docs/                          # Documentation
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### Building MCPB Packages

```powershell
# Show help and available options
.\scripts\build-mcp-package.ps1 -Help

# Build and sign the package (default behavior)
.\scripts\build-mcp-package.ps1

# Build without signing (for development/testing)
.\scripts\build-mcp-package.ps1 -NoSign

# Specify custom output directory
.\scripts\build-mcp-package.ps1 -OutputDir "C:\builds"
```

### Local Development Workflow

```bash
# 1. AI-generate manifest.json (place in mcpb/manifest.json)
# ENSURE: fastmcp>=2.12.0 in requirements.txt
# ENSURE: cwd: "src" and PYTHONPATH: "src" in mcp_config

# 2. Validate manifest
cd mcpb
mcpb validate manifest.json

# 3. Build MCPB package
mcpb pack . ../dist/package.mcpb

# 4. Test installation
# Drag dist/*.mcpb to Claude Desktop
```

## 🎯 Available Tools

### Windows Services Management
- `list_windows_services` - List services with filtering
- `start_windows_service` - Start Windows services
- `stop_windows_service` - Stop Windows services
- `restart_windows_service` - Restart Windows services

### Windows Event Log Tools
- `query_windows_event_log` - Query event logs with filtering
- `export_windows_event_log` - Export event logs to files
- `clear_windows_event_log` - Clear event logs with backup
- `monitor_windows_event_log` - Real-time event log monitoring

### Windows Performance Monitoring
- `get_windows_performance_counters` - Query performance counters
- `monitor_windows_performance` - Monitor performance over time
- `get_windows_system_performance` - Comprehensive system metrics

### Windows Permissions Management
- `get_file_permissions` - Analyze file/directory permissions
- `set_file_permissions` - Modify file permissions
- `analyze_directory_permissions` - Bulk permission analysis
- `fix_file_permissions` - Fix common permission issues

### Archive Management (with exclusions)
- `create_archive` - Create archives with intelligent exclusions
- `extract_archive` - Extract archives
- `list_archive` - List archive contents

### Core Operations
- `run_powershell_tool` - Execute PowerShell commands
- `run_cmd_tool` - Execute CMD commands
- `read_file` / `write_file` - File operations
- `get_system_info` / `health_check` - System monitoring
- `get_help` - Tool documentation and help

## ⚙️ Configuration

### User Configuration Options

When installing the MCPB package, you can configure:

- **Working Directory**: Default directory for file operations
- **Log Level**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- **Performance Monitoring**: Enable detailed metrics collection

### Environment Variables

The server respects these environment variables:

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `PYTHONPATH`: Python module search path
- `PYTHONUNBUFFERED`: Force unbuffered output

## 🔧 Troubleshooting

### Extension Fails to Start

**Symptoms:** Extension shows as failed in Claude Desktop settings.

**Common Causes:**
1. **Python Path Issues**: Incorrect `PYTHONPATH` configuration
2. **Missing Dependencies**: Required packages not installed
3. **Permission Issues**: Insufficient permissions for operations

**Solutions:**
1. **Check Python Path**: Ensure `PYTHONPATH` includes the `src` directory
2. **Verify Dependencies**: Run `pip install -r requirements.txt`
3. **Check Logs**: Review `%APPDATA%\Claude\logs\mcp-server-windows-operations.log`

### Manual Configuration Workaround

If the MCPB package fails to start, add a manual entry to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "windows-operations-manual": {
    "command": "python",
      "args": ["C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.sandraschi.windows-operations-mcp/src/windows_operations_mcp/server.py"],
      "cwd": "C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.sandraschi.windows-operations-mcp/src",
    "env": {
        "PYTHONPATH": "C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.sandraschi.windows-operations-mcp/src",
      "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## 🧪 Testing

### Test Coverage

The project maintains **comprehensive test coverage** across all components:

- **Unit Tests**: 16+ test modules covering all tools and utilities
- **Integration Tests**: MCP server integration testing
- **Coverage Reports**: HTML coverage reports generated automatically
- **Test Categories**: Archive tools, file operations, JSON tools, media tools, command execution

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=src --cov-report=html --cov-report=term

# Run specific test categories
python -m pytest tests/unit/tools/ -v           # Tool tests
python -m pytest tests/unit/utils/ -v           # Utility tests
python -m pytest tests/integration/ -v          # Integration tests

# Run with verbose output
python -m pytest -vv

# Run PowerShell test script
.\tests\run_tests.ps1
```

### Manual Testing

```bash
# Test MCP server directly
cd src
python -m windows_operations_mcp

# Test specific tools
python -c "
from windows_operations_mcp.tools.windows_services import list_windows_services
result = list_windows_services()
print('Services found:', len(result.get('services', [])))
"

# Test package build
.\scripts\build-mcp-package.ps1 -NoSign
```

## 🤝 Contributing

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch**: `git checkout -b feature/new-tool`
4. **Install dependencies**: `pip install -r requirements.txt`
5. **Run tests**: `python -m pytest`
6. **Make your changes** with proper documentation
7. **Submit a pull request**

### Adding New Tools

1. **Create tool module** in `src/windows_operations_mcp/tools/`
2. **Implement tool functions** with proper decorators and documentation
3. **Add registration function** that registers tools with FastMCP
4. **Register in main server** by importing and calling the registration function
5. **Add tests** in `tests/unit/tools/`
6. **Update documentation** in this README

### Code Standards

- **Type Hints**: Use comprehensive type annotations
- **Error Handling**: Implement proper exception handling with logging
- **Documentation**: Use self-documenting multiline decorators
- **Testing**: Maintain >90% test coverage
- **Security**: Validate inputs and handle sensitive operations safely

## 📋 MCPB Compliance Checklist

- ✅ **MCPB Manifest**: Proper `mcpb/manifest.json` with AI generation (v0.2 format)
- ✅ **Python Path Configuration**: Correct `PYTHONPATH` and `cwd` settings
- ✅ **FastMCP 2.12.3**: Latest version requirement enforced
- ✅ **Exclusion Patterns**: Intelligent artifact exclusion for archiving
- ✅ **Self-Documenting Tools**: Comprehensive parameter and return documentation
- ✅ **Error Handling**: Robust error handling with detailed diagnostics
- ✅ **Build Process**: Automated MCPB package building with PowerShell scripts
- ✅ **CI/CD Integration**: GitHub Actions for automated testing and builds
- ✅ **Test Coverage**: Comprehensive unit and integration tests
- ✅ **Documentation**: Complete guides and examples

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support & Resources

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/sandraschi/windows-operations-mcp/issues) - Bug reports and feature requests
- **Discussions**: [GitHub Discussions](https://github.com/sandraschi/windows-operations-mcp/discussions) - Community support
- **Documentation**: Check the `docs/` directory for comprehensive guides

### Documentation
- 📖 **[MCPB Building Guide](docs/MCPB_BUILDING_GUIDE.md)** - Package building instructions
- 📖 **[Getting Started](docs/GETTING_STARTED.md)** - Quick start guide
- 📖 **[Examples](docs/EXAMPLES.md)** - Usage examples
- 📖 **[Repository Status](REPOSITORY_STATUS_REPORT.md)** - Current project status

### Quick Links
- **FastMCP Documentation**: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **Model Context Protocol**: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Claude Desktop**: [https://claude.ai/desktop](https://claude.ai/desktop)

## 📊 Project Status

**Version**: 0.2.0 🎉 (MCPB Release)  
**Status**: ✅ Production Ready  
**Health Score**: 9.0/10  
**Last Updated**: October 8, 2025

See [REPOSITORY_STATUS_REPORT.md](REPOSITORY_STATUS_REPORT.md) for detailed status information.

---

**Built with ❤️ using FastMCP 2.12.3 and MCPB standards**  
*Providing reliable Windows system operations through the Model Context Protocol*