# Changelog

All notable changes to the Windows Operations MCP project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Changelog

All notable changes to the Windows Operations MCP project will be documented in this file.

- ✅ **April 2026 Modernization - FastAPI Orchestration**: Refactored server to use a root FastAPI wrapper for unified API orchestration.
- ✅ **FastMCP 3.1.1 Upgrade**: Advanced support for 2026 SOTA agentic workflows and tool orchestration.
- ✅ **Git Hardening**: Injected `GIT_TERMINAL_PROMPT=0` to prevent hung processes and improved porcelain status parsing.
- ✅ **Modern Test Suite**: Established `tests/unit/tools/test_git_portmanteau.py` for comprehensive portmanteau tool verification.
- ✅ **Fleet Standard Dashboard**: Overhauled web_sota frontend with premium glassmorphism, animations, and telemetry.
- ✅ **Authoritative Port Sync**: Fixed port allocation to 10748 (Backend) and 10749 (Frontend).
- ✅ **Infrastructure Recovery**: Restored missing Tailwind/PostCSS configuration infrastructure.

## [1.18.1] - 2026-01-04

### 🚀 SOTA 2026 Alignment - MCPB Native
- ✅ **Complete DXT Purge**: Final removal of all legacy DXT artifacts and technical debt.
- ✅ **MCPB Native Architecture**: Transitioned to pure MCPB v1.18.1 specification.
- ✅ **FastMCP 2.14.4 Upgrade**: Updated internal logic for SOTA 2026 autonomous agents.
- ✅ **Refined Portmanteau Logic**: Optimized action handling in all 9 management tools.
- ✅ **Autonomous Sampling**: Enhanced support for secure, agent-led tool orchestration.

## [0.3.0] - 2025-12-30

### 🚀 Major Release - Portmanteau Reorganization Complete
- ✅ **9 Portmanteau Tools** replacing 57+ individual legacy tools.
- ✅ **Action-based Interface** for uniform tool interaction.
- ✅ **FastMCP 2.14.1+ Compliance**.

## [0.2.0] - 2025-10-08

### 🎉 MCPB Integration Milestone
- ✅ Transitioned to MCPB (MCP Bundle) packaging system.
- ✅ Implemented automated manifest generation.
- ✅ Added GitHub Actions CI/CD infrastructure.

## [0.1.0] - 2025-09-30

### Initial Release
- ✅ Core Windows system operations (Services, Event Logs, Performance, Permissions).
- ✅ PowerShell & CMD execution support.
- ✅ 139 baseline tests.
