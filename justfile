set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# Sync with pyproject / release tags when cutting a release
__version__ := "14.1.0"
__name__ := "windows-operations-mcp"

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

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

# Build MCPB bundle via project script (legacy helper; prefer `just mcpb-pack` from fleet.just)
build:
	Set-Location '{{justfile_directory()}}'
	uv run python build_mcpb.py

# mcpb-pack, cua-nsis-test: provided by scripts/just/fleet.just

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

# ── Fleet Operations ─────────────────────────────────────────────────────────

# Track modified files in the last N hours (default 4) across the fleet
heartbeat hours="4":
	pwsh -NoProfile -File .\scripts\fleet-heartbeat.ps1 -LookbackHours {{hours}}

# Scan for stale disk bloat (min 500MB, 14 days stale)
audit-leaks min_mb="500" age_days="14":
	pwsh -NoProfile -File .\scripts\substrate-cleaner.ps1 -MinSizeMB {{min_mb}} -MinAgeDays {{age_days}}

# Sync new research from Downloads/Desktop/Documents to ADN Inbox
sync-research:
	pwsh -NoProfile -File .\scripts\deep-memory-sync.ps1

# EMERGENCY: Kill all fleet processes running on ports 10700-10850
kill-fleet:
	pwsh -NoProfile -File .\scripts\kill-fleet.ps1

# ── Tauri NSIS ─────────────────────────────────────────────────────────────────

# Build the PyInstaller backend .exe and copy to Tauri resources
build-sidecar:
	pwsh -NoProfile -File native\build-sidecar.ps1

# Build the Tauri NSIS desktop installer (full pipeline: frontend -> sidecar -> Rust -> NSIS)
build-native: build-sidecar
	$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
	$vcvars = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
	$envOutput = cmd /c "`"$vcvars`" > nul & set" | Where-Object { $_ -match '^(INCLUDE|LIB|LIBPATH|VCToolsVersion|WindowsSdkDir|UniversalCRTSdkDir|UCRTVersion)=' }
	foreach ($line in $envOutput) { $parts = $line.Split('=', 2); Set-Item -Path "env:$($parts[0])" -Value $parts[1] -ErrorAction SilentlyContinue }
	Set-Location '{{justfile_directory()}}\native'
	npx @tauri-apps/cli build --bundles nsis

# cua-nsis-test: provided by scripts/just/fleet.just
