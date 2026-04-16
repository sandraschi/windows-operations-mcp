"""
Structured logging configuration for Windows Operations MCP.

This module configures structured logging using the structlog library,
integrated with FastMCP 2.x patterns for consistent and structured logging.
"""

import datetime
import logging
import logging.config
import os
import platform
import sys
import threading
import uuid

import structlog
from structlog.types import EventDict, Processor, WrappedLogger

# Type aliases
LogLevel = str | int

# Constants
SERVICE_NAME = "windows-operations-mcp"
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_JSON = os.getenv("LOG_JSON", "false").lower() == "true"

# Thread-local storage for request context
_thread_local = threading.local()


class RequestIdFilter(logging.Filter):
    """
    A logging filter that adds a request_id to log records.

    The request_id can be set in the logging context or will be automatically
    generated if not present.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            # Try to get request_id from thread-local storage
            if hasattr(_thread_local, "request_id"):
                record.request_id = _thread_local.request_id
            # Try to get from context
            elif hasattr(record, "context") and "request_id" in record.context:
                record.request_id = record.context["request_id"]
            else:
                record.request_id = str(uuid.uuid4())
        return True


class RequestContext:
    """Context manager for managing request context in logs."""

    def __init__(self, request_id: str | None = None, **context_vars):
        self.request_id = request_id or str(uuid.uuid4())
        self.context_vars = context_vars
        self.old_context = {}

    def __enter__(self):
        # Save old context
        if hasattr(_thread_local, "request_id"):
            self.old_context["request_id"] = _thread_local.request_id

        # Set new context
        _thread_local.request_id = self.request_id
        for key, value in self.context_vars.items():
            self.old_context[key] = getattr(_thread_local, key, None)
            setattr(_thread_local, key, value)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old context
        if "request_id" in self.old_context:
            _thread_local.request_id = self.old_context["request_id"]

        for key, value in self.old_context.items():
            if key != "request_id":
                if value is not None:
                    setattr(_thread_local, key, value)
                else:
                    try:
                        delattr(_thread_local, key)
                    except AttributeError:
                        pass


def add_service_context(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add service context to log events.

    Args:
        logger: The logger instance
        method_name: The log method name (e.g., 'info', 'error')
        event_dict: Current context and event info

    Returns:
        Updated event dictionary with service context
    """
    event_dict["service"] = SERVICE_NAME

    # Add process and thread info
    event_dict["pid"] = os.getpid()
    event_dict["host"] = platform.node()

    # Add timestamp in ISO 8601 format with timezone
    event_dict["timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()

    # Add request ID if available
    if hasattr(_thread_local, "request_id"):
        event_dict["request_id"] = _thread_local.request_id

    # Add thread information
    event_dict["thread_id"] = threading.get_ident()
    event_dict["thread_name"] = threading.current_thread().name

    # Add Python version and platform info
    event_dict["python"] = {
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "compiler": platform.python_compiler(),
    }

    # Add OS/platform information
    event_dict["os"] = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
    }

    # Add thread information
    try:
        thread_id = threading.get_ident()
    except AttributeError:
        # Fallback for older Python versions
        try:
            thread_id = logging.get_ident()
        except AttributeError:
            # Last resort fallback
            thread_id = threading.current_thread().ident

    event_dict["thread"] = thread_id

    # Add correlation ID if available
    if not event_dict.get("correlation_id"):
        event_dict["correlation_id"] = os.getenv("CORRELATION_ID", "")

    return event_dict


def drop_debug_logs(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict | str:
    """Filter out debug logs in production."""
    if method_name == "debug" and os.getenv("ENVIRONMENT") == "production":
        return ""
    return event_dict


def setup_logging(level: LogLevel = DEFAULT_LOG_LEVEL) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Logging level as string or int (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if isinstance(level, str):
        level = level.upper()

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=level,
    )

    # Common processors for both development and production
    processors: list[Processor] = [
        # Add log level and timestamp
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        # Add context variables
        structlog.contextvars.merge_contextvars,
        # Add service context
        add_service_context,
        # Handle stack info and exceptions
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        # Filter debug logs in production
        drop_debug_logs,
        # Decode bytes to unicode
        structlog.processors.UnicodeDecoder(),
    ]

    # Add pretty printing in development
    if os.getenv("ENVIRONMENT") == "development":
        processors.extend([structlog.dev.ConsoleRenderer()])
    else:
        # In production, use JSON format
        processors.append(structlog.processors.JSONRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            level if isinstance(level, int) else logging.getLevelName(level)
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Add request ID filter to all handlers
    for handler in root_logger.handlers:
        handler.addFilter(RequestIdFilter())


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__ of the calling module)

    Returns:
        A configured structlog logger instance
    """
    return structlog.get_logger(name or __name__)


# Initialize logging when module is imported
setup_logging()

# Public API
__all__ = ["get_logger", "setup_logging"]
