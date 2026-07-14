"""
JSON Tools Module

Provides utilities for working with JSON files and data, including reading, writing,
validating, and manipulating JSON content with proper error handling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

from windows_operations_mcp.utils import fail_response

from ..decorators import tool

T = TypeVar("T")


def read_json_file(file_path: str | Path) -> dict | list:
    """
    Read and parse a JSON file, returning its contents as a Python dictionary or list.

    Args:
        file_path: Path to the JSON file (as string or Path object)

    Returns:
        Union[Dict, List]: Parsed JSON data as a Python dictionary or list

    Raises:
        FileNotFoundError: If the specified file does not exist
        json.JSONDecodeError: If the file contains invalid JSON
        PermissionError: If there are insufficient permissions to read the file
        OSError: For other file-related errors
    """
    try:
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {e!s}", e.doc, e.pos) from e
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied when reading file: {file_path}")
    except OSError as e:
        raise OSError(f"Error reading file {file_path}: {e!s}")


def write_json_file(
    data: Any,
    file_path: str | Path,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
    create_dirs: bool = True,
) -> None:
    """
    Write data to a JSON file with proper error handling.

    Args:
        data: Data to be serialized to JSON
        file_path: Path where to save the JSON file
        indent: Number of spaces for indentation (use None for compact output)
        ensure_ascii: If False, non-ASCII characters will be output as-is
        sort_keys: If True, output dictionaries will be sorted by key
        create_dirs: If True, create parent directories if they don't exist

    Raises:
        PermissionError: If there are insufficient permissions to write to the file
        OSError: For other file-related errors
        TypeError: If the data is not JSON serializable
    """
    try:
        file_path = Path(file_path) if isinstance(file_path, str) else file_path

        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys, default=_json_serializer)
    except (TypeError, ValueError) as e:
        raise TypeError(f"Data is not JSON serializable: {e!s}") from e
    except PermissionError:
        raise PermissionError(f"Permission denied when writing to file: {file_path}")
    except OSError as e:
        raise OSError(f"Error writing to file {file_path}: {e!s}")


@tool(
    name="validate_json",
    description="Validate if a string is valid JSON",
    parameters={"json_str": {"type": "string", "description": "String to validate as JSON"}},
    returns={"type": "object", "properties": {"valid": {"type": "boolean"}}},
)
def validate_json(json_str: str) -> dict[str, Any]:
    """
    Validate if a string is valid JSON.

    Args:
        json_str: String to validate as JSON

    Returns:
        Dict[str, Any]: Dictionary with validation result
    """
    try:
        json.loads(json_str)
        return {"valid": True, "success": True}
    except json.JSONDecodeError:
        return {"valid": False, "success": True}


def merge_json(*json_objects: dict) -> dict:
    """
    Deep merge multiple JSON objects (dictionaries) together.

    Args:
        *json_objects: Variable number of dictionaries to merge

    Returns:
        Dict: A new dictionary containing the merged result

    Example:
        >>> a = {"a": 1, "b": {"x": 10}}
        >>> b = {"b": {"y": 20}, "c": 30}
        >>> merge_json(a, b)
        {'a': 1, 'b': {'x': 10, 'y': 20}, 'c': 30}
    """
    result = {}
    for obj in json_objects:
        if not isinstance(obj, dict):
            continue

        for key, value in obj.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_json(result[key], value)
            else:
                result[key] = value
    return result


def json_to_string(data: Any, indent: int = 2, ensure_ascii: bool = False, sort_keys: bool = False) -> str:
    """
    Convert a Python object to a formatted JSON string.

    Args:
        data: Python object to convert to JSON
        indent: Number of spaces for indentation
        ensure_ascii: If False, non-ASCII characters will be output as-is
        sort_keys: If True, output dictionaries will be sorted by key

    Returns:
        str: Formatted JSON string

    Raises:
        TypeError: If the data is not JSON serializable
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys, default=_json_serializer)
    except (TypeError, ValueError) as e:
        raise TypeError(f"Data is not JSON serializable: {e!s}") from e


def _json_serializer(obj: Any) -> Any:
    """
    Custom JSON serializer for objects not serializable by default.

    Args:
        obj: Object to serialize

    Returns:
        A JSON-serializable representation of the object

    Raises:
        TypeError: If the object type is not supported
    """
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    elif isinstance(obj, (set, frozenset)):
        return list(obj)
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    elif hasattr(obj, "to_json"):
        return obj.to_json()
    else:
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


# Example usage
if __name__ == "__main__":
    # Example usage of the JSON tools
    try:
        # Example data
        data = {
            "name": "Example",
            "value": 42,
            "nested": {"items": [1, 2, 3], "active": True},
            "timestamp": datetime.now(),
        }

        # Write to file
        write_json_file(data, "example.json", indent=2)

        # Read from file
        loaded_data = read_json_file("example.json")

        # Validate JSON
        json_str = '{"test": "value"}'
        validate_json(json_str)

        # Merge JSON objects
        merged = merge_json({"a": 1, "b": {"x": 10}}, {"b": {"y": 20}, "c": 30})

    except Exception:
        pass


@tool(
    name="format_json_string",
    description="Format a JSON string with proper indentation",
    parameters={
        "json_str": {"type": "string", "description": "JSON string to format"},
        "indent": {"type": "integer", "description": "Number of spaces for indentation", "default": 2},
        "sort_keys": {"type": "boolean", "description": "Whether to sort dictionary keys", "default": False},
    },
    returns={"type": "object", "properties": {"formatted": {"type": "string"}}},
)
def format_json_string(json_str: str, indent: int = 2, sort_keys: bool = False) -> dict[str, Any]:
    """
    Format a JSON string with proper indentation.

    Args:
        json_str: JSON string to format
        indent: Number of spaces for indentation
        sort_keys: Whether to sort dictionary keys

    Returns:
        Dict[str, Any]: Dictionary with formatted JSON
    """
    try:
        parsed = json.loads(json_str)
        formatted = json.dumps(parsed, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
        return {"formatted": formatted, "success": True}
    except json.JSONDecodeError as e:
        return fail_response(message=f"Invalid JSON: {e!s}")


def convert_to_json(data: Any, indent: int | None = None) -> str:
    """
    Convert a Python object to a JSON string.

    Args:
        data: Python object to convert
        indent: Number of spaces for indentation (None for compact output)

    Returns:
        JSON string representation of the data
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def extract_json_from_text(text: str) -> list[dict]:
    """
    Extract JSON objects from a text string.

    Args:
        text: Text potentially containing JSON objects

    Returns:
        List of extracted JSON objects as dictionaries
    """
    import re

    # Pattern to match JSON objects and arrays
    json_pattern = r"(\{.*?\}|\[.*?\])"

    results = []
    for match in re.finditer(json_pattern, text, re.DOTALL):
        try:
            json_obj = json.loads(match.group(0))
            results.append(json_obj)
        except json.JSONDecodeError:
            continue

    return results
