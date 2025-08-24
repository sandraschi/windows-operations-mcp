#!/usr/bin/env python3
"""
Quick fix script for Windows Operations MCP server disconnection issue.
Copies tools from src/ to root directory and fixes import issues.
"""

import shutil
import os
from pathlib import Path

def main():
    # Define paths
    repo_root = Path(r"D:\Dev\repos\windows-operations-mcp")
    src_tools = repo_root / "src" / "windows_operations_mcp" / "tools"
    target_tools = repo_root / "windows_operations_mcp" / "tools"
    
    print(f"Source: {src_tools}")
    print(f"Target: {target_tools}")
    
    # Check if source exists
    if not src_tools.exists():
        print(f"❌ Source directory not found: {src_tools}")
        return False
    
    # Create target directory if it doesn't exist
    target_tools.mkdir(parents=True, exist_ok=True)
    
    # Copy all files
    try:
        # Copy individual files to avoid overwrite issues
        for item in src_tools.iterdir():
            if item.is_file():
                target_file = target_tools / item.name
                shutil.copy2(item, target_file)
                print(f"✅ Copied {item.name}")
            elif item.is_dir():
                target_dir = target_tools / item.name
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(item, target_dir)
                print(f"✅ Copied directory {item.name}")
        
        print("🎉 All tools copied successfully!")
        
        # Create consolidated file_operations.py
        file_ops_content = '''"""
File operations tools for Windows Operations MCP.
Consolidated from the file_operations package.
"""

import logging
from typing import Dict, Any, Optional, List
from .file_operations.file_operations import register_file_operations

logger = logging.getLogger(__name__)

# Export the registration function
__all__ = ["register_file_operations"]
'''
        
        file_ops_path = target_tools / "file_operations.py"
        file_ops_path.write_text(file_ops_content, encoding='utf-8')
        print("✅ Created consolidated file_operations.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error copying tools: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Fix applied successfully!")
        print("Now try running: python -m windows_operations_mcp")
    else:
        print("\n❌ Fix failed!")
