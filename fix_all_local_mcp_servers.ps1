# Fix all local MCP servers by reinstalling dependencies in Python 3.10

$localServers = @(
    @{ name = "winops"; path = "D:\Dev\repos\windows-operations-mcp" },
    @{ name = "advanced-memory-mcp"; path = "D:\Dev\repos\advanced-memory-mcp" },
    @{ name = "filetools"; path = "D:\Dev\repos\filesystem-mcp" },
    @{ name = "nest-protect"; path = "D:\Dev\repos\nest-protect-mcp" },
    @{ name = "notepadpp"; path = "D:\Dev\repos\notepadpp-mcp" },
    @{ name = "rtorrent-mcp"; path = "D:\Dev\repos\qbtmcp" },
    @{ name = "suno-mcp"; path = "D:\Dev\repos\suno-mcp" },
    @{ name = "winauto"; path = "D:\Dev\repos\pywinauto-mcp" }
)

Write-Host "=== Fixing Local MCP Servers in Python 3.10 ===" -ForegroundColor Cyan
Write-Host ""

foreach ($server in $localServers) {
    Write-Host "Processing $($server.name)..." -ForegroundColor Yellow
    
    if (Test-Path $server.path) {
        Push-Location $server.path
        
        # Check for requirements.txt or pyproject.toml
        if (Test-Path "requirements.txt") {
            Write-Host "  Installing from requirements.txt..." -ForegroundColor Gray
            python -m pip install -r requirements.txt -q
        }
        
        # Install package in editable mode
        Write-Host "  Installing package..." -ForegroundColor Gray
        python -m pip install -e . -q
        
        Write-Host "  ✅ Done" -ForegroundColor Green
        
        Pop-Location
    } else {
        Write-Host "  ⚠️  Path not found: $($server.path)" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "=== All Done! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Now restart Claude Desktop for changes to take effect" -ForegroundColor Cyan

