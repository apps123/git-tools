"""Generic HTTP provider for OpenAI-compatible APIs."""

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

DEFAULT_TIMEOUT = 30  # Local default


class GenericHTTPProvider(LLMProvider):
    """Generic HTTP provider for OpenAI-compatible APIs (Ollama, LocalAI, etc.)."""
    
    DEFAULT_MODEL = "llama2"
    
    def __init__(
        self,
        endpoint: str,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        max_tokens: int = LLMProvider.DEFAULT_MAX_TOKENS,
        temperature: float = LLMProvider.DEFAULT_TEMPERATURE,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """
        Initialize generic HTTP provider.
        
        Args:
            endpoint: API endpoint URL
            model: Model to use
            api_key: Optional API key for authentication
            headers: Optional custom headers
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
                "httpx or requests package required for Generic HTTP provider. "
                "Install with: pip install httpx or pip install requests"
            )
        
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.headers = headers or {}
        
        if self.api_key and "Authorization" not in self.headers:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        self._client = None
    
    def _get_client(self):
        """Get HTTP client instance."""
        if self._client is None:
            if httpx:
                self._client = httpx.Client(timeout=self.timeout, headers=self.headers)
            else:
                self._client = requests.Session()
                self._client.headers.update(self.headers)
        return self._client
    
    def _make_request(self, url: str, json_data: Dict) -> Dict:
        """Make HTTP request to generic API."""
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
        Generate summary using generic HTTP API.
        
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
        
        # OpenAI-compatible API endpoint
        api_url = f"{self.endpoint}/v1/chat/completions"
        if not api_url.startswith("http"):
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
                # Handle alternative formats
                elif "content" in response:
                    return response["content"].strip()
                else:
                    raise RuntimeError(f"Unexpected response format: {response}")
            except Exception as e:
                logger.error(f"Generic HTTP API call failed: {e}")
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
        Check if generic HTTP provider is available.
        
        Returns:
            True if endpoint is reachable
        """
        try:
            from github_tools.summarizers.providers.detector import check_http_endpoint
            return check_http_endpoint(self.endpoint)
        except Exception:
            return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get generic HTTP provider metadata.
        
        Returns:
            Provider metadata dictionary
        """
        return {
            "name": "generic",
            "type": "local",
            "version": "1.0.0",
            "models": [self.model],
            "is_available": self.is_available(),
            "endpoint": self.endpoint,
        }

