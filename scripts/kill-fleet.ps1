<#
.SYNOPSIS
    SOTA Fleet Kill Switch - Terminates all visible and hidden fleet processes.
    Scans the standardized Antigravity port range (10700-10850) to find targets.
#>

$FleetPortRange = 10700..10850

Write-Host "[Fleet-Kill] Initiating Global Fleet Shutdown..." -ForegroundColor Red
Write-Host "[Fleet-Kill] Scanning ports 10700-10850..." -ForegroundColor Gray

$TargetPids = Get-NetTCPConnection -LocalPort $FleetPortRange -ErrorAction SilentlyContinue | `
              Where-Object { $_.OwningProcess -gt 4 } | `
              Select-Object -ExpandProperty OwningProcess -Unique

if ($TargetPids.Count -eq 0) {
    Write-Host "[Fleet-Kill] No active fleet processes detected." -ForegroundColor Green
    return
}

Write-Host "[Fleet-Kill] Found $($TargetPids.Count) process(es) to terminate." -ForegroundColor Yellow

foreach ($targetProcId in $TargetPids) {
    try {
        $proc = Get-Process -Id $targetProcId -ErrorAction Stop
        $desc = "$($proc.ProcessName) (PID: $targetProcId)"
        Write-Host "  -> Terminating $desc..." -ForegroundColor DarkGray
        Stop-Process -Id $targetProcId -Force -ErrorAction Stop
        Write-Host "     ✅ Terminated." -ForegroundColor Green
    } catch {
        Write-Warning "     ❌ Could not terminate PID $pid : $_"
    }
}

Write-Host "`n[Fleet-Kill] Shutdown complete." -ForegroundColor Red
