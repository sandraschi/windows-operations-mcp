"""
Agentic Operations - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Two high-level orchestrators registered directly (no namespace prefix needed — they
are not operation families, they are missions):
  agentic_system_hardening   - Autonomous security hardening of services/registry/accounts
  autonomous_troubleshooter  - Root-cause analysis for Windows operation failures
"""

import asyncio
import json
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)

_SAMPLE_TIMEOUT = 30.0


def register_agentic_operations(parent_mcp: FastMCP) -> None:
    """Register agentic orchestrator tools directly on the parent MCP."""

    @parent_mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def agentic_system_hardening(
        target: Annotated[
            Literal["services", "registry", "accounts"],
            Field(description="Subsystem to harden."),
        ],
        dry_run: Annotated[bool, Field(description="Audit only (True) or apply fixes (False).")] = True,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Autonomous Windows security hardening with SEP-1577 sampling.

        Phases: (1) Inventory the target subsystem, (2) LLM audit for hardening
        recommendations, (3) Apply HIGH-priority fixes in live mode.

        ## Return Format
        ```json
        {
          "success": bool,
          "target": str,
          "dry_run": bool,
          "audit_recommendations": str,
          "actions_taken": [{"action": str, "status": str}]
        }
        ```

        ## Examples
            agentic_system_hardening(target="services", dry_run=True)
            agentic_system_hardening(target="accounts", dry_run=False)

        Notes:
         - ctx is required; returns error if called without it.
         - dry_run=False will queue up to 5 HIGH-priority actions.
        """
        if not ctx:
            return fail_response(
                "Context required for agentic orchestration.",
                suggestions=["Ensure this tool is called via the MCP protocol, not standalone."],
            )

        await ctx.info(f"Mission: Hardening {target} (dry_run={dry_run})")
        await ctx.report_progress(5, 100)

        findings: dict[str, Any] = {}

        try:
            # Phase 1: Inventory
            if target == "services":
                from .windows_services import _list_services_blocking

                findings = await asyncio.to_thread(_list_services_blocking, None, True)
            elif target == "registry":
                from .windows_registry import HIVES, _list_blocking

                subkeys, values = await asyncio.to_thread(
                    _list_blocking,
                    HIVES["HKLM"],
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                )
                findings = {"subkeys": subkeys, "values": values}
            elif target == "accounts":
                proc = await asyncio.create_subprocess_exec(
                    "net.exe",
                    "user",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await proc.communicate()
                findings = {"raw_users": stdout.decode(errors="replace").strip()}

            await ctx.report_progress(30, 100)

            # Phase 2: Sampling audit
            await ctx.info("Phase 2: Agentic audit via sampling...")
            try:
                sampling_res = await asyncio.wait_for(
                    ctx.sample(
                        prompt=(
                            f"Target subsystem: {target}\n"
                            f"Inventory:\n{json.dumps(findings, indent=2, default=str)}\n\n"
                            "List specific hardening actions with priority (HIGH/MED/LOW)."
                        ),
                        system_prompt=(
                            "You are a SOTA Windows Security Researcher. Analyze the inventory and "
                            "identify critical hardening steps. Focus on Principle of Least Privilege, "
                            "persistence reduction, and service surface minimization. Be concise."
                        ),
                        max_tokens=1000,
                    ),
                    timeout=_SAMPLE_TIMEOUT,
                )
                recommendations = (
                    sampling_res.content[0].text if sampling_res and sampling_res.content else "No recommendations."
                )
            except Exception as e:
                recommendations = f"Sampling unavailable: {e}"

            await ctx.report_progress(60, 100)

            # Phase 3: Remediation (live only)
            actions_taken = []
            if not dry_run:
                high_lines = [
                    line.strip() for line in recommendations.splitlines() if "HIGH" in line.upper() and line.strip()
                ]
                for item in high_lines[:5]:
                    actions_taken.append({"action": item, "status": "queued"})

            await ctx.report_progress(100, 100)
            return {
                "success": True,
                "target": target,
                "dry_run": dry_run,
                "audit_recommendations": recommendations,
                "actions_taken": actions_taken,
            }

        except Exception as e:
            return fail_response(str(e))

    @parent_mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=False, openWorldHint=False)
    )
    async def autonomous_troubleshooter(
        operation_failure: Annotated[str, Field(description="Description of the failure to investigate.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Diagnose why a Windows operation failed using event logs, process list, and LLM sampling.

        Phases: (1) Query recent System log errors, (2) Snapshot running processes,
        (3) LLM root-cause analysis with remediation steps.

        ## Return Format
        ```json
        {
          "success": bool,
          "failure_reported": str,
          "event_log_summary": any,
          "root_cause_analysis": str
        }
        ```

        ## Examples
            autonomous_troubleshooter(operation_failure="Could not start WinRM service — access denied")

        Notes:
         - ctx is required for sampling.
        """
        if not ctx:
            return fail_response("Context required for autonomous troubleshooting.")

        await ctx.info(f"Investigating: {operation_failure[:80]}")
        await ctx.report_progress(10, 100)

        findings: dict[str, Any] = {}

        # Phase 1: Event log
        try:
            from .windows_event_logs import _query_events_blocking

            events = await asyncio.to_thread(_query_events_blocking, "System", 20, 1, None)
            findings["event_log_errors"] = [e for e in events if e.get("level") == "Error"]
        except Exception as e:
            findings["event_log_errors"] = f"Unavailable: {e}"

        await ctx.report_progress(35, 100)

        # Phase 2: Process snapshot
        try:
            import psutil

            procs = []
            for p in psutil.process_iter(["pid", "name", "username"]):
                try:
                    procs.append(p.info)
                    if len(procs) >= 30:
                        break
                except Exception:
                    continue
            findings["running_processes_sample"] = procs
        except Exception as e:
            findings["running_processes_sample"] = f"Unavailable: {e}"

        await ctx.report_progress(60, 100)

        # Phase 3: Sampling root cause
        await ctx.info("Phase 3: Root cause analysis via sampling...")
        try:
            sampling_res = await asyncio.wait_for(
                ctx.sample(
                    prompt=(
                        f"Failure: {operation_failure}\n\n"
                        f"Diagnostics:\n{json.dumps(findings, indent=2, default=str)}\n\n"
                        "Provide: (1) Most probable root cause, (2) Verification steps, (3) Fix commands."
                    ),
                    system_prompt=(
                        "You are a senior Windows systems engineer. Given a failure description and "
                        "system diagnostics, identify the most probable root cause. Consider: Permissions, "
                        "Locked Files, Registry corruption, Service dependency, Network/DNS, UAC/Policy."
                    ),
                    max_tokens=800,
                ),
                timeout=_SAMPLE_TIMEOUT,
            )
            advice = sampling_res.content[0].text if sampling_res and sampling_res.content else "Sampling unavailable."
        except Exception as e:
            advice = f"Sampling failed: {e}"

        await ctx.report_progress(100, 100)
        return {
            "success": True,
            "failure_reported": operation_failure,
            "event_log_summary": findings.get("event_log_errors", []),
            "root_cause_analysis": advice,
        }

    logger.info("Registered agentic tools: agentic_system_hardening, autonomous_troubleshooter")
