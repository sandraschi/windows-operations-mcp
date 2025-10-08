# PowerShell Pipe Issues and Fixes

## Overview

The Windows Operations MCP server has identified critical issues with PowerShell pipe operations (`|`) when running through the MCP subprocess environment. This document provides comprehensive solutions and best practices.

## 🚨 Core Problems

### 1. Output Capture Failures
```powershell
# ❌ BROKEN: Output gets truncated or lost
Get-Process | Where-Object {$_.CPU -gt 100} | Select-Object Name, CPU

# ❌ BROKEN: Complex pipes fail silently  
Get-ChildItem | Sort-Object LastWriteTime | Format-Table Name, Length
```

### 2. Encoding Issues
- **Console Encoding**: PowerShell console uses cp850 (OEM)
- **File Encoding**: Windows files typically use cp1252 (ANSI) or UTF-8
- **Pipe Encoding**: Objects get serialized incorrectly through pipe chains
- **Unicode Corruption**: Special characters get mangled

### 3. Error Propagation Loss
```powershell
# ❌ BROKEN: Errors in pipe chain get swallowed
Get-Content "nonexistent.txt" | Sort-Object | Out-File result.txt
# No error reported even though input file doesn't exist
```

### 4. Claude Desktop MCP Interference
- Subprocess pipe handling conflicts with Claude Desktop's execution model
- Stream buffering issues in the MCP tool environment
- Complex object serialization breaks between PowerShell and Python MCP bridge

## ✅ Solutions

### File Redirect Pattern (Primary Solution)

**Instead of pipes, use file redirection with immediate read-back:**

```powershell
# ✅ WORKING: File redirect pattern
Command > C:\temp\output.txt; Get-Content C:\temp\output.txt

# ✅ WORKING: Complex operations  
Get-Process | Where-Object {$_.CPU -gt 100} | Select-Object Name, CPU > C:\temp\processes.txt; Get-Content C:\temp\processes.txt

# ✅ WORKING: With error handling
if (Get-Process | Where-Object {$_.CPU -gt 100} | Select-Object Name, CPU > C:\temp\processes.txt 2>$null) {
    Get-Content C:\temp\processes.txt -Encoding UTF8
} else {
    Write-Output "Error: Failed to get high CPU processes"
}
```

### Unique Temporary Files

**Always use unique temporary file names to avoid conflicts:**

```powershell
# ✅ WORKING: Unique temp files with timestamp
$tempFile = "C:\temp\op_$(Get-Date -Format 'HHmmss').txt"
Get-Process > $tempFile; Get-Content $tempFile -Encoding UTF8
```

### External Command Handling

**For external commands (npm, git, etc), use Start-Process with redirection:**

```powershell
# ✅ WORKING: External command with proper output capture
Start-Process -FilePath "npm.cmd" -ArgumentList "--version" -Wait -RedirectStandardOutput "C:\temp\npm_version.txt" -WindowStyle Hidden
Get-Content "C:\temp\npm_version.txt" -Encoding UTF8
```

### Error Handling Pattern

```powershell
# ✅ WORKING: Comprehensive error handling
$tempFile = "C:\temp\git_status_$(Get-Date -Format 'HHmmss').txt"
$errorFile = "C:\temp\git_error_$(Get-Date -Format 'HHmmss').txt"

try {
    Set-Location "D:\Dev\repos\my-project" -ErrorAction Stop
    Start-Process -FilePath "git.exe" -ArgumentList "status --porcelain" -Wait -RedirectStandardOutput $tempFile -RedirectStandardError $errorFile -WindowStyle Hidden
    
    if (Test-Path $tempFile) {
        $output = Get-Content $tempFile -Encoding UTF8
        $errors = Get-Content $errorFile -Encoding UTF8 -ErrorAction SilentlyContinue
        
        if ($errors) {
            Write-Output "Git Status (with warnings):"
            Write-Output $errors
        }
        Write-Output $output
    }
} catch {
    Write-Output "Error: $($_.Exception.Message)"
} finally {
    # Cleanup temp files
    Remove-Item $tempFile, $errorFile -ErrorAction SilentlyContinue
}
```

## 🔧 Best Practices

### 1. Always Use Full Paths
```powershell
# ❌ BROKEN: Relative paths can fail
Get-Content "config.txt" > temp.txt

# ✅ WORKING: Full paths
Get-Content "D:\Dev\repos\project\config.txt" > "C:\temp\config_output.txt"
```

### 2. Test Paths Before Operations
```powershell
# ✅ WORKING: Path validation
if (Test-Path "D:\Dev\repos\project") {
    Set-Location "D:\Dev\repos\project"
    # ... rest of operations
} else {
    Write-Output "Error: Project directory not found"
}
```

### 3. Specify Encoding Explicitly
```powershell
# ✅ WORKING: Explicit UTF-8 encoding
Get-Content "C:\temp\output.txt" -Encoding UTF8
```

### 4. Handle Large Outputs
```powershell
# ✅ WORKING: Chunked processing for large outputs  
$tempFile = "C:\temp\large_output.txt"
Get-ChildItem -Path "C:\" -Recurse > $tempFile
$content = Get-Content $tempFile -Encoding UTF8 -TotalCount 1000  # First 1000 lines only
```

