<#
.SYNOPSIS
    SOTA Substrate Cleaner - Identifies disk bloat and stale environments.
    Uses WizTree to find massive orphans in the development substrate.

.PARAMETER MinSizeMB
    Minimum size of directory to report (in MB). Default is 500.

.PARAMETER MinAgeDays
    Minimum days since last access/modification to consider "Stale". Default is 14.

.PARAMETER ScanPath
    Root path to scan. Default is "D:\Dev\repos".

.PARAMETER BloatPatterns
    Regex or patterns for common bloat directories.
#>

Param(
    [int]$MinSizeMB = 500,
    [int]$MinAgeDays = 14,
    [string]$ScanPath = "D:\Dev\repos",
    [string[]]$BloatPatterns = @("node_modules", ".venv", "__pycache__", ".ruff_cache", ".pytest_cache", ".next", "dist", "build")
)

$WizTreePath = "C:\Program Files\WizTree\WizTree64.exe"
$TempCsv = Join-Path $env:TEMP "substrate_audit_$(Get-Random).csv"
$ThresholdDate = (Get-Date).AddDays(-$MinAgeDays)
$MinSizeBytes = $MinSizeMB * 1MB

Write-Host "[Cleaner] Auditing substrate at $ScanPath..." -ForegroundColor Cyan
Write-Host "[Cleaner] Threshold: > $MinSizeMB MB and older than $MinAgeDays days." -ForegroundColor Gray

if (-not (Test-Path $ScanPath)) {
    Write-Error "Scan path not found: $ScanPath"
    return
}

# Run WizTree
Start-Process -FilePath $WizTreePath -ArgumentList "`"$ScanPath`"", "/export=`"$TempCsv`"", "/quit", "/admin=1" -Wait -WindowStyle Hidden

if (-not (Test-Path $TempCsv)) {
    Write-Error "WizTree failed to generate export."
    return
}

# Parse results
$CsvContent = Get-Content $TempCsv | Select-Object -Skip 1 | ConvertFrom-Csv
Remove-Item $TempCsv -Force

$BloatTargets = New-Object System.Collections.Generic.List[PSObject]

foreach ($item in $CsvContent) {
    $size = [int64]$item.Size
    $modDate = [DateTime]::Parse($item.Modified)
    $name = $item.'File Name'

    # Check size threshold
    if ($size -lt $MinSizeBytes) { continue }

    # Check age threshold
    if ($modDate -gt $ThresholdDate) { continue }

    # Check if it matches bloat patterns
    $isBloat = $false
    foreach ($pattern in $BloatPatterns) {
        if ($name -like "*\$pattern" -or $name -like "*\$pattern\*") {
            $isBloat = $true
            break
        }
    }

    if ($isBloat) {
        $BloatTargets.Add([PSCustomObject]@{
            Directory = $name
            SizeMB = [math]::Round($size / 1MB, 2)
            LastModified = $modDate
        })
    }
}

# Generate Report
Write-Host "`n[Cleaner] ðŸ-'ï¸ Potential Bloat Targets Identified:" -ForegroundColor Yellow
if ($BloatTargets.Count -eq 0) {
    Write-Host "No stale bloat found matching criteria." -ForegroundColor Green
} else {
    $BloatTargets | Sort-Object SizeMB -Descending | ForEach-Object {
        Write-Host "- [$($_.SizeMB) MB] $($_.LastModified.ToShortDateString()) -> $($_.Directory)" -ForegroundColor White
    }
}

Write-Host "`n[Cleaner] Recommendation: Use 'just clean' in the respective repositories or delete manually." -ForegroundColor Gray
