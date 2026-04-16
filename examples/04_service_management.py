#!/usr/bin/env python3
"""
Example 4: Windows Service Management

This example demonstrates how to manage Windows services
using the Windows Operations MCP tools.

Note: This script requires administrator privileges for some operations.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from windows_operations_mcp.tools.windows_services import (
    get_service_status,
    list_windows_services,
)


def main():
    """Demonstrate Windows service management capabilities."""

    print("=" * 60)
    print("Windows Operations MCP - Service Management Example")
    print("=" * 60)
    print()

    # 1. List all running services
    print("1. List Running Services (First 10)")
    print("-" * 60)

    result = list_windows_services(status_filter="running", max_results=10)

    if result.get("success"):
        services = result.get("services", [])
        print(f"Found {len(services)} running services:")
        for service in services:
            print(f"  • {service.get('name')} - {service.get('display_name')}")
            print(f"    Status: {service.get('status')} | Start Type: {service.get('start_type')}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    print()

    # 2. Search for specific services
    print("2. Search for Windows Update Service")
    print("-" * 60)

    result = list_windows_services(name_filter="wuauserv")

    if result.get("success"):
        services = result.get("services", [])
        if services:
            service = services[0]
            print("✅ Found service:")
            print(f"   Name: {service.get('name')}")
            print(f"   Display Name: {service.get('display_name')}")
            print(f"   Status: {service.get('status')}")
            print(f"   Start Type: {service.get('start_type')}")
            print(f"   Description: {service.get('description', 'N/A')[:100]}...")
        else:
            print("Service not found")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    print()

    # 3. Get detailed service status
    print("3. Get Detailed Service Status (Spooler)")
    print("-" * 60)

    result = get_service_status(service_name="Spooler")

    if result.get("success"):
        service = result.get("service", {})
        print("✅ Service Status:")
        print(f"   Name: {service.get('name')}")
        print(f"   Display Name: {service.get('display_name')}")
        print(f"   Status: {service.get('status')}")
        print(f"   Start Type: {service.get('start_type')}")
        print(f"   Can Pause: {service.get('can_pause_and_continue')}")
        print(f"   Can Stop: {service.get('can_stop')}")
        print(f"   Process ID: {service.get('process_id', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    print()

    # 4. List stopped services
    print("4. List Stopped Services (First 5)")
    print("-" * 60)

    result = list_windows_services(status_filter="stopped", max_results=5)

    if result.get("success"):
        services = result.get("services", [])
        print(f"Found {len(services)} stopped services:")
        for service in services:
            print(f"  • {service.get('display_name')}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    print()

    # 5. Service filtering by start type
    print("5. List Automatic Services (First 10)")
    print("-" * 60)

    result = list_windows_services(start_type_filter="automatic", max_results=10)

    if result.get("success"):
        services = result.get("services", [])
        print(f"Found {len(services)} automatic services:")
        for service in services:
            print(f"  • {service.get('display_name')} [{service.get('status')}]")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    print()
    print("=" * 60)
    print("\n⚠️  Note: Service start/stop/restart requires admin privileges.")
    print("Example commands (run as administrator):")
    print("  • start_windows_service('wuauserv')")
    print("  • stop_windows_service('wuauserv')")
    print("  • restart_windows_service('wuauserv')")
    print("=" * 60)


if __name__ == "__main__":
    main()
