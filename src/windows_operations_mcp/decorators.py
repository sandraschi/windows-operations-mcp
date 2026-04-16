"""
Decorators for Windows Operations MCP tools.

This module provides thread-safe decorators for adding consistent logging,
error handling, rate limiting, and input validation to tool functions.
"""

import functools
import os
import re
import threading
import time
import traceback
from collections import deque
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar, cast

from .logging_config import get_logger

# Type variables for generic function typing
F = TypeVar("F", bound=Callable[..., Any])

logger = get_logger(__name__)

# Thread-local storage for rate limiting
thread_local = threading.local()


class RateLimiter:
    """Thread-safe rate limiter implementation."""

    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: dict[str, deque[float]] = {}
        self.lock = threading.RLock()

    def is_allowed(self, key: str) -> tuple[bool, float]:
        """Check if a call is allowed and return remaining time if not."""
        now = time.monotonic()

        with self.lock:
            # Initialize the queue for this key if it doesn't exist
            if key not in self.calls:
                self.calls[key] = deque(maxlen=self.max_calls)

            calls = self.calls[key]

            # Remove calls outside the time window
            while calls and calls[0] <= now - self.time_window:
                calls.popleft()

            # Check if we've reached the rate limit
            if len(calls) >= self.max_calls:
                return False, (calls[0] + self.time_window) - now

            # Add the current call to the queue
            calls.append(now)
            return True, 0.0


def tool(
    name: str | None = None,
    description: str | None = None,
    parameters: dict[str, dict[str, Any]] | None = None,
    required: list[str] | None = None,
    returns: dict[str, Any] | None = None,
    rate_limit: tuple[int, int] | None = None,
    **kwargs,
):
    """
    Enhanced decorator for tool functions with comprehensive metadata.

    Features:
    - Comprehensive function metadata for better documentation and discovery
    - Input parameter validation
    - Rate limiting
    - Execution time tracking
    - Structured logging
    - Standardized error handling

    Args:
        name: Tool name (defaults to function name)
        description: Detailed description of the tool's purpose
        parameters: Dictionary of parameter schemas
        required: List of required parameter names
        returns: Schema for the return value
        rate_limit: Optional tuple of (max_calls, time_window)

    Example:
        @tool(
            name="example_tool",
            description="Example tool with comprehensive metadata",
            parameters={
                "param1": {
                    "type": "string",
                    "description": "First parameter"
                },
                "param2": {
                    "type": "integer",
                    "description": "Second parameter"
                }
            },
            required=["param1"],
            returns={
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "status": {"type": "string"}
                }
            },
            rate_limit=(100, 60)  # 100 calls per minute
        )
        def example_tool(param1: str, param2: int = 42) -> Dict[str, Any]:
            return {"result": f"Processed {param1} with {param2}", "status": "success"}
    """

    def decorator(func: F) -> F:
        # Set default values if not provided
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or ""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            # Get function name and module for logging
            module_name = func.__module__.split(".")[-1]
            call_id = f"{module_name}.{tool_name}.{int(time.time() * 1000)}"

            # Log function call with metadata
            logger.info(
                "tool_call_started",
                tool=tool_name,
                module=module_name,
                call_id=call_id,
                parameters={
                    k: "[REDACTED]" if k.lower().endswith(("password", "secret", "key")) else v
                    for k, v in kwargs.items()
                },
                metadata={
                    "name": tool_name,
                    "description": tool_description,
                    "parameters": parameters,
                    "required": required,
                    "returns": returns,
                },
            )

            start_time = time.monotonic()

            try:
                # Apply rate limiting if specified
                if rate_limit:
                    max_calls, time_window = rate_limit
                    limiter = get_rate_limiter(tool_name, max_calls, time_window)
                    allowed, wait_time = limiter.is_allowed(tool_name)
                    if not allowed:
                        raise RuntimeError(f"Rate limit exceeded. Try again in {wait_time:.1f} seconds.")

                # Call the original function
                result = func(*args, **kwargs)

                # Calculate execution time
                exec_time = time.monotonic() - start_time

                # Log successful completion
                logger.info(
                    "tool_call_completed",
                    tool=tool_name,
                    module=module_name,
                    call_id=call_id,
                    execution_time_seconds=round(exec_time, 4),
                    success=True,
                )

                # Ensure result is a dictionary with standard fields
                if not isinstance(result, dict):
                    result = {"result": result}

                # Add metadata to the result
                result.update(
                    {
                        "_metadata": {
                            "tool": tool_name,
                            "module": module_name,
                            "call_id": call_id,
                            "execution_time_seconds": round(exec_time, 4),
                            "success": True,
                        }
                    }
                )

                return result

            except Exception as e:
                # Calculate execution time for failed call
                exec_time = time.monotonic() - start_time

                # Log the error
                logger.error(
                    "tool_call_failed",
                    tool=tool_name,
                    module=module_name,
                    call_id=call_id,
                    execution_time_seconds=round(exec_time, 4),
                    error=str(e),
                    error_type=type(e).__name__,
                    traceback=traceback.format_exc(),
                    success=False,
                )

                # Return error in standard format
                return {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "success": False,
                    "_metadata": {
                        "tool": tool_name,
                        "module": module_name,
                        "call_id": call_id,
                        "execution_time_seconds": round(exec_time, 4),
                    },
                }

        # Add metadata to the function for introspection
        wrapper._tool_metadata = {
            "name": tool_name,
            "description": tool_description,
            "parameters": parameters or {},
            "required": required or [],
            "returns": returns or {},
            "rate_limit": rate_limit,
        }

        return cast(F, wrapper)

    return decorator


