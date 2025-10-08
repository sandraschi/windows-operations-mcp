# Run this AFTER restarting Claude Desktop
Write-Host "=== MCP Server Status Check ===" -ForegroundColor Cyan
Write-Host ""

# Check MCP version
Write-Host "MCP Version Installed:" -ForegroundColor Yellow
& "C:\Users\sandr\AppData\Local\Programs\Python\Python313\python.exe" -m pip show mcp | Select-String "Version"

Write-Host ""
Write-Host "Latest log entries (basic-memory):" -ForegroundColor Yellow
Get-Content "$env:APPDATA\Claude\logs\mcp-server-basic memory.log" -Tail 10 | ForEach-Object {
    if ($_ -match "error") {
        Write-Host $_ -ForegroundColor Red
    } elseif ($_ -match "success|connected|ready") {
        Write-Host $_ -ForegroundColor Green
    } else {
        Write-Host $_
    }
}

Write-Host ""
Write-Host "If you see 'TypeError' above, restart Claude Desktop!" -ForegroundColor Red
Write-Host "If you see successful connection logs, it's working!" -ForegroundColor Green

