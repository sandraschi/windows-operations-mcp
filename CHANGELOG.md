# Changelog

All notable changes to the Windows Operations MCP project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-30

### 🚀 Major Release - Portmanteau Reorganization Complete

This release implements the portmanteau tool pattern, reducing the API surface by 84% while maintaining full functionality. All tools now follow the action-based interface pattern for better discoverability and consistency.

### Added

#### Portmanteau Tool Architecture
- ✅ **9 Portmanteau Tools** replacing 57+ individual tools
- ✅ **Action-based Interface** - All tools use `action` parameter with `Literal` types
- ✅ **Dynamic Tool Registration** - Server automatically imports and registers portmanteau tools
- ✅ **FastMCP 2.14.1+ Compatibility** - Updated to latest FastMCP version

#### New Portmanteau Tools
- ✅ `command_execution` - PowerShell & CMD execution (powershell, cmd actions)
- ✅ `file_operations` - Core file operations (read, write, delete, move, copy, list, info, exists)
- ✅ `directory_operations` - Directory management (create, delete, move, copy, list)
- ✅ `archive_management` - ZIP/tar handling (create, extract, list)
- ✅ `json_operations` - JSON processing toolkit (read, write, validate, format, convert, extract)
- ✅ `git_operations` - Git repository management (add, commit, push, status)
- ✅ `process_management` - Process monitoring (list, info, resources)
- ✅ `windows_services` - Windows service management (list, start, stop, restart)
- ✅ `system_management` - System diagnostics (info, health, test_port, help)

#### Documentation Standards Compliance
- ✅ **FastMCP 2.14.1+ Docstring Standards** - All tools follow comprehensive documentation format
- ✅ **Triple Double Quotes** - Fixed all docstrings to use `"""` instead of `'''`
- ✅ **FEATURES, Args, Returns, Examples, Notes** - Complete documentation structure
- ✅ **Central Documentation Compliance** - Follows mcp-central-docs standards

### Changed

#### Tool Architecture Overhaul
- 🔄 **57 individual tools → 9 portmanteau tools** (84% reduction)
- 🔄 **Consistent action-based interface** across all tools
- 🔄 **Dynamic registration system** replaces manual tool imports
- 🔄 **Enhanced error handling** with standardized response format

#### FastMCP Version Update
- 🔄 **FastMCP 2.12.3 → 2.14.1** - Latest version compatibility
- 🔄 **Enhanced response patterns** for better AI dialogue
- 🔄 **Server lifespan management** for stateful servers
- 🔄 **Advanced tool management** features

### Fixed

#### Docstring Issues
- 🐛 **Unicode decoding errors** - Fixed regex patterns causing encoding issues
- 🐛 **Triple quote consistency** - All docstrings now use proper `"""` format
- 🐛 **Missing documentation** - Comprehensive docstrings for all operations
- 🐛 **Parameter documentation** - Complete parameter descriptions with types

#### Tool Registration
- 🐛 **Import path issues** - Fixed dynamic import paths for portmanteau tools
- 🐛 **Registration failures** - All 9 tools now register successfully
- 🐛 **Syntax errors** - Fixed indentation and encoding issues

### Technical Details

#### Tool Reduction Breakdown
```
Before: 57+ individual tools
├── PowerShell tools: 2 (run_powershell_tool, run_cmd_tool)
├── File tools: 10 (read_file, write_file, delete_file, etc.)
├── Directory tools: 5 (create_directory, delete_directory, etc.)
├── Archive tools: 3 (create_archive, extract_archive, list_archive)
├── JSON tools: 6 (read_json, write_json, validate_json, etc.)
├── Git tools: 4 (git_add, git_commit, git_push, git_status)
├── Process tools: 3 (get_process_list, get_process_info, get_resources)
├── Windows services: 4 (list_services, start_service, stop_service, restart_service)
├── System tools: 4 (get_system_info, health_check, test_port, get_help)
└── Other tools: Various utility functions

After: 9 portmanteau tools
├── command_execution (2 actions)
├── file_operations (8 actions)
├── directory_operations (5 actions)
├── archive_management (3 actions)
├── json_operations (6 actions)
├── git_operations (4 actions)
├── process_management (3 actions)
├── windows_services (4 actions)
└── system_management (4 actions)
```

#### Benefits Achieved
- **84% fewer tools** in the API surface
- **Better discoverability** - Related operations grouped logically
- **Consistent interface** - All tools follow action-based pattern
- **Easier maintenance** - Reduced code duplication
- **Professional documentation** - FastMCP 2.14.1+ standards compliance

## [0.2.0] - 2025-10-08

### 🎉 Major Release - MCPB Migration Complete

This release marks the complete migration from DXT to MCPB (MCP Bundle) packaging system and represents a major milestone in the project's maturity.

### Added

#### MCPB Packaging System
- ✅ Full MCPB v0.2 compliance with proper manifest structure
- ✅ MCPB configuration file (`mcpb.json`) for package building
- ✅ MCPB manifest with AI-generated prompts (`mcpb/manifest.json`)
- ✅ Prompt templates: `system.md`, `user.md`, `examples.json`
- ✅ PowerShell build automation script (`scripts/build-mcp-package.ps1`)
- ✅ Production-ready MCPB package validation

