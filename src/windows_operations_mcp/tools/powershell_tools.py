"""
PowerShell and CMD execution tools for Windows Operations MCP.
v15.3 - SAFETY GUARDS + detached-child deadlock fix

SAFETY (June 2026, v15.3):
  - Linux-ism regex guard: blocks grep, tail, rm -rf, chmod,
    sudo, apt, brew, /bin/sh, export VAR= etc. before execution.
  - Em dash (U+2014) block: corrupts PowerShell parser pipeline.
  - Both apply at the executor entry point, before any subprocess call.

DETACHED-CHILD DEADLOCK FIX (v15.1) — "the Start-Process wedge":
  Commands that launched background/detached processes (Start-Process,
  `start /b`, dev servers, NSSM, etc.) wedged the tool until the *entire
  detached process tree* exited, ignoring timeout_seconds entirely.

  Root cause (two layers):
  1. With stdout/stderr captured via pipes, the pipe WRITE handles are
     inheritable. When the shell spawns a grandchild with redirection
     (PowerShell's Start-Process -RedirectStandardOutput uses CreateProcess
     with bInheritHandles=TRUE), the grandchild inherits copies of our pipe
     write handles — even though its own std handles point elsewhere. The
     read side then never sees EOF until every handle holder exits.
  2. CPython's subprocess.run timeout handler makes this fatal on Windows:
     on TimeoutExpired it calls `process.communicate()` with NO timeout to
     collect residual output (CPython subprocess.py, `if _mswindows:` branch).
     That join blocks on the reader threads' fh.read() until EOF — i.e. until
     the detached grandchild dies. `timeout=` is therefore not honored.

  Fix: capture stdout/stderr into TEMP FILES instead of pipes. There is no
  EOF dependency: we wait on the DIRECT child only (process.wait(timeout) —
  no reader threads), then read the files. Detached grandchildren can hold
  inherited file handles forever without blocking us. On a genuine timeout
  of the direct child we kill the process tree (taskkill /T /F) and still
  return whatever partial output reached the files — an improvement over
  the old behavior, which returned empty output on timeout.

  Semantics note: output a detached grandchild writes AFTER the direct shell
  exits is intentionally not captured — redirect such processes to their own
  log files (which is what callers launching servers do anyway).

RETAINED from v15.0:
1. PowerShell: Forces UTF-8 encoding setup before every command
   ([Console]::OutputEncoding + $OutputEncoding)
2. PowerShell: Uses -OutputFormat Text for text-mode output
3. PowerShell: Appends | Out-String -Width 4096 to capture native exe output
   (docker, psql, etc. — PowerShell 5.1 silently drops their stdout otherwise)
4. PowerShell/Cmd: stdin_data parameter for piping input
5. CMD: shell=True with raw command string to prevent list2cmdline
   quote-mangling (fixes nested quoting with docker exec ... sh -c "...")
6. Both: utf-8 encoding consistently instead of brittle console CP detection
"""

import asyncio
import os
import re
import subprocess
import tempfile
import time
from typing import Any

from ..logging_config import get_logger
from ..utils import fail_response

logger = get_logger(__name__)

_TREE_KILL_TIMEOUT = 10  # seconds to allow taskkill /T /F to do its work

# Linux/bash patterns that have zero valid PowerShell/CMD usage.
# Agents trained on Unix frequently emit these into winops tools.
# Each is a full-word regex anchored to catch the command, not a substring.
_LINUX_PATTERNS: list[re.Pattern] = [
    re.compile(r) for r in [
        r"\bgrep\b",
        r"\btail\b",
        r"\brm\s+-[rf]\b",
        r"\bchmod\b",
        r"\bchown\b",
        r"\bsudo\b",
        r"\bapt(?:-get)?(?:\s+install)?\b",
        r"\byum\b",
        r"\bbrew(?:\s+install)?\b",
        r"\bpacman\b",
        r"#!/",
        r"/bin/(?:bash|sh|python)",
        r"\bexport\s+\w+=",
    ]
]

# Claude Desktop's Electron -> uv -> python launch chain can mutilate PATHEXT
# (observed: PATHEXT=".CPL" on Goliath, 2026-06-11). Without ".EXE" in PATHEXT,
# PowerShell refuses to execute exes ("Cannot run a document in the middle of a
# pipeline") and cmd builtins like `cmd` itself become "not recognized".
_DEFAULT_PATHEXT = ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC"


def _sanitized_env() -> dict[str, str]:
    """Copy of os.environ with PATHEXT normalized if it is missing or broken."""
    env = dict(os.environ)
    pathext = env.get("PATHEXT", "")
    if ".EXE" not in pathext.upper():
        logger.warning(f"Inherited PATHEXT is broken ({pathext!r}); normalizing")
        env["PATHEXT"] = _DEFAULT_PATHEXT
    return env


