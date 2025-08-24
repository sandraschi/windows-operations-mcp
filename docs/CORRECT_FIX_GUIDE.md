# Windows Operations MCP - Correct Fix Guide

## 🎯 REAL PROBLEM

The server has **two versions**:
- **Root**: `windows_operations_mcp/` (incomplete, missing tools)  
- **Src**: `src/windows_operations_mcp/` (complete, with tools)

Claude Desktop is running the **root version** which fails because tools are missing.

## ✅ CORRECT FIX

### Fix 1: Update Claude Desktop Config to Use src/

Update your Claude Desktop config to point to the correct location:

```json
{
  "mcpServers": {
    "windows-operations-mcp": {
      "command": "python",
      "args": ["-m", "windows_operations_mcp"],
      "cwd": "D:/Dev/repos/windows-operations-mcp/src"
    }
  }
}
```

**Key change**: `"cwd": "D:/Dev/repos/windows-operations-mcp/src"`

### Fix 2: Test the Correct Version

```bash
# Test the working version
cd D:\Dev\repos\windows-operations-mcp\src
python -m windows_operations_mcp
```

### Fix 3: Verify Tools Exist

```bash
# Check that tools exist in src version
ls D:\Dev\repos\windows-operations-mcp\src\windows_operations_mcp\tools\
```

Should show:
- powershell_tools.py ✅
- system_tools.py ✅  
- process_tools.py ✅
- network_tools.py ✅
- file_operations/ (directory) ✅

## 🧪 TESTING

### Test Server Start
```bash
cd D:\Dev\repos\windows-operations-mcp\src
python -m windows_operations_mcp
```

Should show:
```
Starting Windows Operations MCP server...
Registered tools from powershell_tools
Registered tools from system_tools
Tool registration completed
Starting MCP server with stdio transport
```

### Test MCP Tools List
```json
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

Should return tools like:
- run_powershell
- run_cmd  
- list_directory
- read_file_content
- get_system_info
- get_process_list

## 🚨 WHY THE ROOT VERSION FAILS

The root `windows_operations_mcp/` directory has:
- ❌ Empty tools/ directory
- ❌ Incomplete mcp_server.py
- ❌ Missing imports

The src `src/windows_operations_mcp/` directory has:
- ✅ Complete tools/ with all modules
- ✅ Working mcp_server.py  
- ✅ All imports working

## 🎯 SOLUTION SUMMARY

**Don't copy files** - just update Claude Desktop to use the correct working directory:

```json
"cwd": "D:/Dev/repos/windows-operations-mcp/src"
```

This makes Claude Desktop run the **complete src version** instead of the **incomplete root version**.

## ✅ EXPECTED RESULT

After updating the cwd path:
- ✅ Server starts without disconnection
- ✅ All tools load successfully
- ✅ MCP protocol works correctly
- ✅ Can execute PowerShell, CMD, file operations, etc.

**Root Cause**: Running wrong version of the server (root vs src)  
**Fix**: Point Claude Desktop to the correct working directory
