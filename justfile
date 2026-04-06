set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Variables ────────────────────────────────────────────────────────────────

NAME := "Windows Operations MCP"
DESC := "Specialized Windows Control Plane & Data Surgery Hub"
VER  := "14.0.0"

# ── Dashboard (SOTA v14.0) ──────────────────────────────────────────────────

# Display the Industrial Operations Dashboard
default:
    @powershell -NoLogo -Command " \
        $lines = Get-Content '{{justfile()}}'; \
        Write-Host ' [{{NAME}}] {{DESC}} v{{VER}}' -ForegroundColor White -BackgroundColor Cyan; \
        Write-Host '' ; \
        $currentCategory = ''; \
        foreach ($line in $lines) { \
            if ($line -match '^# ── ([^─]+) ─') { \
                $currentCategory = $matches[1].Trim(); \
                Write-Host \"`n  $currentCategory\" -ForegroundColor Cyan; \
                Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
            } elseif ($line -match '^# ([^─].+)') { \
                $desc = $matches[1].Trim(); \
                $idx = [array]::IndexOf($lines, $line); \
                if ($idx -lt $lines.Count - 1) { \
                    $nextLine = $lines[$idx + 1]; \
                    if ($nextLine -match '^([a-z0-9-]+):') { \
                        $recipe = $matches[1]; \
                        $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                        Write-Host \"    $recipe\" -ForegroundColor White -NoNewline; \
                        Write-Host \"$pad$desc\" -ForegroundColor Gray; \
                    } \
                } \
            } \
        } \
        Write-Host \"`n  [System State: PROD/HARDENED]\" -ForegroundColor DarkGray; \
        Write-Host ''"

# ── Development ──────────────────────────────────────────────────────────────

# Start the server in development mode (stdio)
dev:
    uv run python src/windows_operations_mcp/mcp_server.py

# Install dependencies and sync the environment
install:
    uv sync

# Update lockfile and dependencies
update:
    uv lock --upgrade

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v14.0 linting (uv-first)
lint:
    uv run ruff check .

# Execute Ruff SOTA v14.0 fix and formatting
fix:
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .

# ── Testing ───────────────────────────────────────────────────────────────────

# Execute full SOTA test suite via pytest
test:
    uv run pytest -v

# ── Security ──────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    uv run safety check

# ── Packaging ─────────────────────────────────────────────────────────────────

# Build the SOTA v14.0 MCPB bundle
build:
    uv run python build_mcpb.py

# Verify the manifest and server initialization
verify:
    uv run python -c "from windows_operations_mcp.mcp_server import mcp; print('Server Init Success')"

# ── Housekeeping ─────────────────────────────────────────────────────────────

# Clean all build artifacts and caches
clean:
    if (Test-Path 'dist') { Remove-Item -Recurse -Force 'dist' }
    if (Test-Path 'build') { Remove-Item -Recurse -Force 'build' }
    if (Test-Path '.pytest_cache') { Remove-Item -Recurse -Force '.pytest_cache' }
    if (Test-Path 'src/windows_operations_mcp/__pycache__') { Remove-Item -Recurse -Force 'src/windows_operations_mcp/__pycache__' }
    Get-ChildItem -Path . -Filter "*.mcpb" | Remove-Item -Force
    Write-Host "Caches and build artifacts cleared." -ForegroundColor Green