def _validate_command_safe(command: str) -> str | None:
    """Check command for Linux-isms and em dashes. Returns error message or None."""
    if not command:
        return None
    if "\u2014" in command:
        return (
            "Command contains em dash (U+2014) which corrupts PowerShell parsing. "
            "Use ASCII \"--\" instead."
        )
    for pat in _LINUX_PATTERNS:
        m = pat.search(command)
        if m:
            return (
                f"Command contains Linux-ism '{m.group()}' — "
                "use the native PowerShell equivalent "
                "(see mcp-central-docs/standards/powershell_sota.md)"
            )
    return None


def _kill_process_tree(pid: int) -> None:
    """Kill a process and all its descendants (Windows)."""
    try:
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(pid)],
            capture_output=True,
            timeout=_TREE_KILL_TIMEOUT,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except Exception as e:
        logger.warning(f"taskkill tree-kill failed for pid {pid}: {e}")


def _read_and_cleanup(path: str) -> str:
    """Read a capture file; best-effort delete (a live grandchild may hold it)."""
    data = ""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            data = fh.read()
    except OSError as e:
        logger.warning(f"Could not read capture file {path}: {e}")
    try:
        os.unlink(path)
    except OSError:
        pass  # inherited handle still open; temp dir cleanup will get it
    return data


