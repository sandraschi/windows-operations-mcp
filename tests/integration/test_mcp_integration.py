"""
End-to-end integration test for Windows Operations MCP with FastMCP 2.10.1.

This script tests the full integration of the MCP server with FastMCP 2.10.1,
including HTTP transport and tool registration.
"""

import asyncio
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import FastMCP
from fastmcp import FastMCP, Client

# Configuration
HOST = "localhost"
PORT = 8000
MCP_SERVER_CMD = [sys.executable, "-m", "windows_operations_mcp.mcp_server"]

class MCPTestRunner:
    """Test runner for MCP server integration tests."""
    
    def __init__(self):
        self.server_process = None
        self.client = None
    
    async def start_server(self):
        """Start the MCP server in a subprocess."""
        print("🚀 Starting MCP server...")
        env = os.environ.copy()
        env["MCP_HOST"] = HOST
        env["MCP_PORT"] = str(PORT)
        env["LOG_LEVEL"] = "DEBUG"
        
        self.server_process = subprocess.Popen(
            MCP_SERVER_CMD,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the server time to start
        await asyncio.sleep(2)
        
        # Initialize the client
        self.client = Client(transport={"type": "http", "url": f"http://{HOST}:{PORT}"})
        
        # Wait for server to be ready
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # Try to list tools to check if server is ready
                tools = await self.client.list_tools()
                print(f"✅ Server ready. Available tools: {', '.join(tools.keys())}")
                return True
            except Exception as e:
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)
                else:
                    print(f"❌ Failed to connect to server: {e}")
                    self.print_server_output()
                    return False
    
    async def stop_server(self):
        """Stop the MCP server."""
        if self.server_process:
            print("\n🛑 Stopping MCP server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.print_server_output()
    
    def print_server_output(self):
        """Print server output for debugging."""
        if self.server_process:
            print("\n=== SERVER OUTPUT ===")
            stdout, stderr = self.server_process.communicate()
            if stdout:
                print("STDOUT:", stdout)
            if stderr:
                print("STDERR:", stderr)
            print("====================\n")
    
    async def run_test(self, name: str, tool: str, params: Dict[str, Any]) -> bool:
        """Run a single test case."""
        print(f"\n🔍 Running test: {name}")
        print(f"   Tool: {tool}")
        print(f"   Params: {json.dumps(params, indent=4)}")
        
        try:
            result = await self.client.run(tool, params)
            print(f"✅ Test passed: {name}")
            print(f"   Result: {json.dumps(result, indent=4, default=str)}")
            return True
        except Exception as e:
            print(f"❌ Test failed: {name}")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Run all integration tests."""
    print("=" * 80)
    print("🧪 Windows Operations MCP Integration Tests")
    print("=" * 80)
    
    runner = MCPTestRunner()
    
    try:
        # Start the server
        if not await runner.start_server():
            print("❌ Failed to start MCP server")
            return 1
        
        # Define test cases
        test_cases = [
            {
                "name": "List Directory",
                "tool": "list_directory",
                "params": {"path": "."}
            },
            {
                "name": "Get System Info",
                "tool": "get_system_info",
                "params": {}
            },
            {
                "name": "Run CMD Command",
                "tool": "run_cmd",
                "params": {"command": "echo Hello, World!"}
            },
            {
                "name": "Get Process List",
                "tool": "get_process_list",
                "params": {"max_processes": 5}
            }
        ]
        
        # Run all test cases
        results = []
        for test_case in test_cases:
            success = await runner.run_test(
                test_case["name"],
                test_case["tool"],
                test_case["params"]
            )
            results.append((test_case["name"], success))
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 Test Results:")
        print("=" * 80)
        
        all_passed = True
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {name}")
            if not success:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed. Check the logs above for details.")
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Always stop the server
        await runner.stop_server()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
