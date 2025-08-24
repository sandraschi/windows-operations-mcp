# Windows Operations MCP

A comprehensive Windows system operations server for Claude Desktop, built with FastMCP 2.11.3.

## Features

### ✏️ File Editing

- **Atomic Writes**: Safe file modifications with automatic rollback on failure
- **Automatic Backups**: Configurable backup system with timestamped versions
- **Line Ending Handling**: Automatic detection and normalization of line endings (Windows/Unix/Mac)
- **Markdown Formatting**: Fix common Markdown formatting issues
- **Text Encoding**: Automatic detection and handling of different text encodings
- **File Locking**: Safe concurrent access with file locking
- **Large File Support**: Efficient handling of large text files

### 🚀 Command Execution

- **PowerShell & CMD**: Reliable execution with file-based output capture
- **Working Directory**: Execute commands in specific directories
- **Timeout Control**: Configurable execution timeouts
- **Error Handling**: Comprehensive error reporting and recovery

### 📁 File Operations

- **Core Operations**: Create, delete, move, and copy files and directories
- **File Attributes**: Get and set file attributes (read-only, hidden, system, etc.)
- **File Dates**: Get and set file timestamps (created, modified, accessed)
- **File Information**: Detailed file metadata and content inspection
- **Directory Listing**: Advanced filtering, searching, and tree views
- **Pattern Matching**: Glob pattern support for file filtering
- **Archive Operations**: Create, extract, and list contents of ZIP, RAR, TAR, and TAR.GZ archives
- **Safe Editing**: Atomic file writes with automatic backups
- **Markdown Support**: Built-in Markdown formatting and linting
- **Encoding Detection**: Automatic handling of different text encodings

### 🌐 Network Tools

- **Port Testing**: TCP/UDP port accessibility testing
- **DNS Resolution**: Hostname resolution with error handling
- **Response Timing**: Network latency measurement

### 🔧 Git Tools

- **Repository Operations**: Stage, commit, and push changes
- **Status Checking**: View repository status with detailed changes
- **Branch Management**: Work with branches and remotes
- **Conflict Resolution**: Tools to help resolve merge conflicts

### ❓ Help System

- **Interactive Help**: Multi-level help with different detail levels
- **Command Discovery**: Find commands by category or search term
- **Detailed Documentation**: Access comprehensive documentation for each command
- **Usage Examples**: See examples of how to use each command

### 📊 System Monitoring

- **System Information**: Comprehensive OS and hardware details
- **Process Management**: List and monitor running processes (requires psutil)
- **Resource Usage**: CPU, memory, and disk utilization tracking
- **Health Checks**: Server diagnostics and dependency verification

### 🖼️ Media Metadata

- **Image Metadata**: Read and write EXIF data from images (JPEG, PNG, TIFF, WebP)
- **Audio Metadata**: Read and write ID3 tags from MP3 files
- **Unified Interface**: Consistent API for different media types
- **File Type Detection**: Automatic handling based on file extension

## Archive Tools

The Windows Operations MCP includes comprehensive archive handling capabilities for working with various archive formats including ZIP, RAR, TAR, and TAR.GZ.

### Supported Operations

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

## Code Examples

### Git Operations

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

### Help System

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

## Installation

### Requirements

- Python 3.8+
- Windows (optimized for, but cross-platform compatible)
- FastMCP 2.11.3+

### Install Dependencies

```bash
pip install fastmcp psutil
```

### Install Package

```bash
pip install -e .
```

## Configuration

Add to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "windows-operations-mcp": {
      "command": "windows-operations-mcp"
    }
  }
}
```

## Usage Examples

### Command Execution

```python
# PowerShell
run_powershell("Get-Process | Select-Object -First 5")
run_powershell("Get-ChildItem C:\\", working_directory="C:\\temp")

# CMD
run_cmd("dir /b", working_directory="C:\\Windows")
run_cmd("systeminfo", timeout_seconds=30)
```

### File Operations

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

### Network Testing

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

## Architecture

### Modular Design
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

### Key Features

- **File-based Output Capture**: Works around Claude Desktop PowerShell limitations
- **Robust Error Handling**: Comprehensive validation and error recovery
- **FastMCP 2.11.3 Compliance**: Modern MCP protocol implementation with stateful tools support
- **Austrian Dev Efficiency**: Clean, maintainable, production-ready code

## Development

### Run in Development Mode

```bash
python -m windows_operations_mcp
```

### Enable Debug Logging

```bash
python -m windows_operations_mcp --debug
```

### Testing

```bash
pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Austrian Development Philosophy

This project follows the "Austrian dev efficiency" principle:
- **Working solutions in hours, not days**
- **Clean, maintainable code architecture**
- **Comprehensive error handling**
- **Production-ready from day one**
- **No stubs, no placeholders - everything works**

---

Built with ❤️ for Windows automation and Claude Desktop integration.
