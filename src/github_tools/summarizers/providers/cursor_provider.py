"""Cursor Agent provider implementation."""

import os
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    try:
        import requests
        httpx = None
    except ImportError:
        httpx = None
        requests = None

from github_tools.summarizers.providers.base import LLMProvider
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_ENDPOINT = "http://localhost:8080"
DEFAULT_TIMEOUT = 30  # Local agent default


class CursorProvider(LLMProvider):
    """Cursor Agent provider for PR summarization."""
    
    DEFAULT_MODEL = "cursor-model"
    
    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        model: Optional[str] = None,
        max_tokens: int = LLMProvider.DEFAULT_MAX_TOKENS,
        temperature: float = LLMProvider.DEFAULT_TEMPERATURE,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """
        Initialize Cursor Agent provider.
        
        Args:
            endpoint: Cursor Agent API endpoint
            model: Model to use (optional, uses default if None)
            max_tokens: Maximum tokens for summary
            temperature: Temperature for generation
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries
        """
        super().__init__(
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout or self.DEFAULT_TIMEOUT,
            max_retries=max_retries,
        )
        
        if httpx is None and requests is None:
            raise ImportError(
                "httpx or requests package required for Cursor provider. "
                "Install with: pip install httpx or pip install requests"
            )
        
        self.endpoint = endpoint.rstrip("/")
        self.model = model or self.DEFAULT_MODEL
        self._client = None
    
    def _get_client(self):
        """Get HTTP client instance."""
        if self._client is None:
            if httpx:
                self._client = httpx.Client(timeout=self.timeout)
            else:
                self._client = requests.Session()
        return self._client
    
    def _make_request(self, url: str, json_data: Dict) -> Dict:
        """Make HTTP request to Cursor Agent API."""
        client = self._get_client()
        
        if httpx:
            response = client.post(url, json=json_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        else:
            response = client.post(url, json=json_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
    
    def summarize(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate summary using Cursor Agent API.
        
        Args:
            prompt: User prompt for summarization
            system_prompt: System prompt (uses default if None)
            max_tokens: Override max_tokens
            temperature: Override temperature
        
        Returns:
            Generated summary string
        
        Raises:
            ValueError: If prompt is empty
            RuntimeError: If API call fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature if temperature is not None else self.temperature
        
        # Cursor Agent API endpoint (assuming OpenAI-compatible format)
        api_url = f"{self.endpoint}/api/v1/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        def _call_api():
            try:
                response = self._make_request(api_url, payload)
                # Handle OpenAI-compatible response format
                if "choices" in response and len(response["choices"]) > 0:
                    return response["choices"][0]["message"]["content"].strip()
                # Handle Cursor-specific format if different
                elif "content" in response:
                    return response["content"].strip()
                else:
                    raise RuntimeError(f"Unexpected response format: {response}")
            except Exception as e:
                logger.error(f"Cursor Agent API call failed: {e}")
                raise
        
        try:
            return self._retry_with_backoff(
                _call_api,
                retryable_errors=(ConnectionError, TimeoutError),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {e}") from e
    
    def is_available(self) -> bool:
        """
        Check if Cursor Agent is available.
        
        Returns:
            True if endpoint is reachable
        """
        try:
            from github_tools.summarizers.providers.detector import check_cursor_agent
            return check_cursor_agent(self.endpoint)
        except Exception:
            return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get Cursor Agent provider metadata.
        
        Returns:
            Provider metadata dictionary
        """
        return {
            "name": "cursor",
            "type": "local",
            "version": "1.0.0",
            "models": [self.model],
            "is_available": self.is_available(),
            "endpoint": self.endpoint,
        }

