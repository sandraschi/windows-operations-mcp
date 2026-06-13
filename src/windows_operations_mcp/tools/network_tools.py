"""
Network operations tools for Windows Operations MCP.

This module provides tools for network operations with structured logging,
input validation, and security checks.
"""

import re
import socket
import time
from typing import Any

from ..decorators import tool
from ..logging_config import get_logger
from ..utils import fail_response

# Initialize structured logger
logger = get_logger(__name__)

# Constants
MAX_PORT_NUMBER = 65535
DEFAULT_TIMEOUT = 5  # seconds
MAX_TIMEOUT = 300  # 5 minutes
SUPPORTED_PROTOCOLS = ["tcp", "udp"]


def _validate_network_inputs(host: str, port: int, timeout_seconds: int, protocol: str) -> tuple[bool, str | None]:
    """
    Validate network tool input parameters.

    Args:
        host: Hostname or IP address to validate
        port: Port number to validate
        timeout_seconds: Timeout in seconds to validate
        protocol: Protocol to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate host
    if not host or not isinstance(host, str):
        return False, "Host must be a non-empty string"

    # Basic hostname/IP validation
    if not re.match(r"^[a-zA-Z0-9.-]+$", host):
        return False, f"Invalid hostname or IP address: {host}"

    # Validate port
    if not isinstance(port, int) or not (0 < port <= MAX_PORT_NUMBER):
        return False, f"Port must be an integer between 1 and {MAX_PORT_NUMBER}"

    # Validate timeout
    if not isinstance(timeout_seconds, (int, float)) or not (0 < timeout_seconds <= MAX_TIMEOUT):
        return False, f"Timeout must be a number between 1 and {MAX_TIMEOUT} seconds"

    # Validate protocol
    if protocol.lower() not in SUPPORTED_PROTOCOLS:
        return False, f"Unsupported protocol: {protocol}. Must be one of: {', '.join(SUPPORTED_PROTOCOLS)}"

    return True, None


def _resolve_host(host: str) -> tuple[bool, str, str | None]:
    """
    Resolve a hostname to an IP address.

    Args:
        host: Hostname or IP address to resolve

    Returns:
        Tuple of (success, result, error_message)
    """
    try:
        # Check if host is already an IP address
        try:
            socket.inet_pton(socket.AF_INET, host)
            return True, host, None
        except OSError:
            try:
                socket.inet_pton(socket.AF_INET6, host)
                return True, host, None
            except OSError:
                pass  # Not an IP address, continue with hostname resolution

        # Resolve hostname
        ip_address = socket.gethostbyname(host)
        return True, ip_address, None

    except socket.gaierror as e:
        return False, host, f"Failed to resolve host: {e}"
    except Exception as e:
        return False, host, f"Unexpected error resolving host: {e}"


def _test_tcp_port(ip: str, port: int, timeout_seconds: int, start_time: float) -> dict[str, Any]:
    """Test TCP port connectivity."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_seconds)

        connect_start = time.time()
        result = sock.connect_ex((ip, port))
        connect_time = time.time() - connect_start

        sock.close()

        if result == 0:
            return {
                "success": True,
                "status": "open",
                "connect_time": round(connect_time, 3),
                "message": f"TCP port {port} is open",
            }
        else:
            return fail_response(f"TCP port {port} is closed or filtered", status="closed", connect_time=round(connect_time, 3), error_code=result)

    except TimeoutError:
        return fail_response(f"TCP connection to port {port} timed out after {timeout_seconds} seconds", status="timeout")
    except Exception as e:
        return fail_response(f"TCP test failed: {e!s}", status="error")


def _test_udp_port(ip: str, port: int, timeout_seconds: int, start_time: float) -> dict[str, Any]:
    """Test UDP port connectivity (limited - sends a packet and checks for response)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout_seconds)

        # Send a small packet
        test_data = b"test"
        send_start = time.time()
        sock.sendto(test_data, (ip, port))

        try:
            # Try to receive a response
            data, _addr = sock.recvfrom(1024)
            response_time = time.time() - send_start
            sock.close()

            return {
                "success": True,
                "status": "responding",
                "response_time": round(response_time, 3),
                "message": f"UDP port {port} is responding",
                "response_size": len(data),
            }

        except TimeoutError:
            # No response doesn't necessarily mean the port is closed for UDP
            sock.close()
            return {
                "success": True,
                "status": "no_response",
                "message": f"UDP port {port} - no response (port may be open but service doesn't respond)",
            }

    except Exception as e:
        return fail_response(f"UDP test failed: {e!s}", status="error")


@tool(
    name="test_port",
    description="Test network port accessibility with detailed diagnostics",
    parameters={
        "host": {"type": "string", "description": "Hostname or IP address to test"},
        "port": {"type": "integer", "description": "Port number to test (1-65535)"},
        "timeout_seconds": {"type": "integer", "description": "Connection timeout in seconds (1-300)", "default": 30},
        "protocol": {"type": "string", "description": "Protocol to test (tcp or udp)", "default": "tcp"},
    },
    required=["host", "port"],
    returns={
        "type": "object",
        "properties": {
            "accessible": {"type": "boolean"},
            "response_time_ms": {"type": "number"},
            "error": {"type": "string"},
        },
    },
)
def test_port(host: str, port: int, timeout_seconds: int = DEFAULT_TIMEOUT, protocol: str = "tcp") -> dict[str, Any]:
    """
    Test network port accessibility with detailed diagnostics.

    This tool tests whether a specific port on a host is accessible,
    providing detailed timing and connection information.

    Args:
        host: Hostname or IP address to test
        port: Port number to test (1-65535)
        timeout_seconds: Connection timeout in seconds (1-300)
        protocol: Protocol to test (tcp or udp)

    Returns:
        Dict containing test results, timing information, and diagnostics
    """
    start_time = time.time()

    # Validate inputs
    is_valid, error_msg = _validate_network_inputs(host, port, timeout_seconds, protocol)
    if not is_valid:
        return fail_response(f"Invalid parameters: {error_msg}", execution_time=time.time() - start_time)

    # Log the test attempt
    logger.info("port_test_started", host=host, port=port, protocol=protocol, timeout_seconds=timeout_seconds)

    try:
        # Resolve hostname first
        resolve_success, resolved_ip, resolve_error = _resolve_host(host)
        if not resolve_success:
            logger.error(f"Host resolution failed: {resolve_error}")
            return fail_response(resolve_error, host=host, port=port, protocol=protocol, execution_time=time.time() - start_time)

        # Test the port
        if protocol.lower() == "tcp":
            result = _test_tcp_port(resolved_ip, port, timeout_seconds, start_time)
        else:  # UDP
            result = _test_udp_port(resolved_ip, port, timeout_seconds, start_time)

        # Add common fields
        result.update(
            {
                "host": host,
                "resolved_ip": resolved_ip,
                "port": port,
                "protocol": protocol,
                "execution_time": time.time() - start_time,
            }
        )

        # Log the result
        logger.info(
            "port_test_completed",
            host=host,
            port=port,
            protocol=protocol,
            success=result.get("success", False),
            execution_time=result["execution_time"],
        )

        return result

    except Exception as e:
        error_msg = f"Port test failed: {e!s}"
        logger.error("port_test_error", host=host, port=port, protocol=protocol, error=error_msg, exc_info=True)
        return fail_response(error_msg, host=host, port=port, protocol=protocol, execution_time=time.time() - start_time)


def register_network_tools(mcp):
    """Register network tools with FastMCP."""
    # Register the test_port tool with MCP
    mcp.tool(test_port)

    logger.info("network_tools_registered", tools=["test_port"])
