# DXT Package Build Guide

This guide explains how to properly build a DXT (Desktop eXtension) package, including the correct directory structure, manifest format, and build commands.

## Directory Structure

```
project_root/
├── dxt/                  # DXT package directory (required)
│   ├── __init__.py       # Package initialization (required)
│   ├── manifest.json     # DXT manifest (required)
│   ├── requirements.txt  # Python dependencies (recommended)
│   └── prompts/          # System and user prompts (optional)
│       ├── system.md
│       ├── user.md
│       └── examples.json
└── src/                  # Your application code
    └── ...
```

## Manifest Structure (manifest.json)

```json
{
  "dxt_version": "0.1",
  "name": "your-extension-name",
  "version": "1.0.0",
  "description": "Brief description of your extension",
  "author": {
    "name": "Your Name",
    "email": "your.email@example.com"
  },
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/your-repo"
  },
  "prompts": [
    {
      "name": "system",
      "text": "dxt/prompts/system.md"
    },
    {
      "name": "user",
      "text": "dxt/prompts/user.md"
    },
    {
      "name": "examples",
      "text": "dxt/prompts/examples.json"
    }
  ],
  "server": {
    "type": "python",
    "entry_point": "your_package.your_module",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "your_package.your_module"],
      "env": {
        "PYTHONPATH": ".",
        "PYTHONUNBUFFERED": "1"
      }
    }
  },
  "user_config": {
    "config_option_1": {
      "type": "string",
      "default": "default_value",
      "title": "Config Option 1",
      "description": "Description of this config option"
    },
    "config_option_2": {
      "type": "boolean",
      "default": true,
      "title": "Enable Feature",
      "description": "Enable or disable this feature"
    }
  }
}
```

## Building the DXT Package

### 1. Install Dependencies

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install DXT CLI
pip install dxt

# Install package dependencies
pip install -r dxt/requirements.txt
```

### 2. Update the Manifest

Ensure your `dxt/manifest.json` is properly configured with the correct entry points and configuration.

### 3. Build the DXT Package

```bash
# Correct syntax: dxt pack <source_directory> <output_file>
dxt pack dxt dist/your-extension.dxt
```

> **Important**: Do NOT use the `-o` flag. The correct syntax is `dxt pack <source> <destination>`.

### 4. Verify the Package

```bash
# Check package info
dxt info dist/your-extension.dxt

# Unpack to verify contents
dxt unpack dist/your-extension.dxt temp_extract
```

## Including Dependencies

To include all dependencies in the DXT package:

1. Create a virtual environment in your package directory:
   ```bash
   python -m venv dxt/.venv
   dxt\.venv\Scripts\activate
   pip install -r dxt/requirements.txt
   ```

2. Update the manifest to use the virtual environment's Python:
   ```json
   "mcp_config": {
     "command": ".venv\\Scripts\\python.exe",
     "args": ["-m", "your_package.your_module"],
     "env": {
       "PYTHONPATH": ".",
       "PYTHONUNBUFFERED": "1"
     }
   }
   ```

3. Build the package including the virtual environment:
   ```bash
   dxt pack dxt dist/your-extension.dxt
   ```

## Common Issues and Solutions

- **Manifest Validation Errors**: Ensure all required fields are present and no unsupported keys are used.
- **Missing Dependencies**: All dependencies must be either included in the package or installed on the target system.
- **Incorrect Paths**: Use forward slashes (/) in paths within the manifest, even on Windows.
- **Package Too Small**: If your DXT file is very small (e.g., 10KB), it likely doesn't include the required dependencies.

## Best Practices

1. Always test the DXT package on a clean system.
2. Keep the package size reasonable by only including necessary files.
3. Use relative paths in the manifest.
4. Document all user-configurable options in the `user_config` section.
5. Include a comprehensive README with installation and usage instructions.

## Troubleshooting

- If the DXT CLI doesn't work, verify it's installed in your Python environment.
- Check the manifest with `dxt validate dxt/manifest.json` before building.
- For large packages, consider using a `.dxtignore` file to exclude unnecessary files.

---

*Last updated: August 2025*
