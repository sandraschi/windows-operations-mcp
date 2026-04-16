# 📝 Changelog

All notable changes to the `windows-operations-mcp` project will be documented in this file.

---

## [Unreleased]

### Changed
- **`mcp_server.py`**: Lifespan typing uses `collections.abc.AsyncGenerator`; registration comments aligned with **FastMCP 3.2+** (prompts, skills, prefab).

---

## [14.2.0] - 2026-04-09

### FastMCP 3.2 Full Conformance
- **SkillsDirectoryProvider**: Skills now served via proper `skill://windows-expert/SKILL.md` URI (FastMCP 3.1+ skills provider) — replaces manual `resource://` workaround.
- **Prefab UI tools** (`system_health_card`, `process_list_card`): New `tools/prefab/` module with `@mcp.tool(app=True)` + `ToolResult` + `PrefabApp` — rich in-chat cards for system health and process data. Guarded by `WINOPS_PREFAB_APPS` env var; install with `uv sync --extra apps`.
- **`prefab-ui` made optional**: Moved from core deps to `[project.optional-dependencies] apps`. Core server no longer fails if prefab-ui absent.
- **Prompts hardened**: Added `name=`, `description=`, `tags=` to all four `@mcp.prompt()` decorators — required for proper MCP prompt discovery/listing.
- **`server.py`**: `mcp.http_app()` → `mcp.asgi()` (former removed in FastMCP 3.2); switched from FastAPI to Starlette root (fleet standard).
- **`autonomous_troubleshooter`**: Was a 4-line stub (implementation honesty violation). Replaced with real 3-phase implementation: Event Log scan → process list → SEP-1577 root cause sampling.
- **`resources.py`**: Added `llms-full.txt` resource; kept legacy `resource://windows/expert-skill` for back-compat.
- **`command_execution.py`** (bug fix): Executor called with both `working_directory=` and `working_dir=` simultaneously regardless of action type — caused `PowerShellExecutor.execute() got an unexpected keyword argument 'working_directory'`. Fixed by splitting into action-specific branches.
- **`__init__.py`**: Version synced to 14.2.0; stale FastMCP 2.12.3 reference removed.

---

## 🏆 [14.1.0] - 2026-04-09

### 🌐 Windows Expansion (Networking & Environment)
- **Networking**: New `windows_network` portmanteau for native firewall orchestration (`netsh`) and adapter diagnostics.
- **Environment Surgery**: New `windows_environment` tool for persistent variable management with system-wide change broadcasting.
- **App Management**: New `windows_apps` tool for AppX/Store package management and automated bloatware removal.

### 🛡️ Tool Hardening & Extensions
- **Event Log Completion**: Implemented the previously placeholder `export` action and added `list` for channel discovery.
- **Group Auditing**: Added `get_group_members` to `windows_accounts` for deeper security introspection.
- **Registration Stabilization**: Expanded the core registry to include all 18 portmanteau tool modules for full SOTA compliance.

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