def validate_inputs(*validators: Callable[..., tuple[bool, str]]) -> Callable[[F], F]:
    """
    Decorator to validate input parameters with detailed error messages.

    Args:
        *validators: Validation functions that take the function arguments
                     and return a tuple of (is_valid: bool, error_message: str)

    Example:
        @validate_inputs(
            lambda x: (x > 0, "Value must be positive"),
            lambda x: (x < 100, "Value must be less than 100")
        )
        def my_function(x):
            return {"result": x * 2}
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            # Run all validators and collect error messages
            errors: list[str] = []

            for validator in validators:
                try:
                    is_valid, error_msg = validator(*args, **kwargs)
                    if not is_valid:
                        errors.append(error_msg)
                except Exception as e:
                    errors.append(f"Validation error: {e!s}")

            # If there are validation errors, return them
            if errors:
                return {
                    "success": False,
                    "error": "Input validation failed",
                    "error_type": "ValidationError",
                    "validation_errors": errors,
                    "tool": func.__name__,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # All validations passed, call the function
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


# Global rate limiters
_rate_limiters: dict[tuple[str, int, int], RateLimiter] = {}
_rate_limiters_lock = threading.Lock()


def get_rate_limiter(key: str, max_calls: int, time_window: int) -> RateLimiter:
    """Get or create a rate limiter for the given key and parameters."""
    cache_key = (key, max_calls, time_window)

    # Double-checked locking pattern for thread safety
    if cache_key not in _rate_limiters:
        with _rate_limiters_lock:
            if cache_key not in _rate_limiters:
                _rate_limiters[cache_key] = RateLimiter(max_calls, time_window)

    return _rate_limiters[cache_key]


def rate_limited(max_calls: int, time_window: int, key: str = "default") -> Callable[[F], F]:
    """
    Thread-safe decorator to limit the rate of function calls.

    Args:
        max_calls: Maximum number of calls allowed in the time window
        time_window: Time window in seconds
        key: Optional key to group rate limits (default: function name)
    """

    def decorator(func: F) -> F:
        # Use function name as the default key if not provided
        limiter_key = key if key != "default" else func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            # Get the rate limiter for this function/limit
            limiter = get_rate_limiter(limiter_key, max_calls, time_window)

            # Check if the call is allowed
            allowed, retry_after = limiter.is_allowed(limiter_key)

            if not allowed:
                return {
                    "success": False,
                    "error": "Rate limit exceeded",
                    "error_type": "RateLimitError",
                    "retry_after_seconds": round(retry_after, 2),
                    "tool": func.__name__,
                    "max_calls": max_calls,
                    "time_window_seconds": time_window,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Call the original function
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def log_execution(log_name: str | None = None) -> Callable[[F], F]:
    """
    Decorator to log detailed function execution metrics.

    Args:
        log_name: Optional base name for log messages (defaults to function name)
    """

    def decorator(func: F) -> F:
        nonlocal log_name
        if log_name is None:
            log_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            # Generate a unique ID for this execution
            call_id = f"{int(time.time() * 1000)}-{threading.get_ident()}"
            start_time = time.monotonic()

            # Log function start
            logger.info(
                f"{log_name}.started",
                call_id=call_id,
                function=func.__name__,
                module=func.__module__,
                thread_id=threading.get_ident(),
                timestamp=datetime.utcnow().isoformat(),
                has_args=bool(args),
                has_kwargs=bool(kwargs),
            )

            try:
                # Call the original function
                result = func(*args, **kwargs)
                exec_time = time.monotonic() - start_time

                # Log successful completion
                logger.info(
                    f"{log_name}.completed",
                    call_id=call_id,
                    function=func.__name__,
                    execution_time_seconds=round(exec_time, 4),
                    success=True,
                    has_result=result is not None,
                )
                return result

            except Exception as e:
                # Log the error with context
                exec_time = time.monotonic() - start_time
                error_type = e.__class__.__name__

                logger.error(
                    f"{log_name}.failed",
                    call_id=call_id,
                    function=func.__name__,
                    error_type=error_type,
                    error=str(e),
                    execution_time_seconds=round(exec_time, 4),
                    exc_info=True,
                )

                # Re-raise the exception to be handled by the tool_decorator
                raise

        return cast(F, wrapper)

    return decorator


# Enhanced Validators


def is_positive_number(value: Any) -> tuple[bool, str]:
    """
    Validate that a value is a positive number.

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not isinstance(value, (int, float)):
        return False, f"Expected a number, got {type(value).__name__}"
    if value <= 0:
        return False, f"Value must be positive, got {value}"
    return True, ""


