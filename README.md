# 🪟 Windows Operations MCP — SOTA v14.1.0

[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.2.0-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/sandraschi/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Linted with Biome](https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white)](https://biomejs.dev/) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

### Native Windows Control Plane & Data Surgery for Agentic Ecosystems

`windows-operations-mcp` is a specialized, industrial-grade MCP server designed to provide LLMs with a high-fidelity control plane for Windows-native operations and complex data manipulation. It bypasses generic filesystem overhead to offer deep integration with Registry, User Accounts, Task Automation, and SOTA Data Logic.

---

## 🚀 Key Capabilities (SOTA v14.0)

### 🛠️ Windows Native Control
- **Registry Management**: Safe-mode editing with auto-backups, deep tree queries, and value manipulation.
- **Account Operations**: Local user and group management (listing, adding, password resets).
- **Automation Hub**: Scheduled task (schtasks) orchestration and WMI/CIM system introspection.
- **Permissions (ICACLS)**: Granular NTFS ACL management with recursive inheritance control.
- **Networking Control**: Native firewall orchestration (`netsh`) and adapter diagnostics. [NEW]
- **Environment Surgery**: Persistent User/System environment variable management with system-wide broadcasting. [NEW]
- **App Management**: AppX/Store package management and automated bloatware removal. [NEW]

### 🧬 Specialized Data Surgery
- **JSON Portmanteau**: Deep patching (recursive merging), fuzzy JSON extraction from unstructured text, and standards-compliant validation.
- **Archive Logic**: Unified interface for ZIP, TAR, and native Windows Cabinet (.cab) expansion.
- **Safe Mode**: Automatic state preservation (e.g., Registry exports) before destructive operations.

### 🛰️ Agentic Telemetry & Sampling
- **FastMCP 3.2.0+**: Full support for `ctx: Context` telemetry.
- **LLM-in-the-loop**: Integrated `ctx.sample()` for autonomous failure recovery and repair suggestions.
- **Industrial Logging**: Structured async logging for high-concurrency environments.

---

## 📦 Installation

```powershell
mcp install windows-operations-mcp
```

Or manually via `mcp_config.json`:

```json
{
  "mcpServers": {
    "windows-operations": {
      "command": "python",
      "args": ["-m", "windows_operations_mcp"],
      "env": {
        "PYTHONPATH": "C:/path/to/repo/src"
      }
    }
  }
}
```

---

## 🛠️ Tool Registry Reference

| Tool | Portmanteau Action | Description |
| :--- | :--- | :--- |
| `windows_registry` | `read`, `write`, `delete`, `export` | Native Winreg control with Safe Mode protection. |
| `windows_accounts` | `list_users`, `manage_group`, `get_group_members` | Local SAM database and security group auditing. |
| `windows_services` | `list`, `start`, `stop`, `restart` | Native Windows Service Control Manager orchestration. |
| `windows_event_logs` | `query`, `clear`, `export`, `list` | Comprehensive Event Log management and channel discovery. |
| `windows_network` | `firewall_list`, `firewall_add`, `diag` | Firewall rule management and networking diagnostics. |
| `windows_environment` | `get`, `set`, `delete`, `list` | Persistent User/System environment variable control. |
| `windows_apps` | `list`, `uninstall` | AppX/Store package auditing and uninstallation. |
| `windows_permissions` | `get`, `grant`, `revoke`, `set_owner` | ICACLS-backed ACL management. |
| `windows_automation` | `list_tasks`, `create_task`, `wmi_query` | System scheduling & state introspection. |
| `windows_performance` | `system`, `process`, `counters` | High-fidelity telemetry and performance monitoring. |
| `json_operations` | `read`, `patch`, `extract_from_text` | Deep JSON surgery and fuzzy parsing. |
| `archive_management` | `list`, `extract`, `expand_cab` | ZIP/TAR/CAB management. |
| `agentic_operations` | `system_hardening`, `audit_report` | High-level autonomous troubleshooting workflows. |

---

## 📜 Ethical Guardrails & Safety
1. **Safe Mode (Registry)**: Setting `safe_mode=True` (default) automatically exports Registry keys to `backups/registry/` before any write/delete.
2. **Contextual Awareness**: Agents are provided with real-time progress reports and warning logs for high-impact operations.
3. **Reductionist Logic**: No redundant tools. We defer standard filesystem tasks to `filesystem-mcp` to maintain a lean, high-performance orchestration layer.

---

## 🧪 Development & Testing

### Prerequisites
- Windows 10/11 Pro
- Python 3.10+
- `fastmcp` 3.2.0

### Running Tests
```powershell
pytest
```

---

*Author: Sandra Schipal (Vienna, AT)*  
*License: MIT*


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.
