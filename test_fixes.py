#!/usr/bin/env python3
"""
Test script for the FIXED PowerShell tools.
Tests the most common scenarios that were failing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windows_operations_mcp.tools.powershell_tools import _powershell_executor

def test_powershell_fixes():
    print("🚀 Testing FIXED PowerShell Tools")
    print("=" * 50)
    
    # Test 1: Format-Table (was previously blocked)
    print("\n1. Testing Format-Table (was blocked before):")
    result = _powershell_executor.execute('Get-ChildItem C:\\ | Select-Object Name, Length | Format-Table -AutoSize')
    print(f"   Success: {result['success']}")
    print(f"   Exit Code: {result['exit_code']}")
    print(f"   Output Length: {len(result['stdout'])} chars")
    if result['stdout']:
        print(f"   First 200 chars: {result['stdout'][:200]}...")
    if result['stderr']:
        print(f"   Stderr: {result['stderr']}")
    
    # Test 2: Simple command with native encoding
    print("\n2. Testing simple Get-Date:")
    result = _powershell_executor.execute('Get-Date')
    print(f"   Success: {result['success']}")
    print(f"   Output: {result['stdout']}")
    print(f"   Encoding Used: {result['encoding_used']}")
    
    # Test 3: Command with pipe
    print("\n3. Testing piped command:")
    result = _powershell_executor.execute('Get-Process | Where-Object {$_.ProcessName -like "exp*"} | Select-Object ProcessName, Id')
    print(f"   Success: {result['success']}")
    print(f"   Exit Code: {result['exit_code']}")
    if result['stdout']:
        print(f"   Output: {result['stdout'][:300]}...")
    
    # Test 4: File operations
    print("\n4. Testing file operations:")
    result = _powershell_executor.execute('Test-Path "C:\\temp"; Get-ChildItem C:\\ -Name | Measure-Object')
    print(f"   Success: {result['success']}")
    print(f"   Output: {result['stdout']}")
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    return True

if __name__ == "__main__":
    test_powershell_fixes()
