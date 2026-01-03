"""OpenAI provider implementation."""

import os
from typing import Any, Dict, Optional

try:
    import openai
except ImportError:
    openai = None

from github_tools.summarizers.providers.base import LLMProvider
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider for PR summarization."""
    
    DEFAULT_TIMEOUT = 60  # Cloud provider default
    DEFAULT_MODEL = "gpt-3.5-turbo"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = "https://api.openai.com/v1",
        max_tokens: int = LLMProvider.DEFAULT_MAX_TOKENS,
        temperature: float = LLMProvider.DEFAULT_TEMPERATURE,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if None)
            model: Model to use (default: gpt-3.5-turbo)
            base_url: OpenAI API base URL
            max_tokens: Maximum tokens for summary
            temperature: Temperature for generation
            timeout: Request timeout in seconds (default: 60)
            max_retries: Maximum number of retries
        """
        super().__init__(
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout or self.DEFAULT_TIMEOUT,
            max_retries=max_retries,
        )
        
        if openai is None:
            raise ImportError(
                "openai package is required for OpenAI provider. "
                "Install with: pip install openai"
            )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url
        
        if self.api_key:
            openai.api_key = self.api_key
            openai.api_base = base_url
        else:
            logger.warning("OpenAI API key not provided. Provider may not work.")
    
    def summarize(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate summary using OpenAI API.
        
        Args:
            prompt: User prompt for summarization
            system_prompt: System prompt (uses default if None)
            max_tokens: Override max_tokens
            temperature: Override temperature
        
        Returns:
            Generated summary string
        
        Raises:
            ValueError: If prompt is empty
            RuntimeError: If API call fails after retries
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if not self.api_key:
            raise RuntimeError("OpenAI API key not configured")
        
        system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature if temperature is not None else self.temperature
        
        def _call_api():
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        
        # Use retry logic for transient errors
        try:
            return self._retry_with_backoff(
                _call_api,
                retryable_errors=(Exception,),  # OpenAI library raises various exceptions
            )
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise RuntimeError(f"Failed to generate summary: {e}") from e
    
    def is_available(self) -> bool:
        """
        Check if OpenAI provider is available.
        
        Returns:
            True if API key is configured, False otherwise
        """
        return self.api_key is not None and bool(self.api_key.strip())
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get OpenAI provider metadata.
        
        Returns:
            Provider metadata dictionary
        """
        return {
            "name": "openai",
            "type": "cloud",
            "version": "1.0.0",
            "models": [self.model],
            "is_available": self.is_available(),
            "base_url": self.base_url,
        }

