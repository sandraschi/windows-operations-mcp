"""Test FastMCP HTTP endpoint directly."""

import asyncio
import httpx


async def test_mcp_http():
    """Test FastMCP HTTP endpoint."""
    async with httpx.AsyncClient(base_url="http://127.0.0.1:13000/mcp", timeout=10.0) as client:
        # FastMCP HTTP uses root path for tool calls (mounted at /mcp)
        # Format: POST to root with JSON-RPC format
        try:
            response = await client.post(
                "",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_libraries",
                        "arguments": {"operation": "list"}
                    }
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            if response.status_code == 200:
                print("[SUCCESS] FastMCP HTTP endpoint working!")
            else:
                print(f"[FAILED] HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_http())
