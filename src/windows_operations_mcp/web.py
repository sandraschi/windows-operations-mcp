import psutil
import platform
from fastapi import FastAPI, Body, Depends, HTTPException
from fastmcp import FastMCP
from .ai import AIRouter

async def authenticate():
    """Simple standard authentication dependency placeholder."""
    return "sandra"

def setup_webapp(app: FastAPI, mcp_app: FastMCP):
    """Setup standard SOTA web endpoints for Windows Operations Hub."""
    ai_router = AIRouter(mcp_app)

    @app.get("/api/health")
    async def health_check():
        """Standard SOTA health check."""
        return {
            "status": "healthy",
            "service": "windows-operations-mcp",
            "version": "2.0.0",
            "platform": platform.system()
        }

    @app.get("/api/status")
    async def get_status(user: str = Depends(authenticate)):
        return {
            "status": "connected",
            "user": user,
            "mcp": mcp_app.name,
            "platform": platform.system(),
            "release": platform.release(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total
        }

    @app.get("/api/system-stats")
    async def get_system_stats(user: str = Depends(authenticate)):
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage("C:\\")._asdict(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/processes")
    async def get_processes(user: str = Depends(authenticate)):
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                # Some processes might terminate during iteration
                info = p.info
                if info["cpu_percent"] is None:
                    info["cpu_percent"] = 0.0
                if info["memory_percent"] is None:
                    info["memory_percent"] = 0.0
                procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by CPU usage and take top 10
        sorted_procs = sorted(procs, key=lambda x: x["cpu_percent"], reverse=True)[:10]
        return {"processes": sorted_procs}

    @app.get("/api/tools")
    async def list_tools(_user: str = Depends(authenticate)):
        tools = await ai_router.get_tools_list()
        return {"tools": tools}

    @app.get("/api/workflows")
    async def list_workflows(_user: str = Depends(authenticate)):
        workflows = await ai_router.get_workflows_list()
        return {"workflows": workflows}

    @app.post("/api/chat")
    async def chat(
        query: str = Body(..., embed=True), user: str = Depends(authenticate)
    ):
        try:
            response = await ai_router.process_command(query)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
