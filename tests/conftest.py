import pytest
import asyncio
from fastmcp import FastMCP, Context
from windows_operations_mcp.mcp_server import mcp as server_instance

@pytest.fixture(scope="session")
def event_loop():
    """Create a session-wide event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mcp():
    """Fixture to provide the FastMCP server instance for unit tests."""
    return server_instance

@pytest.fixture
def mock_ctx():
    """Fixture providing a mock Context for tool simulation."""
    class MockContext:
        def info(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass
        def report_progress(self, current, total): pass
        async def sample(self, prompt, **kwargs):
            # Mock successful sampling response
            from dataclasses import dataclass
            @dataclass
            class Choice:
                text: str
            @dataclass
            class SampleResponse:
                content: list
            return SampleResponse(content=[Choice(text="Mocked sampling advice for testing.")])
            
    return MockContext()

@pytest.fixture
async def mcp_client(mcp):
    """Fixture for an end-to-end MCP client simulation."""
    # In FastMCP 3.2, we can test by calling mcp.call_tool() directly
    # which simulates the host's call.
    yield mcp
