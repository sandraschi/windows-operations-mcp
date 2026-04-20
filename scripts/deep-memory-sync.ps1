<#
.SYNOPSIS
    SOTA Deep Memory Sync - Orchestrates ingestion of external research into the ADN pipeline.
    Uses WizFile for instantaneous location of new documents.

.PARAMETER HotFolders
    Array of directories to monitor for new research.

.PARAMETER ProcessedLog
    Path to a file tracking already ingested documents.

.PARAMETER IngestExtensions
    File extensions to ingest (e.g., "*.pdf", "*.docx").
#>

Param(
    [string[]]$HotFolders = @("$env:USERPROFILE\Downloads", "$env:USERPROFILE\Desktop", "$env:USERPROFILE\Documents"),
    [string]$ProcessedLog = "D:\Dev\repos\windows-operations-mcp\scripts\ingested_files.log",
    [string[]]$IngestExtensions = @("*.pdf", "*.docx", "*.html", "*.pptx", "*.epub", "*.md")
)

$WizFilePath = "C:\Program Files\WizFile\WizFile64.exe"
$AdnInbox = "D:\Dev\repos\advanced-memory-mcp\zettelkasten\inbox"
$TempCsv = Join-Path $env:TEMP "deep_memory_sync_$(Get-Random).csv"

if (-not (Test-Path $AdnInbox)) {
    Write-Error "ADN Inbox not found at $AdnInbox"
    return
}

if (-not (Test-Path $ProcessedLog)) {
    New-Item $ProcessedLog -Type File -Force | Out-Null
}

$ProcessedFiles = Get-Content $ProcessedLog

Write-Host "[Sync] Scanning Hot Folders: $($HotFolders -join ', ')..." -ForegroundColor Cyan

foreach ($Folder in $HotFolders) {
    if (-not (Test-Path $Folder)) { continue }

    foreach ($Ext in $IngestExtensions) {
        Write-Host "  Searching for $Ext in $Folder..." -ForegroundColor Gray
        
        # WizFile CLI: /search="pattern" /export="file.csv" /quit
        # Note: WizFile's CLI is simpler. We might need to filter by folder in PS if WizFile doesn't support path-restricted search well via CLI.
        # Actually WizFile CLI /search can include paths: "C:\Path\*.pdf"
        $SearchPattern = Join-Path $Folder $Ext
        Start-Process -FilePath $WizFilePath -ArgumentList "/search=`"$SearchPattern`"", "/export=`"$TempCsv`"", "/quit" -Wait -WindowStyle Hidden

        if (Test-Path $TempCsv) {
            $CsvContent = Import-Csv $TempCsv
            
            foreach ($item in $CsvContent) {
                # WizFile CSV headers: "File Name","Extension","Size","Modified","Created","Attributes","Folder"
                $FullPath = Join-Path $item.Folder $item.'File Name'
                
                if ($ProcessedFiles -contains $FullPath) {
                    continue
                }

                Write-Host "    [New] Found: $($item.'File Name')" -ForegroundColor White
                
                try {
                    $Dest = Join-Path $AdnInbox $item.'File Name'
                    Copy-Item $FullPath $Dest -ErrorAction Stop
                    $FullPath | Out-File -FilePath $ProcessedLog -Append
                    Write-Host "      ✅ Staged to ADN Inbox." -ForegroundColor Green
                } catch {
                    Write-Warning "      ❌ Failed to stage: $_"
                }
            }
            Remove-Item $TempCsv -Force
        }
    }
}

Write-Host "`n[Sync] Deep Memory Sync Complete." -ForegroundColor Green
Write-Host "[Sync] Run 'adn_inbox(operation=`"process`")' to finalize ingestion." -ForegroundColor Gray
