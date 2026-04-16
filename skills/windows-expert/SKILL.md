# 🛠️ Skill: Windows Native Hardening & Data Surgery

### Name: windows-expert
### Description: Expert in Windows-native orchestration, registry hardening, account management, and high-fidelity JSON/Archive surgery.

---

## 📖 Overview
This skill provides the operational logic and safe-mode patterns for managing Windows systems at an industrial grade. It prioritizes system integrity via "Safe Mode" registry operations and "Lean SOTA" data manipulation.

---

## 🛠️ Tool Interaction Patterns

### 1. Registry Hardening (`windows_registry`)
- **Pattern**: Always perform a read/export before a write.
- **Safe Mode**: The `safe_mode=True` parameter (default) automatically exports the target key to `backups/registry/` before any destructive action.
- **Hardening Example**: 
  - Action: `delete`
  - Key: `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\UnwantedApp`
  - Result: Auto-backup created.

### 2. Local Account Management (`windows_accounts`)
- **Pattern**: List users before adding or modifying passwords.
- **Groups**: Use `manage_group` to enforce the Principle of Least Privilege (PoLP).
- **Audit**: Run `get_group_members` on the "Administrators" group to identify SID-based privilege creep.

### 3. Networking & Perimeter (`windows_network`)
- **Firewall**: Use `firewall_list` before adding new rules.
- **Diagnostics**: Always `flush_dns` as a first step in network-related agentic troubleshooting.

### 4. Environment Surgery (`windows_environment`)
- **Persistence**: Distinguish between `User` and `System` scopes.
- **Synchronization**: Always trigger a `broadcast` after modifications to ensure running processes adopt the new environment map.

---

## 🛰️ Agentic Workflows (FastMCP 3.2+)

### ⚡ Thinking Pattern: Autonomous Hardening
1.  **Inventory**: Run `windows_automation(action="wmi_query", wmi_class="Win32_OperatingSystem")` to identify the environment.
2.  **Audit**: Run `windows_accounts(action="list_users")` or `windows_services(action="list")`.
3.  **Diagnostic Sampling**: Use **SEP-1577 Sampling** (`ctx.sample()`) with a 'Reasoning' prompt to identify vulnerabilities in the inventory.
4.  **Remediation**: Use `windows_registry` or `windows_services` to apply changes.
5.  **Verification**: Re-audit and log the results using `json_operations(action="write")` to a status report.

### 🔍 Workflow Introspection
Tools in this server use `ctx: Context` for deep telemetry. You can view progress logs and sampling advice in the `windows_operations_mcp` dashboard (Port 10749).

---

## 📜 Ethical Protocols
1. **No Redundancy**: Do NOT use this server for generic file CRUD (use `filesystem-mcp`).
2. **Safe Mode Enforcement**: Never disable `safe_mode` in the registry without a risk assessment.
3. **Sampling First**: Always use `ctx.sample()` before bulk remediation to confirm policy alignment.

---

*Author: Sandra Schipal (Vienna, AT)*  
*Industrial Grade v14.1.0 Gold Standard Compliance*
