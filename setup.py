#!/usr/bin/env python3
# -*- coding: utf-8-
"""Windows Operations MCP - Setup configuration."""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Main dependencies
install_requires = [
    'fastmcp>=2.11.3,<3.0.0',  # Using 2.11.3 for stateful tools support
    'psutil>=5.9.0',
    'structlog>=23.0.0',
    'fastapi>=0.95.0',
    'uvicorn>=0.22.0',
    'pydantic>=1.10.0',
    'python-dotenv>=1.0.0',
    'pywin32>=305; sys_platform == "win32"',
    'rarfile>=4.0',
    'python-libarchive-c>=4.0',
]

# Optional dependencies
extras_require = {
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-mock>=3.10.0',
        'pytest-asyncio>=0.20.0',
        'pytest-xdist>=3.0.0',
        'pytest-randomly>=3.10.0',
        'coverage>=6.0.0',
        'black>=23.0.0',
        'isort>=5.12.0',
        'flake8>=6.0.0',
        'mypy>=1.0.0',
        'pylint>=2.12.0',
        'mkdocs>=1.4.0',
        'mkdocs-material>=9.0.0',
        'mkdocstrings[python]>=0.20.0',
    ],
    'dxt': ['dxt>=0.1.0']
}

# Get all package data files
def get_package_data():
    data_files = {}
    
    # Include all files in dxt directory
    dxt_files = []
    for root, _, files in os.walk('dxt'):
        for file in files:
            if not file.endswith('.pyc'):
                rel_path = os.path.relpath(os.path.join(root, file), 'dxt')
                dxt_files.append(rel_path)
    
    if dxt_files:
        data_files['dxt'] = dxt_files
    
    return data_files

if __name__ == "__main__":
    setup(
        name="windows-operations-mcp",
        version="0.1.0",
        description="Windows Operations MCP - Comprehensive Windows system operations",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="Sandra",
        author_email="sandra@example.com",
        url="https://github.com/sandraschi/windows-operations-mcp",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        package_data={
            "windows_operations_mcp": ["*.txt", "*.md", "*.json", "*.yaml", "*.yml"],
            **get_package_data()
        },
        python_requires=">=3.8",
        install_requires=install_requires,
        extras_require=extras_require,
        entry_points={
            "console_scripts": [
                "windows-operations-mcp = windows_operations_mcp.__main__:main",
            ],
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: Microsoft :: Windows",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: System :: Systems Administration",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        project_urls={
            "Homepage": "https://github.com/sandraschi/windows-operations-mcp",
            "Documentation": "https://github.com/sandraschi/windows-operations-mcp#readme",
            "Issues": "https://github.com/sandraschi/windows-operations-mcp/issues",
            "Source": "https://github.com/sandraschi/windows-operations-mcp"
        },
        include_package_data=True,
        zip_safe=False,
    )
