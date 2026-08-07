#Requires -Version 5.1

<#
.SYNOPSIS
    Build script for MCPB (MCP Bundle) package creation.

.DESCRIPTION
    This script builds and optionally signs MCPB packages for the Windows Operations MCP server.
    It follows the MCPB building guidelines for consistent builds across environments.

.PARAMETER OutputDir
    Directory where the built package will be placed.
    Default: "dist"

.PARAMETER NoSign
    Skip package signing (for development/testing).

.PARAMETER Help
    Show this help message.

.EXAMPLE
    .\scripts\build-mcp-package.ps1

.EXAMPLE
    .\scripts\build-mcp-package.ps1 -OutputDir "C:\builds" -NoSign

.EXAMPLE
    .\scripts\build-mcp-package.ps1 -Help
#>

param(
    [string]$OutputDir = "dist",
    [switch]$NoSign,
    [switch]$Help
)

# Show help if requested
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

Write-Host "ðŸ› ï¸  MCPB Package Builder for Windows Operations MCP" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

try {
    # Ensure we're in the project root
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptDir
    Set-Location $projectRoot

    # Create output directory
    if (!(Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }

    Write-Host "ðŸ" Project root: $projectRoot" -ForegroundColor Yellow
    Write-Host "ðŸ"¦ Output directory: $OutputDir" -ForegroundColor Yellow

    # Step 1: Validate manifest
    Write-Host "ðŸ" Validating MCPB manifest..." -ForegroundColor Blue
    try {
        # Check if MCPB CLI is available
        $mcpbVersion = & mcpb --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "MCPB CLI not found. Install with: npm install -g @anthropic-ai/mcpb"
        }
        Write-Host "âœ... MCPB CLI version: $mcpbVersion" -ForegroundColor Green

        # Validate manifest
        & mcpb validate mcpb/manifest.json
        if ($LASTEXITCODE -ne 0) {
            throw "Manifest validation failed. Check mcpb/manifest.json for errors."
        }
        Write-Host "âœ... Manifest validation passed" -ForegroundColor Green

    } catch {
        Write-Error "Validation failed: $_"
        exit 1
    }

    # Step 2: Build the package
    Write-Host "ðŸ-ï¸  Building MCPB package..." -ForegroundColor Blue
    try {
        $packageName = "windows-operations-mcp.mcpb"
        $packagePath = Join-Path $OutputDir $packageName

        # Remove existing package if it exists
        if (Test-Path $packagePath) {
            Remove-Item $packagePath -Force
        }

        # Build the package
        & mcpb pack mcpb $packagePath
        if ($LASTEXITCODE -ne 0) {
            throw "Package build failed. Check the build output for errors."
        }

        Write-Host "âœ... Package built: $packagePath" -ForegroundColor Green

    } catch {
        Write-Error "Build failed: $_"
        exit 1
    }

    # Step 3: Sign the package (if not disabled)
    if (-not $NoSign) {
        Write-Host "ðŸ" Signing MCPB package..." -ForegroundColor Blue
        try {
            # Note: Package signing requires proper signing infrastructure
            # For now, we'll skip signing but show the command that would be used
            Write-Host "â„¹ï¸  Package signing skipped (requires signing infrastructure)" -ForegroundColor Yellow
            Write-Host "   To sign: mcpb sign --key your-key.pem $packagePath" -ForegroundColor Gray

        } catch {
            Write-Warning "Package signing failed: $_"
        }
    } else {
        Write-Host "â­ï¸  Package signing skipped (--NoSign specified)" -ForegroundColor Yellow
    }

    # Step 4: Verify the package
    Write-Host "ðŸ" Verifying MCPB package..." -ForegroundColor Blue
    try {
        & mcpb verify $packagePath
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Package verification failed, but package may still work."
        } else {
            Write-Host "âœ... Package verification passed" -ForegroundColor Green
        }
    } catch {
        Write-Warning "Package verification failed: $_"
    }

    # Step 5: Show package information
    Write-Host "ðŸ"Š Package Information:" -ForegroundColor Blue
    try {
        $packageSize = (Get-Item $packagePath).Length
        Write-Host "   ðŸ"¦ Package size: $([math]::Round($packageSize / 1MB, 2)) MB" -ForegroundColor Gray
        Write-Host "   ðŸ" Location: $packagePath" -ForegroundColor Gray
        Write-Host "   ðŸ"‹ To install: Drag the .mcpb file to Claude Desktop" -ForegroundColor Gray
    } catch {
        Write-Warning "Could not get package information: $_"
    }

    Write-Host ""
    Write-Host "ðŸŽ‰ MCPB package build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Test the package in Claude Desktop" -ForegroundColor White
    Write-Host "2. Check logs in %APPDATA%\Claude\logs\" -ForegroundColor White
    Write-Host "3. Report any issues to the project repository" -ForegroundColor White

} catch {
    Write-Error "Build failed: $_"
    Write-Host ""
    Write-Host "ðŸ"§ Troubleshooting:" -ForegroundColor Red
    Write-Host "1. Ensure all dependencies are installed" -ForegroundColor White
    Write-Host "2. Check mcpb/manifest.json for errors" -ForegroundColor White
    Write-Host "3. Verify Python environment is clean" -ForegroundColor White
    Write-Host "4. Check the MCPB CLI documentation" -ForegroundColor White
    exit 1
}

