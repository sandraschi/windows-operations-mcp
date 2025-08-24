# Windows Operations MCP - Server Disconnection Fix

## 🚨 PROBLEM ANALYSIS

**Root Cause**: Server disconnects immediately due to import failures and missing modules.

### Issues Found:

1. **Path Mismatch**: Tools in `src/windows_operations_mcp/tools/` but imports expect `windows_operations_mcp/tools/`
2. **Missing Module**: `file_operations` is a package directory, not a module
3. **Import Failures**: Server crashes on startup due to failed imports

## 🛠️ COMPREHENSIVE FIX

### Quick Solution: Copy Tools & Fix Imports

Run this PowerShell script to fix the server:

```powershell
# Navigate to repo
Set-Location "D:\Dev\repos\windows-operations-mcp"

# 1. Copy tools from src to root
$sourceDir = "src\windows_operations_mcp\tools"
$targetDir = "windows_operations_mcp\tools"

# Copy all files and directories
Copy-Item -Path "$sourceDir\*" -Destination $targetDir -Recurse -Force
Write-Host "✅ Tools copied from src to root" -ForegroundColor Green

# 2. Create missing file_operations.py module
$fileOpsContent = @"
"""
File operations tools - consolidated module.
"""
from .file_operations.file_operations import register_file_operations

__all__ = ["register_file_operations"]
"@

$fileOpsContent | Out-File -FilePath "$targetDir\file_operations.py" -Encoding UTF8
Write-Host "✅ Created file_operations.py module" -ForegroundColor Green

# 3. Test import
python -c "
import sys
sys.path.insert(0, '.')
try:
    from windows_operations_mcp.tools import powershell_tools
    print('✅ PowerShell tools import OK')
except Exception as e:
    print(f'❌ Import failed: {e}')
"

Write-Host "🚀 Fix complete! Try running the server now." -ForegroundColor Cyan
```

### Alternative: Update Python Path

Add this to `__main__.py` at the top:

```python
import sys
from pathlib import Path

# Add src directory to Python path for development
src_dir = Path(__file__).parent.parent / "src"
if src_dir.exists():
    sys.path.insert(0, str(src_dir))
```

## 🧪 TEST THE FIX

### Test 1: Import Test
```python
# Create test_imports.py
import sys
sys.path.insert(0, r"D:\Dev\repos\windows-operations-mcp")

try:
    from windows_operations_mcp.tools import powershell_tools
    print("✅ PowerShell tools imported")
    
    from windows_operations_mcp.tools import file_operations  
    print("✅ File operations imported")
    
    from windows_operations_mcp.mcp_server import mcp
    print("✅ MCP server imported")
    
    print("🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
```

### Test 2: Server Start
```bash
cd D:\Dev\repos\windows-operations-mcp
python -m windows_operations_mcp
```

Should show:
```
Starting Windows Operations MCP server...
Tool registration completed
Starting MCP server with stdio transport
```

## 🎯 EXPECTED RESULTS

After the fix:
- ✅ Server starts without disconnection
- ✅ All tool modules import successfully
- ✅ MCP tools registered and available
- ✅ Claude Desktop can connect

**Available Tools**:
- `run_powershell` - Execute PowerShell commands
- `run_cmd` - Execute CMD commands  
- `list_directory` - List directory contents
- `read_file_content` - Read file contents
- `write_file_content` - Write file contents
- `get_process_list` - List running processes
- `get_system_info` - Get system information
- `test_port` - Test network connectivity
- `health_check` - Server diagnostics

## 🚨 IF STILL FAILING

Check logs and run diagnostic:

```python
# Create debug_mcp.py
import sys
import os
sys.path.insert(0, r"D:\Dev\repos\windows-operations-mcp")

def debug_imports():
    print("=== MCP Import Debug ===")
    
    modules_to_test = [
        "windows_operations_mcp",
        "windows_operations_mcp.mcp_server", 
        "windows_operations_mcp.tools.powershell_tools",
        "windows_operations_mcp.tools.file_operations",
        "windows_operations_mcp.tools.system_tools"
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name}: {e}")

debug_imports()
```

This fix should resolve the server disconnection issue completely! 🎯