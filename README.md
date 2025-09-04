# Windows Operations MCP

A high-performance Windows system operations server implementing the FastMCP 2.13 protocol, providing seamless integration with Claude Desktop and other MCP clients through both stdio and HTTP interfaces.

## 🚀 Key Features

### FastMCP 2.13 Integration

- **Dual Protocol Support**: Implements both stdio and HTTP transport layers for maximum compatibility
- **Stateful Tools**: Leverages FastMCP 2.13's stateful tool capabilities for efficient operations
- **Type Safety**: Full type annotations and validation using Pydantic models
- **Async I/O**: Built on Python's asyncio for high concurrency

## 🛠️ Core Capabilities

## 📡 Communication Protocols

### stdio (Primary)

- **Default Transport**: Uses stdio for maximum compatibility with Claude Desktop
- **Low Latency**: Direct process communication for minimal overhead
- **Simple Integration**: No network configuration required

### HTTP/HTTPS (Optional)

- **RESTful API**: Standardized endpoints for tool execution
- **WebSocket Support**: Real-time event streaming
- **Authentication**: JWT-based security (when enabled)
- **Swagger UI**: Interactive API documentation at `/docs`

## 🏛️ Architecture

```mermaid
graph TD
    A[MCP Client] -->|stdio/HTTP| B[Windows Operations MCP]
    B --> C[Tool Registry]
    C --> D[File Operations]
    C --> E[System Tools]
    C --> F[Network Tools]
    C --> G[Media Tools]
    D --> H[Atomic Operations]
    D --> I[Backup System]
    E --> J[Process Management]
    E --> K[System Monitoring]
```


## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- FastMCP 2.13+
- Windows 10/11 or Windows Server 2016+

### Installation

```bash
# Install from source
pip install -e .

# Or from PyPI (when published)
pip install windows-operations-mcp
```

### Running the Server

#### stdio Mode (Recommended for Claude Desktop)

```bash
python -m windows_operations_mcp
```

#### HTTP Server Mode

```bash
python -m windows_operations_mcp --http --port 8000
```

## 🔌 Integration

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "windows-operations-mcp": {
      "command": "windows-operations-mcp",
      "transport": "stdio"
    }
  }
}
```

### HTTP API Clients

```python
import httpx

async def run_command():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/tools/run_powershell",
            json={"command": "Get-Process | Select-Object -First 5"}
        )
        return response.json()
```

## 📂 File Management

### Core File Operations
- **Atomic Writes**: Safe file modifications with automatic rollback on failure
- **Automatic Backups**: Configurable backup system with timestamped versions
- **Line Ending Handling**: Automatic detection and normalization of line endings (Windows/Unix/Mac)
- **Text Encoding**: Automatic detection and handling of different text encodings
- **File Locking**: Safe concurrent access with file locking
- **Large File Support**: Efficient handling of large text files

## 🖥️ Command Execution

### Process Management
- **PowerShell & CMD**: Reliable execution with file-based output capture
- **Working Directory**: Execute commands in specific directories
- **Timeout Control**: Configurable execution timeouts
- **Error Handling**: Comprehensive error reporting and recovery

### Advanced File Operations
- **File Attributes**: Get and set file attributes (read-only, hidden, system, etc.)
- **File Timestamps**: Get and set file creation, modification, and access times
- **Metadata Inspection**: Detailed file metadata and content inspection
- **Directory Navigation**: Advanced filtering, searching, and tree views
- **Pattern Matching**: Glob pattern support for file filtering
- **Archive Handling**: Create, extract, and list contents of ZIP, RAR, TAR, and TAR.GZ archives
- **Markdown Tools**: Built-in Markdown formatting and linting
- **Encoding Detection**: Automatic handling of different text encodings

### 🌍 Network Tools

### Network Diagnostics
- **Port Testing**: TCP/UDP port accessibility testing
- **DNS Resolution**: Hostname resolution with error handling
- **Response Timing**: Network latency measurement

## 💻 Git Integration

### Version Control Features
- **Repository Operations**: Stage, commit, and push changes
- **Status Checking**: View repository status with detailed changes
- **Branch Management**: Work with branches and remotes
- **Conflict Resolution**: Tools to help resolve merge conflicts

## ❓ Help & Documentation

### Help System Features
- **Interactive Help**: Multi-level help with different detail levels
- **Command Discovery**: Find commands by category or search term
- **Detailed Documentation**: Access comprehensive documentation for each command
- **Usage Examples**: See examples of how to use each command

## 📈 System Monitoring

### Monitoring Capabilities
- **System Information**: Comprehensive OS and hardware details
- **Process Management**: List and monitor running processes (requires psutil)
- **Resource Usage**: CPU, memory, and disk utilization tracking
- **Health Checks**: Server diagnostics and dependency verification

## 🎨 Media Handling

### Media Processing Features
- **Image Metadata**: Read and write EXIF data from images (JPEG, PNG, TIFF, WebP)
- **Audio Metadata**: Read and write ID3 tags from MP3 files
- **Unified Interface**: Consistent API for different media types
- **File Type Detection**: Automatic handling based on file extension

## 📦 Archive Management

### Supported Archive Operations

- **Create Archives**: Create new archives from files and directories
- **Extract Archives**: Extract files from existing archives
- **List Contents**: View the contents of an archive without extracting
- **Password Protection**: Support for password-protected archives
- **Streaming**: Efficient handling of large archives

### Requirements

- For RAR support: `rarfile` package and `unrar` command-line tool in PATH
- For TAR.GZ support: `python-libarchive-c` package

### Usage Examples

#### Create an Archive

```python
from windows_operations_mcp.tools.archive_tools import create_archive_tool

