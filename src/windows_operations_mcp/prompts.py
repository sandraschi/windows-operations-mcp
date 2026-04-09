"""
Windows Operations MCP - FastMCP 3.2 SOTA Prompts Registry
Registers standardized prompt prefabs for agentic system interaction.
Follows the 3-4-100 rule (3-4 high-quality prompts).
"""

from typing import List, Optional
from fastmcp import FastMCP

def register_all_prompts(mcp: FastMCP) -> None:
    """Register all SOTA 2026 prompt templates."""
    
    @mcp.prompt()
    def registry_hardening_wizard(target_hive: str = "HKLM") -> str:
        """Guide for identifying and fixing insecure registry keys."""
        return f"""
        ### 🛡️ Windows Registry Hardening Wizard (SOTA v14.0)

        **Objective**: Evaluate and harden the {target_hive} hive for security baseline compliance.

        **Sequence**:
        1.  **Inventory**: Use windows_registry action="list_keys" on critical paths (e.g., Software\\Microsoft\\Windows\\CurrentVersion\\Run).
        2.  **Audit**: Analyze subkeys for unusual persistence points or unauthorized apps.
        3.  **Remediation**: Use windows_registry action="delete" or "write" to disable insecure entries.
        4.  **Verification**: Re-list the keys to confirm they are no longer present or are set to secure values.

        **Safety**: 'Safe Mode' (auto-backup) is enabled by default. Confirm backups in 'backups/registry/' before destructive edits.
        """

    @mcp.prompt()
    def powershell_agent_scaffold(task: str) -> str:
        """Generate a robust, error-tolerant PowerShell script for a system task."""
        return f"""
        ### 🚀 PowerShell SOTA 2026 Scaffolding

        **Task**: {task}

        **Requirements**:
        - **$ErrorActionPreference = 'Stop'** must be set at the top for strict failure handling.
        - **Try/Catch/Finally** blocks for robust execution and cleanup.
        - **Structured Output**: Resulting data should be converted to JSON via 'ConvertTo-Json'.
        - **Execution**: Use the command_execution action="powershell" tool for invocation.

        **Example Pattern**:
        ```powershell
        $ErrorActionPreference = 'Stop'
        try {{
            $result = # Perform task here
            $result | ConvertTo-Json
        }} catch {{
            Write-Error $_
            exit 1
        }}
        ```
        """

    @mcp.prompt()
    def system_account_audit() -> str:
        """Review local user accounts and group memberships for security alignment."""
        return """
        ### 👥 Local Account Security Audit

        **Mission**: Audit the local SAM database for privilege escalation risks.

        **Checklist**:
        1.  **User Enumeration**: Run windows_accounts action="list_users".
        2.  **Privilege Check**: For each non-standard user, check membership in 'Administrators' or 'Remote Desktop Users'.
        3.  **Stale Account Identification**: Use windows_automation action="wmi_query" for 'Win32_UserAccount' to check last login dates.
        4.  **Remediation**: Use windows_accounts action="remove_user" or "manage_group" to trim unauthorized access.

        **Hardening**: Ensure the Principal of Least Privilege (PoLP) is maintained across all local accounts.
        """

    @mcp.prompt()
    def data_surgery_forensics() -> str:
        """Guide for using JSON/Archive tools to extract and analyze system artifacts."""
        return """
        ### 🧪 Forensic Data Surgery Hub

        **Mission**: Collect and analyze system configuration artifacts.

        **Orchestration**:
        1.  **Collection**: Use archive_management action="create" to zip critical config dirs (e.g., C:\\Windows\\System32\\config).
        2.  **Extraction**: Use archive_management action="extract" to a secure /tmp/ for inspection.
        3.  **JSON Patching**: Use json_operations action="patch" to evaluate config differences against a known secure baseline.
        4.  **Deep Search**: Use json_operations action="fuzzy_extract" to identify secrets or misconfigurations in unstructured log artifacts.
        """

__all__ = ["register_all_prompts"]
