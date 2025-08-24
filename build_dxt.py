#!/usr/bin/env python3
"""
Build script for Windows Operations MCP DXT package
"""
import os
import shutil
import zipfile
from pathlib import Path

def create_dxt_package():
    """Create a DXT package from the dxt directory"""
    # Define paths
    project_root = Path(__file__).parent
    dxt_dir = project_root / "dxt"
    dist_dir = project_root / "dist"
    package_name = "windows-operations-mcp.dxt"
    
    # Create dist directory if it doesn't exist
    dist_dir.mkdir(exist_ok=True)
    
    # Create the package file
    package_path = dist_dir / package_name
    
    # Remove existing package if it exists
    if package_path.exists():
        os.remove(package_path)
    
    # Create a zip file with the contents of the dxt directory
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dxt_dir):
            for file in files:
                # Skip pycache and other unnecessary files
                if '__pycache__' in root or file.endswith('.pyc'):
                    continue
                    
                file_path = Path(root) / file
                arcname = os.path.relpath(file_path, dxt_dir)
                zipf.write(file_path, arcname)
    
    print(f"Successfully created DXT package at: {package_path}")
    return package_path

if __name__ == "__main__":
    package_path = create_dxt_package()
    print(f"DXT package created at: {package_path}")
