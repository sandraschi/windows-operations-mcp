# Windows Operations MCP

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.2%2B-6366f1?logo=python&logoColor=white)](https://github.com/jlowin/fastmcp)
[![Ruff](https://img.shields.io/badge/Ruff-passing-22c55e?logo=ruff)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/badge/License-MIT-3b82f6)](LICENSE)
[![GitHub](https://img.shields.io/github/v/release/sandraschi/windows-operations-mcp?logo=github)](https://github.com/sandraschi/windows-operations-mcp/releases)

MCP server for native Windows system administration — services, registry, accounts, event logs, networking, firewall, scheduled tasks, environment variables, AppX management, NTFS permissions, process monitoring, archive management, and JSON data operations.

Built on FastMCP 3.2+ with dual-transport (stdio + HTTP), a React dashboard, and an optional Tauri/NSIS desktop installer.

---

## Quick Start

```powershell
git clone https://github.com/sandraschi/windows-operations-mcp
cd windows-operations-mcp
just install
just mcp
```

For the web dashboard: `just web` (backend on `:10748`, frontend on `:10749`).

See [INSTALL.md](INSTALL.md) for manual setup or Claude Desktop integration.

---

## Tools

| Tool | What it does |
|------|-------------|
| `windows_registry` | Read, write, delete, export registry keys with auto-backup |
| `windows_accounts` | List/add/remove users and groups, manage group membership |
| `windows_services` | List, start, stop, restart Windows services |
| `windows_event_logs` | Query, clear, export event logs across all channels |
| `windows_network` | Firewall rule management (`netsh`) and adapter diagnostics |
| `windows_environment` | Get, set, delete persistent user/system env vars |
| `windows_apps` | List and uninstall AppX/Store packages |
| `windows_permissions` | View, grant, revoke NTFS ACLs (ICACLS) with inheritance control |
| `windows_automation` | Scheduled tasks (schtasks) and WMI/CIM queries |
| `windows_performance` | CPU, memory, disk, network metrics per-process and system-wide |
| `json_operations` | Read, write, deep-merge, validate, fuzzy-extract JSON |
| `archive_management` | Create, list, extract ZIP, TAR, and Windows CAB archives |
| `agentic_operations` | Autonomous system hardening and troubleshooting (LLM sampling) |
| `command_execution` | Execute PowerShell and CMD commands with reliable output capture |
| `container_execution` | Docker exec and file copy inside containers |

All tools use the [portmanteau pattern](https://opencode.ai) — a single tool with an `operation` parameter instead of many individual tools.

---

## Documentation

| Document | Contents |
|----------|----------|
| [INSTALL.md](INSTALL.md) | Installation, Claude Desktop config, troubleshooting |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute guide with examples |
| [docs/](docs/README.md) | Full documentation index |
| [examples/](examples/README.md) | Runnable usage examples |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
| [llms.txt](llms.txt) | LLM-friendly index |
| [llms-full.txt](llms-full.txt) | Full LLM context |

---

## Stack

- **Backend**: Python 3.12+, FastMCP 3.2+, FastAPI, Starlette, psutil, pywin32
- **Frontend**: React 19, Vite 7, TypeScript, TailwindCSS, Framer Motion, TanStack Query
- **Desktop**: Tauri 2.0, NSIS installer (embedded PyInstaller backend)
- **Ports**: Backend `10748`, Frontend `10749`

---

## License

MIT &mdash; Sandra Schipal, Vienna
