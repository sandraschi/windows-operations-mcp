#!/usr/bin/env python3
"""
Example 3: PowerShell Automation

This example demonstrates how to execute PowerShell commands and scripts
using the Windows Operations MCP tools.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from windows_operations_mcp.tools.powershell_tools import (
    run_powershell,
    run_cmd
)


def main():
    """Execute various PowerShell commands."""
    
    print("=" * 60)
    print("Windows Operations MCP - PowerShell Automation Example")
    print("=" * 60)
    print()
    
    # 1. Simple PowerShell command
    print("1. Simple PowerShell Command")
    print("-" * 60)
    
    result = run_powershell(command="Get-Date")
    
    if result.get("success"):
        print(f"✅ Command executed successfully:")
        print(f"   Output: {result.get('output', '').strip()}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    
    # 2. Get running processes
    print("2. Get Top 5 Processes by CPU")
    print("-" * 60)
    
    ps_command = "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 | Format-Table Name, CPU, WorkingSet -AutoSize"
    
    result = run_powershell(command=ps_command)
    
    if result.get("success"):
        print(f"✅ Top processes:")
        print(result.get('output', ''))
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    
    # 3. System information with PowerShell
    print("3. System Information via PowerShell")
    print("-" * 60)
    
    sys_command = """
    $os = Get-CimInstance Win32_OperatingSystem
    $cs = Get-CimInstance Win32_ComputerSystem
    
    Write-Output "Computer: $($cs.Name)"
    Write-Output "OS: $($os.Caption)"
    Write-Output "Version: $($os.Version)"
    Write-Output "Total RAM: $([math]::Round($cs.TotalPhysicalMemory/1GB, 2)) GB"
    """
    
    result = run_powershell(command=sys_command)
    
    if result.get("success"):
        print(f"✅ System information:")
        for line in result.get('output', '').strip().split('\n'):
            print(f"   {line}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    
    # 4. Create and run a PowerShell script file
    print("4. Execute PowerShell Script File")
    print("-" * 60)
    
    script_path = os.path.join(os.path.dirname(__file__), "test_script.ps1")
    
    # Create script file
    script_content = """
    # Test PowerShell Script
    Write-Output "Script execution started..."
    
    $numbers = 1..5
    $sum = ($numbers | Measure-Object -Sum).Sum
    
    Write-Output "Numbers: $($numbers -join ', ')"
    Write-Output "Sum: $sum"
    Write-Output "Script execution completed!"
    """
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    result = run_powershell(command=f". '{script_path}'")
    
    if result.get("success"):
        print(f"✅ Script executed:")
        print(result.get('output', ''))
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    # Cleanup
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"   Cleaned up: {script_path}")
    
    print()
    
    # 5. CMD command for comparison
    print("5. CMD Command (for comparison)")
    print("-" * 60)
    
    result = run_cmd(command="echo Hello from CMD!")
    
    if result.get("success"):
        print(f"✅ CMD output: {result.get('output', '').strip()}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()

