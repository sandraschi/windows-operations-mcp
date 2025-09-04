# PowerShell Tool Migration Guide

## Quick Reference for Fixing Existing Tools

### 🔄 Migration Patterns

#### Before (Broken Pipes)
```powershell
# ❌ OLD: Direct pipe usage
Get-Process | Where-Object {$_.CPU -gt 100} | Select-Object Name, CPU

# ❌ OLD: Complex pipe chains
Get-ChildItem -Path $path | Where-Object {$_.Extension -eq ".txt"} | Sort-Object Name | Format-Table

# ❌ OLD: External commands with pipes  
& npm list | findstr "express"
```

#### After (File Redirect)
```powershell
# ✅ NEW: File redirect pattern
$tempFile = "C:\temp\processes_$(Get-Date -Format 'HHmmss').txt"
Get-Process | Where-Object {$_.CPU -gt 100} | Select-Object Name, CPU > $tempFile
Get-Content $tempFile -Encoding UTF8
Remove-Item $tempFile -ErrorAction SilentlyContinue

# ✅ NEW: Complex operations with error handling
$tempFile = "C:\temp\files_$(Get-Date -Format 'HHmmss').txt"
try {
    Get-ChildItem -Path $path | Where-Object {$_.Extension -eq ".txt"} | Sort-Object Name | Format-Table > $tempFile
    if (Test-Path $tempFile) {
        Get-Content $tempFile -Encoding UTF8
    }
} finally {
    Remove-Item $tempFile -ErrorAction SilentlyContinue
}

# ✅ NEW: External commands properly handled
$tempFile = "C:\temp\npm_$(Get-Date -Format 'HHmmss').txt"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm list | findstr express" -Wait -RedirectStandardOutput $tempFile -WindowStyle Hidden
Get-Content $tempFile -Encoding UTF8
Remove-Item $tempFile -ErrorAction SilentlyContinue
```

### 🛠️ Tool Update Checklist

For each PowerShell tool function:

1. **Identify Pipe Usage**: Search for `|` operators
2. **Add Temp File Generation**: Use `"C:\temp\op_$(Get-Date -Format 'HHmmss').txt"`
3. **Replace Pipe with Redirect**: Change `|` chains to `> $tempFile`
4. **Add Content Read**: `Get-Content $tempFile -Encoding UTF8`
5. **Add Cleanup**: `Remove-Item $tempFile -ErrorAction SilentlyContinue`
6. **Test Error Cases**: Ensure proper error handling

### 🎯 Priority Tool Fixes

Based on common MCP operations, prioritize fixing these tool types:

1. **Process Management Tools**: `Get-Process` operations
2. **File System Tools**: `Get-ChildItem`, `Search-Files`
3. **Git Operations**: All git command wrappers
4. **System Info**: `Get-SystemInfo`, resource monitoring
5. **External Command Wrappers**: npm, python, docker commands

### 🧪 Testing Each Fix

```powershell
# Test pattern for each updated tool
function Test-ToolFunction {
    param([string]$ToolName)
    
    Write-Output "Testing $ToolName..."
    
    try {
        # Call your updated tool function here
        $result = & $ToolName
        
        if ($result) {
            Write-Output "✅ $ToolName works correctly"
        } else {
            Write-Output "⚠️ $ToolName returned no output"
        }
    } catch {
        Write-Output "❌ $ToolName failed: $($_.Exception.Message)"
    }
}
```

---

**Implementation Priority**: Critical - Fix immediately for reliable MCP operation  
**Testing Required**: Yes - Test each updated tool thoroughly
