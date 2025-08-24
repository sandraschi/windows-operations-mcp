"""
Basic functionality tests for Windows Operations MCP.

This script tests the core functionality of the Windows Operations MCP server
using the stdio transport required for Claude Desktop and Windsurf integration.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import the MCP server
from windows_operations_mcp.logging_config import get_logger

# Get a logger
logger = get_logger("test_script")

def print_result(operation: str, result: Dict[str, Any]) -> None:
    """Print test result in a consistent format."""
    status = "✅ PASS" if not result.get("error") else "❌ FAIL"
    print(f"\n{status} - {operation}")
    print("-" * 50)
    
    # Print the result with indentation for better readability
    print(json.dumps(result, indent=2, default=str))
    print("=" * 50)

def run_mcp_command(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Run an MCP command using the stdio transport.
    
    This function starts the MCP server as a subprocess and communicates with it
    using the stdio transport protocol.
    """
    try:
        # Build the command to execute
        python_exe = sys.executable
        mcp_script = str(project_root / "windows_operations_mcp" / "mcp_server.py")
        
        # Create the request JSON-RPC 2.0 message
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        # Start the MCP server as a subprocess with stdio transport
        process = subprocess.Popen(
            [python_exe, mcp_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # Send the request
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        
        # Read the response
        response = process.stdout.readline()
        
        # Clean up
        process.terminate()
        
        # Parse and return the response
        return json.loads(response)
    except Exception as e:
        return {"error": str(e), "result": None}

def test_powershell_command() -> Dict[str, Any]:
    """Test executing a simple PowerShell command."""
    logger.info("Testing PowerShell command execution")
    return run_mcp_command("run_powershell", {"command": "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"})

def test_cmd_command() -> Dict[str, Any]:
    """Test executing a simple CMD command."""
    logger.info("Testing CMD command execution")
    return run_mcp_command("run_cmd", {"command": "echo Hello, World!"})

def test_list_directory() -> Dict[str, Any]:
    """Test listing directory contents."""
    logger.info("Testing directory listing")
    return run_mcp_command("list_directory", {"path": "."})

def test_get_system_info() -> Dict[str, Any]:
    """Test getting system information."""
    logger.info("Testing system info retrieval")
    return run_mcp_command("get_system_info", {})

def test_process_list() -> Dict[str, Any]:
    """Test getting process list."""
    logger.info("Testing process list retrieval")
    return run_mcp_command("get_process_list", {})

def run_tests() -> None:
    """Run all tests and report results."""
    test_functions = [
        ("PowerShell Command", test_powershell_command),
        ("CMD Command", test_cmd_command),
        ("List Directory", test_list_directory),
        ("Get System Info", test_get_system_info),
        ("Get Process List", test_process_list),
    ]
    
    print("\n🚀 Starting Windows Operations MCP Tests")
    print("=" * 50)
    
    results = {}
    # Run each test and collect results
    for name, test_func in test_functions:
        try:
            result = test_func()
            results[name] = result
            print_result(name, result)
        except Exception as e:
            print(f"\n❌ ERROR - {name}")
            print("-" * 50)
            print(f"Error: {str(e)}")
            print("=" * 50)
            results[name] = {"error": str(e), "success": False}
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    for test_name, result in results.items():
        status = "✅ PASS" if not result.get("error") else "❌ FAIL"
        print(f"{status} - {test_name}")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    # Run the tests
    run_tests()
