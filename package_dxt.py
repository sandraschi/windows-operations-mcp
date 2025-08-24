import os
import sys
import json
import zipfile
from pathlib import Path
from typing import List, Optional

def get_file_list(directory: str) -> List[str]:
    """Get a list of all files in a directory recursively."""
    file_list = []
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
        return file_list
    except Exception as e:
        print(f"Error listing files in {directory}: {str(e)}")
        return []

def create_dxt_package(source_dir: str, output_file: str) -> bool:
    """
    Create a .dxt package from the source directory.
    
    Args:
        source_dir: Path to the directory containing the DXT package
        output_file: Path to the output .dxt file
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n🔍 Preparing to create DXT package from: {source_dir}")
    
    # Ensure source directory exists
    if not os.path.exists(source_dir):
        print(f"❌ Error: Source directory '{source_dir}' does not exist.")
        return False
    
    # Ensure config.json exists
    config_path = os.path.join(source_dir, 'config.json')
    if not os.path.exists(config_path):
        print("❌ Error: config.json not found in the source directory.")
        return False
    
    # Get list of files to include
    print("📂 Scanning for files to include...")
    files_to_include = get_file_list(source_dir)
    
    if not files_to_include:
        print("❌ No files found in the source directory.")
        return False
    
    print(f"✅ Found {len(files_to_include)} files to include in the package.")
    
    # Remove existing output file if it exists
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"⚠️  Removed existing file: {output_file}")
        except Exception as e:
            print(f"❌ Error removing existing file: {str(e)}")
            return False
    
    # Create the .dxt file (which is just a zip file with a different extension)
    print(f"\n📦 Creating DXT package: {output_file}")
    success_count = 0
    
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            total_files = len(files_to_include)
            for i, file_path in enumerate(files_to_include, 1):
                try:
                    # Calculate relative path for the zip file
                    arcname = os.path.relpath(file_path, source_dir)
                    # Use forward slashes for zip file paths (Windows compatibility)
                    arcname = arcname.replace('\\', '/')
                    
                    # Add file to zip
                    zipf.write(file_path, arcname)
                    success_count += 1
                    
                    # Show progress
                    if i % 10 == 0 or i == total_files:
                        print(f"  - Added {i}/{total_files}: {arcname[:60]}{'...' if len(arcname) > 60 else ''}")
                        
                except Exception as e:
                    print(f"⚠️  Warning: Could not add {file_path}: {str(e)}"
                          " (This file will be skipped)")
        
        print(f"\n✅ Successfully created DXT package: {output_file}")
        print(f"   - Total files included: {success_count}/{len(files_to_include)}")
        print(f"   - Package size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating DXT package: {str(e)}")
        # Clean up partially created file
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                print("Cleaned up partially created package file.")
            except:
                pass
        return False

def main():
    """Main function to handle command line execution."""
    # Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(current_dir, "dxt_package")
    output_file = os.path.join(current_dir, "windows_operations_mcp.dxt")
    
    print("=" * 70)
    print("Windows Operations MCP - DXT Package Creator")
    print("=" * 70)
    
    # Create the package
    print(f"\n🔧 Configuration:")
    print(f"- Source directory: {source_dir}")
    print(f"- Output file: {output_file}")
    
    success = create_dxt_package(source_dir, output_file)
    
    if success:
        print("\n🎉 DXT package created successfully!")
        print("\nTo use this package with Claude Desktop:")
        print(f"1. Open Claude Desktop")
        print(f"2. Go to Settings > Extensions")
        print(f"3. Click 'Install from File'")
        print(f"4. Select: {output_file}")
        print("\nFor command line usage, copy the .dxt file to your Claude Desktop extensions folder.")
    else:
        print("\n❌ Failed to create DXT package. See errors above for details.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
