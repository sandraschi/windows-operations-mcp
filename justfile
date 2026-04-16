set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# Sync with pyproject / release tags when cutting a release
__version__ := "14.1.0"
__name__ := "windows-operations-mcp"

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the SOTA Industrial Dashboard (lists recipes below)
default:
	@$lines = Get-Content '{{justfile()}}'; \
	Write-Host (' [{0}] Windows Operations MCP v{1}' -f '{{__name__}}', '{{__version__}}') -ForegroundColor White -BackgroundColor Cyan; \
	Write-Host '' ; \
	$currentCategory = ''; \
	foreach ($line in $lines) { \
		if ($line -match '^# ── ([^─]+) ─') { \
			$currentCategory = $matches[1].Trim(); \
			Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
			Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
		} elseif ($line -match '^# ([^─].+)') { \
			$desc = $matches[1].Trim(); \
			$idx = [array]::IndexOf($lines, $line); \
			if ($idx -lt $lines.Count - 1) { \
				$nextLine = $lines[$idx + 1]; \
				if ($nextLine -match '^([a-z0-9-]+):') { \
					$recipe = $matches[1]; \
					$pad = ' ' * [math]::Max(2, (22 - $recipe.Length)); \
					Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
					Write-Host "$pad$desc" -ForegroundColor Gray; \
				} \
			} \
		} \
	} \
	Write-Host "`n  [System State: UV + WEB_SOTA]" -ForegroundColor DarkGray; \
	Write-Host ''

# ── Environment ────────────────────────────────────────────────────────────────

# Install Python deps (uv sync)
install:
	Set-Location '{{justfile_directory()}}'
	uv sync

# Upgrade locked dependencies
update:
	Set-Location '{{justfile_directory()}}'
	uv lock --upgrade

# ── Development ──────────────────────────────────────────────────────────────

# Run MCP server over stdio (Claude Desktop / MCP clients)
mcp:
	Set-Location '{{justfile_directory()}}'
	uv run windows-operations-mcp

# Start Vite + FastAPI hub (ports 10749 / 10748) — same as .\\start.ps1
web:
	Set-Location '{{justfile_directory()}}'
	pwsh -NoProfile -File .\start.ps1

# Run API + UI from web_sota launcher only
web-sota:
	Set-Location '{{justfile_directory()}}'
	pwsh -NoProfile -File .\web_sota\start.ps1

# API only: uvicorn with reload (127.0.0.1:10748)
api:
	Set-Location '{{justfile_directory()}}'
	$env:PYTHONPATH = "$(Get-Location);$(Get-Location)\src"
	uv run uvicorn windows_operations_mcp.server:app --host 127.0.0.1 --port 10748 --reload --log-level info

# Frontend only: Vite dev (after npm install in web_sota)
ui:
	Set-Location '{{justfile_directory()}}\web_sota'
	npm run dev -- --port 10749 --host

# ── Quality ───────────────────────────────────────────────────────────────────

# Ruff + Biome (CI-style, no writes)
lint:
	Set-Location '{{justfile_directory()}}'
	uv run ruff check .
	Set-Location '{{justfile_directory()}}\web_sota'
	npx biome ci .

# Ruff and Biome auto-fix + format
fix:
	Set-Location '{{justfile_directory()}}'
	uv run ruff check . --fix --unsafe-fixes
	uv run ruff format .
	Set-Location '{{justfile_directory()}}\web_sota'
	npx biome check --write .

# Format only (Python + JSON in web_sota via Biome)
format:
	Set-Location '{{justfile_directory()}}'
	uv run ruff format .
	Set-Location '{{justfile_directory()}}\web_sota'
	npx biome format --write .

# ── Testing ───────────────────────────────────────────────────────────────────

# Full pytest run (verbose)
test:
	Set-Location '{{justfile_directory()}}'
	uv run pytest -v

# Lint + tests (quick gate)
check: lint test

# ── Security ─────────────────────────────────────────────────────────────────

# Bandit scan on src/ (install dev tools if missing: uv tool install bandit)
check-sec:
	Set-Location '{{justfile_directory()}}'
	uv run bandit -r src/

# Dependency vulnerability scan (requires safety)
audit-deps:
	Set-Location '{{justfile_directory()}}'
	uv run safety check

# ── Packaging & verify ─────────────────────────────────────────────────────

# Build MCPB bundle via project script
build:
	Set-Location '{{justfile_directory()}}'
	uv run python build_mcpb.py

# Pack with mcpb CLI when available (output under dist/)
mcpb-pack:
	Set-Location '{{justfile_directory()}}'
	mcpb pack . "dist/{{__name__}}-v{{__version__}}.mcpb"

# Smoke-test MCP server import
verify:
	Set-Location '{{justfile_directory()}}'
	uv run python -c "from windows_operations_mcp.mcp_server import mcp; print('OK:', mcp.name)"

# ── Housekeeping ─────────────────────────────────────────────────────────────

# Remove build artifacts and common caches
clean:
	Set-Location '{{justfile_directory()}}'
	if (Test-Path 'dist') { Remove-Item -Recurse -Force 'dist' }
	if (Test-Path 'build') { Remove-Item -Recurse -Force 'build' }
	if (Test-Path '.pytest_cache') { Remove-Item -Recurse -Force '.pytest_cache' }
	if (Test-Path 'web_sota\node_modules\.cache') { Remove-Item -Recurse -Force 'web_sota\node_modules\.cache' }
	Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue | ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
	Get-ChildItem -Path . -Filter '*.mcpb' -ErrorAction SilentlyContinue | Remove-Item -Force
	Write-Host 'Clean complete.' -ForegroundColor Green
