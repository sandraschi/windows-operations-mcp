#!/usr/bin/env python3
"""
Fix test imports across all test files.

This script fixes the import paths in test files to work with pytest's pythonpath configuration.
"""

from pathlib import Path


def fix_imports(file_path):
    """Fix imports in a test file."""
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    skip_next_blank = False

    for _i, line in enumerate(lines):
        # Skip sys.path.insert lines
        if "sys.path.insert(0, str(Path(__file__)" in line:
            skip_next_blank = True
            continue

        # Skip blank line after sys.path.insert
        if skip_next_blank and line.strip() == "":
            skip_next_blank = False
            continue

        # Fix import statements
        if "from src.windows_operations_mcp" in line:
            line = line.replace("from src.windows_operations_mcp", "from windows_operations_mcp")

        fixed_lines.append(line)

    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    return True


def main():
    """Main function to fix all test files."""
    test_dir = Path("tests")
    files_fixed = 0

    print("=" * 60)
    print("Fixing Test Imports")
    print("=" * 60)
    print()

    # Find all test files
    test_files = list(test_dir.rglob("test_*.py"))

    print(f"Found {len(test_files)} test files")
    print()

    for test_file in test_files:
        # Read and check if fix needed
        with open(test_file, encoding="utf-8") as f:
            content = f.read()

        needs_fix = "from src.windows_operations_mcp" in content or "sys.path.insert(0, str(Path(__file__)" in content

        if needs_fix:
            print(f"✅ Fixing: {test_file}")
            fix_imports(test_file)
            files_fixed += 1
        else:
            print(f"⏭️  Skipped: {test_file} (already correct)")

    print()
    print("=" * 60)
    print(f"Fixed {files_fixed} files")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: pytest tests/unit/test_init.py -v")
    print("2. Run: pytest --cov-report=html")
    print("3. Open: htmlcov/index.html")


if __name__ == "__main__":
    main()
