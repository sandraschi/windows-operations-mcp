#!/usr/bin/env python3
"""
Example 1: System Information Query

This example demonstrates how to get comprehensive system information
using the Windows Operations MCP tools.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from windows_operations_mcp.tools.system_tools import (
    get_system_info,
    get_system_health
)


def main():
    """Get and display system information."""
    
    print("=" * 60)
    print("Windows Operations MCP - System Information Example")
    print("=" * 60)
    print()
    
    # Get basic system information
    print("1. Basic System Information")
    print("-" * 60)
    system_info = get_system_info()
    
    if system_info.get("success"):
        info = system_info.get("system_info", {})
        print(f"OS: {info.get('os', 'N/A')}")
        print(f"Platform: {info.get('platform', 'N/A')}")
        print(f"Architecture: {info.get('architecture', 'N/A')}")
        print(f"Hostname: {info.get('hostname', 'N/A')}")
        print(f"Python Version: {info.get('python_version', 'N/A')}")
    else:
        print(f"Error: {system_info.get('error', 'Unknown error')}")
    
    print()
    
    # Get system health
    print("2. System Health Check")
    print("-" * 60)
    health = get_system_health()
    
    if health.get("success"):
        health_data = health.get("health", {})
        print(f"Status: {health_data.get('status', 'N/A')}")
        print(f"CPU Usage: {health_data.get('cpu_percent', 'N/A')}%")
        print(f"Memory Usage: {health_data.get('memory_percent', 'N/A')}%")
        print(f"Disk Usage: {health_data.get('disk_percent', 'N/A')}%")
        print(f"Uptime: {health_data.get('uptime_hours', 'N/A')} hours")
    else:
        print(f"Error: {health.get('error', 'Unknown error')}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()

