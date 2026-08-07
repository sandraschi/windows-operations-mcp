# Legacy root launcher — delegates to the fleet start engine.
# Backend: uvicorn windows_operations_mcp.server:app on 10748 (FastAPI bridge).
# Frontend: Vite on 10749. See web_sota/start.ps1 + fleet-start.config.ps1.
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'web_sota\start.ps1') @PSBoundParameters
