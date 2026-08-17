<#
.SYNOPSIS
    Fleet Heartbeat — recently modified files under D:\Dev\repos via WizTree MFT export.

.PARAMETER LookbackHours
    Hours to look back. Default 4.

.PARAMETER ScanPaths
    Roots to scan. Default D:\Dev\repos.

.PARAMETER OutputFile
    Markdown report path. Default D:\Dev\repos\mcp-central-docs\just_reports\fleet-heartbeat-report.md
#>

Param(
    [int]$LookbackHours = 4,
    [string[]]$ScanPaths = @("D:\Dev\repos"),
    [string]$OutputFile = "D:\Dev\repos\mcp-central-docs\just_reports\fleet-heartbeat-report.md"
)

$ReportDir = Split-Path -Parent $OutputFile
if ($ReportDir -and -not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}

$WizTreePath = "C:\Program Files\WizTree\WizTree64.exe"
$LookbackDate = (Get-Date).AddHours(-$LookbackHours)
$StartedAt = Get-Date

Write-Host "[Heartbeat] Lookback: since $($LookbackDate.ToString('yyyy-MM-dd HH:mm:ss')) ($LookbackHours h)" -ForegroundColor Gray
Write-Host "[Heartbeat] Scan roots: $($ScanPaths -join ', ')" -ForegroundColor Cyan

if (-not (Test-Path $WizTreePath)) {
    Write-Error "WizTree not found at $WizTreePath — install WizTree or fix path."
    exit 1
}

$Results = New-Object System.Collections.Generic.List[PSObject]
$SkipDirNames = @(
    'node_modules', '.git', '__pycache__', '.venv', 'venv', '.ruff_cache', '.pytest_cache',
    'dist', 'build', '.next', '.mypy_cache', '.tox', 'coverage'
)

