import shutil
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def file_operations(
    action: Literal["read", "write", "delete", "move", "copy", "list", "info", "exists"],
    path: str,
    content: Optional[str] = None,
    destination: Optional[str] = None,
    overwrite: bool = False,
    encoding: str = "utf-8",
    create_dirs: bool = False,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform core file operations with comprehensive error handling and agentic telemetry.

    RATIONALE:
    Consolidates reading, writing, moving, copying, and deleting into a single portmanteau.
    Integrates with FastMCP 3.2 Context for real-time progress reporting and LLM-in-the-loop diagnostics.

    Args:
        action: The file operation to perform.
        path: Target file or directory path.
        content: Text content to write (for "write" action).
        destination: Destination path (for "move" and "copy" actions).
        overwrite: Allow overwriting existing files (default: False).
        encoding: Text encoding for read/write (default: "utf-8").
        create_dirs: Automatically create parent directories (default: False).
        ctx: FastMCP Context for telemetry and sampling (injected).

    Examples:
        - file_operations(action="read", path="C:/temp/config.json")
        - file_operations(action="write", path="notes.txt", content="SOTA 2026", create_dirs=True)
    """
    if ctx:
        ctx.info(f"FileSystem Op: {action} on {path}")
        ctx.report_progress(10, 100)

    try:
        path_obj = Path(path).resolve()
        
        if action == "read":
            if not path_obj.is_file():
                return {"success": False, "error": f"Path is not a file: {path}"}
            
            if ctx: ctx.report_progress(50, 100)
            content_str = path_obj.read_text(encoding=encoding)
            return {
                "success": True, 
                "action": action, 
                "data": {"content": content_str, "size": len(content_str)}
            }

        elif action == "write":
            if content is None:
                return {"success": False, "error": "Content required for write"}
            
            if path_obj.exists() and not overwrite:
                return {"success": False, "error": "File exists and overwrite is False"}
            
            if create_dirs:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            if ctx: ctx.report_progress(50, 100)
            path_obj.write_text(content, encoding=encoding)
            return {"success": True, "action": action, "data": {"path": str(path_obj), "bytes": len(content)}}

        elif action == "delete":
            if not path_obj.exists():
                return {"success": False, "error": "Path does not exist"}
            
            if ctx: ctx.report_progress(50, 100)
            if path_obj.is_file():
                path_obj.unlink()
            else:
                shutil.rmtree(path_obj)
            return {"success": True, "action": action, "data": {"deleted": str(path_obj)}}

        elif action == "move":
            if not destination:
                return {"success": False, "error": "Destination required for move"}
            dest_obj = Path(destination).resolve()
            if dest_obj.exists() and not overwrite:
                 return {"success": False, "error": "Destination exists and overwrite is False"}
            
            if ctx: ctx.report_progress(50, 100)
            shutil.move(str(path_obj), str(dest_obj))
            return {"success": True, "action": action, "data": {"from": str(path_obj), "to": str(dest_obj)}}

        elif action == "copy":
            if not destination:
                return {"success": False, "error": "Destination required for copy"}
            dest_obj = Path(destination).resolve()
            if dest_obj.exists() and not overwrite:
                 return {"success": False, "error": "Destination exists and overwrite is False"}
            
            if ctx: ctx.report_progress(50, 100)
            if path_obj.is_dir():
                shutil.copytree(str(path_obj), str(dest_obj), dirs_exist_ok=overwrite)
            else:
                shutil.copy2(str(path_obj), str(dest_obj))
            return {"success": True, "action": action, "data": {"copied_to": str(dest_obj)}}

        elif action == "list":
            if not path_obj.is_dir():
                return {"success": False, "error": f"Path is not a directory: {path}"}
            
            if ctx: ctx.report_progress(50, 100)
            items = []
            for item in path_obj.iterdir():
                items.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else 0
                })
            return {"success": True, "action": action, "data": {"items": items, "count": len(items)}}

        elif action == "info":
            if not path_obj.exists():
                return {"success": False, "error": "Path does not exist"}
            stat = path_obj.stat()
            return {
                "success": True,
                "action": action,
                "data": {
                    "name": path_obj.name,
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "is_dir": path_obj.is_dir()
                }
            }

        elif action == "exists":
            return {
                "success": True,
                "action": action,
                "data": {"exists": path_obj.exists(), "path": str(path_obj)}
            }

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"FileSystem Error: {e}"
        if ctx: 
            ctx.error(error_msg)
            # Sampling logic for FileSystem errors
            try:
                advice = await ctx.sample(f"FileSystem operation '{action}' failed on '{path}'. Error: {e}. Provide a brief fix.", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except Exception:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx: ctx.report_progress(100, 100)

def register_file_operations(mcp) -> None:
    """Register the modernized file operations tool."""
    mcp.tool()(file_operations)