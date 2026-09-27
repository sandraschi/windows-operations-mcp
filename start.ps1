# *********************************************************************************
# * SOTA Fleet Orchestration - Standardized Start System (v1.19.0)                *
# * Generated/Repaired by Antigravity on 2026-09-27                  *
# *********************************************************************************

# Legacy root launcher — delegates to the fleet start engine.
# --- SOTA PORT SAFETY START ---
# Ports live in fleet-start.config.ps1 (no $Port var in this file).
foreach ($portNum in @(10748, 10749)) {
    Get-NetTCPConnection -LocalPort $portNum -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.OwningProcess -ne $PID) {
            Write-Host "Clearing stale listener on port $portNum (PID $($_.OwningProcess))..." -ForegroundColor Yellow
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}
Start-Sleep -Seconds 1
# --- SOTA PORT SAFETY END ---
# Backend: uvicorn windows_operations_mcp.server:app on 10748 (FastAPI bridge).
# Frontend: Vite on 10749. See web_sota/start.ps1 + fleet-start.config.ps1.
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'web_sota\start.ps1') @PSBoundParameters

