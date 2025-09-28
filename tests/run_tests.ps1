# Windows Operations MCP - Test Runner
param(
    [string]$TestType = "unit",
    [string]$TestPath = "tests\unit",
    [switch]$Coverage,
    [switch]$Verbose
)

Write-Host "Windows Operations MCP - Test Runner" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Change to the project root
Set-Location $PSScriptRoot\..

# Set Python path to include src
$env:PYTHONPATH = "$PWD\src"

# Build pytest command
$pytestArgs = @()

if ($TestType -eq "unit") {
    $pytestArgs += "tests\unit"
}
elseif ($TestType -eq "integration") {
    $pytestArgs += "tests\integration"
}
elseif ($TestType -eq "all") {
    $pytestArgs += "tests"
}
else {
    $pytestArgs += $TestPath
}

if ($Coverage) {
    $pytestArgs += "--cov=src"
    $pytestArgs += "--cov-report=term-missing"
    $pytestArgs += "--cov-report=html:htmlcov"
    $pytestArgs += "--cov-fail-under=20"  # Lower initial requirement
}

if ($Verbose) {
    $pytestArgs += "-v"
}

# Run tests
Write-Host "Running tests: pytest $pytestArgs" -ForegroundColor Yellow
python -m pytest $pytestArgs

# Show results
Write-Host ""
Write-Host "Test Results:" -ForegroundColor Cyan

if ($Coverage) {
    Write-Host "- Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
}

Write-Host "- Test runner completed" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Green


