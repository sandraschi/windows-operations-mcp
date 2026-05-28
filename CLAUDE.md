# windows-operations-mcp — Claude Code Guide

## Overview
Windows Operations MCP - Comprehensive Windows system operations for Claude Desktop with MCPB packaging

## Entry Points
- `uv run windows-operations-mcp` → `windows_operations_mcp.__main__:main`

## Standards
- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http`)
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `AGENTS.md` — OpenAI Codex agent context (if present)
