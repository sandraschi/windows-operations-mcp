# Webapp Start - Standardized SOTA (Auto-Repaired V2.5)
$WebPort = 10749
$BackendPort = 10748
$ProjectRoot = $PSScriptRoot
$FrontendPath = Join-Path $ProjectRoot "web_sota"

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup
Set-Location $FrontendPath
if (-not (Test-Path "node_modules")) { npm install }

# 3. Start the Python backend (Background)
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan

# Use uv run with PYTHONPATH pointing to src
$backendCmd = "`$env:PYTHONPATH = '$ProjectRoot;$ProjectRoot\src'; Set-Location '$ProjectRoot'; uv run uvicorn windows_operations_mcp.server:app --host 127.0.0.1 --port $BackendPort --log-level info --reload"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Run server (Vite dev)
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
Set-Location $FrontendPath
npm run dev -- --port $WebPort --host

