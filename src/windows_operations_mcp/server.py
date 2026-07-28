from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from windows_operations_mcp.mcp_server import mcp, register_all_tools
from windows_operations_mcp.web import setup_webapp

# 1. Initialize tools
register_all_tools()

# 2. HTTP API (SOTA hub) + MCP transport (FastMCP 3.2+ exposes ASGI via http_app())
_mcp_http = mcp.http_app(path="/")
app = FastAPI(lifespan=_mcp_http.lifespan)
setup_webapp(app, mcp)
app.mount("/mcp", _mcp_http)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
