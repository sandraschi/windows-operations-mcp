import tempfile
import unittest

# Add the project root to Python path
from windows_operations_mcp.mcp_server import FastMCP, register_all_tools
from windows_operations_mcp.tools.help_tools import register_help_tools
from windows_operations_mcp.tools.system_tools import register_system_tools


class TestMCPServerDetailed(unittest.TestCase):
    """Detailed test of MCP server functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

        # Create a fresh MCP instance for testing
        self.mcp = FastMCP("test-detailed-server")

        # Register all tools using the main server registration logic
        # We need to monkeypatch the register_all_tools to use our test mcp
        import windows_operations_mcp.mcp_server as mcp_server

        original_mcp = mcp_server.mcp
        mcp_server.mcp = self.mcp
        try:
            register_all_tools()
        finally:
            mcp_server.mcp = original_mcp

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mcp_server_initialization(self):
        """Test MCP server initialization."""
        self.assertIsNotNone(self.mcp)
        self.assertEqual(self.mcp.name, "test-detailed-server")

    def test_mcp_server_tool_registration(self):
        """Test tool registration functionality."""
        initial_tool_count = len(self.mcp.get_tools())

        # Register additional tools
        register_help_tools(self.mcp)
        register_system_tools(self.mcp)

        # Should have more tools now
        final_tool_count = len(self.mcp.get_tools())
        self.assertGreater(final_tool_count, initial_tool_count)

    def test_mcp_server_tool_discovery(self):
        """Test tool discovery and verify specific v14.1.0 tools."""
        tools = self.mcp.get_tools()
        tool_names = [t.name if hasattr(t, "name") else t.get("name") for t in tools]

        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 10)

        # Verify registration of key v14.1.0 tools
        expected_tools = [
            "windows_network",
            "windows_environment",
            "windows_apps",
            "windows_event_logs",
            "windows_accounts",
            "agentic_operations",
        ]
        for expected in expected_tools:
            self.assertIn(expected, tool_names, f"Tool '{expected}' not found in registered tools")

        # Check that tools have required attributes
        for tool in tools:
            # FastMCP 3.2 tool objects might have different structure than dicts
            name = tool.name if hasattr(tool, "name") else tool.get("name")
            desc = tool.description if hasattr(tool, "description") else tool.get("description")
            self.assertIsNotNone(name)
            self.assertIsNotNone(desc)

    def test_mcp_server_tool_validation(self):
        """Test tool input validation."""
        # This is a basic test - in reality we'd test specific tool calls
        tools = self.mcp.get_tools()

        # All tools should have valid schemas
        for tool in tools:
            schema = tool.get("inputSchema", {})
            self.assertIn("type", schema)

    def test_mcp_server_capabilities(self):
        """Test MCP server capabilities."""
        # Test that server has basic MCP capabilities
        capabilities = self.mcp.get_capabilities()

        self.assertIn("tools", capabilities)
        self.assertIn("resources", capabilities)

    def test_mcp_server_multiple_registrations(self):
        """Test registering multiple tool sets."""
        # Register the same tools multiple times
        initial_count = len(self.mcp.list_tools())

        register_help_tools(self.mcp)
        register_system_tools(self.mcp)

        # Count should remain the same (no duplicates)
        final_count = len(self.mcp.list_tools())
        self.assertEqual(final_count, initial_count)

    def test_mcp_server_tool_metadata(self):
        """Test tool metadata."""
        tools = self.mcp.get_tools()

        for tool in tools:
            # Check required metadata
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)

            # Name should be a string
            self.assertIsInstance(tool["name"], str)
            self.assertGreater(len(tool["name"]), 0)

            # Description should be meaningful
            self.assertIsInstance(tool["description"], str)
            self.assertGreater(len(tool["description"]), 10)

    def test_mcp_server_schema_validation(self):
        """Test schema validation."""
        tools = self.mcp.get_tools()

        for tool in tools:
            schema = tool.get("inputSchema", {})

            # Schema should be a dict
            self.assertIsInstance(schema, dict)
            self.assertIn("type", schema)
            self.assertEqual(schema["type"], "object")

            # Should have properties if it's an object schema
            if schema["type"] == "object":
                self.assertIn("properties", schema)

    def test_mcp_server_error_handling(self):
        """Test MCP server error handling."""
        # Test that server handles errors gracefully
        try:
            tools = self.mcp.get_tools()
            # Should not raise exceptions
            self.assertIsInstance(tools, list)
        except Exception as e:
            self.fail(f"MCP server raised exception: {e}")

    def test_mcp_server_state_management(self):
        """Test MCP server state management."""
        # Server should maintain state between operations
        initial_tools = len(self.mcp.list_tools())

        # Perform operations
        register_help_tools(self.mcp)

        # State should be consistent
        final_tools = len(self.mcp.list_tools())
        self.assertGreaterEqual(final_tools, initial_tools)


if __name__ == "__main__":
    unittest.main()
