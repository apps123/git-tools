"""Provider detection and availability checking."""

import os
import socket
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    try:
        import requests
        httpx = None
    except ImportError:
        httpx = None
        requests = None

from github_tools.utils.logging import get_logger

logger = get_logger(__name__)

# Provider detection priority (highest to lowest)
PROVIDER_PRIORITY = [
    "claude-local",  # Local, most capable for code
    "cursor",        # Local, code-focused
    "gemini",        # Cloud alternative
    "generic",       # Generic local LLM
    "openai",        # Fallback cloud provider
]

# Default endpoints for local providers
DEFAULT_CLAUDE_ENDPOINT = "http://localhost:11434"
DEFAULT_CURSOR_ENDPOINT = "http://localhost:8080"


def check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """
    Check if a port is open on a host.
    
    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Connection timeout in seconds
    
    Returns:
        True if port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host.replace("http://", "").replace("https://", ""), port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_http_endpoint(url: str, timeout: float = 2.0) -> bool:
    """
    Check if an HTTP endpoint is available.
    
    Args:
        url: Endpoint URL
        timeout: Request timeout in seconds
    
    Returns:
        True if endpoint responds, False otherwise
    """
    try:
        if httpx:
            response = httpx.get(url, timeout=timeout, follow_redirects=True)
            return response.status_code < 500
        elif requests:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            return response.status_code < 500
        else:
            # Fallback to port check only
            return check_port("localhost", int(url.split(":")[-1].split("/")[0]) if ":" in url else 80, timeout)
    except Exception:
        return False


def check_claude_desktop(endpoint: Optional[str] = None) -> bool:
    """
    Check if Claude Desktop is available.
    
    Args:
        endpoint: Custom endpoint (default: http://localhost:11434)
    
    Returns:
        True if Claude Desktop is running
    """
    endpoint = endpoint or DEFAULT_CLAUDE_ENDPOINT
    
    # Check if port is open (basic check)
    if ":" in endpoint:
        try:
            host, port_str = endpoint.split("://")[1].split(":")
            port = int(port_str)
            if not check_port(host, port):
                return False
        except (ValueError, IndexError):
            pass
    
    # Try health check endpoint
    health_url = f"{endpoint}/health" if not endpoint.endswith("/health") else endpoint
    return check_http_endpoint(health_url)


def check_cursor_agent(endpoint: Optional[str] = None) -> bool:
    """
    Check if Cursor Agent is available.
    
    Args:
        endpoint: Custom endpoint (default: http://localhost:8080)
    
    Returns:
        True if Cursor Agent is running
    """
    endpoint = endpoint or DEFAULT_CURSOR_ENDPOINT
    
    # Check if port is open
    if ":" in endpoint:
        try:
            host, port_str = endpoint.split("://")[1].split(":")
            port = int(port_str)
            if not check_port(host, port):
                return False
        except (ValueError, IndexError):
            pass
    
    # Try API endpoint
    api_url = f"{endpoint}/api/v1" if not endpoint.endswith("/api") else endpoint
    return check_http_endpoint(api_url)


def check_gemini() -> bool:
    """
    Check if Gemini API is available (has API key).
    
    Returns:
        True if GOOGLE_API_KEY is set
    """
    return bool(os.getenv("GOOGLE_API_KEY"))


def check_openai() -> bool:
    """
    Check if OpenAI API is available (has API key).
    
    Returns:
        True if OPENAI_API_KEY is set
    """
    return bool(os.getenv("OPENAI_API_KEY"))


def detect_available_providers(
    provider_configs: Optional[Dict[str, Dict]] = None,
) -> List[str]:
    """
    Detect available LLM providers in priority order.
    
    Args:
        provider_configs: Optional provider-specific configurations
    
    Returns:
        List of available provider names in priority order
    """
    available = []
    provider_configs = provider_configs or {}
    
    # Check Claude Desktop
    claude_config = provider_configs.get("claude_local", {})
    claude_endpoint = claude_config.get("endpoint", DEFAULT_CLAUDE_ENDPOINT)
    if check_claude_desktop(claude_endpoint):
        available.append("claude-local")
        logger.debug(f"Claude Desktop detected at {claude_endpoint}")
    
    # Check Cursor Agent
    cursor_config = provider_configs.get("cursor", {})
    cursor_endpoint = cursor_config.get("endpoint", DEFAULT_CURSOR_ENDPOINT)
    if check_cursor_agent(cursor_endpoint):
        available.append("cursor")
        logger.debug(f"Cursor Agent detected at {cursor_endpoint}")
    
    # Check Gemini (has API key)
    if check_gemini():
        available.append("gemini")
        logger.debug("Gemini API key detected")
    
    # Check OpenAI (has API key)
    if check_openai():
        available.append("openai")
        logger.debug("OpenAI API key detected")
    
    return available


def get_detection_status(
    provider_configs: Optional[Dict[str, Dict]] = None,
) -> Dict[str, Dict[str, str]]:
    """
    Get detailed detection status for all providers.
    
    Args:
        provider_configs: Optional provider-specific configurations
    
    Returns:
        Dictionary mapping provider names to detection status information:
        {
            "provider_name": {
                "status": "available" | "unavailable",
                "reason": "reason description",
                "hint": "actionable configuration hint"
            }
        }
    """
    status = {}
    provider_configs = provider_configs or {}
    
    # Claude Desktop
    claude_config = provider_configs.get("claude_local", {})
    claude_endpoint = claude_config.get("endpoint", DEFAULT_CLAUDE_ENDPOINT)
    if check_claude_desktop(claude_endpoint):
        status["claude-local"] = {
            "status": "available",
            "reason": f"Running at {claude_endpoint}",
            "hint": "",
        }
    else:
        status["claude-local"] = {
            "status": "unavailable",
            "reason": f"Not running at {claude_endpoint}",
            "hint": "Start Claude Desktop or configure custom endpoint",
        }
    
    # Cursor Agent
    cursor_config = provider_configs.get("cursor", {})
    cursor_endpoint = cursor_config.get("endpoint", DEFAULT_CURSOR_ENDPOINT)
    if check_cursor_agent(cursor_endpoint):
        status["cursor"] = {
            "status": "available",
            "reason": f"Running at {cursor_endpoint}",
            "hint": "",
        }
    else:
        status["cursor"] = {
            "status": "unavailable",
            "reason": f"Not running at {cursor_endpoint}",
            "hint": "Start Cursor Agent or configure custom endpoint",
        }
    
    # Gemini
    if check_gemini():
        status["gemini"] = {
            "status": "available",
            "reason": "API key configured",
            "hint": "",
        }
    else:
        status["gemini"] = {
            "status": "unavailable",
            "reason": "API key missing",
            "hint": "Set GOOGLE_API_KEY environment variable",
        }
    
    # OpenAI
    if check_openai():
        status["openai"] = {
            "status": "available",
            "reason": "API key configured",
            "hint": "",
        }
    else:
        status["openai"] = {
            "status": "unavailable",
            "reason": "API key missing",
            "hint": "Set OPENAI_API_KEY environment variable",
        }
    
    return status

