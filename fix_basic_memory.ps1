# Fix basic-memory MCP server dependencies
Write-Host "=== Fixing basic-memory Dependencies ===" -ForegroundColor Cyan

# Reinstall basic-memory from source
Write-Host "`nReinstalling basic-memory with updated dependencies..." -ForegroundColor Yellow
Set-Location "D:\Dev\repos\basic-memory"

# Uninstall first
& "C:\Users\sandr\AppData\Local\Programs\Python\Python313\python.exe" -m pip uninstall basic-memory -y

# Reinstall from source (editable mode)
& "C:\Users\sandr\AppData\Local\Programs\Python\Python313\python.exe" -m pip install -e .

Write-Host "`nDone! Now restart Claude Desktop" -ForegroundColor Green

