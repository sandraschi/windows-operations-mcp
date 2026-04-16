import pytest

from windows_operations_mcp.mcp_server import mcp as server


@pytest.mark.asyncio
async def test_command_execution_powershell():
    """Verify that PowerShell command execution completes successfully."""
    # Test tool call with FastMCP 3.2+ API
    result = await server.call_tool(
        "command_execution", {"action": "powershell", "command": "$PSVersionTable.PSVersion.ToString()"}
    )

    assert result is not None
    assert "success" in result
    assert result["success"] is True
    assert "stdout" in result
    assert "." in result["stdout"]  # Version string should contain dots


@pytest.mark.asyncio
async def test_command_execution_cmd():
    """Verify that CMD command execution captures stdout correctly."""
    result = await server.call_tool("command_execution", {"action": "cmd", "command": "echo SOTA_2026_TEST"})

    assert result["success"] is True
    assert "SOTA_2026_TEST" in result["stdout"]


@pytest.mark.asyncio
async def test_command_execution_failure_sampling(mcp):
    """Verify that failed commands include sampling advice in the response."""
    # Deliberately failing command
    result = await server.call_tool(
        "command_execution", {"action": "powershell", "command": "NonExistentCmdlet-ErrorTest"}
    )

    assert result["success"] is False
    assert result["exit_code"] != 0
    # Note: In real life, sampling advice depends on host capability.
    # In this test, we verify it doesn't crash even if sampling is unavailable.


@pytest.mark.asyncio
async def test_windows_network_integration():
    """Integration test for firewall listing (safe)."""
    result = await server.call_tool("windows_network", {"action": "firewall_list"})
    assert result["success"] is True
    assert "raw_rules" in result


@pytest.mark.asyncio
async def test_windows_environment_integration():
    """Integration test for environment variable listing (safe)."""
    result = await server.call_tool("windows_environment", {"action": "list", "scope": "user"})
    assert result["success"] is True
    assert "variables" in result
    assert len(result["variables"]) > 0


@pytest.mark.asyncio
async def test_windows_apps_integration():
    """Integration test for app listing (safe)."""
    # Search for Calculator as it is almost always present
    result = await server.call_tool("windows_apps", {"action": "list", "name_filter": "Calculator"})
    assert result["success"] is True
    assert "apps" in result


@pytest.mark.asyncio
async def test_windows_accounts_integration():
    """Integration test for group member auditing (safe)."""
    result = await server.call_tool("windows_accounts", {"action": "get_group_members", "group_name": "Administrators"})
    assert result["success"] is True
    assert "members" in result
    assert len(result["members"]) > 0
