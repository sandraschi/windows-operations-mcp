# Fix Windows Operations MCP Installation
Write-Host "=== Fixing Windows Operations MCP Installation ===" -ForegroundColor Green

# Navigate to the repo
Set-Location "D:\Dev\repos\windows-operations-mcp"

# Check current directory structure
Write-Host "Current directory:" -ForegroundColor Yellow
Get-Location

Write-Host "Directory contents:" -ForegroundColor Yellow
Get-ChildItem -Name

# Check if setup.py or pyproject.toml exists
if (Test-Path "setup.py") {
    Write-Host "Found setup.py - installing with pip" -ForegroundColor Green
    python -m pip install -e .
} elseif (Test-Path "pyproject.toml") {
    Write-Host "Found pyproject.toml - installing with pip" -ForegroundColor Green
    python -m pip install -e .
} else {
    Write-Host "No setup.py or pyproject.toml found - checking src structure" -ForegroundColor Yellow
    
    # Check if src/windows_operations_mcp exists
    if (Test-Path "src\windows_operations_mcp") {
        Write-Host "Found src/windows_operations_mcp - using that path" -ForegroundColor Green
        # Add to PYTHONPATH temporarily and install
        $env:PYTHONPATH = "D:\Dev\repos\windows-operations-mcp\src;$env:PYTHONPATH"
        python -m pip install -e .
    } else {
        Write-Host "ERROR: Cannot find proper package structure" -ForegroundColor Red
        exit 1
    }
}

# Verify installation
Write-Host "=== Verifying Installation ===" -ForegroundColor Green
python -c "import windows_operations_mcp; print('SUCCESS: Module imported successfully')"

# Test the module entry point
Write-Host "=== Testing Module Entry Point ===" -ForegroundColor Green
python -m windows_operations_mcp --help

Write-Host "=== Installation Complete ===" -ForegroundColor Green
