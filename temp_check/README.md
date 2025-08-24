# Windows Operations MCP - DXT Configuration

This directory contains the DXT (Data eXchange Tools) configuration for the Windows Operations MCP package.

## Files

- `manifest.json`: The main DXT manifest file that defines the package metadata, server configuration, and user configuration options.
- `requirements.txt`: DXT-specific requirements. This should be a subset of the main project requirements.
- `prompts/`: Directory containing system and user prompts for the DXT interface.

## Building the DXT Package

To build the DXT package, run the following command from the project root:

```bash
# Build the package
dxt pack -o dist/windows-operations-mcp.dxt

# Validate the package
dxt validate dist/windows-operations-mcp.dxt

# Sign the package (requires signing key)
dxt sign dist/windows-operations-mcp.dxt

# Publish the package (if applicable)
dxt publish dist/windows-operations-mcp.dxt
```

## Development

When making changes to the DXT configuration:

1. Update the `manifest.json` with any new configuration options or changes.
2. Update this README if you add new files or change the build process.
3. Test the package locally before committing changes.

## Versioning

The DXT package version should match the main package version defined in `pyproject.toml`.
