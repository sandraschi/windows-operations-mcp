#!/usr/bin/env python3
"""
Test script for Windows Operations MCP to diagnose connection issues.
"""

import sys
import os

# Add the repo to Python path
sys.path.insert(0, r"D:\Dev\repos\windows-operations-mcp")

def test_imports():
    """Test if all modules can be imported."""
    print("Testing imports...")
    
    try:
        import windows_operations_mcp
        print("✅ Main module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import main module: {e}")
        return False
    
    try:
        from windows_operations_mcp.mcp_server import mcp
        print("✅ MCP server imported successfully")
    except Exception as e:
        print(f"❌ Failed to import MCP server: {e}")
        return False
    
    try:
        import fastmcp
        print(f"✅ FastMCP imported: {getattr(fastmcp, '__version__', 'unknown version')}")
    except Exception as e:
        print(f"❌ Failed to import FastMCP: {e}")
        return False
    
    return True

def test_server_init():
    """Test if the server can initialize."""
    print("\nTesting server initialization...")
    
    try:
        from windows_operations_mcp.mcp_server import mcp, register_all_tools
        print("✅ MCP instance created")
        
        # Test tool registration
        register_all_tools()
        print("✅ Tools registered successfully")
        
        # Count tools
        if hasattr(mcp, '_tools'):
            tool_count = len(mcp._tools)
            print(f"✅ Found {tool_count} registered tools")
        else:
            print("⚠️ Cannot count tools - mcp._tools not accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_registration():
    """Test individual tool modules."""
    print("\nTesting tool modules...")
    
    tool_modules = [
        "windows_operations_mcp.tools.powershell_tools",
        "windows_operations_mcp.tools.file_operations", 
        "windows_operations_mcp.tools.system_tools",
        "windows_operations_mcp.tools.process_tools"
    ]
    
    for module_name in tool_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            print(f"✅ {module_name} imported")
        except Exception as e:
            print(f"❌ {module_name} failed: {e}")

def main():
    """Run all tests."""
    print("Windows Operations MCP Diagnostic Test")
    print("=" * 50)
    
    if not test_imports():
        print("\n❌ Import test failed - cannot proceed")
        return False
    
    if not test_server_init():
        print("\n❌ Server initialization failed")
        return False
    
    test_tool_registration()
    
    print("\n" + "=" * 50)
    print("✅ All tests passed - MCP server should work")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
