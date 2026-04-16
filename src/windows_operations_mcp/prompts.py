"""
Windows Operations MCP - FastMCP 3.2 SOTA Prompts Registry
Registers standardized prompts for agentic system interaction.
Follows the 3-4-100 rule: 4 high-quality, parameterized prompts.
"""

from fastmcp import FastMCP


def register_all_prompts(mcp: FastMCP) -> None:
    """Register all SOTA 2026 prompt templates."""

    @mcp.prompt(
        name="registry_hardening_wizard",
        description="Guide for identifying and fixing insecure registry keys in a given hive.",
        tags={"security", "registry", "hardening"},
    )
    def registry_hardening_wizard(target_hive: str = "HKLM") -> str:
        """Guide for identifying and fixing insecure registry keys."""
        return f"""
### Windows Registry Hardening Wizard (SOTA v14.2.0)

**Objective**: Evaluate and harden the {target_hive} hive for security baseline compliance.

**Sequence**:
1. **Inventory**: Use `windows_registry` action="list_keys" on critical paths
   (e.g., `Software\\Microsoft\\Windows\\CurrentVersion\\Run`).
2. **Audit**: Analyze subkeys for unusual persistence points or unauthorized apps.
3. **Remediation**: Use `windows_registry` action="delete" or "write" to disable insecure entries.
4. **Verification**: Re-list the keys to confirm removal or secure values.

**Safety**: safe_mode=True (default) auto-exports the target key to backups/registry/ before any
destructive action. Confirm backups exist before proceeding.
"""

    @mcp.prompt(
        name="powershell_agent_scaffold",
        description="Generate a robust, error-tolerant PowerShell script scaffold for a given Windows task.",
        tags={"powershell", "scripting", "agentic"},
    )
    def powershell_agent_scaffold(task: str) -> str:
        """Generate a robust, error-tolerant PowerShell script for a system task."""
        return f"""
### PowerShell SOTA 2026 Scaffolding

**Task**: {task}

**Requirements**:
- Set `$ErrorActionPreference = 'Stop'` at the top for strict failure propagation.
- Use Try/Catch/Finally blocks for execution and cleanup.
- Emit structured output via `ConvertTo-Json` so results are agent-parseable.
- Invoke via `command_execution` action="powershell".

**Template**:
```powershell
$ErrorActionPreference = 'Stop'
try {{
    $result = # Perform task here
    $result | ConvertTo-Json -Depth 5
}} catch {{
    Write-Error $_
    exit 1
}} finally {{
    # Cleanup if needed
}}
```
"""

    @mcp.prompt(
        name="system_account_audit",
        description="Review local user accounts and group memberships for security and privilege alignment.",
        tags={"security", "accounts", "audit"},
    )
    def system_account_audit() -> str:
        """Review local user accounts and group memberships for security alignment."""
        return """
### Local Account Security Audit

**Mission**: Audit the local SAM database for privilege escalation risks.

**Checklist**:
1. **User Enumeration**: Run `windows_accounts` action="list_users".
2. **Privilege Check**: For each non-standard user, check membership in Administrators
   or Remote Desktop Users via `windows_accounts` action="get_group_members".
3. **Stale Account Detection**: Use `windows_automation` action="wmi_query"
   class="Win32_UserAccount" to check last login dates.
4. **Remediation**: Use `windows_accounts` action="remove_user" or "manage_group"
   to trim unauthorized access.

**Principle**: Enforce Least Privilege (PoLP) across all local accounts.
"""

    @mcp.prompt(
        name="data_surgery_forensics",
        description="Guide for using JSON and Archive tools to collect and analyze system configuration artifacts.",
        tags={"forensics", "json", "archive", "data"},
    )
    def data_surgery_forensics() -> str:
        """Guide for using JSON/Archive tools to extract and analyze system artifacts."""
        return """
### Forensic Data Surgery Hub

**Mission**: Collect and analyze system configuration artifacts for forensic or compliance review.

**Orchestration**:
1. **Collection**: Use `archive_management` action="create" to zip critical config dirs.
2. **Extraction**: Use `archive_management` action="extract" to a secure temp path for inspection.
3. **JSON Patching**: Use `json_operations` action="patch" to compare config deltas against
   a known secure baseline.
4. **Deep Search**: Use `json_operations` action="fuzzy_extract" to surface secrets or
   misconfigurations in unstructured log artifacts.

**Output**: Write findings to a structured JSON report via `json_operations` action="write".
"""


__all__ = ["register_all_prompts"]
