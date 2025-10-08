# PyPI and Package Distribution Guide

Complete guide for distributing Windows Operations MCP through PyPI and other package repositories.

## 📦 Distribution Platforms Overview

### PyPI (Python Package Index)
**URL**: https://pypi.org  
**Purpose**: Primary Python package repository  
**Audience**: Python developers and users  
**Install Method**: `pip install windows-operations-mcp`

**Advantages**:
- ✅ Industry standard for Python packages
- ✅ Integrated with pip
- ✅ Automatic dependency resolution
- ✅ Version management built-in
- ✅ Free for open source

**Requirements**:
- Python package structure
- `pyproject.toml` or `setup.py`
- Account on PyPI
- Package name availability

### Test PyPI
**URL**: https://test.pypi.org  
**Purpose**: Testing ground for PyPI packages  
**Use**: Test uploads before production

**Why Use Test PyPI**:
- ✅ Test installation process
- ✅ Verify package metadata
- ✅ Check dependencies
- ✅ Safe experimentation
- ✅ No impact on production PyPI

### Conda / Anaconda
**URL**: https://anaconda.org  
**Purpose**: Scientific Python distribution  
**Install Method**: `conda install windows-operations-mcp`

**When to Use**:
- Scientific computing users
- Data science community
- Complex binary dependencies
- Cross-platform compatibility

### GitHub Packages
**URL**: https://github.com/features/packages  
**Purpose**: GitHub-integrated package hosting  
**Install Method**: `pip install --index-url https://...`

**Advantages**:
- ✅ Integrated with GitHub
- ✅ Free for public repos
- ✅ Private package hosting
- ✅ CI/CD integration

### Glama.ai (MCP Specific)
**URL**: https://glama.ai  
**Purpose**: MCP server directory  
**Install Method**: Drag-and-drop MCPB file

**MCP Focus**:
- ✅ MCP server discovery
- ✅ MCPB package hosting
- ✅ Claude Desktop integration
- ✅ MCP community visibility

---

## 🚀 Publishing to PyPI

### 1. Prerequisites

#### Required Tools
```bash
# Install build tools
pip install --upgrade build twine

# Verify installation
python -m build --version
twine --version
```

#### Account Setup
1. Create PyPI account: https://pypi.org/account/register/
2. Create Test PyPI account: https://test.pypi.org/account/register/
3. Enable 2FA (recommended)
4. Generate API tokens:
   - PyPI: https://pypi.org/manage/account/token/
   - Test PyPI: https://test.pypi.org/manage/account/token/

#### Configure Credentials
```bash
# Create ~/.pypirc file
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
EOF

# Secure the file
chmod 600 ~/.pypirc
```

### 2. Package Preparation

#### Verify pyproject.toml
```toml
[project]
name = "windows-operations-mcp"
version = "0.2.0"
description = "Comprehensive Windows system operations for Claude Desktop"
readme = "README.md"
authors = [
    { name = "Sandra Schi", email = "sandra@sandraschi.dev" },
]
license = { text = "MIT" }
requires-python = ">=3.9"

dependencies = [
    "fastmcp>=2.12.3,<3.0.0",
    "psutil>=5.9.0",
    "structlog>=23.0.0",
    # ... other dependencies
]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.urls]
Homepage = "https://github.com/sandraschi/windows-operations-mcp"
Documentation = "https://github.com/sandraschi/windows-operations-mcp#readme"
Issues = "https://github.com/sandraschi/windows-operations-mcp/issues"
Source = "https://github.com/sandraschi/windows-operations-mcp"

[project.scripts]
windows-operations-mcp = "windows_operations_mcp.__main__:main"
```

#### Check Package Files
```bash
# Verify structure
tree src/
├── windows_operations_mcp/
│   ├── __init__.py        # Must have __version__
│   ├── __main__.py        # Entry point
│   ├── mcp_server.py
│   └── tools/

# Verify MANIFEST.in
cat MANIFEST.in
include README.md
include LICENSE
include CHANGELOG.md
recursive-include src *.py
```

### 3. Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distribution packages
python -m build

# Verify created files
ls -lh dist/
# Should show:
# - windows_operations_mcp-0.2.0.tar.gz (source distribution)
# - windows_operations_mcp-0.2.0-py3-none-any.whl (wheel)
```

### 4. Test Installation Locally

```bash
# Create test virtual environment
python -m venv test-env
source test-env/bin/activate  # or test-env\Scripts\activate on Windows

# Install from local wheel
pip install dist/windows_operations_mcp-0.2.0-py3-none-any.whl

# Test import
python -c "import windows_operations_mcp; print(windows_operations_mcp.__version__)"

# Test CLI
windows-operations-mcp --help

# Cleanup
deactivate
rm -rf test-env
```

### 5. Upload to Test PyPI

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Verify upload
open https://test.pypi.org/project/windows-operations-mcp/

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    windows-operations-mcp

# Note: --extra-index-url allows dependencies from main PyPI
```

### 6. Upload to Production PyPI

```bash
# Final checks
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*

# Verify
open https://pypi.org/project/windows-operations-mcp/

# Test installation
pip install windows-operations-mcp
```

---

## 🔄 Version Management

### Semantic Versioning

Format: `MAJOR.MINOR.PATCH` (e.g., 0.2.0)

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Pre-release Versions

```bash
# Alpha release
version = "0.3.0a1"

# Beta release
version = "0.3.0b1"

# Release candidate
version = "0.3.0rc1"

# Development release
version = "0.3.0.dev1"
```

