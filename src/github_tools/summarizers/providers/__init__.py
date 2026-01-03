"""LLM provider implementations for PR summarization."""

from github_tools.summarizers.providers.base import LLMProvider
from github_tools.summarizers.providers.registry import (
    ProviderRegistry,
    get_provider,
    register_provider,
    list_providers,
)
from github_tools.summarizers.providers.detector import (
    detect_available_providers,
    get_detection_status,
)

# Import providers (will register themselves)
try:
    from github_tools.summarizers.providers.openai_provider import OpenAIProvider
    from github_tools.summarizers.providers.claude_local_provider import ClaudeLocalProvider
    from github_tools.summarizers.providers.cursor_provider import CursorProvider
    from github_tools.summarizers.providers.gemini_provider import GeminiProvider
    from github_tools.summarizers.providers.generic_http_provider import GenericHTTPProvider
    
    # Register all providers
    register_provider("openai", OpenAIProvider)
    register_provider("claude-local", ClaudeLocalProvider)
    register_provider("cursor", CursorProvider)
    register_provider("gemini", GeminiProvider)
    register_provider("generic", GenericHTTPProvider)
except ImportError:
    # Some providers may not be available if dependencies are missing
    pass

__all__ = [
    "LLMProvider",
    "ProviderRegistry",
    "get_provider",
    "register_provider",
    "list_providers",
    "detect_available_providers",
    "get_detection_status",
]

