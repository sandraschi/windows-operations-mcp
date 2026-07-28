import json

import pytest

from windows_operations_mcp.mcp_server import mcp as server
from windows_operations_mcp.mcp_server import register_all_tools

# Must register tools on the module-level mcp instance before calling tools
register_all_tools()


def _parse(result):
    """Extract dict from ToolResult."""
    for item in result.content:
        if hasattr(item, "text"):
            return json.loads(item.text)
    return {}


@pytest.mark.asyncio
async def test_command_execution_powershell():
    """Verify PowerShell command execution (requires MCP session for ctx)."""
    try:
        result = await server.call_tool("winops_cmd_powershell", {"command": "$PSVersionTable.PSVersion.ToString()"})
        data = _parse(result)
        assert data.get("success") is True
        assert "." in data.get("stdout", "")
    except Exception as e:
        if "session is not available" in str(e):
            pytest.skip("MCP session required for ctx-dependent tools")
        raise


@pytest.mark.asyncio
async def test_command_execution_cmd():
    """Verify CMD command execution (requires MCP session for ctx)."""
    try:
        result = await server.call_tool("winops_cmd_cmd", {"command": "echo SOTA_2026_TEST"})
        data = _parse(result)
        assert data.get("success") is True
        assert "SOTA_2026_TEST" in data.get("stdout", "")
    except Exception as e:
        if "session is not available" in str(e):
            pytest.skip("MCP session required for ctx-dependent tools")
        raise


@pytest.mark.asyncio
async def test_command_execution_failure_sampling():
    """Verify failed commands report failure (requires MCP session for ctx)."""
    try:
        result = await server.call_tool("winops_cmd_powershell", {"command": "NonExistentCmdlet-ErrorTest"})
        data = _parse(result)
        assert data.get("success") is False
        assert data.get("exit_code") != 0
    except Exception as e:
        if "session is not available" in str(e):
            pytest.skip("MCP session required for ctx-dependent tools")
        raise


@pytest.mark.asyncio
async def test_windows_network_integration():
    """Integration test for firewall listing (safe)."""
    result = await server.call_tool("winops_net_firewall_list", {})
    data = _parse(result)
    assert data.get("success") is True
    assert "raw_rules" in data


@pytest.mark.asyncio
async def test_windows_environment_integration():
    """Integration test for environment variable listing (safe)."""
    result = await server.call_tool("winops_env_list", {"scope": "user"})
    data = _parse(result)
    assert data.get("success") is True
    assert "variables" in data


@pytest.mark.asyncio
async def test_windows_apps_integration():
    """Integration test for app listing (safe)."""
    result = await server.call_tool("winops_apps_list", {"name_filter": "Calculator"})
    data = _parse(result)
    assert data.get("success") is True
    assert "apps" in data


@pytest.mark.asyncio
async def test_windows_accounts_integration():
    """Integration test for group member auditing (safe)."""
    result = await server.call_tool("winops_accounts_group_members", {"group": "Administrators"})
    data = _parse(result)
    assert data.get("success") is True
    assert "members" in data
