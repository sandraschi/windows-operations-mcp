"""
JSON Tools Module

Provides utilities for working with JSON files and data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union, Optional

from ..utils.extended_command_executor import ExtendedCommandExecutor

def read_json_file(file_path: Union[str, Path]) -> Union[Dict, List]:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data (dict or list)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(
    file_path: Union[str, Path], 
    data: Any, 
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    """
    Write data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to write (must be JSON-serializable)
        indent: Number of spaces for indentation
        ensure_ascii: If True, escape non-ASCII characters
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

def validate_json(json_str: str) -> bool:
    """
    Check if a string is valid JSON.
    
    Args:
        json_str: String to validate
        
    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def format_json_string(
    json_str: str, 
    indent: int = 2, 
    sort_keys: bool = False
) -> str:
    """
    Format a JSON string with proper indentation.
    
    Args:
        json_str: JSON string to format
        indent: Number of spaces for indentation
        sort_keys: Whether to sort dictionary keys
        
    Returns:
        Formatted JSON string
        
    Raises:
        json.JSONDecodeError: If the input is not valid JSON
    """
    parsed = json.loads(json_str)
    return json.dumps(parsed, indent=indent, sort_keys=sort_keys, ensure_ascii=False)

def convert_to_json(data: Any, indent: Optional[int] = None) -> str:
    """
    Convert a Python object to a JSON string.
    
    Args:
        data: Python object to convert
        indent: Number of spaces for indentation (None for compact output)
        
    Returns:
        JSON string representation of the data
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)

def extract_json_from_text(text: str) -> List[Dict]:
    """
    Extract JSON objects from a text string.
    
    Args:
        text: Text potentially containing JSON objects
        
    Returns:
        List of extracted JSON objects as dictionaries
    """
    import re
    
    # Pattern to match JSON objects and arrays
    json_pattern = r'(\{.*?\}|\[.*?\])'
    
    results = []
    for match in re.finditer(json_pattern, text, re.DOTALL):
        try:
            json_obj = json.loads(match.group(0))
            results.append(json_obj)
        except json.JSONDecodeError:
            continue
            
    return results
