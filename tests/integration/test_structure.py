#!/usr/bin/env python3
"""
Quick test script to validate the modular Windows Operations MCP structure.
"""

import sys
import os
from pathlib import Path

# Add the package to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all module imports."""
    print("🔧 Testing Windows Operations MCP imports...")
    
    try:
        # Test main server import
        print("  ├─ Importing main server...")
        from windows_operations_mcp.mcp_server import mcp
        print("  │  ✅ Main server imported successfully")
        
        # Test utils imports
        print("  ├─ Importing utilities...")
        from windows_operations_mcp.utils import create_temp_file, validate_directory
        from windows_operations_mcp.utils.command_executor import CommandExecutor
        print("  │  ✅ Utilities imported successfully")
        
        # Test tools imports
        print("  ├─ Importing tools...")
        from windows_operations_mcp.tools import powershell_tools, network_tools, system_tools, process_tools
        from windows_operations_mcp.tools import file_operations  # Updated to use new file_operations module
        print("  │  ✅ All tools imported successfully")
        
        print("  └─ 🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"  └─ ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"  └─ ❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality."""
    print("\\n🧪 Testing basic functionality...")
    
    try:
        # Test temp file creation
        from windows_operations_mcp.utils import create_temp_file, safe_cleanup_file
        temp_path = create_temp_file('.test', 'Hello World')
        print(f"  ├─ Created temp file: {temp_path}")
        
        # Clean up
        safe_cleanup_file(temp_path)
        print("  ├─ Cleaned up temp file")
        
        # Test directory validation
        from windows_operations_mcp.utils import validate_directory
        result = validate_directory(str(project_root))
        print(f"  ├─ Directory validation: {result['valid']}")
        
        print("  └─ ✅ Basic functionality works!")
        return True
        
    except Exception as e:
        print(f"  └─ ❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Windows Operations MCP - Structure Validation")
    print("=" * 50)
    
    # Test imports
    import_success = test_imports()
    
    # Test basic functionality
    func_success = test_basic_functionality()
    
    # Final result
    print("\\n" + "=" * 50)
    if import_success and func_success:
        print("🎯 SUCCESS: Windows Operations MCP structure is valid!")
        print("✅ Ready for Claude Desktop integration")
        return 0
    else:
        print("❌ FAILED: Issues found in structure")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
