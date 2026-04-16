#!/usr/bin/env python3
"""
Example 2: Archive Creation with Exclusions

This example demonstrates how to create archives with intelligent
exclusion patterns using the Windows Operations MCP tools.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from windows_operations_mcp.tools.archive_tools import create_archive, extract_archive, list_archive


def main():
    """Create, list, and extract archives with exclusions."""

    print("=" * 60)
    print("Windows Operations MCP - Archive Management Example")
    print("=" * 60)
    print()

    # Define paths
    source_dir = os.path.dirname(__file__)
    archive_path = os.path.join(source_dir, "examples_backup.zip")
    extract_dir = os.path.join(source_dir, "extracted")

    # 1. Create archive with exclusions
    print("1. Creating Archive with Exclusions")
    print("-" * 60)

    exclusions = [
        "*.pyc",  # Python compiled files
        "__pycache__",  # Python cache directories
        "*.tmp",  # Temporary files
        ".git",  # Git directory
        "node_modules",  # Node modules if any
    ]

    result = create_archive(
        archive_path=archive_path, source_paths=[source_dir], exclusion_patterns=exclusions, compression_level=6
    )

    if result.get("success"):
        print(f"✅ Archive created: {result.get('archive_path')}")
        print(f"   Files archived: {result.get('files_archived', 0)}")
        print(f"   Total size: {result.get('total_size', 0)} bytes")
        print(f"   Excluded patterns: {', '.join(exclusions)}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    print()

    # 2. List archive contents
    print("2. Listing Archive Contents")
    print("-" * 60)

    list_result = list_archive(archive_path=archive_path)

    if list_result.get("success"):
        files = list_result.get("files", [])
        print(f"Archive contains {len(files)} files:")
        for file in files[:10]:  # Show first 10
            print(f"  - {file.get('name')} ({file.get('size', 0)} bytes)")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")
    else:
        print(f"❌ Error: {list_result.get('error', 'Unknown error')}")

    print()

    # 3. Extract archive
    print("3. Extracting Archive")
    print("-" * 60)

    extract_result = extract_archive(archive_path=archive_path, destination_path=extract_dir)

    if extract_result.get("success"):
        print(f"✅ Archive extracted to: {extract_result.get('destination_path')}")
        print(f"   Files extracted: {extract_result.get('files_extracted', 0)}")
    else:
        print(f"❌ Error: {extract_result.get('error', 'Unknown error')}")

    print()

    # Cleanup
    print("4. Cleanup")
    print("-" * 60)
    if os.path.exists(archive_path):
        os.remove(archive_path)
        print(f"✅ Removed: {archive_path}")

    if os.path.exists(extract_dir):
        import shutil

        shutil.rmtree(extract_dir)
        print(f"✅ Removed: {extract_dir}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
