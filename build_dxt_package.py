#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the DXT package with all necessary files.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def build_dxt_package():
    """Build the DXT package with all necessary files."""
    print("Building DXT package...")
    
    # Create a temporary directory for the package
    temp_dir = Path("dxt_package_temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Copy all necessary files to the temporary directory
    print("Copying files to temporary directory...")
    
    # Copy the dxt directory
    shutil.copytree("dxt", temp_dir / "dxt")
    
    # Copy the src directory
    shutil.copytree("src", temp_dir / "src")
    
    # Copy required root files
    files_to_copy = [
        "setup.py",
        "MANIFEST.in",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "LICENSE"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, temp_dir / file)
    
    # Build the DXT package
    print("Running dxt pack...")
    try:
        # Change to the temp directory
        os.chdir(temp_dir)
        
        # Run dxt pack
        result = subprocess.run(
            ["dxt", "pack", "dxt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error building DXT package: {result.stderr}")
            return False
        
        # Move the built package to the root directory
        dxt_file = next(Path(".").glob("*.dxt"), None)
        if dxt_file:
            shutil.move(str(dxt_file), "../")
            print(f"Successfully built DXT package: {dxt_file.name}")
            
            # Check the size of the built package
            dxt_path = Path("..") / dxt_file.name
            size_mb = dxt_path.stat().st_size / (1024 * 1024)
            print(f"Package size: {size_mb:.2f} MB")
            
            # List contents of the package
            print("\nPackage contents:")
            subprocess.run(["dxt", "info", str(dxt_path)])
            
            return True
        else:
            print("Error: No DXT package was created.")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        # Clean up
        os.chdir("..")
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    if build_dxt_package():
        sys.exit(0)
    else:
        sys.exit(1)
