#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

from windows_operations_mcp.tools.archive_tools import create_archive
import tempfile

# Create a test directory with some files
with tempfile.TemporaryDirectory() as temp_dir:
    # Create test files
    test_file = os.path.join(temp_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('Hello World')

    # Create node_modules directory (should be excluded by default)
    node_modules_dir = os.path.join(temp_dir, 'node_modules')
    os.makedirs(node_modules_dir)
    node_modules_file = os.path.join(node_modules_dir, 'package.json')
    with open(node_modules_file, 'w') as f:
        f.write('{"name": "test"}')

    # Create __pycache__ directory (should be excluded by default)
    pycache_dir = os.path.join(temp_dir, '__pycache__')
    os.makedirs(pycache_dir)
    pycache_file = os.path.join(pycache_dir, 'module.pyc')
    with open(pycache_file, 'w') as f:
        f.write('fake bytecode')

    print(f"Test directory: {temp_dir}")
    print(f"Test file exists: {os.path.exists(test_file)}")
    print(f"node_modules exists: {os.path.exists(node_modules_dir)}")
    print(f"__pycache__ exists: {os.path.exists(pycache_dir)}")

    # Create archive
    archive_path = os.path.join(temp_dir, 'test.zip')
    result = create_archive(
        archive_path=archive_path,
        source_paths=[temp_dir],
        use_default_exclusions=True,
        use_gitignore=False
    )

    print('Archive creation result:', result)
    print('Success:', result.get('success', False))
    print('Excluded count:', result.get('excluded_count', 0))
    print('Included count:', result.get('included_count', 0))

    # Check if archive was created
    if os.path.exists(archive_path):
        print('Archive created successfully!')
        import zipfile
        with zipfile.ZipFile(archive_path, 'r') as zf:
            files = zf.namelist()
            print('Files in archive:', files)
            print('node_modules excluded:', not any('node_modules' in f for f in files))
            print('__pycache__ excluded:', not any('__pycache__' in f for f in files))
            print('test.txt included:', any('test.txt' in f for f in files))
    else:
        print('Archive creation failed')
