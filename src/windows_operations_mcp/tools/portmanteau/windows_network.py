"""
Windows Network Portmanteau - SOTA v14.1 (FastMCP 3.2+)
Provides comprehensive Windows Networking and Firewall management.
"""

import asyncio
from typing import Any, Literal

from fastmcp import Context

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def windows_network(
    action: Literal["firewall_list", "firewall_add", "firewall_delete", "diag"],
    rule_name: str | None = None,
    rule_dir: Literal["in", "out"] = "in",
    rule_action: Literal["allow", "block"] = "allow",
    rule_program: str | None = None,
    rule_port: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Perform Windows networking and firewall operations with specialized orchestration.

    RATIONALE:
    Consolidates complex 'netsh' and PowerShell networking commands into a single portmanteau.
    Enables autonomous security auditing and perimeter hardening.

    Args:
        action: The networking operation to perform.
        rule_name: Name of the firewall rule.
        rule_dir: Direction of the traffic (in/out).
        rule_action: Action (allow/block).
        rule_program: Path to the executable (for firewall_add).
        rule_port: Local port number (for firewall_add).
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"Network Op: {action}")
        ctx.report_progress(10, 100)

    try:
        if action == "firewall_list":
            if ctx:
                ctx.report_progress(50, 100)
            cmd = ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"]
            output = await _run_cmd(cmd)
            return {"success": True, "action": action, "data": {"raw_rules": output}}

        if action == "firewall_add":
            if not rule_name:
                return {"success": False, "error": "rule_name required"}
            if ctx:
                ctx.report_progress(50, 100)
            cmd = [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                f"name={rule_name}",
                f"dir={rule_dir}",
                f"action={rule_action}",
            ]
            if rule_program:
                cmd.append(f"program={rule_program}")
            if rule_port:
                cmd.append("protocol=TCP")
                cmd.append(f"localport={rule_port}")
            await _run_cmd(cmd)
            return {"success": True, "action": action, "data": {"status": f"Rule '{rule_name}' added"}}

        if action == "firewall_delete":
            if not rule_name:
                return {"success": False, "error": "rule_name required"}
            if ctx:
                ctx.report_progress(50, 100)
            cmd = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"]
            await _run_cmd(cmd)
            return {"success": True, "action": action, "data": {"status": f"Rule '{rule_name}' deleted"}}

        if action == "diag":
            if ctx:
                ctx.report_progress(30, 100)
            results = {}
            # Flush DNS
            await _run_cmd(["ipconfig", "/flushdns"])
            results["dns_flushed"] = True
            # Get IP config
            results["ipconfig"] = await _run_cmd(["ipconfig", "/all"])
            return {"success": True, "action": action, "data": results}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"Network Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(
                    f"Windows Network operation '{action}' failed. Error: {e}. Suggest repair.", max_tokens=100
                )
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx:
            ctx.report_progress(100, 100)


async def _run_cmd(cmd: list[str]) -> str:
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(stderr.decode().strip() or stdout.decode().strip())
    return stdout.decode().strip()


def register_windows_network(mcp) -> None:
    """Register the modernized Windows network tool."""
    mcp.tool()(windows_network)
