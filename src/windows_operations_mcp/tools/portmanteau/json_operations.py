"""
JSON Operations Portmanteau - SOTA v14.0 (FastMCP 3.2+)
Provides specialized JSON data handling: Deep Patching, Text Extraction, and Validation.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from fastmcp import Context
from windows_operations_mcp.logging_config import get_logger

logger = get_logger(__name__)

async def json_operations(
    action: Literal["read", "write", "validate", "patch", "extract_from_text", "format"],
    path: Optional[str] = None,
    data: Optional[Any] = None,
    text: Optional[str] = None,
    indent: int = 2,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Perform specialized JSON data operations with agentic telemetry.

    RATIONALE:
    Agents often need to "patch" existing configs or extract JSON from unstructured logs.
    This portmanteau provides the specialized logic required for high-level data surgery.

    Args:
        action: The JSON operation to perform.
        path: File path for read/write/patch operations.
        data: Data to write or merge (for "write"/"patch").
        text: Raw text to extract JSON from (for "extract_from_text").
        indent: Indentation for formatting.
        ctx: FastMCP Context for telemetry and sampling.
    """
    if ctx:
        ctx.info(f"JSON Op: {action}")
        ctx.report_progress(10, 100)

    try:
        if action == "read":
            if not path:
                return {"success": False, "error": "Path required for read"}
            content = await asyncio.to_thread(_read_json, path)
            return {"success": True, "action": action, "data": content}

        if action == "write":
            if not path or data is None:
                return {"success": False, "error": "Path and data required for write"}
            await asyncio.to_thread(_write_json, path, data, indent)
            return {"success": True, "action": action, "data": {"status": "Written"}}

        if action == "validate":
            if text is None:
                return {"success": False, "error": "Text required for validate"}
            valid, error = _validate_json(text)
            return {"success": True, "action": action, "data": {"valid": valid, "error": error}}

        if action == "patch":
            if not path or data is None:
                return {"success": False, "error": "Path and data required for patch"}
            updated = await asyncio.to_thread(_patch_json, path, data, indent)
            return {"success": True, "action": action, "data": {"status": "Patched", "updated_keys": list(updated.keys())}}

        if action == "extract_from_text":
            if text is None:
                return {"success": False, "error": "Text required for extract"}
            results = _extract_json(text)
            return {"success": True, "action": action, "data": {"found": len(results), "items": results}}

        if action == "format":
            if text is None:
                return {"success": False, "error": "Text required for format"}
            # Parse logic: if text is a string, load it. If it's already an object, use it directly.
            try:
                obj = json.loads(text)
            except Exception:
                return {"success": False, "error": "Invalid JSON text provided for format"}
            formatted = json.dumps(obj, indent=indent, ensure_ascii=False)
            return {"success": True, "action": action, "data": {"formatted": formatted}}

        return {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        error_msg = f"JSON Error: {e}"
        if ctx:
            ctx.error(error_msg)
            try:
                advice = await ctx.sample(f"JSON operation '{action}' failed. Error: {e}. Suggest repair or alternative.", max_tokens=100)
                if advice and advice.content:
                    return {"success": False, "error": error_msg, "sampling_advice": advice.content[0].text}
            except Exception:
                pass
        return {"success": False, "error": error_msg}
    finally:
        if ctx:
            ctx.report_progress(100, 100)

def _read_json(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _write_json(path: str, data: Any, indent: int) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def _validate_json(text: str) -> Tuple[bool, Optional[str]]:
    try:
        json.loads(text)
        return True, None
    except Exception as e:
        return False, str(e)

def _patch_json(path: str, patch_data: Dict, indent: int) -> Dict:
    if not Path(path).exists():
        existing = {}
    else:
        with open(path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    
    if not isinstance(existing, dict) or not isinstance(patch_data, dict):
        updated = patch_data
    else:
        updated = _deep_merge(existing.copy(), patch_data)
    
    _write_json(path, updated, indent)
    return updated

def _deep_merge(base: Dict, patch: Dict) -> Dict:
    for key, value in patch.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base

def _extract_json(text: str) -> List[Any]:
    results = []
    # Heuristic for finding JSON blobs in unstructured text
    potential_blobs = re.findall(r'(\{.*?\}|\[.*?\])', text, re.DOTALL)
    for blob in potential_blobs:
        try:
            results.append(json.loads(blob))
        except Exception:
            continue
    return results

def register_json_operations(mcp) -> None:
    """Register the modernized JSON operations tool."""
    mcp.tool()(json_operations)