# Windows Operations MCP

[![FastMCP](https://img.shields.io/badge/FastMCP-3.1.1-blue)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![SOTA](https://img.shields.io/badge/SOTA-April%202026-violet)](file:///D:/Dev/repos/mcp-central-docs/standards/AGENT_PROTOCOLS.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Fleet%20Standard-green)](REPOSITORY_STATUS_REPORT.md)

A high-performance Windows system orchestration platform built with **FastMCP 3.1.1** and a unified **SOTA v1.18.1** FastAPI architecture.

##  SOTA v1.18.1 Modernization (April 2026)

- ** Unified FastAPI Bridge**: Root orchestration layer on port **10748** with ASGI-mounted FastMCP.
- ** Fleet Standard Dashboard**: Premium glassmorphic Vite dashboard on port **10749**.
- ** 10 Portmanteau Tools**: Optimized from 57+ legacy tools into consolidated management interfaces.
- ** AI Command Center**: Integrated natural language orchestration for complex system tasks.
- ** Discovery Manifests**: Standard `llms.txt` and `glama.json` for autonomous fleet integration.

##  Key Features

###  Windows System Orchestration
- **Windows Services**: Full lifecycle management (Start, Stop, Restart, List) for system services.
- **Process Management**: Real-time monitoring and resource analysis with PID-level granularity.
- **System Diagnostics**: Comprehensive hardware, software, and health monitoring.
- **Command Execution**: High-fidelity PowerShell/CMD execution with reliable output capture.

###  File & Data Operations
- **File System**: Consolidated `read`, `write`, `delete`, `move`, `copy`, and `info` actions.
- **Archive Management**: Multi-format support (ZIP, TAR, GZ) with intelligent exclusion logic.
- **JSON Orchestration**: Query, validate, and format JSON workloads using JSONPath patterns.
- **Git Operations**: Seamless repository synchronization (Commit, Push, Status).

##  Quick Start

###  Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+
- Node.js & npm (for Dashboard development)

###  Global Installation
Run the server immediately via `uvx`:
```bash
uvx windows-operations-mcp
```

###  Local Deployment (Fleet standard)
Run the root startup script to initiate the full SOTA stack (Backend + Dashboard):
```powershell
.\start.ps1
```
- **Backend Hub**: `http://localhost:10748`
- **Dashboards**: `http://localhost:10749`

##  Repository Structure

```
windows-operations-mcp/
 src/                           # Python Backend (Port 10748)
    windows_operations_mcp/
        mcp_server.py          # FastMCP 3.1+ server logic
        server.py              # Root FastAPI wrapper logic
        web.py                 # Telemetry API endpoints
        tools/                 # 10 Portmanteau Tool modules
 web_sota/                      # Vite Frontend (Port 10749)
    src/                       # Glassmorphic React UI
    tailwind.config.js         # SOTA Vibrant theme
 glama.json                     # Server manifest for fleet discovery
 llms.txt                       # Technical digest for LLM context
```

##  Portmanteau Toolset

| Tool | Action Context |
| :--- | :--- |
| **system_management** | Health, Info, Test-Port, Help |
| **process_management** | List, Info, Resources |
| **file_operations** | Read, Write, Delete, Move, Copy, Info |
| **command_execution** | PowerShell, CMD |
| **windows_services** | List, Start, Stop, Restart |
| **archive_management** | Create, Extract, List |
| **json_operations** | Read, Write, Validate, Format, Extract |
| **git_operations** | Commit, Push, Status |
| **agentic_operations** | Autonomous mission orchestration |

##  Configuration

- **BACKEND_PORT**: 10748
- **FRONTEND_PORT**: 10749
- **LOG_LEVEL**: DEBUG, INFO, WARNING, ERROR

##  Compliance Checklist

-  **FastMCP 3.1.1 compliant**
-  **SOTA April 2026 standards**
-  **Fleet Registry synchronization** (glama.json)
-  **Authoritative README documentation**

---

**Built with  for the Windows Orchestration Ecosystem**  
*SOTA v1.18.1 - April 2026*