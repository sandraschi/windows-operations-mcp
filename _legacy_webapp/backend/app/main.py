from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
import platform
import datetime

# Import the MCP server instance
# We assume the user runs this from the repo root or installed package
try:
    # Add source to path for dev environment
    import sys
    import os

    # Assuming running from webapp/backend/app or webapp/backend
    # We need to reach src
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.abspath(os.path.join(current_dir, "../../../src"))
    if src_path not in sys.path:
        sys.path.append(src_path)

    from windows_operations_mcp.mcp_server import mcp, register_all_tools

    # Initialize the MCP instance with tools
    register_all_tools()
except ImportError:
    # Fallback/Mock if running effectively isolated
    mcp = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tools")
async def list_tools():
    if not mcp:
        return {"tools": [], "error": "MCP Server not found in python path"}

    tools_data = []

    # FastMCP 2.14+ stores tools in _tool_manager._tools
    try:
        # Check for _tool_manager
        if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools"):
            for tool in mcp._tool_manager._tools.values():
                tools_data.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.parameters,
                    }
                )
        # Fallback to _tools (older versions)
        elif hasattr(mcp, "_tools"):
            for tool_name, tool_func in mcp._tools.items():
                tools_data.append(
                    {
                        "name": tool_name,
                        "description": tool_func.__doc__ or "",
                        "inputSchema": {},  # Placeholder
                    }
                )
        else:
            return {"tools": [], "error": "Could not inspect tools on MCP instance"}

    except Exception as e:
        return {"tools": [], "error": str(e)}

    return {"tools": tools_data}


@app.get("/api/system-stats")
def get_system_stats():
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("C:\\")._asdict(),
        "platform": platform.system(),
        "release": platform.release(),
    }


@app.get("/api/processes")
def get_processes():
    # Return top 10 CPU consuming processes
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sort by CPU usage
    sorted_procs = sorted(procs, key=lambda x: x["cpu_percent"] or 0, reverse=True)[:10]
    return {"processes": sorted_procs}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=10752)
