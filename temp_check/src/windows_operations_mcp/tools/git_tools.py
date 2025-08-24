"""Git version control system tools for the Windows Operations MCP."""
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from ..logging_config import get_logger

logger = get_logger(__name__)

def _run_git_command(args: List[str], repo_path: Optional[str] = None) -> Dict[str, Any]:
    """Run a git command and return the result."""
    try:
        cwd = repo_path if repo_path else os.getcwd()
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        return {
            "success": True,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "stdout": e.stdout.strip() if e.stdout else "",
            "stderr": e.stderr.strip() if e.stderr else str(e),
            "returncode": e.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Git command failed: {str(e)}",
            "returncode": -1
        }

def register_git_tools(mcp):
    """Register Git tools with FastMCP."""
    
    @mcp.tool()
    def git_add(pathspec: str = ".", all: bool = False, force: bool = False, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Add file contents to the Git staging area."""
        args = ["add"]
        if all:
            args.append("--all")
        if force:
            args.append("--force")
        args.append(pathspec)
        
        result = _run_git_command(args, repo_path)
        if result["success"]:
            logger.info(f"Git add successful: {pathspec}")
            return {"status": "success", "message": "Files added successfully", "pathspec": pathspec}
        else:
            logger.error(f"Git add failed: {result['stderr']}")
            return {"status": "error", "message": result["stderr"]}

    @mcp.tool()
    def git_commit(message: str, all: bool = False, amend: bool = False, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Record changes to the repository."""
        args = ["commit", "-m", message]
        if all:
            args.append("-a")
        if amend:
            args.append("--amend")
            
        result = _run_git_command(args, repo_path)
        if result["success"]:
            logger.info(f"Git commit successful: {message}")
            return {"status": "success", "message": result["stdout"] or "Commit created successfully"}
        else:
            logger.error(f"Git commit failed: {result['stderr']}")
            return {"status": "error", "message": result["stderr"]}

    @mcp.tool()
    def git_push(remote: str = "origin", branch: Optional[str] = None, 
                force: bool = False, set_upstream: bool = False, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Update remote refs along with associated objects."""
        args = ["push"]
        if force:
            args.append("--force")
        if set_upstream:
            args.append("--set-upstream")
        
        args.append(remote)
        if branch:
            args.append(branch)
            
        result = _run_git_command(args, repo_path)
        if result["success"]:
            logger.info(f"Git push successful to {remote}")
            return {"status": "success", "message": result["stdout"] or "Push successful"}
        else:
            logger.error(f"Git push failed: {result['stderr']}")
            return {"status": "error", "message": result["stderr"]}

    @mcp.tool()
    def git_status(repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Show the working tree status."""
        result = _run_git_command(["status", "--porcelain"], repo_path)
        if result["success"]:
            changes = result["stdout"].split("\n") if result["stdout"] else []
            changes = [line for line in changes if line.strip()]
            logger.info(f"Git status retrieved: {len(changes)} changes")
            return {
                "status": "success",
                "changes": changes,
                "change_count": len(changes),
                "message": "Repository status retrieved successfully"
            }
        else:
            logger.error(f"Git status failed: {result['stderr']}")
            return {"status": "error", "message": result["stderr"]}
    
    logger.info("git_tools_registered", tools=["git_add", "git_commit", "git_push", "git_status"])
