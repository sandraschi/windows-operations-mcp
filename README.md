# 🪟 Windows Operations MCP — SOTA v14.0.1

### Native Windows Control Plane & Data Surgery for Agentic Ecosystems

`windows-operations-mcp` is a specialized, industrial-grade MCP server designed to provide LLMs with a high-fidelity control plane for Windows-native operations and complex data manipulation. It bypasses generic filesystem overhead to offer deep integration with Registry, User Accounts, Task Automation, and SOTA Data Logic.

---

## 🚀 Key Capabilities (SOTA v14.0)

### 🛠️ Windows Native Control
- **Registry Management**: Safe-mode editing with auto-backups, deep tree queries, and value manipulation.
- **Account Operations**: Local user and group management (listing, adding, password resets).
- **Automation Hub**: Scheduled task (schtasks) orchestration and WMI/CIM system introspection.
- **Permissions (ICACLS)**: Granular NTFS ACL management with recursive inheritance control.

### 🧬 Specialized Data Surgery
- **JSON Portmanteau**: Deep patching (recursive merging), fuzzy JSON extraction from unstructured text, and standards-compliant validation.
- **Archive Logic**: Unified interface for ZIP, TAR, and native Windows Cabinet (.cab) expansion.
- **Safe Mode**: Automatic state preservation (e.g., Registry exports) before destructive operations.

### 🛰️ Agentic Telemetry & Sampling
- **FastMCP 3.2+**: Full support for `ctx: Context` telemetry.
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
| `windows_accounts` | `list_users`, `add_user`, `manage_group` | Local SAM database operations. |
| `windows_automation` | `list_tasks`, `create_task`, `wmi_query` | System scheduling & state introspection. |
| `windows_permissions` | `get`, `grant`, `revoke`, `set_owner` | ICACLS-backed ACL management. |
| `json_operations` | `read`, `patch`, `extract_from_text` | Deep JSON surgery and fuzzy parsing. |
| `archive_management` | `list`, `extract`, `expand_cab` | ZIP/TAR/CAB management. |

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