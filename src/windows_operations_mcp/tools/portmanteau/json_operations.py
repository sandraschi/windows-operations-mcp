"""
JSON Operations - SOTA v15.0 (FastMCP 3.2+ Projected Atomic Tools)

Atomic tools mounted under namespace "winops_json":
  winops_json/read              - Read a JSON file
  winops_json/write             - Write data to a JSON file
  winops_json/validate          - Validate a JSON string
  winops_json/patch             - Deep-merge patch data into an existing JSON file
  winops_json/extract_from_text - Extract JSON blobs from unstructured text
  winops_json/format            - Pretty-print a JSON string
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from windows_operations_mcp.logging_config import get_logger
from windows_operations_mcp.utils import fail_response

logger = get_logger(__name__)


def _read_blocking(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_blocking(path: str, data: Any, indent: int) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def _patch_blocking(path: str, patch_data: dict, indent: int) -> dict:
    existing = {}
    if Path(path).exists():
        with open(path, encoding="utf-8") as f:
            existing = json.load(f)

    def deep_merge(base: dict, patch: dict) -> dict:
        for k, v in patch.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                deep_merge(base[k], v)
            else:
                base[k] = v
        return base

    updated = deep_merge(existing.copy() if isinstance(existing, dict) else {}, patch_data) \
        if isinstance(patch_data, dict) else patch_data
    _write_blocking(path, updated, indent)
    return updated


def register_json_operations(parent_mcp: FastMCP) -> None:
    """Mount atomic JSON operation tools under namespace 'winops_json'."""
    ns = FastMCP(name="winops_json")

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def read(
        path: Annotated[str, Field(description="Path to the JSON file.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Read and parse a JSON file.

        ## Return Format
        ```json
        {"success": bool, "data": any}
        ```

        ## Examples
            read(path="D:\\\\config\\\\settings.json")
        """
        try:
            data = await asyncio.to_thread(_read_blocking, path)
            return {"success": True, "data": data}
        except FileNotFoundError:
            return fail_response(f"File not found: {path}")
        except json.JSONDecodeError as e:
            return fail_response(f"Invalid JSON: {e}",
                    suggestions=["Use winops_json/validate to check the file first."])

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def write(
        path: Annotated[str, Field(description="Destination file path.")],
        data: Annotated[Any, Field(description="Data to serialise as JSON.")],
        indent: Annotated[int, Field(description="Indentation spaces.", ge=0, le=8)] = 2,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Write data to a JSON file, creating parent directories as needed.

        ## Return Format
        ```json
        {"success": bool, "path": str}
        ```

        ## Examples
            write(path="D:\\\\config\\\\settings.json", data={"debug": true})
        """
        try:
            await asyncio.to_thread(_write_blocking, path, data, indent)
            return {"success": True, "path": path}
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def validate(
        text: Annotated[str, Field(description="JSON string to validate.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Validate whether a string is valid JSON.

        ## Return Format
        ```json
        {"success": true, "valid": bool, "error": str | null}
        ```

        ## Examples
            validate(text='{\"key\": \"value\"}')
        """
        try:
            json.loads(text)
            return {"success": True, "valid": True, "error": None}
        except json.JSONDecodeError as e:
            return {"success": True, "valid": False, "error": str(e)}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def patch(
        path: Annotated[str, Field(description="JSON file to patch.")],
        data: Annotated[dict, Field(description="Dict of keys to deep-merge into the existing file.")],
        indent: Annotated[int, Field(description="Indentation spaces.", ge=0, le=8)] = 2,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Deep-merge patch data into an existing JSON file (creates file if missing).

        ## Return Format
        ```json
        {"success": bool, "path": str, "updated_keys": [str]}
        ```

        ## Examples
            patch(path="D:\\\\config\\\\app.json", data={"logging": {"level": "DEBUG"}})
        """
        try:
            updated = await asyncio.to_thread(_patch_blocking, path, data, indent)
            return {"success": True, "path": path,
                    "updated_keys": list(updated.keys()) if isinstance(updated, dict) else []}
        except Exception as e:
            return fail_response(str(e))

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def extract_from_text(
        text: Annotated[str, Field(description="Unstructured text that may contain JSON blobs.")],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Extract all valid JSON objects/arrays found in unstructured text.

        ## Return Format
        ```json
        {"success": true, "found": int, "items": [any]}
        ```

        ## Examples
            extract_from_text(text="log output: {\\\"status\\\": 200} and more text")
        """
        results = []
        for blob in re.findall(r"(\{.*?\}|\[.*?\])", text, re.DOTALL):
            try:
                results.append(json.loads(blob))
            except Exception:
                continue
        return {"success": True, "found": len(results), "items": results}

    @ns.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False))
    async def format(
        text: Annotated[str, Field(description="JSON string to pretty-print.")],
        indent: Annotated[int, Field(description="Indentation spaces.", ge=0, le=8)] = 2,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Parse and pretty-print a JSON string.

        ## Return Format
        ```json
        {"success": bool, "formatted": str}
        ```

        ## Examples
            format(text='{\"a\":1,\"b\":2}')
        """
        try:
            obj = json.loads(text)
            return {"success": True, "formatted": json.dumps(obj, indent=indent, ensure_ascii=False)}
        except json.JSONDecodeError as e:
            return fail_response(str(e),
                    suggestions=["Use winops_json/validate first to locate syntax errors."])

    parent_mcp.mount(ns, prefix="winops_json")
    logger.info("Mounted atomic tools: winops_json/read, /write, /validate, /patch, /extract_from_text, /format")
