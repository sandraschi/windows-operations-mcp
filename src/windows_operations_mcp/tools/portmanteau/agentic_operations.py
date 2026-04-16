"""
Agentic Operations - SOTA v14.2.0 (FastMCP 3.2+)
Autonomous workflows with full SEP-1577 sampling integration.
"""

import json
from typing import Any, Literal

from fastmcp import Context

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def agentic_system_hardening(
    target: Literal["services", "registry", "accounts"],
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Execute an autonomous system hardening mission with SEP-1577 Sampling.

    RATIONALE:
    This orchestrator coordinates multiple specialized tools to reach a
    security baseline. It uses 'Reasoning-First' sampling to identify
    vulnerabilities before action.

    Args:
        target: The subsystem to harden.
        dry_run: If True, only audit and recommend (default: True).
        ctx: FastMCP Context for telemetry and sampling.
    """
    if not ctx:
        return {"success": False, "error": "Context required for agentic orchestration."}

    ctx.info(f"Mission: Hardening {target} (dry_run={dry_run})")
    ctx.report_progress(5, 100)

    try:
        # Phase 1: Inventory
        inventory: dict[str, Any] = {}
        if target == "services":
            from .windows_services import windows_services

            inventory = await windows_services(action="list", ctx=ctx)
        elif target == "registry":
            from .windows_registry import windows_registry

            inventory = await windows_registry(
                action="list_keys",
                key_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                hive="HKLM",
                ctx=ctx,
            )
        elif target == "accounts":
            from .windows_accounts import windows_accounts

            inventory = await windows_accounts(action="list_users", ctx=ctx)

        ctx.report_progress(30, 100)

        # Phase 2: SEP-1577 Diagnostic Sampling
        ctx.info("Phase 2: Agentic audit via sampling...")
        system_prompt = (
            "You are a SOTA Windows Security Researcher. Analyze the provided inventory "
            "and identify critical hardening steps. Focus on: Principle of Least Privilege (PoLP), "
            "persistence reduction, and service surface minimization. Be concise and actionable."
        )
        user_prompt = (
            f"Target subsystem: {target}\n"
            f"Inventory:\n{json.dumps(inventory, indent=2, default=str)}\n\n"
            "List specific hardening actions with priority (HIGH/MED/LOW)."
        )

        sampling_res = await ctx.sample(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
        )
        recommendations = (
            sampling_res.content[0].text if sampling_res and sampling_res.content else "Sampling returned no advice."
        )
        ctx.info(f"Audit complete: {recommendations[:120]}...")
        ctx.report_progress(60, 100)

        # Phase 3: Remediation (live mode only)
        actions_taken = []
        if not dry_run:
            ctx.warning("Phase 3: Execution mode — applying recommendations.")
            # Parse sampling output for actionable items (simplified heuristic)
            high_priority_lines = [
                line.strip() for line in recommendations.splitlines() if "HIGH" in line.upper() and line.strip()
            ]
            for item in high_priority_lines[:5]:  # cap at 5 automated actions
                actions_taken.append({"action": item, "status": "queued"})
            ctx.info(f"Queued {len(actions_taken)} HIGH priority actions.")
        else:
            ctx.info("Phase 3: Dry run — no changes applied.")

        ctx.report_progress(100, 100)
        return {
            "success": True,
            "mission": "hardening",
            "target": target,
            "dry_run": dry_run,
            "inventory_keys": list(inventory.keys()) if isinstance(inventory, dict) else [],
            "audit_recommendations": recommendations,
            "actions_taken": actions_taken,
        }

    except Exception as e:
        if ctx:
            ctx.error(f"Mission failed: {e}")
        return {"success": False, "error": str(e)}


async def autonomous_troubleshooter(
    operation_failure: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Diagnose WHY a Windows operation failed (Permissions vs Process vs Registry).

    Uses a 3-phase approach:
    1. Scan recent Event Log errors
    2. Check running processes for blockers
    3. Sample for probable root cause and remediation steps

    Args:
        operation_failure: Description of the failure to investigate.
        ctx: FastMCP Context for telemetry and sampling (required).
    """
    if not ctx:
        return {"success": False, "error": "Context required for autonomous troubleshooting."}

    ctx.info(f"Investigating failure: {operation_failure[:80]}")
    ctx.report_progress(10, 100)

    findings: dict[str, Any] = {}

    # Phase 1: Recent Event Log errors
    try:
        from .windows_event_logs import windows_event_logs

        log_result = await windows_event_logs(
            action="query",
            log_name="System",
            level="Error",
            max_events=20,
            ctx=ctx,
        )
        findings["event_log_errors"] = log_result.get("data", {})
    except Exception as e:
        findings["event_log_errors"] = f"Unavailable: {e}"

    ctx.report_progress(35, 100)

    # Phase 2: Running processes that might block the operation
    try:
        from .process_management import process_management

        proc_result = await process_management(action="list", max_processes=50, ctx=ctx)
        findings["running_processes_sample"] = proc_result.get("data", {})
    except Exception as e:
        findings["running_processes_sample"] = f"Unavailable: {e}"

    ctx.report_progress(60, 100)

    # Phase 3: SEP-1577 Root Cause Sampling
    ctx.info("Phase 3: Root cause analysis via sampling...")
    system_prompt = (
        "You are a senior Windows systems engineer. Given a failure description and "
        "system diagnostics, identify the most probable root cause and provide step-by-step "
        "remediation. Categories to consider: Permissions, Locked Files/Processes, "
        "Registry corruption, Service dependency failure, Network/DNS, UAC/Policy."
    )
    user_prompt = (
        f"Failure reported: {operation_failure}\n\n"
        f"Diagnostics:\n{json.dumps(findings, indent=2, default=str)}\n\n"
        "Provide: (1) Most probable root cause, (2) Verification steps, (3) Fix commands."
    )

    try:
        sampling_res = await ctx.sample(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=800,
        )
        advice = sampling_res.content[0].text if sampling_res and sampling_res.content else "Sampling unavailable."
    except Exception as e:
        advice = f"Sampling failed: {e}"

    ctx.report_progress(100, 100)

    return {
        "success": True,
        "failure_reported": operation_failure,
        "event_log_summary": findings.get("event_log_errors", {}),
        "root_cause_analysis": advice,
    }


def register_agentic_operations(mcp) -> None:
    """Register SOTA v14.2.0 agentic orchestrators."""
    mcp.tool()(agentic_system_hardening)
    mcp.tool()(autonomous_troubleshooter)
