"""
Common utility functions for Windows Operations MCP.
"""

from typing import Any

from .command_executor import ProcessOutput


def get_execution_result(output: ProcessOutput | dict[str, Any]) -> dict[str, Any]:
    """
    Convert a ProcessOutput object or dict to a standardized result dictionary.

    Args:
        output: A ProcessOutput instance or dictionary with command results

    Returns:
        Dictionary with standardized result fields
    """
    if isinstance(output, ProcessOutput):
        return output.to_dict()
    elif isinstance(output, dict):
        return {
            "success": output.get("exit_code", -1) == 0 and not output.get("error"),
            "stdout": output.get("stdout", ""),
            "stderr": output.get("stderr", ""),
            "exit_code": output.get("exit_code", -1),
            "error": output.get("error"),
            "execution_time": output.get("execution_time", 0.0),
        }
    else:
        return {
            "success": False,
            "error": f"Unexpected output type: {type(output).__name__}",
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
        }