### Version Update Checklist

- [ ] Update `pyproject.toml` version
- [ ] Update `src/windows_operations_mcp/__init__.py` __version__
- [ ] Update `mcpb/manifest.json` version
- [ ] Update `CHANGELOG.md` with changes
- [ ] Update `README.md` if needed
- [ ] Git tag: `git tag v0.3.0`
- [ ] Build and test
- [ ] Upload to PyPI

---

## 🤖 Automated Publishing with GitHub Actions

### Create PyPI Publish Workflow

```yaml
# .github/workflows/publish-pypi.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Publish to Test PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
      run: |
        twine upload --repository testpypi dist/*
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        twine upload dist/*
```

### Setup GitHub Secrets

1. Go to repository Settings → Secrets → Actions
2. Add secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: Your Test PyPI API token

---

## 📊 Package Metadata Best Practices

### Complete pyproject.toml Example

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "windows-operations-mcp"
version = "0.2.0"
description = "Comprehensive Windows system operations MCP server"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}

authors = [
    {name = "Sandra Schi", email = "sandra@sandraschi.dev"}
]

keywords = [
    "mcp",
    "windows",
    "system-administration",
    "powershell",
    "automation",
    "claude-desktop"
]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: System :: Systems Administration",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

dependencies = [
    "fastmcp>=2.12.3,<3.0.0",
    "psutil>=5.9.0",
    "structlog>=23.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
]

[project.urls]
Homepage = "https://github.com/sandraschi/windows-operations-mcp"
Documentation = "https://github.com/sandraschi/windows-operations-mcp#readme"
Repository = "https://github.com/sandraschi/windows-operations-mcp"
Issues = "https://github.com/sandraschi/windows-operations-mcp/issues"
Changelog = "https://github.com/sandraschi/windows-operations-mcp/blob/main/CHANGELOG.md"

[project.scripts]
windows-operations-mcp = "windows_operations_mcp.__main__:main"
```

### README for PyPI

Your README.md is displayed on PyPI. Ensure it includes:

- [ ] Clear description
- [ ] Installation instructions
- [ ] Quick start example
- [ ] Key features
- [ ] Links to documentation
- [ ] License information
- [ ] Badges (optional)

---

## 🔍 Package Discovery & SEO

### PyPI Search Optimization

1. **Keywords**: Use relevant, searchable keywords
2. **Classifiers**: Choose appropriate PyPI classifiers
3. **Description**: Clear, concise, keyword-rich
4. **README**: Comprehensive with examples

### PyPI Badges

Add to README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/windows-operations-mcp.svg)](https://pypi.org/project/windows-operations-mcp/)
[![Downloads](https://pepy.tech/badge/windows-operations-mcp)](https://pepy.tech/project/windows-operations-mcp)
[![Python Versions](https://img.shields.io/pypi/pyversions/windows-operations-mcp)](https://pypi.org/project/windows-operations-mcp/)
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Package name already taken
```bash
# Solution: Choose different name or request name transfer
# Check availability:
pip install package-name-checker
package-name-checker windows-operations-mcp
```

**Issue**: Invalid distribution
```bash
# Solution: Verify package structure
python -m build
twine check dist/*
```

**Issue**: Dependency conflicts
```bash
# Solution: Use compatible versions
# Test in clean environment:
python -m venv test-env
pip install dist/*.whl
```

**Issue**: README not rendering
```bash
# Solution: Validate Markdown
pip install readme-renderer
python -m readme_renderer README.md
```

---

## 📈 Post-Publication

### Monitor Package

- **PyPI Stats**: https://pypistats.org/packages/windows-operations-mcp
- **Download Analytics**: https://pepy.tech/
- **Security Scanning**: https://snyk.io/
- **Documentation**: https://readthedocs.org/

### Maintenance

- Respond to issues promptly
- Update dependencies regularly
- Fix security vulnerabilities
- Publish bug fix releases
- Maintain CHANGELOG.md

### Promotion

- Announce on social media
- Submit to Python Weekly
- Update Glama.ai listing
- Create blog post
- Share in MCP community

---

## 📋 Complete Publishing Checklist

### Pre-Publication
- [ ] Version number updated everywhere
- [ ] CHANGELOG.md updated
- [ ] README.md complete and accurate
- [ ] All tests passing
- [ ] Documentation up to date
- [ ] License file included
- [ ] Dependencies version pinned correctly

### Build & Test
- [ ] Clean build directory
- [ ] Build source and wheel distributions
- [ ] Check package with twine
- [ ] Test local installation
- [ ] Upload to Test PyPI
- [ ] Test installation from Test PyPI
- [ ] Verify package metadata on Test PyPI

### Production Release
- [ ] Create Git tag
- [ ] Upload to production PyPI
- [ ] Verify on PyPI
- [ ] Test installation from PyPI
- [ ] Create GitHub release
- [ ] Update documentation links
- [ ] Announce release

### Post-Release
- [ ] Monitor for issues
- [ ] Respond to feedback
- [ ] Update Glama.ai listing
- [ ] Share announcement
- [ ] Plan next version

---

## 📚 Additional Resources

- **PyPI Official Docs**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Build Documentation**: https://build.pypa.io/
- **Setuptools Guide**: https://setuptools.pypa.io/
- **Python Packaging Guide**: https://packaging.python.org/guides/

---

**Last Updated**: October 8, 2025  
**Version**: 0.2.0  
**Status**: Ready for PyPI publication

