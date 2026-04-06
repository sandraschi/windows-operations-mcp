#!/usr/bin/env python3
"""
Build script for Windows Operations MCPB package - SOTA v14.0
IMPORTANT: MCPB packages contain NO external dependencies - handled by MCPB runtime.
This script packages all tools, prompts, and skills into the .mcpb bundle.
"""
import json
import zipfile
import os
from pathlib import Path


def create_mcpb_package():
    """Create a minimal MCPB package containing all source logic."""
    project_root = Path(__file__).parent
    mcpb_dir = project_root / "mcpb"
    dist_dir = project_root / "dist"
    src_dir = project_root / "src"
    skills_dir = project_root / "skills"

    # Ensure dist directory exists
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Read manifest from mcpb directory
    manifest_path = mcpb_dir / "manifest.json"
    if not manifest_path.exists():
        print("[ERROR] MCPB manifest not found in mcpb/")
        return False

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    package_name = manifest.get('name', 'windows-operations-mcp')
    version = manifest.get('version', '14.0.0')
    output_file = dist_dir / f"{package_name}-{version}.mcpb"

    print(f"📦 Packaging SOTA v14.0: {package_name}-{version}")

    # Create MCPB package
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Write the manifest (to the root of the zip)
        zipf.writestr("manifest.json", json.dumps(manifest, indent=2))

        # 2. Add all source files recursively
        if src_dir.exists():
            for root, _, files in os.walk(src_dir):
                for file in files:
                    if file.endswith('.py') or file.endswith('.md') or file.endswith('.json'):
                        file_path = Path(root) / file
                        # Arcname should be relative to project_root to preserve src/ prefix
                        arcname = file_path.relative_to(project_root)
                        zipf.write(str(file_path), str(arcname))
        else:
            print("[ERROR] src/ directory not found")
            return False

        # 3. Add skills if they exist
        if skills_dir.exists():
            for root, _, files in os.walk(skills_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_root)
                    zipf.write(str(file_path), str(arcname))

        # 4. Add core docs
        for doc in ["README.md", "CHANGELOG.md", "LICENSE"]:
            doc_path = project_root / doc
            if doc_path.exists():
                zipf.write(str(doc_path), doc)

    print(f"\n[SUCCESS] MCPB package created successfully!")
    print(f"Package: {output_file}")
    print(f"Size: {os.path.getsize(output_file) / 1024:.2f} KB")
    
    # List contents
    print("\nPackage contents (top level):")
    with zipfile.ZipFile(output_file, 'r') as zipf:
        top_level = set()
        for file in zipf.namelist():
            parts = file.split('/')
            top_level.add(parts[0])
        for tl in sorted(list(top_level)):
            print(f"- {tl}")

    return True


def main():
    """Main entry point."""
    print("\n=== Building Windows Operations MCPB Package ===\n")
    success = create_mcpb_package()
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
