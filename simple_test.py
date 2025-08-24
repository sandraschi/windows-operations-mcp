"""
Simple test script to verify FastMCP 2.11.3 integration with stateful tools support.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import FastMCP
from fastmcp import FastMCP

async def main():
    # Initialize FastMCP
    mcp = FastMCP(
        name="windows-operations-mcp-test",
        version="0.1.0"
    )
    
    # Register a simple tool for testing
    @mcp.tool
    async def hello(name: str = "World") -> str:
        """Say hello to someone."""
        return f"Hello, {name}!"
    
    # Print available tools
    print("Available tools:", list(mcp.tools.keys()))
    
    # Test the tool directly
    result = await hello("FastMCP")
    print("Direct call result:", result)
    
    # Test the tool through MCP
    mcp_result = await mcp.run("hello", {"name": "MCP User"})
    print("MCP call result:", mcp_result)
    
    # Start the server
    print("\nStarting MCP server...")
    await mcp.serve(transport={"type": "stdio"})

if __name__ == "__main__":
    asyncio.run(main())
