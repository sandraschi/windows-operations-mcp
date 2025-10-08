# Claude Desktop MCP Server Fix Guide

**Date**: October 8, 2025  
**Issue**: All local MCP servers stopped working  
**Root Cause**: MCP 1.14.1 auto-upgrade + dependency conflicts

## 🔍 What Happened

### The Cascade of Failures

1. **MCP 1.14.1 Released** - Python 3.13 compatibility bug
2. **Auto-Upgrade** - pip upgraded MCP from 1.13.x to 1.14.1
3. **Breaking Change** - TypeError: 'function' object is not subscriptable
4. **Pydantic Upgrade** - When downgrading MCP, Pydantic upgraded to 2.12.0
5. **FastAPI Conflict** - Old FastAPI 0.104.1 incompatible with Pydantic 2.12
6. **Dependency Hell** - Multiple Python versions with different dependency states

### Two Python Environments

**Python 3.13** (used by basic-memory):
- Path: `C:\Users\sandr\AppData\Local\Programs\Python\Python313\`
- Command: `py -3.13`
- Servers: basic-memory
- **Fixed**: MCP 1.13.1 + FastAPI 0.118.1

**Python 3.10** (used by most servers):
- Path: `C:\Users\sandr\AppData\Local\Programs\Python\Python310\`
- Command: `python`
- Servers: 8 local MCP servers
- **Issue**: Missing dependencies

## ✅ Fixes Applied

### Fix 1: Python 3.13 (basic-memory)
```bash
# Downgrade MCP (fix Python 3.13 bug)
py -3.13 -m pip install "mcp<1.14" --force-reinstall

# Upgrade FastAPI (fix Pydantic compatibility)
py -3.13 -m pip install "fastapi>=0.115.0" --upgrade
```

**Result**: ✅ basic-memory works

### Fix 2: Python 3.10 (local servers)
```bash
# Install dependencies for each server
cd D:\Dev\repos\windows-operations-mcp
python -m pip install -e .

cd D:\Dev\repos\filesystem-mcp
python -m pip install -e .

# ... etc for each server
```

**Result**: ✅ winops, filetools, notepadpp, suno-mcp, winauto work

### Fix 3: Advanced Memory (Python version mismatch)

**Problem**: Requires Python ≥3.11, configured to use Python 3.10

**Solution**: Update Claude Desktop config:

```json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "command": "py",
      "args": [
        "-3.13",
        "src/advanced_memory/mcp/server.py"
      ],
      "env": {
        "PYTHONPATH": "D:/Dev/repos/advanced-memory-mcp/src",
        "PYTHONUNBUFFERED": "1",
        "ADVANCED_MEMORY_HOME": "D:/Dev/repos/advanced-memory-mcp/data"
      },
      "cwd": "D:/Dev/repos/advanced-memory-mcp"
    }
  }
}
```

Then:
```bash
py -3.13 -m pip install -e D:\Dev\repos\advanced-memory-mcp
```

## 🐛 Remaining Issues

### Issue 1: rtorrent-mcp
**Error**: Missing package `xmlrpc3`  
**Fix**: Install the package or update requirements
```bash
# Try alternative package
python -m pip install xmlrpc
```

### Issue 2: nest-protect
**Error**: Permission denied on websockets package  
**Fix**: Run as administrator or use --user flag
```bash
python -m pip install -r requirements.txt --user
```

## 📋 Complete Fix Checklist

- [x] Downgrade MCP in Python 3.13 (1.14.1 → 1.13.1)
- [x] Upgrade FastAPI in Python 3.13 (0.104.1 → 0.118.1)
- [x] Install winops dependencies in Python 3.10
- [x] Install filetools dependencies
- [x] Install notepadpp dependencies
- [x] Install suno-mcp dependencies
- [x] Install winauto dependencies
- [ ] Fix advanced-memory-mcp Python version
- [ ] Fix rtorrent-mcp xmlrpc3 dependency
- [ ] Fix nest-protect permission issue

## 🎯 Quick Command Reference

### Check MCP Version
```powershell
# Python 3.13
py -3.13 -m pip show mcp

# Python 3.10
python -m pip show mcp
```

### Check Server Status
```powershell
# List all MCP server logs
Get-ChildItem "$env:APPDATA\Claude\logs\mcp-*.log" | Sort-Object LastWriteTime -Descending

# Check specific server
Get-Content "$env:APPDATA\Claude\logs\mcp-server-NAME.log" -Tail 30
```

### Install Server Dependencies
```powershell
# For any server
cd D:\Dev\repos\SERVER-NAME
python -m pip install -e .

# Or with requirements.txt
python -m pip install -r requirements.txt
```

### Update Claude Desktop Config
```powershell
# Edit config
notepad "$env:APPDATA\Claude\claude_desktop_config.json"

# Then restart Claude Desktop
```

## 💡 Lessons Learned

### Problem 1: Auto-Upgrades Are Dangerous
**Issue**: MCP auto-upgraded from 1.13 to 1.14.1 without warning  
**Solution**: Pin versions in requirements:
```python
mcp==1.13.1  # Exact version
# or
mcp>=1.13.1,<1.14  # Safe range
```

### Problem 2: Multiple Python Versions
**Issue**: Different servers use different Python installations  
**Solution**: Document which Python each server needs

### Problem 3: Dependency Drift
**Issue**: Dependencies get out of sync between Python installations  
**Solution**: Regular maintenance and version pinning

## 🛡️ Prevention

### For MCP Server Developers

1. **Pin Dependencies**:
   ```toml
   dependencies = [
       "mcp==1.13.1",  # Not >=1.13.1
       "fastmcp==2.12.3",
       "pydantic>=2.0,<3.0"
   ]
   ```

2. **Test with Multiple Python Versions**:
   - Test with Python 3.10, 3.11, 3.12, 3.13
   - CI/CD matrix builds

3. **Document Python Requirements**:
   ```markdown
   **Python**: 3.11+ required (does not work with 3.10)
   ```

### For MCP Server Users

1. **Check Logs Regularly**:
   ```powershell
   Get-ChildItem "$env:APPDATA\Claude\logs\mcp-*.log" -Filter "*error*"
   ```

2. **Pin MCP Version Globally**:
   ```bash
   pip install "mcp==1.13.1"
   ```

3. **Use Virtual Environments** (if possible):
   - Each server in its own venv
   - Isolated dependencies

## 📊 Summary of Fixes

| Server | Python | Issue | Fix | Status |
|--------|--------|-------|-----|--------|
| basic-memory | 3.13 | MCP 1.14.1 bug | Downgrade MCP | ✅ Fixed |
| winops | 3.10 | Missing deps | Install deps | ✅ Fixed |
| filetools | 3.10 | Missing deps | Install deps | ✅ Fixed |
| notepadpp | 3.10 | Missing deps | Install deps | ✅ Fixed |
| suno-mcp | 3.10 | Missing deps | Install deps | ✅ Fixed |
| winauto | 3.10 | Missing deps | Install deps | ✅ Fixed |
| advanced-memory | 3.10 | Wrong Python | Use 3.13 | ⚠️ Pending |
| rtorrent-mcp | 3.10 | Missing xmlrpc3 | Find package | ⚠️ Pending |
| nest-protect | 3.10 | Permissions | Admin/user | ⚠️ Pending |

---

**Last Updated**: October 8, 2025  
**Status**: Mostly Fixed - 6 of 9 Python servers working

