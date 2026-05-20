"""
Container Execution - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_container":
  winops_container/exec  - Execute a command inside a Docker container
  winops_container/cp    - Copy files between host and container

Solves the bug report's core workflow gap: reliable Docker exec with stdin support
and proper quoting on Windows. Uses subprocess directly (not CMD/PowerShell wrapper)
to avoid the nested-quoting and list2cmdline issues documented in winops_stdout_bug_report.md.
"""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def _docker(args: list[str], cwd: str | None = None, timeout: int = 60, stdin_data: str | None = None) -> dict[str, Any]:
    """Run a docker command via subprocess with reliable output capture."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "docker", *args,
            cwd=cwd,
            stdin=asyncio.subprocess.PIPE if stdin_data else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(input=stdin_data.encode() if stdin_data else None),
            timeout=timeout,
        )
        stdout = stdout_bytes.decode(errors="replace") if stdout_bytes else ""
        stderr = stderr_bytes.decode(errors="replace") if stderr_bytes else ""
        return {
            "success": proc.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": proc.returncode,
        }
    except asyncio.TimeoutError:
        if proc:
            proc.kill()
        return {"success": False, "stdout": "", "stderr": f"Command timed out after {timeout}s", "exit_code": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": "Docker CLI not found. Install Docker Desktop or add docker to PATH.", "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}


def register_container_execution(parent_mcp: FastMCP) -> None:
    """Mount atomic container execution tools under namespace 'winops_container'."""
    ns = FastMCP(name="winops_container")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def exec(
        container: Annotated[str, Field(description="Container name or ID.")],
        command: Annotated[str, Field(description="Command to execute inside the container.")],
        workdir: Annotated[str | None, Field(description="Working directory inside the container.")] = None,
        user: Annotated[str | None, Field(description="User to run as (e.g. 'root').")] = None,
        stdin_data: Annotated[str | None, Field(description="Text to pipe to stdin of the command.")] = None,
        timeout_seconds: Annotated[int, Field(description="Hard timeout 1-300s.", ge=1, le=300)] = 60,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Execute a command inside a Docker container.

        Uses subprocess directly (not CMD/PowerShell wrapper) to avoid nested-quoting
        issues and list2cmdline mangling. stdin_data is piped directly to the container
        command — no need for `docker cp` + exec dance.

        ## Return Format
        ```json
        {"success": bool, "stdout": str, "stderr": str, "exit_code": int}
        ```

        ## Examples
            exec(container="postgres", command="psql -U user -d db -c 'SELECT 1'")
            exec(container="python-app", command="python /tmp/run.py", stdin_data="input data")
            exec(container="nginx", command="nginx -t", timeout_seconds=10)
        """
        if not command:
            return {"success": False, "error": "command must be non-empty"}

        if ctx:
            await ctx.info(f"Docker exec in {container}: {command[:80]}")
            await ctx.report_progress(10, 100)

        args = ["exec", "-i"]
        if user:
            args.extend(["--user", user])
        if workdir:
            args.extend(["--workdir", workdir])
        args.append(container)
        args.extend(["sh", "-c", command])

        result = await _docker(args, timeout=timeout_seconds, stdin_data=stdin_data)

        if ctx:
            await ctx.report_progress(100, 100)

        return {
            "success": result["success"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "exit_code": result["exit_code"],
        }

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    async def cp(
        container: Annotated[str, Field(description="Container name or ID.")],
        source: Annotated[str, Field(description="Source path. Format: 'host:/path/file' or 'container:/path/file' (prefix determines direction).")],
        destination: Annotated[str, Field(description="Destination path. Format: 'host:/path/' or 'container:/path/'.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Copy files between the host and a Docker container.

        Direction is determined by the source prefix:
        - `source="container:/tmp/data.json", destination="host:./out/"` copies FROM container TO host
        - `source="host:./script.py", destination="container:/tmp/"` copies FROM host TO container

        ## Return Format
        ```json
        {"success": bool, "source": str, "destination": str}
        ```

        ## Examples
            cp(container="app", source="host:./script.py", destination="container:/tmp/")
            cp(container="db", source="container:/tmp/result.csv", destination="host:./output/")
        """
        try:
            src_is_container = source.startswith("container:")
            src_path = source.split(":", 1)[1].lstrip("/")

            dst_is_container = destination.startswith("container:")
            dst_path = destination.split(":", 1)[1].lstrip("/")

            if src_is_container and not dst_is_container:
                args = ["cp", f"{container}:{src_path}", dst_path]
            elif not src_is_container and dst_is_container:
                args = ["cp", src_path, f"{container}:{dst_path}"]
            else:
                return {"success": False, "error": "Exactly one of source/destination must have the 'container:' prefix.",
                        "suggestions": ["Use 'container:/path' for Docker paths and 'host:/path' for local paths.",
                                        "Example: source='host:./file.txt', destination='container:/tmp/file.txt'"]}

            if ctx:
                await ctx.info(f"Docker cp {' '.join(args)}")

            result = await _docker(args, timeout=30)
            return {
                "success": result["success"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    parent_mcp.mount(ns, prefix="winops_container")
    logger.info("Mounted atomic tools: winops_container/exec, winops_container/cp")
