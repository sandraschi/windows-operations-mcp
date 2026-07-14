# Quick Start

## Install

```powershell
git clone https://github.com/sandraschi/windows-operations-mcp
cd windows-operations-mcp
uv sync --all-extras
```

## Run the MCP server

```powershell
uv run python -m windows_operations_mcp
```

This starts stdio mode for Claude Desktop / Cursor.

## Run the web dashboard

```powershell
uv run uvicorn windows_operations_mcp.server:app --port 10748
```

Then open `http://localhost:10748` or the Vite frontend on `:10749`.

## Claude Desktop config

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "windows-operations": {
      "command": "uv",
      "args": ["run", "--directory", "C:/path/to/windows-operations-mcp", "python", "-m", "windows_operations_mcp"]
    }
  }
}
```

## Try it out

In Claude, ask:

- "List running Windows services"
- "Show me the last 10 Application event log errors"
- "What's my disk usage?"
- "Create a firewall rule to block port 445 inbound"
- "List installed AppX packages related to Xbox"
- "Export the registry key HKLM\Software\MyApp"

## What's included

| Tool | Ask Claude to... |
|------|-----------------|
| `windows_registry` | read/write/export registry keys |
| `windows_accounts` | list users, manage groups |
| `windows_services` | list/start/stop services |
| `windows_event_logs` | query event logs by channel/level/ID |
| `windows_network` | manage firewall rules, run diagnostics |
| `windows_environment` | set/get/delete env vars |
| `windows_apps` | list/uninstall AppX packages |
| `windows_permissions` | view/grant/revoke NTFS permissions |
| `windows_automation` | create scheduled tasks, run WMI queries |
| `windows_performance` | check CPU/memory/disk/network |
| `json_operations` | read/write/merge/validate JSON |
| `archive_management` | create/extract ZIP, TAR, CAB |
| `command_execution` | run PowerShell or CMD commands |

See [examples/](examples/) for runnable Python scripts.
