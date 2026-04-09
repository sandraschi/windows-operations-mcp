# 📝 Changelog

All notable changes to the `windows-operations-mcp` project will be documented in this file.

---

## 🏆 [14.0.1] - 2026-04-09

### 🛡️ Gold Standard Stabilization
- **FastAPI Fix**: Resolved a critical 500 error in the `/api/tools` endpoint by refactoring `AIRouter` to use asynchronous `list_tools()` (FastMCP 3.2+ compatibility).
- **Build Hardening**: Hardened `build_mcpb.py` against `UnicodeEncodeError` in Windows terminal environments by removing non-ASCII characters.
- **Manifest Synchronization**: Reconciled `mcpb/manifest.json` with code-based prompts, ensuring high-fidelity discovery in MCPB runtimes.

## 🚀 [14.0.0] - 2026-04-06

### ✨ SOTA v14.0 Modernization
- **Core Refactoring**: Migrated entire tool registry to the `mcp.run()` pattern (FastMCP 3.2+).
- **Agentic Telemetry**: Integrated `ctx: Context` across all tools for progress reporting and structured logging.
- **LLM Sampling**: Added `ctx.sample()` logic to all error handlers for autonomous diagnostic advice and failure recovery.
- **Lean Tooling**: Purged redundant generic file/directory/git operations in favor of `filesystem-mcp`.

### 🪟 Windows Expansion (New & Modernized Tools)
- **`windows_registry`**: Implemented native `winreg` control with **Safe Mode** (automatic backups before modification).
- **`windows_accounts`**: Native management of local users and groups using `net.exe`.
- **`windows_automation`**: Portmanteau for `schtasks` (Scheduled Tasks) and `wmic` (WMI/CIM) introspection.
- **`windows_permissions`**: Consolidated ICACLS management for granular NTFS ACL surgery.
- **`archive_management`**: Modernized ZIP/TAR support and added specialized Windows Cabinet (`.cab`) expansion via `expand.exe`.

### 🧬 Specialized Data Handling
- **`json_operations`**: Advanced portmanteau for deep-patching (recursive merge), fuzzy JSON extraction, and validation.

### 🛠️ Infrastructure & Dev
- **Ruff Hardening**: Comprehensive linting and formatting pass for full industrial compliance.
- **Log Management**: Standardized SOTA logging configuration.
- **SOTA README**: Completely redesigned the Documentation Hub for agentic discoverability.

---

## 🛠️ [13.2.0] - 2026-03-20

### Added
- Initial portmanteau stubs for Windows system tools.
- FastMCP 2.x compatibility layer.

---

## 🧪 [13.0.0] - 2026-03-01

### Internal
- Initial repository layout and CI/CD scaffolding.
- Legacy file tool registrations (now deprecated).