function Test-HeartbeatSkipPath {
    param([string]$Path)
    if ($Path.EndsWith('\')) { return $true }
    foreach ($dir in $SkipDirNames) {
        if ($Path -like "*\$dir" -or $Path -like "*\$dir\*") { return $true }
    }
    return $false
}

function Test-WizTreeLeafFile {
    param($Item)
    $files = if ($null -eq $Item.Files -or $Item.Files -eq '') { 0 } else { [int]$Item.Files }
    $folders = if ($null -eq $Item.Folders -or $Item.Folders -eq '') { 0 } else { [int]$Item.Folders }
    return ($files -eq 0 -and $folders -eq 0)
}

function Import-WizTreeCsv {
    param([string]$Path)
    $lines = Get-Content -Path $Path -Encoding UTF8
    $start = 0
    for ($i = 0; $i -lt [Math]::Min($lines.Count, 6); $i++) {
        if ($lines[$i] -match '^"?File Name"?,\s*"?Size"?') {
            $start = $i
            break
        }
    }
    return $lines[$start..($lines.Count - 1)] | ConvertFrom-Csv
}

function Get-WizTreeItemSize {
    param($Item, [string]$FullPath)
    foreach ($prop in @('Size', 'Allocated')) {
        $raw = $Item.$prop
        if ($null -eq $raw -or "$raw" -eq '') { continue }
        $clean = ("$raw" -replace ',', '').Trim()
        if ($clean -match '^\d+$') {
            return [int64]$clean
        }
    }
    if ($FullPath -and -not $FullPath.EndsWith('\') -and (Test-Path -LiteralPath $FullPath)) {
        try {
            return (Get-Item -LiteralPath $FullPath).Length
        } catch {
            return 0
        }
    }
    return 0
}

function Format-HeartbeatSize {
    param([Int64]$Bytes)
    if ($Bytes -ge 1GB) { return ('{0:N2} GB' -f ($Bytes / 1GB)) }
    if ($Bytes -ge 1MB) { return ('{0:N2} MB' -f ($Bytes / 1MB)) }
    if ($Bytes -ge 1KB) { return ('{0:N1} KB' -f ($Bytes / 1KB)) }
    return "$Bytes B"
}

foreach ($Path in $ScanPaths) {
    if (-not (Test-Path $Path)) {
        Write-Warning "[Heartbeat] Path not found: $Path"
        continue
    }

    $TempCsv = Join-Path $env:TEMP "fleet_heartbeat_$(Get-Random).csv"
    Write-Host "[Heartbeat] WizTree scanning $Path ... (1–5 min on full fleet; MFT export)" -ForegroundColor Yellow

    $Proc = Start-Process `
        -FilePath $WizTreePath `
        -ArgumentList "`"$Path`"", "/export=`"$TempCsv`"", "/quit", "/admin=0" `
        -Wait -PassThru -WindowStyle Hidden

    if ($Proc.ExitCode -ne 0) {
        Write-Warning "[Heartbeat] WizTree exited $($Proc.ExitCode) for $Path"
    }

    if (-not (Test-Path $TempCsv)) {
        Write-Error "[Heartbeat] WizTree did not write $TempCsv — try running WizTree once manually or use /admin=1 with elevation."
        continue
    }

    Write-Host "[Heartbeat] Parsing WizTree CSV ..." -ForegroundColor Gray
    $CsvContent = Import-WizTreeCsv -Path $TempCsv
    Remove-Item $TempCsv -Force -ErrorAction SilentlyContinue

    $matched = 0
    foreach ($item in $CsvContent) {
        if (-not (Test-WizTreeLeafFile $item)) { continue }

        $fullPath = $item.'File Name'
        if ([string]::IsNullOrWhiteSpace($fullPath)) { continue }
        if (Test-HeartbeatSkipPath $fullPath) { continue }

        try {
            $modDate = [DateTime]::Parse($item.Modified)
        } catch {
            continue
        }

        if ($modDate -lt $LookbackDate) { continue }

        $repo = 'unknown'
        if ($fullPath -match '^[A-Za-z]:\\Dev\\repos\\([^\\]+)') {
            $repo = $Matches[1]
        }

        $Results.Add([PSCustomObject]@{
            Repo     = $repo
            Path     = $fullPath
            Size     = Get-WizTreeItemSize -Item $item -FullPath $fullPath
            Modified = $modDate
        })
        $matched++
    }

    Write-Host "[Heartbeat] $Path — $matched files in window" -ForegroundColor Green
}

$SortedResults = $Results | Sort-Object Modified -Descending
$Elapsed = (Get-Date) - $StartedAt

# Console summary
Write-Host ""
Write-Host "[Heartbeat] Done in $([math]::Round($Elapsed.TotalSeconds, 1))s — $($SortedResults.Count) files" -ForegroundColor Cyan

if ($SortedResults.Count -eq 0) {
    Write-Host "[Heartbeat] No file changes in lookback window." -ForegroundColor Gray
} else {
    Write-Host "[Heartbeat] By repo:" -ForegroundColor White
    $SortedResults | Group-Object Repo | Sort-Object Count -Descending | ForEach-Object {
        Write-Host ("  {0,-28} {1,4} files" -f $_.Name, $_.Count) -ForegroundColor Gray
    }
    Write-Host "[Heartbeat] Latest 12:" -ForegroundColor White
    $SortedResults | Select-Object -First 12 | ForEach-Object {
        $sizeLabel = Format-HeartbeatSize $_.Size
        $rel = $_.Path -replace [regex]::Escape("D:\Dev\repos\$($_.Repo)\"), ''
        Write-Host ("  {0:HH:mm}  {1,-22}  {2,-10}  {3}" -f $_.Modified, $_.Repo, $sizeLabel, $rel) -ForegroundColor DarkGray
        if ($rel.Length -gt 60) { Write-Host ("           $($_.Path)") -ForegroundColor DarkGray }
    }
}

# Markdown report
$ByRepo = $SortedResults | Group-Object Repo | Sort-Object Name
$ReportBody = if ($SortedResults.Count -eq 0) {
    "No modifications found in the lookback window."
} else {
    ($ByRepo | ForEach-Object {
        $section = "### $($_.Name) ($($_.Count) files)`n"
        $section += ($_.Group | Sort-Object Modified -Descending | ForEach-Object {
            $sizeLabel = Format-HeartbeatSize $_.Size
            $rel = $_.Path -replace [regex]::Escape("D:\Dev\repos\$($_.Repo)\"), ''
            "- **$($_.Modified.ToString('HH:mm:ss'))** ``$rel`` ($sizeLabel)"
        }) -join "`n"
        $section
    }) -join "`n`n"
}

$Report = @"
# Fleet Heartbeat Report

**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**Lookback:** $LookbackHours hours (since $($LookbackDate.ToString('yyyy-MM-dd HH:mm:ss')))  
**WizTree:** $WizTreePath  
**Elapsed:** $([math]::Round($Elapsed.TotalSeconds, 1))s  
**Files matched:** $($SortedResults.Count)

## Recently modified files (by repo)

$ReportBody

---
*Fleet Heartbeat — WizTree MFT export*
"@

$Report | Out-File -FilePath $OutputFile -Encoding utf8
Write-Host "[Heartbeat] Report: $OutputFile" -ForegroundColor Green