def is_valid_path(path: str, check_readable: bool = False, check_writable: bool = False) -> tuple[bool, str]:
    """
    Validate that a path exists and is accessible.

    Args:
        path: The path to validate
        check_readable: If True, check that the path is readable
        check_writable: If True, check that the path is writable

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not isinstance(path, str):
        return False, f"Path must be a string, got {type(path).__name__}"

    try:
        if not os.path.exists(path):
            return False, f"Path does not exist: {path}"

        if check_readable and not os.access(path, os.R_OK):
            return False, f"Path is not readable: {path}"

        if check_writable and not os.access(path, os.W_OK):
            return False, f"Path is not writable: {path}"

        return True, ""

    except Exception as e:
        return False, f"Error validating path {path}: {e!s}"


# Additional validators
def is_valid_port(port: Any) -> tuple[bool, str]:
    """Validate that a port number is in the valid range (1-65535)."""
    if not isinstance(port, int):
        return False, f"Port must be an integer, got {type(port).__name__}"
    if port < 1 or port > 65535:
        return False, f"Port must be between 1 and 65535, got {port}"
    return True, ""


def is_safe_command(command: str) -> tuple[bool, str]:
    """
    Validate that a command doesn't contain potentially dangerous patterns.

    Returns:
        Tuple of (is_safe: bool, error_message: str)
    """
    if not isinstance(command, str):
        return False, "Command must be a string"

    dangerous_patterns = [
        (r"[;&|]", "Command chaining is not allowed"),
        (r"`", "Backticks are not allowed"),
        (r"\$\s*\{", "Variable expansion is not allowed"),
        (r"\$\s*\(", "Command substitution is not allowed"),
        (r"\|\s*[&;]", "Command chaining after pipe is not allowed"),
        (r"\b(rm|mv|dd|shred|mkfs|fdisk|mkfs\.|/dev/)\b", "Dangerous command detected"),
    ]

    for pattern, message in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Security violation: {message}"

    return True, ""
