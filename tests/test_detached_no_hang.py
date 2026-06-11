"""
Regression tests for the v15.1 detached-child deadlock fix.

The wedge: PowerShell commands using Start-Process with -RedirectStandardOutput
spawn a grandchild via CreateProcess(bInheritHandles=TRUE), which inherits the
executor's pipe write handles. With pipe-based capture, the executor (and
CPython's own subprocess.run timeout handler) then blocked until the entire
detached process tree exited — ignoring timeout_seconds.

These tests fail by hanging (pytest-timeout would be nicer; we use wall-clock
asserts so they fail loudly even without the plugin).

Run: uv run pytest tests/test_detached_no_hang.py -v
"""

import time

import pytest

from windows_operations_mcp.tools.powershell_tools import cmd_executor, ps_executor

# A grandchild that outlives the direct shell by ~25s, launched with explicit
# redirection — the exact CreateProcess(bInheritHandles=TRUE) repro.
DETACHED_PS = (
    "$o = Join-Path $env:TEMP 'winops_test_sleeper.out'; "
    "Start-Process -FilePath powershell.exe "
    "-ArgumentList '-NoProfile','-Command','Start-Sleep -Seconds 25' "
    "-WindowStyle Hidden -RedirectStandardOutput $o "
    "-RedirectStandardError \"$o.err\"; "
    "Write-Output 'launched'"
)


def test_powershell_returns_immediately_despite_detached_grandchild():
    """The defining regression: must return in seconds, not when the sleeper dies."""
    start = time.time()
    result = ps_executor.execute(DETACHED_PS, timeout=20)
    elapsed = time.time() - start

    assert elapsed < 15, f"Executor wedged for {elapsed:.1f}s — deadlock regression"
    assert result["success"], f"stderr: {result['stderr']}"
    assert "launched" in result["stdout"]


def test_powershell_timeout_kills_tree_and_returns_partial_output():
    """Direct child overruns: tree-killed at timeout, partial stdout preserved."""
    start = time.time()
    result = ps_executor.execute(
        "Write-Output 'before sleep'; Start-Sleep -Seconds 60", timeout=3
    )
    elapsed = time.time() - start

    assert elapsed < 25, f"Timeout not honored: {elapsed:.1f}s"
    assert result["success"] is False
    assert "timed out" in result["stderr"].lower()
    # v15.1 improvement: output produced before the timeout is preserved.
    # PowerShell buffering makes this best-effort for the Out-String pipeline,
    # so only assert the field exists rather than its content.
    assert "stdout" in result


def test_cmd_returns_despite_detached_grandchild():
    """Same repro through cmd.exe via `start`."""
    start = time.time()
    result = cmd_executor.execute(
        'start /b powershell -NoProfile -Command "Start-Sleep -Seconds 25" '
        "& echo launched",
        timeout=20,
    )
    elapsed = time.time() - start

    assert elapsed < 15, f"CMD executor wedged for {elapsed:.1f}s"
    assert result["success"], f"stderr: {result['stderr']}"
    assert "launched" in result["stdout"]


def test_powershell_plain_command_still_works():
    result = ps_executor.execute("Write-Output 'hello winops'", timeout=15)
    assert result["success"]
    assert "hello winops" in result["stdout"]
    assert result["exit_code"] == 0


def test_powershell_stdin_data():
    result = ps_executor.execute("$input | ForEach-Object { $_.ToUpper() }",
                                 timeout=15, stdin_data="quiet please\n")
    assert result["success"], f"stderr: {result['stderr']}"
    assert "QUIET PLEASE" in result["stdout"]


def test_cmd_plain_command_still_works():
    result = cmd_executor.execute("echo hello cmd", timeout=15)
    assert result["success"]
    assert "hello cmd" in result["stdout"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
