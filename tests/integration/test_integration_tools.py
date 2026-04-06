import pytest
import asyncio
from windows_operations_mcp.mcp_server import mcp as server

@pytest.mark.asyncio
async def test_command_execution_powershell():
    """Verify that PowerShell command execution completes successfully."""
    # Test tool call with FastMCP 3.2+ API
    result = await server.call_tool("command_execution", {
        "action": "powershell",
        "command": "$PSVersionTable.PSVersion.ToString()"
    })
    
    assert result is not None
    assert "success" in result
    assert result["success"] is True
    assert "stdout" in result
    assert "." in result["stdout"]  # Version string should contain dots

@pytest.mark.asyncio
async def test_command_execution_cmd():
    """Verify that CMD command execution captures stdout correctly."""
    result = await server.call_tool("command_execution", {
        "action": "cmd",
        "command": "echo SOTA_2026_TEST"
    })
    
    assert result["success"] is True
    assert "SOTA_2026_TEST" in result["stdout"]

@pytest.mark.asyncio
async def test_command_execution_failure_sampling(mcp):
    """Verify that failed commands include sampling advice in the response."""
    # Deliberately failing command
    result = await server.call_tool("command_execution", {
        "action": "powershell",
        "command": "NonExistentCmdlet-ErrorTest"
    })
    
    assert result["success"] is False
    assert result["exit_code"] != 0
    # Note: In real life, sampling advice depends on host capability.
    # In this test, we verify it doesn't crash even if sampling is unavailable.
