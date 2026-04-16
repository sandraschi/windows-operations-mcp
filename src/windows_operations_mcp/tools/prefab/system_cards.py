"""
Prefab UI Tools - SOTA v14.2.0 (FastMCP 3.2+ / prefab-ui>=0.18.0)

Rich in-chat cards for Windows Operations data.
Requires: uv sync --extra apps
Disable: WINOPS_PREFAB_APPS=0
"""

from typing import Any

from fastmcp import Context
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Text

from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)


async def system_health_card(ctx: Context | None = None) -> Any:
    """
    Display a rich system health card with CPU, memory, and disk IO stats.
    Returns a Prefab UI card in capable MCP hosts; plain text fallback otherwise.
    """
    import psutil

    if ctx:
        ctx.info("Collecting system health for Prefab card...")

    cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
    cpu_avg = sum(cpu_per_core) / len(cpu_per_core) if cpu_per_core else 0.0
    mem = psutil.virtual_memory()
    mem_used_gb = mem.used / (1024**3)
    mem_total_gb = mem.total / (1024**3)
    mem_pct = mem.percent
    disk = psutil.disk_io_counters()
    disk_read_gb = (disk.read_bytes / (1024**3)) if disk else 0.0
    disk_write_gb = (disk.write_bytes / (1024**3)) if disk else 0.0

    summary = (
        f"CPU avg {cpu_avg:.1f}% | "
        f"RAM {mem_used_gb:.1f}/{mem_total_gb:.1f} GB ({mem_pct}%) | "
        f"Disk R:{disk_read_gb:.1f}GB W:{disk_write_gb:.1f}GB"
    )

    with Card(css_class="max-w-lg") as view:
        with CardHeader():
            CardTitle("Goliath — System Health")
        with CardContent():
            Text(f"CPU Average: {cpu_avg:.1f}%")
            Text(f"CPU Cores: {len(cpu_per_core)} ({min(cpu_per_core):.1f}% min / {max(cpu_per_core):.1f}% max)")
            Text(f"RAM: {mem_used_gb:.1f} GB used / {mem_total_gb:.1f} GB total ({mem_pct}%)")
            Text(f"Disk Read: {disk_read_gb:.1f} GB  |  Disk Write: {disk_write_gb:.1f} GB")

    return ToolResult(
        content=summary,
        structured_content=PrefabApp(view=view, title="System Health"),
    )


async def process_list_card(
    name_filter: str | None = None,
    max_processes: int = 20,
    ctx: Context | None = None,
) -> Any:
    """
    Display a rich card listing running processes, optionally filtered by name.
    Returns a Prefab UI card in capable MCP hosts; plain text fallback otherwise.
    """
    import psutil

    if ctx:
        ctx.info(f"Building process list card (filter={name_filter}, max={max_processes})")

    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "username"]):
        try:
            info = p.info
            if name_filter and name_filter.lower() not in (info.get("name") or "").lower():
                continue
            procs.append(info)
            if len(procs) >= max_processes:
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    summary = f"{len(procs)} processes" + (f" matching '{name_filter}'" if name_filter else "")

    with Card(css_class="max-w-xl") as view:
        with CardHeader():
            CardTitle(f"Processes — {summary}")
        with CardContent():
            for p in procs:
                name = p.get("name") or "unknown"
                pid = p.get("pid", "?")
                cpu = p.get("cpu_percent") or 0.0
                mem = p.get("memory_percent") or 0.0
                Text(f"[{pid}] {name}  CPU:{cpu:.1f}%  MEM:{mem:.1f}%")

    return ToolResult(
        content=summary,
        structured_content=PrefabApp(view=view, title="Process List"),
    )
