"""
Windows Performance Monitoring Tools for Windows Operations MCP.

This module provides comprehensive Windows performance monitoring functionality
including real-time metrics, performance counters, and system resource monitoring.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..logging_config import get_logger
from ..decorators import tool

logger = get_logger(__name__)

@tool(
    name="get_windows_performance_counters",
    description="Get Windows performance counter values",
    parameters={
        "counter_names": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of performance counter names to query"
        },
        "object_name": {
            "type": "string",
            "description": "Performance object name (Processor, Memory, Disk, Network, etc.)",
            "default": "Processor"
        },
        "instance_name": {
            "type": "string",
            "description": "Specific instance name (_Total, 0, etc.)",
            "default": "_Total"
        }
    },
    required=["counter_names"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "counters": {"type": "object"},
            "timestamp": {"type": "string"}
        }
    }
)
def get_windows_performance_counters(
    counter_names: List[str],
    object_name: str = "Processor",
    instance_name: str = "_Total"
) -> Dict[str, Any]:
    """
    Get Windows performance counter values.

    Args:
        counter_names: List of performance counter names to query
        object_name: Performance object name
        instance_name: Specific instance name

    Returns:
        Dictionary with counter values and metadata
    """
    try:
        import win32pdh

        counters = {}
        timestamp = datetime.now().isoformat()

        for counter_name in counter_names:
            try:
                # Build the counter path
                counter_path = f"\\{object_name}({instance_name})\\{counter_name}"

                # Query the counter
                win32pdh.AddCounter(None, counter_path)
                value = win32pdh.GetFormattedCounterValue(None)[1]

                counters[counter_name] = {
                    "value": value,
                    "object": object_name,
                    "instance": instance_name,
                    "counter_path": counter_path
                }

            except Exception as e:
                counters[counter_name] = {
                    "error": str(e),
                    "object": object_name,
                    "instance": instance_name
                }
                logger.warning(f"Failed to get counter {counter_name}: {e}")

        return {
            "success": True,
            "counters": counters,
            "timestamp": timestamp
        }

    except ImportError:
        return {
            "success": False,
            "error": "win32pdh not available. Install with: pip install pywin32"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get performance counters: {str(e)}"
        }

@tool(
    name="monitor_windows_performance",
    description="Monitor Windows performance metrics over time",
    parameters={
        "counter_names": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of performance counter names to monitor"
        },
        "object_name": {
            "type": "string",
            "description": "Performance object name",
            "default": "Processor"
        },
        "instance_name": {
            "type": "string",
            "description": "Specific instance name",
            "default": "_Total"
        },
        "duration_seconds": {
            "type": "integer",
            "description": "How long to monitor (seconds)",
            "default": 60
        },
        "sample_interval": {
            "type": "integer",
            "description": "Sampling interval in seconds",
            "default": 5
        }
    },
    required=["counter_names"],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "samples": {"type": "array"},
            "summary": {"type": "object"},
            "duration": {"type": "number"}
        }
    }
)
def monitor_windows_performance(
    counter_names: List[str],
    object_name: str = "Processor",
    instance_name: str = "_Total",
    duration_seconds: int = 60,
    sample_interval: int = 5
) -> Dict[str, Any]:
    """
    Monitor Windows performance metrics over time.

    Args:
        counter_names: List of performance counter names to monitor
        object_name: Performance object name
        instance_name: Specific instance name
        duration_seconds: How long to monitor
        sample_interval: Sampling interval in seconds

    Returns:
        Dictionary with performance samples and summary statistics
    """
    try:
        import win32pdh

        samples = []
        start_time = time.time()
        next_sample_time = start_time

        while time.time() - start_time < duration_seconds:
            current_time = time.time()

            if current_time >= next_sample_time:
                sample_data = {}

                for counter_name in counter_names:
                    try:
                        counter_path = f"\\{object_name}({instance_name})\\{counter_name}"
                        win32pdh.AddCounter(None, counter_path)
                        value = win32pdh.GetFormattedCounterValue(None)[1]

                        sample_data[counter_name] = value

                    except Exception as e:
                        sample_data[counter_name] = None
                        logger.warning(f"Failed to get counter {counter_name}: {e}")

                samples.append({
                    "timestamp": datetime.now().isoformat(),
                    "values": sample_data
                })

                next_sample_time = current_time + sample_interval

            time.sleep(0.1)  # Small delay to prevent busy waiting

        # Calculate summary statistics
        summary = {}
        for counter_name in counter_names:
            values = [sample["values"].get(counter_name) for sample in samples if sample["values"].get(counter_name) is not None]
            if values:
                summary[counter_name] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "samples": len(values)
                }

        return {
            "success": True,
            "samples": samples,
            "summary": summary,
            "duration": time.time() - start_time
        }

    except ImportError:
        return {
            "success": False,
            "error": "win32pdh not available. Install with: pip install pywin32"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to monitor performance: {str(e)}"
        }

@tool(
    name="get_windows_system_performance",
    description="Get comprehensive Windows system performance metrics",
    parameters={
        "include_cpu": {
            "type": "boolean",
            "description": "Include CPU performance metrics",
            "default": True
        },
        "include_memory": {
            "type": "boolean",
            "description": "Include memory performance metrics",
            "default": True
        },
        "include_disk": {
            "type": "boolean",
            "description": "Include disk performance metrics",
            "default": True
        },
        "include_network": {
            "type": "boolean",
            "description": "Include network performance metrics",
            "default": True
        }
    },
    required=[],
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "performance": {"type": "object"},
            "timestamp": {"type": "string"}
        }
    }
)
def get_windows_system_performance(
    include_cpu: bool = True,
    include_memory: bool = True,
    include_disk: bool = True,
    include_network: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive Windows system performance metrics.

    Args:
        include_cpu: Include CPU performance metrics
        include_memory: Include memory performance metrics
        include_disk: Include disk performance metrics
        include_network: Include network performance metrics

    Returns:
        Dictionary with comprehensive performance data
    """
    try:
        import win32pdh
        import psutil

        performance = {}
        timestamp = datetime.now().isoformat()

        # CPU Performance
        if include_cpu:
            try:
                cpu_counters = [
                    "% Processor Time",
                    "% User Time",
                    "% Privileged Time",
                    "% Interrupt Time"
                ]

                cpu_data = {}
                for counter in cpu_counters:
                    try:
                        counter_path = f"\\Processor(_Total)\\{counter}"
                        win32pdh.AddCounter(None, counter_path)
                        value = win32pdh.GetFormattedCounterValue(None)[1]
                        cpu_data[counter] = value
                    except Exception as e:
                        cpu_data[counter] = None
                        logger.warning(f"Failed to get CPU counter {counter}: {e}")

                performance["cpu"] = cpu_data

            except Exception as e:
                performance["cpu"] = {"error": str(e)}

        # Memory Performance
        if include_memory:
            try:
                memory_counters = [
                    "Available MBytes",
                    "Committed Bytes",
                    "Commit Limit",
                    "Pool Nonpaged Bytes",
                    "Pool Paged Bytes"
                ]

                memory_data = {}
                for counter in memory_counters:
                    try:
                        counter_path = f"\\Memory\\{counter}"
                        win32pdh.AddCounter(None, counter_path)
                        value = win32pdh.GetFormattedCounterValue(None)[1]
                        memory_data[counter] = value
                    except Exception as e:
                        memory_data[counter] = None
                        logger.warning(f"Failed to get memory counter {counter}: {e}")

                performance["memory"] = memory_data

            except Exception as e:
                performance["memory"] = {"error": str(e)}

        # Disk Performance
        if include_disk:
            try:
                # Get disk performance for all physical disks
                disk_counters = [
                    "% Disk Time",
                    "Avg. Disk Queue Length",
                    "Disk Bytes/sec",
                    "Disk Read Bytes/sec",
                    "Disk Write Bytes/sec"
                ]

                disk_data = {}
                for counter in disk_counters:
                    try:
                        counter_path = f"\\PhysicalDisk(_Total)\\{counter}"
                        win32pdh.AddCounter(None, counter_path)
                        value = win32pdh.GetFormattedCounterValue(None)[1]
                        disk_data[counter] = value
                    except Exception as e:
                        disk_data[counter] = None
                        logger.warning(f"Failed to get disk counter {counter}: {e}")

                performance["disk"] = disk_data

            except Exception as e:
                performance["disk"] = {"error": str(e)}

        # Network Performance
        if include_network:
            try:
                # Get network performance for all adapters
                network_counters = [
                    "Bytes Total/sec",
                    "Bytes Received/sec",
                    "Bytes Sent/sec",
                    "Packets/sec",
                    "Packets Received/sec",
                    "Packets Sent/sec"
                ]

                network_data = {}
                for counter in network_counters:
                    try:
                        counter_path = f"\\Network Interface(_Total)\\{counter}"
                        win32pdh.AddCounter(None, counter_path)
                        value = win32pdh.GetFormattedCounterValue(None)[1]
                        network_data[counter] = value
                    except Exception as e:
                        network_data[counter] = None
                        logger.warning(f"Failed to get network counter {counter}: {e}")

                performance["network"] = network_data

            except Exception as e:
                performance["network"] = {"error": str(e)}

        return {
            "success": True,
            "performance": performance,
            "timestamp": timestamp
        }

    except ImportError:
        return {
            "success": False,
            "error": "Required modules not available. Install with: pip install pywin32 psutil"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get system performance: {str(e)}"
        }

def register_windows_performance_tools(mcp):
    """Register Windows performance monitoring tools with FastMCP."""
    # Register the Windows performance tools with MCP
    mcp.tool(get_windows_performance_counters)
    mcp.tool(monitor_windows_performance)
    mcp.tool(get_windows_system_performance)

    logger.info("windows_performance_tools_registered", tools=[
        "get_windows_performance_counters", "monitor_windows_performance",
        "get_windows_system_performance"
    ])
