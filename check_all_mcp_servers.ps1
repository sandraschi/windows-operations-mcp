# Check status of all MCP servers
$servers = @(
    "advanced-memory-mcp",
    "basic memory",
    "brightdata", 
    "fetch",
    "filetools",
    "mcp-server-docker",
    "nest-protect",
    "notepadpp",
    "rtorrent-mcp",
    "suno-mcp",
    "winauto",
    "winops"
)

Write-Host "=== MCP Server Status Check ===" -ForegroundColor Cyan
Write-Host ""

foreach ($server in $servers) {
    $logFile = "$env:APPDATA\Claude\logs\mcp-server-$server.log"
    
    if (Test-Path $logFile) {
        $lastError = Get-Content $logFile -Tail 5 | Where-Object { $_ -match "error|Error|ERROR|TypeError|AttributeError|failed|disconnect" } | Select-Object -First 1
        
        if ($lastError) {
            Write-Host "❌ $server" -ForegroundColor Red
            Write-Host "   Error: $($lastError.Substring(0, [Math]::Min(120, $lastError.Length)))..." -ForegroundColor DarkRed
        } else {
            Write-Host "✅ $server" -ForegroundColor Green
        }
    } else {
        Write-Host "⚪ $server (no log)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Checking for Python 3.13 compatibility issues..." -ForegroundColor Yellow