def _run_with_file_capture(
    args: list[str] | str,
    *,
    shell: bool,
    cwd: str | None,
    timeout: int,
    stdin_data: str | None,
) -> dict[str, Any]:
    """
    Execute a command with stdout/stderr captured to temp files.

    Deadlock-proof against detached grandchildren holding inherited handles:
    we only ever wait on the direct child, never on pipe EOF.
    """
    start_time = time.time()

    out_fd, out_path = tempfile.mkstemp(prefix="winops_cap_", suffix=".out")
    err_fd, err_path = tempfile.mkstemp(prefix="winops_cap_", suffix=".err")
    timed_out = False

    try:
        with os.fdopen(out_fd, "wb") as out_fh, os.fdopen(err_fd, "wb") as err_fh:
            process = subprocess.Popen(
                args,
                cwd=cwd,
                shell=shell,
                stdout=out_fh,
                stderr=err_fh,
                stdin=subprocess.PIPE if stdin_data is not None else subprocess.DEVNULL,
                env=_sanitized_env(),
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            if stdin_data is not None:
                try:
                    process.stdin.write(stdin_data.encode("utf-8", errors="replace"))
                    process.stdin.close()
                except OSError as e:
                    logger.warning(f"stdin write failed (process exited early?): {e}")

            try:
                exit_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                logger.error(f"Direct child (pid {process.pid}) exceeded {timeout}s; killing tree")
                _kill_process_tree(process.pid)
                try:
                    exit_code = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    exit_code = -1

        # Write handles are closed here; read whatever reached the files.
        stdout = _read_and_cleanup(out_path)
        stderr = _read_and_cleanup(err_path)
        execution_time = time.time() - start_time

        if timed_out:
            timeout_msg = f"Command timed out after {timeout} seconds (process tree killed)"
            stderr = f"{stderr}\n{timeout_msg}" if stderr else timeout_msg
            return fail_response(
                timeout_msg,
                stdout=stdout,
                stderr=stderr,
                exit_code=-1,
                execution_time=execution_time,
                next_steps="Increase timeout_seconds or simplify the command",
            )

        success = exit_code == 0
        return {
            "success": success,
            "message": "Command completed successfully" if success else f"Command failed with exit code {exit_code}",
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "execution_time": execution_time,
            "next_steps": [] if success else "Check stderr for error details",
        }

    except Exception as e:
        # Ensure capture files don't accumulate on unexpected errors
        for p in (out_path, err_path):
            try:
                os.unlink(p)
            except OSError:
                pass
        execution_time = time.time() - start_time
        logger.error(f"Execution error: {e}")
        return fail_response(
            f"Execution error: {e!s}",
            stdout="",
            stderr=f"Execution error: {e!s}",
            exit_code=-1,
            execution_time=execution_time,
            next_steps="Verify the command is valid PowerShell/CMD syntax",
        )


class CMDExecutor:
    """
    CMD execution with safety guards, reliable output capture and proper quoting.

    v15.4: `& {{ ... }}` scriptblock wrap (statement-final commands no longer break the pipe).
    v15.3: safety guards (Linux-ism regex + em dash block).
    v15.1: file-based capture (detached-child deadlock fix). See module docstring.
    v15.0: shell=True prevents list2cmdline from mangling nested quotes;
           stdin_data support; utf-8 throughout.
    """

    def __init__(self):
        logger.info("CMD executor initialized (v15.3 — safety guards, file-capture, tree-kill)")

    def execute(
        self,
        command: str,
        working_directory: str | None = None,
        timeout: int = 30,
        stdin_data: str | None = None,
    ) -> dict[str, Any]:
        """Execute CMD command with reliable, deadlock-proof output capture."""
        err = _validate_command_safe(command)
        if err:
            return fail_response(
                f"SAFETY GUARD: {err}",
                stdout="",
                stderr=err,
                exit_code=-1,
                execution_time=0,
                next_steps="Replace the blocked pattern with the native Windows equivalent (see mcp-central-docs/standards/powershell_sota.md)",
            )
        # shell=True passes the raw string as "COMSPEC /c <command>", preserving
        # nested quoting like: docker exec container sh -c "python -c '...'"
        return _run_with_file_capture(  # noqa: S604 - preserves nested quoting for docker exec etc.
            command,
            shell=True,
            cwd=working_directory or os.getcwd(),
            timeout=timeout,
            stdin_data=stdin_data,
        )


class PowerShellExecutor:
    """
    PowerShell execution with safety guards and guaranteed native exe output capture.

    v15.3: safety guards (Linux-ism regex + em dash block).
    v15.1: file-based capture (detached-child deadlock fix). See module docstring.
    v15.0: UTF-8 encoding setup, -OutputFormat Text, | Out-String -Width 4096
           (PowerShell 5.1 silently drops native exe stdout otherwise).
    """

    def __init__(self):
        logger.info("PowerShell executor initialized (v15.4 — scriptblock wrap, safety guards, file-capture, tree-kill)")

    def _build_command(self, command: str) -> str:
        """Wrap command with encoding setup and output-forcing pipeline.

        The | Out-String -Width 4096 suffix is critical for PowerShell 5.1:
        without it, native executables (docker, psql, etc.) have their stdout
        silently dropped when PowerShell writes to a redirected handle.

        v15.4: the user command is wrapped in `& { ... }` before piping.
        Piping directly off the raw command is a parser error when the command
        ends in a statement (if/foreach/try block, assignment, trailing `}`):
        'An empty pipe element is not allowed'. Scriptblock invocation turns
        any statement sequence into a single legal pipeline element and pipes
        the output of ALL statements through Out-String, not just the last one.
        """
        setup = (
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "$OutputEncoding = [System.Text.Encoding]::UTF8"
        )
        return f"{setup}; & {{ {command}\n }} | Out-String -Width 4096"

    def execute(
        self,
        command: str,
        working_dir: str | None = None,
        timeout: int = 60,
        stdin_data: str | None = None,
    ) -> dict[str, Any]:
        """Execute PowerShell command with reliable, deadlock-proof output capture.

        Args:
            command: PowerShell command to execute
            working_dir: Working directory (optional)
            timeout: Hard timeout for the DIRECT child process in seconds.
                Detached grandchildren (Start-Process etc.) do not extend it.
            stdin_data: Optional data to pipe to stdin

        Returns:
            dict with success, stdout, stderr, exit_code, execution_time
        """
        err = _validate_command_safe(command)
        if err:
            return fail_response(
                f"SAFETY GUARD: {err}",
                stdout="",
                stderr=err,
                exit_code=-1,
                execution_time=0,
                next_steps="Replace the blocked pattern with the native PowerShell equivalent (see mcp-central-docs/standards/powershell_sota.md)",
            )
        full_command = self._build_command(command)
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-OutputFormat",
            "Text",
            "-Command",
            full_command,
        ]
        logger.debug(f"Executing PowerShell: {command[:100]}...")
        return _run_with_file_capture(
            cmd,
            shell=False,
            cwd=working_dir,
            timeout=timeout,
            stdin_data=stdin_data,
        )


# Module-level executor instances for import by portmanteau command_execution
ps_executor = PowerShellExecutor()
cmd_executor = CMDExecutor()


def register_powershell_tools(mcp):
    """Register PowerShell and CMD execution tools with FastMCP."""
    @mcp.tool()
    async def run_powershell_tool(
        command: str,
        working_directory: str | None = None,
        timeout_seconds: int = 60,
        max_output_size: int = 10000,
        stdin_data: str | None = None,
    ) -> dict[str, Any]:
        """Execute PowerShell command with reliable output capture."""
        return await asyncio.to_thread(
            ps_executor.execute,
            command=command,
            working_dir=working_directory,
            timeout=timeout_seconds,
            stdin_data=stdin_data,
        )

    @mcp.tool()
    async def run_cmd_tool(
        command: str,
        working_directory: str | None = None,
        timeout_seconds: int = 30,
        max_output_size: int = 10000,
        stdin_data: str | None = None,
    ) -> dict[str, Any]:
        """Execute CMD command with reliable output capture."""
        return await asyncio.to_thread(
            cmd_executor.execute,
            command=command,
            working_directory=working_directory,
            timeout=timeout_seconds,
            stdin_data=stdin_data,
        )

    logger.info("PowerShell and CMD tools registered successfully")