# Create a ZIP archive
create_archive_tool(
    archive_path="C:\\path\\to\\archive.zip",
    source_paths=["C:\\path\\to\\file1.txt", "C:\\path\\to\\folder1"],
    compression_level=6,  # 0-9 where 0 is no compression, 9 is maximum
    password=None,        # Optional password for encryption
    include_base_dir=True # Include the base directory in the archive
)
```

#### Extract an Archive

```python
from windows_operations_mcp.tools.archive_tool import extract_archive_tool

# Extract a ZIP archive
extract_archive_tool(
    archive_path="C:\\path\\to\\archive.zip",
    output_dir="C:\\path\\to\\extract\\to",
    password=None,        # Required if archive is password protected
    members=None,         # Optional: list of specific files to extract
    overwrite=False,      # Overwrite existing files
    create_subdir=True    # Create a subdirectory with the archive name
)
```

#### List Archive Contents

```python
from windows_operations_mcp.tools.archive_tools import list_archive_tool

# List contents of an archive
contents = list_archive_tool(
    archive_path="C:\\path\\to\\archive.zip",
    password=None  # Required if archive is password protected
)

# Print the contents
for file_info in contents:
    print(f"{file_info['filename']} - {file_info['size']} bytes")
```

### Configuration Options

You can configure archive operations through the DXT manifest's `user_config` section:

- `enable_archive_operations`: Enable/disable all archive operations (default: `true`)
- `max_archive_size_mb`: Maximum archive size in MB for extraction (default: `1024`)
- `allowed_archive_extensions`: Comma-separated list of allowed archive file extensions (default: `.zip,.rar,.tar,.tar.gz,.tgz`)

## 💻 Code Examples

### Git Integration Examples

```python
# Stage all changes
git.add(all=True)

# Check repository status
git.status()

# Create a commit
git.commit(message="Update project files", all=True)

# Push changes to remote
git.push(remote="origin", set_upstream=True)
```

### Help System Examples

```python
# Basic help - list all commands
help()

# Help for a specific command
help("git.add")

# Detailed help with all parameters
help("git.commit", detail=2)

# List commands in a category
help(category="git")
```

## 🛠️ Installation

### System Requirements

- Python 3.8+
- Windows (optimized for, but cross-platform compatible)
- FastMCP 2.11.3+

### Install Dependencies

```bash
# Core dependencies
pip install fastmcp>=2.13.0 psutil>=5.9.0

# Optional dependencies for extended functionality
pip install python-libarchive-c rarfile
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/sandraschi/windows-operations-mcp.git
cd windows-operations-mcp

# Install in development mode
pip install -e .
```

## ⚙️ Configuration

### Claude Desktop Integration

Add to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "windows-operations-mcp": {
      "command": "windows-operations-mcp",
      "transport": "stdio"
    }
  }
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `HTTP_PORT` | `8000` | Port for HTTP server (when enabled) |
| `ENABLE_HTTP` | `false` | Enable HTTP server interface |
| `MAX_WORKERS` | `10` | Maximum number of concurrent operations |

## 🚀 Usage Examples

### Command Execution

```python
# PowerShell
run_powershell("Get-Process | Select-Object -First 5")
run_powershell("Get-ChildItem C:\\", working_directory="C:\\temp")

