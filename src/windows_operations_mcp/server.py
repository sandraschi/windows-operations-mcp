from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from windows_operations_mcp.mcp_server import mcp, register_all_tools
from windows_operations_mcp.web import setup_webapp

# 1. Initialize tools
register_all_tools()

# 2. Create the root FastAPI application
app = FastAPI(title="Windows Operations SOTA")

# 3. Add CORS middleware for the frontend (port 10749 by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Setup custom SOTA web endpoints
setup_webapp(app, mcp)

# 5. Mount the FastMCP server at the root (handling SSE and other MCP routes)
app.mount("/", mcp.http_app())