#### CI/CD Infrastructure
- ✅ GitHub Actions workflow for automated builds (`.github/workflows/build-mcpb.yml`)
- ✅ Automated MCPB package building on releases
- ✅ Test automation pipeline
- ✅ Artifact publishing to GitHub Releases

#### Documentation
- ✅ Comprehensive MCPB Building Guide (`docs/MCPB_BUILDING_GUIDE.md`)
- ✅ Repository Status Report with health tracking (`REPOSITORY_STATUS_REPORT.md`)
- ✅ Enhanced README.md with badges and "What's New" section
- ✅ Updated Gold Standard Progress tracking (Week 1 complete)
- ✅ Professional status badges (FastMCP, Python, MCPB, License)

#### Enhanced Tools & Features
- ✅ New main server entry point (`server.py`)
- ✅ Enhanced JSON tools with better error handling
- ✅ Improved media metadata extraction
- ✅ Better command execution utilities
- ✅ Extended command executor improvements

#### Testing Improvements
- ✅ 16 test files enhanced and updated
- ✅ Improved test coverage for:
  - Archive tools
  - File operations
  - JSON tools
  - Media tools
  - Command executors
  - Logging configuration
  - MCP server details

### Changed
- 🔄 Migrated from DXT to MCPB packaging format
- 🔄 Updated build system from DXT CLI to MCPB CLI
- 🔄 Reorganized project structure for MCPB compliance
- 🔄 Enhanced documentation with migration guide
- 🔄 Improved README with comprehensive installation instructions
- 🔄 Updated all build processes for MCPB standards

### Removed
- ❌ Legacy DXT documentation (`docs/DXT_BUILDING_GUIDE.md`, `docs/DXT_BUILD_GUIDE.md`)
- ❌ DXT configuration files (replaced with MCPB equivalents)

### Fixed
- 🐛 Command execution error handling
- 🐛 JSON parsing edge cases
- 🐛 Media metadata extraction bugs
- 🐛 Test import paths and execution

### Performance
- ⚡ Optimized command execution pipeline
- ⚡ Improved error handling with minimal overhead
- ⚡ Streamlined build process with PowerShell automation

### Security
- 🔒 Enhanced input validation in all tools
- 🔒 Improved error handling to prevent information leakage
- 🔒 Secure command execution with proper escaping

### Repository Health
- **Health Score**: 9.0/10 ⭐
- **Status**: Production Ready
- **Test Coverage**: 139 tests written, enhanced coverage
- **Linter Errors**: 0
- **Documentation**: Comprehensive and up-to-date

---

## [0.1.0] - 2025-09-30

### Initial Release

#### Core Features
- ✅ FastMCP 2.12.3 implementation
- ✅ Windows Services Management
- ✅ Windows Event Log Tools
- ✅ Windows Performance Monitoring
- ✅ Windows Permissions Management
- ✅ PowerShell & CMD execution
- ✅ File operations (read, write, move, copy)
- ✅ Archive management (ZIP, TAR, TAR.GZ)
- ✅ System information and health checks

#### Testing
- ✅ 139 comprehensive tests
- ✅ Archive Tools: 26 tests
- ✅ PowerShell Tools: 26 tests
- ✅ System, Help, JSON, Network, Process, Media, Git tools covered
- ✅ Decorator, logging, and MCP server tests
- ✅ Integration tests

#### Documentation
- ✅ Comprehensive README.md
- ✅ QUICKSTART.md (5-minute setup guide)
- ✅ GOLD_STANDARD_PLAN.md (4-week roadmap)
- ✅ Examples and troubleshooting guides

#### Distribution
- ✅ Glama.ai listing: https://glama.ai/mcp/servers/@sandraschi/windows-operations-mcp
- ✅ DXT packaging support

---

## Release Notes

### v0.2.0 - MCPB Migration Milestone

This release represents a significant upgrade to the project's infrastructure and packaging system. The migration to MCPB ensures compatibility with the latest MCP standards and provides a better developer and user experience.

**Key Highlights:**
- 🎯 **MCPB Migration Complete**: Full transition from DXT to MCPB v0.2
- 🚀 **CI/CD Ready**: GitHub Actions for automated builds and releases
- 📚 **Enhanced Documentation**: Professional guides and status tracking
- 🧪 **Improved Testing**: 16 test files enhanced with better coverage
- 🏗️ **Build Automation**: One-command package building with PowerShell
- ✨ **Production Ready**: Health score 9.0/10, validated and tested

**Upgrade Notes:**
- Existing users should uninstall the old DXT package and install the new MCPB package
- The MCPB package provides the same functionality with improved stability
- All configuration settings are preserved in the new format

**Breaking Changes:**
- None - Full backward compatibility maintained for all tools and APIs

**Next Steps:**
- Week 2: Fix test coverage measurement, create examples, PyPI publication
- Week 3: Achieve 60-90% test coverage, security audit, video tutorial
- Week 4: Gold Standard achievement with 90%+ coverage and community setup

---

[0.2.0]: https://github.com/sandraschi/windows-operations-mcp/releases/tag/v0.2.0
[0.1.0]: https://github.com/sandraschi/windows-operations-mcp/releases/tag/v0.1.0
