import asyncio
import unittest
from unittest.mock import patch

from windows_operations_mcp.tools.portmanteau.windows_accounts import windows_accounts
from windows_operations_mcp.tools.portmanteau.windows_apps import windows_apps
from windows_operations_mcp.tools.portmanteau.windows_environment import windows_environment
from windows_operations_mcp.tools.portmanteau.windows_event_logs import windows_event_logs

# Target tools
from windows_operations_mcp.tools.portmanteau.windows_network import windows_network


class MockProcess:
    """Mock for asyncio subprocess."""

    def __init__(self, stdout=b"", stderr=b"", returncode=0):
        self.stdout_data = stdout
        self.stderr_data = stderr
        self.returncode = returncode

    async def communicate(self):
        return self.stdout_data, self.stderr_data


class TestPortmanteauExt(unittest.IsolatedAsyncioTestCase):
    """Isolated unit tests for v14.1.0 Portmanteau extensions with high-fidelity mocking."""

    async def test_windows_network_firewall_list(self):
        """Verify firewall listing logic and command construction."""
        mock_output = b"Rule Name: Allow Web\n------------------\nAction: Allow"
        mock_proc = MockProcess(stdout=mock_output)

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            result = await windows_network(action="firewall_list")

            self.assertTrue(result["success"])
            self.assertEqual(result["data"]["raw_rules"], mock_output.decode())
            mock_exec.assert_called_with(
                "netsh",
                "advfirewall",
                "firewall",
                "show",
                "rule",
                "name=all",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

    async def test_windows_environment_get(self):
        """Verify registry 'get' logic for environment variables."""
        with (
            patch("winreg.OpenKey") as mock_open,
            patch("winreg.QueryValueEx", return_value=("test_val", 1)) as mock_query,
        ):
            result = await windows_environment(action="get", name="TEST_VAR", scope="user")

            self.assertTrue(result["success"])
            self.assertEqual(result["data"]["value"], "test_val")
            mock_query.assert_called_with(mock_open.return_value.__enter__.return_value, "TEST_VAR")

    async def test_windows_apps_list(self):
        """Verify PowerShell JSON parsing for app listing."""
        mock_app_json = b'[{"Name": "Microsoft.Calculator", "Version": "10.0"}]'
        mock_proc = MockProcess(stdout=mock_app_json)

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            result = await windows_apps(action="list", name_filter="Calc")

            self.assertTrue(result["success"])
            self.assertEqual(len(result["data"]["apps"]), 1)
            self.assertEqual(result["data"]["apps"][0]["Name"], "Microsoft.Calculator")
            # Verify PS command contains name filter
            cmd_args = mock_exec.call_args[0]
            self.assertIn("Get-AppxPackage", cmd_args[-1])
            self.assertIn("-like '*Calc*'", cmd_args[-1])

    async def test_windows_event_logs_export(self):
        """Verify wevtutil orchestration for log export."""
        mock_proc = MockProcess()

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            result = await windows_event_logs(action="export", log_name="System", output_path="C:\\temp\\sys.evtx")

            self.assertTrue(result["success"])
            mock_exec.assert_called_with(
                "wevtutil.exe",
                "epl",
                "System",
                "C:\\temp\\sys.evtx",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

    async def test_windows_accounts_get_group_members(self):
        """Verify net.exe table parsing for group members."""
        mock_net_output = b"Members\r\n---------------------------------\r\nAdminUser\r\nGuestUser\r\nThe command completed successfully."
        mock_proc = MockProcess(stdout=mock_net_output)

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await windows_accounts(action="get_group_members", group="Administrators")

            self.assertTrue(result["success"])
            members = result["data"]["members"]
            self.assertIn("AdminUser", members)
            self.assertIn("GuestUser", members)
            self.assertEqual(len(members), 2)


if __name__ == "__main__":
    unittest.main()
