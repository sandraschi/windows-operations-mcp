#!/usr/bin/env pwsh
# Auto-generated fix script for windows-operations-mcp
# Generated: 2025-10-26_00-31-23
# Issues to fix: 5

param([switch]$DryRun = $false)

Write-Host '🔧 Fixing Repository Standards...' -ForegroundColor Cyan
if ($DryRun) { Write-Host '🔍 DRY RUN MODE' -ForegroundColor Yellow }

$centralDocs = 'D:\Dev\repos\mcp-central-docs'

# Fix: Remove description= parameters from @mcp.tool() decorators

# Fix: Create assets/icon.svg

# Fix: Create requirements.txt

# Fix: Create CONTRIBUTING.md from central docs template
if (-not (Test-Path 'CONTRIBUTING.md')) {
    if (Test-Path "$centralDocs/templates/CONTRIBUTING.md") {
        Copy-Item "$centralDocs/templates/CONTRIBUTING.md" 'CONTRIBUTING.md' -Force
        Write-Host '  ✅ Copied: CONTRIBUTING.md' -ForegroundColor Green
    }
}

# Fix: Add ruff configuration to pyproject.toml

Write-Host '✅ Fix script complete!' -ForegroundColor Green