# CMD
run_cmd("dir /b", working_directory="C:\\Windows")
run_cmd("systeminfo", timeout_seconds=30)
```

### File Management

```python
# List directory with advanced filtering
from windows_operations_mcp.tools.file_operations import list_directory_tool

# List directory contents
result = list_directory_tool(
    path="C:\\temp",
    include_hidden=True,
    include_system=False,
    file_pattern="*.txt",
    max_items=50,
    include_stats=True
)

# Get detailed file information
from windows_operations_mcp.tools.file_operations import get_file_info_tool

file_info = get_file_info_tool(
    file_path="C:\\path\\to\\file.txt",
    include_content=True,
    include_metadata=True,
    include_attributes=True
)

# Set file attributes
from windows_operations_mcp.tools.file_operations.attributes import set_file_attributes_tool

set_file_attributes_tool(
    file_path="C:\\path\\to\\file.txt",
    attributes={
        'readonly': True,
        'hidden': False,
        'archive': True
    }
)

# Set file dates
from windows_operations_mcp.tools.file_operations.dates import set_file_dates_tool
from datetime import datetime, timezone

set_file_dates_tool(
    file_path="C:\\path\\to\\file.txt",
    modified=datetime.now(timezone.utc).isoformat(),
    accessed=datetime.now(timezone.utc).isoformat()
)
```

### Network Diagnostics

```python
# Test TCP port
test_port("google.com", 80, protocol="tcp")

# Test local service
test_port("localhost", 3306, timeout_seconds=10)
```

### System Monitoring

```python
# Get system information
get_system_info()

# List processes
get_process_list(filter_name="chrome", max_processes=50)

# Monitor resources
get_system_resources()
```

## 🏗️ System Architecture

### Component Structure
```text
windows_operations_mcp/
├── mcp_server.py           # Main server and tool registration
├── utils/
│   ├── __init__.py         # Common utilities
│   └── command_executor.py  # Command execution engine
└── tools/
    ├── powershell_tools.py  # PowerShell/CMD tools
    ├── file_operations/     # File system operations
    │   ├── __init__.py      # Package initialization
    │   ├── base.py          # Common utilities and base classes
    │   ├── file_operations.py # Core file operations
    │   ├── attributes.py     # File attribute handling
    │   ├── dates.py         # File date operations
    │   └── info.py          # File information and directory listing
    ├── network_tools.py     # Network testing tools
    ├── system_tools.py      # System information tools
    └── process_tools.py     # Process monitoring tools
```

### Technical Highlights

- **File-based Output Capture**: Works around Claude Desktop PowerShell limitations
- **Robust Error Handling**: Comprehensive validation and error recovery
- **FastMCP 2.11.3 Compliance**: Modern MCP protocol implementation with stateful tools support
- **Austrian Dev Efficiency**: Clean, maintainable, production-ready code

## 🛠 Development

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sandraschi/windows-operations-mcp.git
   cd windows-operations-mcp
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # On Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```

### Run in Development Mode

```bash
python -m windows_operations_mcp
```

### Enable Debug Logging

```bash
# Set debug log level
$env:LOG_LEVEL="DEBUG"
python -m windows_operations_mcp

# Or use the debug flag
python -m windows_operations_mcp --debug
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_file_operations.py -v
```

### Code Quality

```bash
# Run linters
flake8 src/
black --check src/
mypy src/

# Auto-format code
black src/
isort src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Write docstrings for all public functions and classes
- Include type hints for better code maintainability
- Add tests for new features and bug fixes
- Update documentation when adding new features

### Reporting Issues

Please use the [GitHub issue tracker](https://github.com/sandraschi/windows-operations-mcp/issues) to report bugs or suggest enhancements.

## 🏭 Development Philosophy

This project follows pragmatic development principles:

- **Working Solutions**: Focus on delivering functional solutions quickly
- **Clean Code**: Maintainable and well-documented codebase
- **Robustness**: Comprehensive error handling and recovery
- **Production-Ready**: Battle-tested in real-world scenarios
- **No Placeholders**: Every feature is fully implemented and tested

## 🌟 Features in Development

- [ ] Enhanced file watching with inotify
- [ ] Advanced process management
- [ ] Network monitoring tools
- [ ] System performance optimization

## 🤝 Community & Support

- **GitHub Discussions**: [Join the conversation](https://github.com/sandraschi/windows-operations-mcp/discussions)
- **Issue Tracker**: [Report issues](https://github.com/sandraschi/windows-operations-mcp/issues)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

---

Built with ❤️ for Windows automation and Claude Desktop integration.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
