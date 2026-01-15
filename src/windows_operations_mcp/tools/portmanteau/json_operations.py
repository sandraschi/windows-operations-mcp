"""
JSON Operations Portmanteau Tool for Windows Operations MCP.

Consolidates JSON operations (read, write, validate, format, convert, extract) into a single portmanteau tool.
Provides comprehensive JSON file handling and manipulation functionality.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Literal, List, Union

from ...logging_config import get_logger

logger = get_logger(__name__)


def json_operations(
    action: Literal["read", "write", "validate", "format", "convert", "extract"],
    file_path: Optional[str] = None,
    content: Optional[str] = None,
    data: Optional[Any] = None,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
    encoding: str = "utf-8",
    compact: bool = False
) -> Dict[str, Any]:
    """
    Perform JSON operations with comprehensive error handling and formatting.

    Args:
        action: The JSON operation to perform. Must be one of: "read", "write", "validate", "format", "convert", "extract"
        file_path: Path to JSON file (required for read/write/validate when content not provided)
        content: Raw JSON string content (required for validate/format/extract when file_path not provided)
        data: Python data structure to write as JSON (required for write action)
        indent: Indentation spaces for formatted output (default: 2)
        ensure_ascii: Escape non-ASCII characters (default: False)
        sort_keys: Sort dictionary keys alphabetically (default: False)
        encoding: File encoding for read/write operations (default: "utf-8")
        compact: Use compact formatting (default: False)

    Returns:
        Dict containing success status and operation results
    """
    logger.info("json_operations_started", action=action, file_path=file_path)

    try:
        # Route to appropriate action
        if action == "read":
            if not file_path:
                return {
                    "success": False,
                    "action": action,
                    "error": "file_path is required for read action"
                }
            return _read_json_file(file_path, encoding)

        elif action == "write":
            if data is None:
                return {
                    "success": False,
                    "action": action,
                    "error": "data is required for write action"
                }
            if not file_path:
                return {
                    "success": False,
                    "action": action,
                    "error": "file_path is required for write action"
                }
            return _write_json_file(file_path, data, indent, ensure_ascii, sort_keys, compact, encoding)

        elif action == "validate":
            if not file_path and not content:
                return {
                    "success": False,
                    "action": action,
                    "error": "Either file_path or content is required for validate action"
                }
            return _validate_json(file_path, content, encoding)

        elif action == "format":
            if not content:
                return {
                    "success": False,
                    "action": action,
                    "error": "content is required for format action"
                }
            return _format_json(content, indent, ensure_ascii, sort_keys, compact)

        elif action == "convert":
            # For now, just format JSON (could be extended to other formats)
            if not content:
                return {
                    "success": False,
                    "action": action,
                    "error": "content is required for convert action"
                }
            return _format_json(content, indent, ensure_ascii, sort_keys, compact)

        elif action == "extract":
            if not content:
                return {
                    "success": False,
                    "action": action,
                    "error": "content is required for extract action"
                }
            return _extract_json_objects(content)

        else:
            return {
                "success": False,
                "action": action,
                "error": f"Unknown action: {action}"
            }

    except Exception as e:
        error_msg = f"JSON operation failed: {str(e)}"
        logger.error("json_operations_error", action=action, file_path=file_path, error=error_msg, exc_info=True)
        return {
            "success": False,
            "action": action,
            "error": error_msg
        }


def _read_json_file(file_path: str, encoding: str) -> Dict[str, Any]:
    """Read and parse JSON from file."""
    try:
        file_obj = Path(file_path)
        if not file_obj.exists():
            return {
                "success": False,
                "action": "read",
                "error": f"File does not exist: {file_path}"
            }

        with open(file_obj, 'r', encoding=encoding) as f:
            content = f.read()

        try:
            data = json.loads(content)
            return {
                "success": True,
                "action": "read",
                "data": {
                    "content": data,
                    "file_path": str(file_obj),
                    "size": len(content),
                    "encoding": encoding
                }
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "action": "read",
                "error": f"Invalid JSON in file: {str(e)}"
            }

    except UnicodeDecodeError:
        return {
            "success": False,
            "action": "read",
            "error": f"File cannot be read with encoding {encoding}: {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "action": "read",
            "error": f"Failed to read JSON file: {str(e)}"
        }


def _write_json_file(file_path: str, data: Any, indent: int, ensure_ascii: bool,
                    sort_keys: bool, compact: bool, encoding: str) -> Dict[str, Any]:
    """Write data to JSON file."""
    try:
        file_obj = Path(file_path)

        # Create parent directories if needed
        file_obj.parent.mkdir(parents=True, exist_ok=True)

        # Determine formatting options
        if compact:
            indent = None

        with open(file_obj, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys)

        # Get file size
        size = file_obj.stat().st_size

        return {
            "success": True,
            "action": "write",
            "data": {
                "file_path": str(file_obj),
                "size": size,
                "encoding": encoding,
                "indent": indent,
                "ensure_ascii": ensure_ascii,
                "sort_keys": sort_keys,
                "compact": compact
            }
        }

    except Exception as e:
        return {
            "success": False,
            "action": "write",
            "error": f"Failed to write JSON file: {str(e)}"
        }


def _validate_json(file_path: Optional[str], content: Optional[str], encoding: str) -> Dict[str, Any]:
    """Validate JSON string or file."""
    try:
        if file_path:
            file_obj = Path(file_path)
            if not file_obj.exists():
                return {
                    "success": False,
                    "action": "validate",
                    "error": f"File does not exist: {file_path}"
                }

            with open(file_obj, 'r', encoding=encoding) as f:
                json_str = f.read()
        else:
            json_str = content

        try:
            parsed = json.loads(json_str)
            return {
                "success": True,
                "action": "validate",
                "data": {
                    "valid": True,
                    "file_path": file_path,
                    "size": len(json_str) if json_str else 0,
                    "encoding": encoding if file_path else None,
                    "type": type(parsed).__name__
                }
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "action": "validate",
                "error": f"Invalid JSON: {str(e)}",
                "data": {
                    "valid": False,
                    "error_position": e.pos if hasattr(e, 'pos') else None,
                    "error_line": getattr(e, 'lineno', None),
                    "error_column": getattr(e, 'colno', None)
                }
            }

    except Exception as e:
        return {
            "success": False,
            "action": "validate",
            "error": f"Failed to validate JSON: {str(e)}"
        }


def _format_json(content: str, indent: int, ensure_ascii: bool,
                sort_keys: bool, compact: bool) -> Dict[str, Any]:
    """Format/beautify JSON string."""
    try:
        # Parse the JSON
        parsed = json.loads(content)

        # Format it back
        if compact:
            formatted = json.dumps(parsed, ensure_ascii=ensure_ascii, sort_keys=sort_keys, separators=(',', ':'))
        else:
            formatted = json.dumps(parsed, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys)

        return {
            "success": True,
            "action": "format",
            "data": {
                "formatted_json": formatted,
                "original_size": len(content),
                "formatted_size": len(formatted),
                "indent": indent,
                "ensure_ascii": ensure_ascii,
                "sort_keys": sort_keys,
                "compact": compact
            }
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "action": "format",
            "error": f"Invalid JSON: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "action": "format",
            "error": f"Failed to format JSON: {str(e)}"
        }


def _extract_json_objects(content: str) -> Dict[str, Any]:
    """Extract JSON objects from mixed text."""
    try:
        # Find JSON-like structures using regex
        # Pattern matches objects {...} and arrays [...] with balanced braces/brackets
        json_pattern = r'\{[^{}]*\}|\[[^\[\]]*\]'
        matches = re.findall(json_pattern, content)

        extracted_objects = []
        for match in matches:
            try:
                parsed = json.loads(match)
                extracted_objects.append({
                    "json": parsed,
                    "raw": match,
                    "size": len(match),
                    "type": type(parsed).__name__
                })
            except json.JSONDecodeError:
                # Skip invalid JSON matches
                continue

        return {
            "success": True,
            "action": "extract",
            "data": {
                "objects": extracted_objects,
                "count": len(extracted_objects),
                "total_text_size": len(content)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "action": "extract",
            "error": f"Failed to extract JSON objects: {str(e)}"
        }


def register_json_operations(mcp):
    """Register the JSON operations portmanteau tool with FastMCP."""
    mcp.tool(json_operations)