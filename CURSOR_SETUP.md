# Windows Operations MCP - Cursor IDE Setup Guide

**Quick setup guide for running Windows Operations MCP in Cursor IDE.**

## Prerequisites

1. **Python 3.12+** (matches `pyproject.toml`). On Windows, the **`py` launcher** is reliable even when `python` is not on PATH.
2. **Windows OS** (required for Windows-specific operations)
3. **Windows Operations MCP** dependencies installed for that interpreter (editable install recommended)

## Installation

**Important:** Cursor uses the system Python, so dependencies must be installed globally or in the Python that Cursor uses.

```powershell
cd d:\Dev\repos\windows-operations-mcp

# Option 1: Install for the same interpreter you use in MCP (recommended on Windows)
py -3 -m pip install -e .

# Optional dev deps if requirements-dev.txt exists
py -3 -m pip install -r requirements-dev.txt

# Option 2: Virtual environment — then point MCP "command" at venv\Scripts\python.exe
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -e .
```

**Note:** Dependencies are defined in `pyproject.toml`. If `requirements-dev.txt` does not exist, `py -3 -m pip install -e .` is enough.

## Cursor Configuration

Add to your Cursor MCP configuration file:
**Location**: `%APPDATA%\Cursor\User\globalStorage\cursor-storage\mcp_config.json`

```json
{
  "mcpServers": {
    "windows-operations-mcp": {
      "command": "py",
      "args": [
        "-3",
        "-m",
        "windows_operations_mcp.__main__"
      ],
      "env": {
        "PYTHONPATH": "D:/Dev/repos/windows-operations-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Why `py` instead of `python`:** On many Windows setups, `python.exe` is not on PATH for GUI apps (including Cursor), so MCP fails to spawn the process. The **`py`** launcher is usually available. Use a concrete `python.exe` path if you prefer.

**Note:** Some JSON linters object to `cwd` parameter. Using `-m` module execution with `PYTHONPATH` avoids this issue.

### Using Virtual Environment

If using a virtual environment:

```json
{
  "mcpServers": {
    "windows-operations-mcp": {
      "command": "d:\\Dev\\repos\\windows-operations-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "windows_operations_mcp.__main__"
      ],
      "env": {
        "PYTHONPATH": "D:/Dev/repos/windows-operations-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Alternative: Using mcp_server.py with Absolute Path

If you prefer using `mcp_server.py` directly (avoids `cwd` which some linters reject):

```json
{
  "mcpServers": {
    "windows-operations-mcp": {
      "command": "py",
      "args": [
        "-3",
        "D:/Dev/repos/windows-operations-mcp/src/windows_operations_mcp/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "D:/Dev/repos/windows-operations-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Verification

1. **Check Python import:**
   ```powershell
   py -3 -c "import sys; sys.path.insert(0, 'src'); from windows_operations_mcp.mcp_server import mcp; print('SUCCESS')"
   ```

2. **Test MCP server startup:**
   ```powershell
   $env:PYTHONPATH = "D:\Dev\repos\windows-operations-mcp\src"
   py -3 -m windows_operations_mcp.__main__
   ```
   Should start without errors and wait for JSON-RPC messages on stdin.

3. **Check Cursor logs:**
   - Location: `%APPDATA%\Cursor\logs\`
   - Look for `windows-operations-mcp` in log files
   - Check for any import errors or startup failures

## Troubleshooting

### MCP never connects / Cursor shows the server failed (spawn error)

If **`python` is not a recognized command** in a normal PowerShell window, Cursor cannot start an MCP block that uses `"command": "python"`. Switch the config to **`py`** with args **`"-3"`**, **`"-m"`**, **`"windows_operations_mcp.__main__"`**, or set `"command"` to the full path of `python.exe` (for example under `AppData\Local\Programs\Python\`).

### ImportError: No module named 'fastmcp' / ModuleNotFoundError: Missing dependencies

**Solution:**
1. **Critical:** Cursor uses system Python, not your current shell's Python
2. Find system Python path from Cursor error logs (e.g., `C:\Users\sandr\AppData\Local\Programs\Python\Python310\python.exe`)
3. Install dependencies for that interpreter, for example:
   ```powershell
   py -3 -m pip install -e D:\Dev\repos\windows-operations-mcp
   ```
4. Or use the full path to `python.exe` shown in Cursor MCP logs with `-m pip install -e .` for this repo

### ModuleNotFoundError: No module named 'windows_operations_mcp'

**Solution:**
1. Ensure package is installed in the Python that Cursor uses: `python -m pip install -e .`
2. Set PYTHONPATH in Cursor config: `"PYTHONPATH": "D:/Dev/repos/windows-operations-mcp/src"`
3. Use absolute path to Python executable in venv if using virtual environment

### Server starts but tools don't appear

**Solution:**
1. Check Cursor logs for JSON-RPC errors
2. Verify FastMCP version: `py -3 -m pip show fastmcp` (see `pyproject.toml` for the supported range)
3. Restart Cursor after configuration changes

### Windows-specific errors (pywin32, permissions)

**Solution:**
1. Ensure `pywin32>=305` is installed: `pip install pywin32>=305`
2. Run as administrator if operations require elevated permissions
3. Check Windows Event Viewer for system-level errors

## Available Tools

Windows Operations MCP provides portmanteau tools for:
- **Command Execution**: PowerShell and CMD command execution
- **File Operations**: Read, write, delete, move, copy, list, info, exists
- **Directory Operations**: Create, delete, move, copy, list directories
- **Archive Management**: Create, extract, list ZIP/tar archives
- **JSON Operations**: Read, write, validate, format, convert, extract JSON
- **Git Operations**: Add, commit, push, status
- **Process Management**: List, info, resources for Windows processes
- **Windows Services**: List, start, stop, restart Windows services
- **System Management**: Info, health, test_port, help

## Reference

- **Generalized Setup Guide**: `mcp-central-docs/docs/patterns/WEBAPP_SETUP_GUIDE.md`
- **Cursor Standards**: `mcp-central-docs/docs/ecosystem/cursor/README.md`
- **MCP Standards**: `mcp-central-docs/STANDARDS.md`
- **Project README**: `README.md`
