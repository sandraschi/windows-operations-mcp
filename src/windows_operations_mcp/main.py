"""
Windows Operations MCP - Main Entry Point

This module provides the main entry point for the Windows Operations MCP server.
It's a thin wrapper around the __main__ module to maintain compatibility.
"""

from .__main__ import main

if __name__ == "__main__":
    main()
