"""Git version control system tools for the Windows Operations MCP."""

import os
import subprocess
from typing import Any

from windows_operations_mcp.utils import fail_response

from ..decorators import tool
from ..logging_config import get_logger

logger = get_logger(__name__)


def _run_git_command(args: list[str], repo_path: str | None = None) -> dict[str, Any]:
    """Run a git command and return the result."""
    try:
        cwd = repo_path if repo_path else os.getcwd()
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True, timeout=30)
        return {
            "success": True,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.CalledProcessError as e:
        return fail_response(
            message=e.stderr.strip() if e.stderr else str(e),
            stdout=e.stdout.strip() if e.stdout else "",
            stderr=e.stderr.strip() if e.stderr else str(e),
            returncode=e.returncode,
        )
    except Exception as e:
        return fail_response(
            message=f"Git command failed: {e!s}", stdout="", stderr=f"Git command failed: {e!s}", returncode=-1
        )


@tool(
    name="git_add",
    description="Add file contents to the Git staging area",
    parameters={
        "pathspec": {"type": "string", "description": "Path specification for files to add", "default": "."},
        "all": {"type": "boolean", "description": "Add all files", "default": False},
        "force": {"type": "boolean", "description": "Force add files", "default": False},
        "repo_path": {"type": "string", "description": "Path to the git repository (optional)"},
    },
    required=[],
    returns={
        "type": "object",
        "properties": {"status": {"type": "string"}, "message": {"type": "string"}, "pathspec": {"type": "string"}},
    },
)
def git_add(
    pathspec: str = ".", all: bool = False, force: bool = False, repo_path: str | None = None
) -> dict[str, Any]:
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


@tool(
    name="git_commit",
    description="Record changes to the repository",
    parameters={
        "message": {"type": "string", "description": "Commit message"},
        "all": {"type": "boolean", "description": "Stage all changes before committing", "default": False},
        "amend": {"type": "boolean", "description": "Amend the previous commit", "default": False},
        "repo_path": {"type": "string", "description": "Path to the git repository (optional)"},
    },
    required=["message"],
    returns={
        "type": "object",
        "properties": {"status": {"type": "string"}, "message": {"type": "string"}, "commit_hash": {"type": "string"}},
    },
)
def git_commit(message: str, all: bool = False, amend: bool = False, repo_path: str | None = None) -> dict[str, Any]:
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


@tool(
    name="git_push",
    description="Update remote refs along with associated objects",
    parameters={
        "remote": {"type": "string", "description": "Remote repository name", "default": "origin"},
        "branch": {"type": "string", "description": "Branch to push"},
        "force": {"type": "boolean", "description": "Force push", "default": False},
        "set_upstream": {"type": "boolean", "description": "Set upstream branch", "default": False},
        "repo_path": {"type": "string", "description": "Path to the git repository (optional)"},
    },
    required=["remote"],
    returns={"type": "object", "properties": {"status": {"type": "string"}, "message": {"type": "string"}}},
)
def git_push(
    remote: str = "origin",
    branch: str | None = None,
    force: bool = False,
    set_upstream: bool = False,
    repo_path: str | None = None,
) -> dict[str, Any]:
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


@tool(
    name="git_status",
    description="Show the working tree status",
    parameters={"repo_path": {"type": "string", "description": "Path to the git repository (optional)"}},
    required=[],
    returns={
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "changes": {"type": "array", "items": {"type": "string"}},
            "change_count": {"type": "integer"},
            "message": {"type": "string"},
        },
    },
)
def git_status(repo_path: str | None = None) -> dict[str, Any]:
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
            "message": "Repository status retrieved successfully",
        }
    else:
        logger.error(f"Git status failed: {result['stderr']}")
        return {"status": "error", "message": result["stderr"]}


def register_git_tools(mcp):
    """Register Git tools with FastMCP."""
    mcp.tool(git_add)
    mcp.tool(git_commit)
    mcp.tool(git_push)
    mcp.tool(git_status)

    logger.info("git_tools_registered", tools=["git_add", "git_commit", "git_push", "git_status"])
