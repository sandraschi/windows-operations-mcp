from fastapi import FastAPI
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from windows_operations_mcp.mcp_server import mcp, register_all_tools
from windows_operations_mcp.web import setup_webapp


def create_bridge_app(mcp_app: FastMCP) -> FastAPI:
    """Build the FastAPI bridge: REST /api/*, /health, and MCP streamable HTTP at /mcp.

    Shared by the uvicorn entry point (server.py) and the transport http mode, so
    both launch paths serve the same surface with the fleet CORS standard applied.
    """
    # 1. HTTP API (SOTA hub) + MCP transport (FastMCP 3.2+ exposes ASGI via http_app())
    _mcp_http = mcp_app.http_app(path="/")
    web_app = FastAPI(lifespan=_mcp_http.lifespan)
    setup_webapp(web_app, mcp_app)
    web_app.mount("/mcp", _mcp_http)

    # Fleet CORS standard — unconditional allow_origin_regex covering Tailscale,
    # LAN IPs, Tailscale CGNAT, localhost, and Tauri webview origins.
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:10749",
            "http://127.0.0.1:10749",
            "http://tauri.localhost",
            "https://tauri.localhost",
            "tauri://localhost",
        ],
        allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return web_app


# 1. Initialize tools (idempotent — safe to import from multiple paths)
register_all_tools()

# 2. Build the bridge
app = create_bridge_app(mcp)
