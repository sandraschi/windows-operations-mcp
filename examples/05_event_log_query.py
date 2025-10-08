#!/usr/bin/env python3
"""
Example 5: Windows Event Log Query

This example demonstrates how to query Windows Event Logs
using the Windows Operations MCP tools.

Note: Some operations may require administrator privileges.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from windows_operations_mcp.tools.windows_event_logs import (
    query_windows_event_log,
    list_event_log_providers
)


def main():
    """Demonstrate Windows Event Log querying capabilities."""
    
    print("=" * 60)
    print("Windows Operations MCP - Event Log Query Example")
    print("=" * 60)
    print()
    
    # 1. Query recent system events
    print("1. Recent System Events (Last 10)")
    print("-" * 60)
    
    result = query_windows_event_log(
        log_name="System",
        max_events=10,
        level="Error,Warning"
    )
    
    if result.get("success"):
        events = result.get("events", [])
        print(f"Found {len(events)} events:")
        for event in events:
            timestamp = event.get('time_created', 'N/A')
            level = event.get('level', 'N/A')
            source = event.get('source', 'N/A')
            message = event.get('message', 'N/A')[:80]
            print(f"\n  [{timestamp}] {level}")
            print(f"  Source: {source}")
            print(f"  Message: {message}...")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    
    # 2. Query Application events
    print("2. Application Events with Errors")
    print("-" * 60)
    
    result = query_windows_event_log(
        log_name="Application",
        max_events=5,
        level="Error"
    )
    
    if result.get("success"):
        events = result.get("events", [])
        print(f"Found {len(events)} error events:")
        for event in events:
            print(f"\n  Event ID: {event.get('id')}")
            print(f"  Source: {event.get('source')}")
            print(f"  Time: {event.get('time_created')}")
            print(f"  Message: {event.get('message', 'N/A')[:100]}...")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    
    # 3. Query with time filter
    print("3. Security Events from Last 24 Hours")
    print("-" * 60)
    
    # Calculate time range
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    result = query_windows_event_log(
        log_name="Security",
        max_events=10,
        start_time=yesterday.isoformat(),
        end_time=now.isoformat()
    )
    
    if result.get("success"):
        events = result.get("events", [])
        print(f"Found {len(events)} security events in last 24 hours")
        
        # Group by event ID
        event_counts = {}
        for event in events:
            event_id = event.get('id', 'Unknown')
            event_counts[event_id] = event_counts.get(event_id, 0) + 1
        
        print("\n  Event ID Summary:")
        for event_id, count in sorted(event_counts.items()):
            print(f"    Event ID {event_id}: {count} occurrences")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    
    # 4. List available event log providers
    print("4. Available Event Log Providers (First 10)")
    print("-" * 60)
    
    result = list_event_log_providers(max_results=10)
    
    if result.get("success"):
        providers = result.get("providers", [])
        print(f"Found {len(providers)} providers:")
        for provider in providers:
            print(f"  • {provider.get('name')}")
            if provider.get('message_file'):
                print(f"    Message File: {provider.get('message_file')[:60]}...")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    
    # 5. Query specific event ID
    print("5. Query Specific Event ID (4624 - Logon Success)")
    print("-" * 60)
    
    result = query_windows_event_log(
        log_name="Security",
        event_id=4624,
        max_events=5
    )
    
    if result.get("success"):
        events = result.get("events", [])
        print(f"Found {len(events)} logon success events:")
        for event in events:
            print(f"\n  Time: {event.get('time_created')}")
            print(f"  Computer: {event.get('computer', 'N/A')}")
            print(f"  User: {event.get('user_name', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("=" * 60)
    print("\n📝 Event Log Query Tips:")
    print("  • Use level filter: 'Information', 'Warning', 'Error', 'Critical'")
    print("  • Combine levels with comma: 'Error,Warning'")
    print("  • Use time filters for specific ranges")
    print("  • Query by event ID for specific event types")
    print("  • Admin privileges may be required for Security log")
    print("=" * 60)


if __name__ == "__main__":
    main()

