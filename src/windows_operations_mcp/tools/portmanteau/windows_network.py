"""
Windows Network - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_net":
  winops_net/firewall_list   - List all firewall rules
  winops_net/firewall_add    - Add a firewall rule
  winops_net/firewall_delete - Delete a firewall rule by name
  winops_net/diag            - Flush DNS and return ipconfig output
"""

import asyncio
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)


async def _run_cmd(cmd: list[str]) -> str:
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode(errors="replace").strip() or stdout.decode(errors="replace").strip())
    return stdout.decode(errors="replace").strip()


def register_windows_network(parent_mcp: FastMCP) -> None:
    """Mount atomic network tools under namespace 'winops_net'."""
    ns = FastMCP(name="winops_net")

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    )
    async def firewall_list(ctx: Context | None = None) -> dict[str, Any]:
        """List all Windows Firewall rules via netsh.

        ## Return Format
        ```json
        {"success": bool, "raw_rules": str}
        ```

        ## Examples
            firewall_list()
        """
        try:
            raw = await _run_cmd(["netsh", "advfirewall", "firewall", "show", "rule", "name=all"])
            return {"success": True, "raw_rules": raw}
        except Exception as e:
            return fail_response(
                str(e), suggestions=["Ensure the MCP server is running with Administrator privileges."]
            )

    @ns.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
        )
    )
    async def firewall_add(
        rule_name: Annotated[str, Field(description="Unique name for the firewall rule.")],
        direction: Annotated[Literal["in", "out"], Field(description="Traffic direction.")] = "in",
        action: Annotated[Literal["allow", "block"], Field(description="Rule action.")] = "allow",
        program: Annotated[str | None, Field(description="Path to executable (optional).")] = None,
        port: Annotated[str | None, Field(description="TCP port number (optional).")] = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Add a Windows Firewall rule.

        ## Return Format
        ```json
        {"success": bool, "rule_name": str}
        ```

        ## Examples
            firewall_add(rule_name="Allow SSH", direction="in", action="allow", port="22")
        """
        try:
            cmd = [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                f"name={rule_name}",
                f"dir={direction}",
                f"action={action}",
            ]
            if program:
                cmd.append(f"program={program}")
            if port:
                cmd += ["protocol=TCP", f"localport={port}"]
            await _run_cmd(cmd)
            return {"success": True, "rule_name": rule_name}
        except Exception as e:
            return fail_response(str(e), suggestions=["Run as Administrator. Verify rule_name is unique."])

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False)
    )
    async def firewall_delete(
        rule_name: Annotated[str, Field(description="Name of the firewall rule to delete.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Delete a Windows Firewall rule by name.

        ## Return Format
        ```json
        {"success": bool, "rule_name": str}
        ```

        ## Examples
            firewall_delete(rule_name="Allow SSH")
        """
        try:
            await _run_cmd(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"])
            return {"success": True, "rule_name": rule_name}
        except Exception as e:
            return fail_response(str(e), suggestions=["Verify rule exists with winops_net/firewall_list."])

    @ns.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True)
    )
    async def diag(ctx: Context | None = None) -> dict[str, Any]:
        """Flush DNS cache and return full ipconfig output.

        ## Return Format
        ```json
        {"success": bool, "dns_flushed": bool, "ipconfig": str}
        ```

        ## Examples
            diag()
        """
        try:
            await _run_cmd(["ipconfig", "/flushdns"])
            ipconfig = await _run_cmd(["ipconfig", "/all"])
            return {"success": True, "dns_flushed": True, "ipconfig": ipconfig}
        except Exception as e:
            return fail_response(str(e))

    parent_mcp.mount(ns, prefix="winops_net")
    logger.info("Mounted atomic tools: winops_net/firewall_list, /firewall_add, /firewall_delete, /diag")
