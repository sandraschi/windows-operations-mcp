import asyncio
import tempfile
import unittest

from windows_operations_mcp.mcp_server import FastMCP, register_all_tools


class TestMCPServerDetailed(unittest.TestCase):
    """Detailed test of MCP server functionality."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.mcp = FastMCP("test-detailed-server")

        import windows_operations_mcp.mcp_server as mcp_server

        original_mcp = mcp_server.mcp
        mcp_server.mcp = self.mcp
        try:
            register_all_tools()
        finally:
            mcp_server.mcp = original_mcp

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _list_tools(self):
        return asyncio.run(self.mcp.list_tools())

    def test_mcp_server_initialization(self):
        self.assertIsNotNone(self.mcp)
        self.assertEqual(self.mcp.name, "test-detailed-server")

    def test_mcp_server_tool_registration(self):
        tools = self._list_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 10)

    def test_mcp_server_tool_discovery(self):
        tools = self._list_tools()
        tool_names = [t.name for t in tools]

        expected_tools = [
            "winops_net_firewall_list",
            "winops_env_list",
            "winops_apps_list",
            "winops_evtlog_query",
            "winops_accounts_list_users",
            "agentic_system_hardening",
        ]
        for expected in expected_tools:
            self.assertIn(expected, tool_names, f"Tool '{expected}' not found in registered tools")

        for tool in tools:
            self.assertIsNotNone(tool.name)
            self.assertIsNotNone(tool.description)

    def test_mcp_server_tool_validation(self):
        tools = self._list_tools()
        for tool in tools:
            schema = tool.parameters
            self.assertIsNotNone(schema)

    def test_mcp_server_multiple_registrations(self):
        tools_before = self._list_tools()
        count_before = len(tools_before)
        register_all_tools()
        tools_after = self._list_tools()
        self.assertEqual(len(tools_after), count_before)

    def test_mcp_server_tool_metadata(self):
        tools = self._list_tools()
        for tool in tools:
            name = tool.name
            desc = tool.description
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)
            self.assertIsInstance(desc, str)
            self.assertGreater(len(desc), 10)

    def test_mcp_server_schema_validation(self):
        tools = self._list_tools()
        for tool in tools:
            schema = tool.parameters
            self.assertIsNotNone(schema)

    def test_mcp_server_error_handling(self):
        try:
            tools = self._list_tools()
            self.assertIsInstance(tools, list)
        except Exception as e:
            self.fail(f"MCP server raised exception: {e}")

    def test_mcp_server_state_management(self):
        tools_before = self._list_tools()
        count_before = len(tools_before)
        tools_after = self._list_tools()
        self.assertEqual(len(tools_after), count_before)


if __name__ == "__main__":
    unittest.main()