### 5. Environment Refresh
```powershell
# ✅ WORKING: Refresh PATH environment
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
```

## 🛠️ Tool Implementation Examples

### Process Management
```powershell
function Get-ProcessInfo {
    param([string]$ProcessName)
    
    $tempFile = "C:\temp\processes_$(Get-Date -Format 'HHmmss').txt"
    
    if ($ProcessName) {
        Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | 
        Select-Object Name, Id, CPU, WorkingSet > $tempFile
    } else {
        Get-Process | Select-Object Name, Id, CPU, WorkingSet > $tempFile
    }
    
    if (Test-Path $tempFile) {
        Get-Content $tempFile -Encoding UTF8
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
}
```

### Git Operations
```powershell
function Get-GitStatus {
    param([string]$RepoPath)
    
    $tempFile = "C:\temp\git_status_$(Get-Date -Format 'HHmmss').txt"
    $currentDir = Get-Location
    
    try {
        if ($RepoPath -and (Test-Path $RepoPath)) {
            Set-Location $RepoPath
        }
        
        Start-Process -FilePath "git.exe" -ArgumentList "status --porcelain" -Wait -RedirectStandardOutput $tempFile -WindowStyle Hidden
        
        if (Test-Path $tempFile) {
            $content = Get-Content $tempFile -Encoding UTF8
            return $content
        }
    } finally {
        Set-Location $currentDir
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
}
```

### File System Operations
```powershell
function Search-Files {
    param(
        [string]$Path,
        [string]$Pattern,
        [string]$ContentMatch
    )
    
    $tempFile = "C:\temp\search_$(Get-Date -Format 'HHmmss').txt"
    
    if ($ContentMatch) {
        Get-ChildItem -Path $Path -Filter $Pattern -Recurse | 
        Where-Object { $_.PSIsContainer -eq $false } |
        Select-String -Pattern $ContentMatch | 
        Select-Object Filename, LineNumber, Line > $tempFile
    } else {
        Get-ChildItem -Path $Path -Filter $Pattern -Recurse | 
        Select-Object Name, FullName, Length, LastWriteTime > $tempFile
    }
    
    if (Test-Path $tempFile) {
        Get-Content $tempFile -Encoding UTF8
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
}
```

## 🚀 Performance Considerations

### Temporary File Management
- Use unique timestamps in temp file names
- Always clean up temp files in `finally` blocks
- Consider using `C:\temp\` for consistent temp location
- Monitor temp directory size for large operations

### Memory Usage
- For large outputs, use `-TotalCount` to limit lines read
- Process files in chunks rather than loading everything into memory
- Use streaming where possible

### Error Recovery
- Always use `try/catch/finally` for file operations
- Test paths before operations
- Provide meaningful error messages
- Save operation state for debugging

## 🧪 Testing

### Validation Script
```powershell
# Test script to validate pipe fixes
function Test-PipeFixes {
    Write-Output "Testing PowerShell pipe fixes..."
    
    # Test 1: Basic process listing
    Write-Output "`nTest 1: Process listing"
    $tempFile = "C:\temp\test_processes.txt"
    Get-Process | Select-Object Name, Id -First 5 > $tempFile
    if (Test-Path $tempFile) {
        Write-Output "✅ Process listing works"
        Get-Content $tempFile -Encoding UTF8
        Remove-Item $tempFile
    } else {
        Write-Output "❌ Process listing failed"
    }
    
    # Test 2: External command
    Write-Output "`nTest 2: External command (PowerShell version)"
    $tempFile = "C:\temp\test_version.txt"
    Start-Process -FilePath "powershell.exe" -ArgumentList "-Command `$PSVersionTable.PSVersion" -Wait -RedirectStandardOutput $tempFile -WindowStyle Hidden
    if (Test-Path $tempFile) {
        Write-Output "✅ External command works"
        Get-Content $tempFile -Encoding UTF8
        Remove-Item $tempFile
    } else {
        Write-Output "❌ External command failed"
    }
    
    # Test 3: Error handling
    Write-Output "`nTest 3: Error handling"
    $tempFile = "C:\temp\test_error.txt"
    Get-Process -Name "nonexistent_process" -ErrorAction SilentlyContinue > $tempFile 2>$null
    if ((Test-Path $tempFile) -and (Get-Content $tempFile -ErrorAction SilentlyContinue)) {
        Write-Output "❌ Error handling failed - should be empty"
    } else {
        Write-Output "✅ Error handling works - no false output"
    }
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    
    Write-Output "`nPipe fix tests completed!"
}

# Run the test
Test-PipeFixes
```

## 📚 Additional Resources

- [PowerShell Redirection Operators](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_redirection)
- [PowerShell Encoding Issues](https://docs.microsoft.com/en-us/powershell/scripting/dev-cross-plat/writing-portable-cmdlets#string-encoding-and-cmdlet-parameters)  
- [MCP Protocol Specification](https://modelcontextprotocol.io/docs/concepts/architecture)

---

**Last Updated**: 2025-08-28  
**Status**: Active - Use file redirect pattern for all PowerShell operations in MCP tools
