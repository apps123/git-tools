"""Google Gemini provider implementation."""

import os
from typing import Any, Dict, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from github_tools.summarizers.providers.base import LLMProvider
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = 60  # Cloud provider default
DEFAULT_MODEL = "gemini-pro"


class GeminiProvider(LLMProvider):
    """Google Gemini API provider for PR summarization."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = LLMProvider.DEFAULT_MAX_TOKENS,
        temperature: float = LLMProvider.DEFAULT_TEMPERATURE,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key (uses GOOGLE_API_KEY env var if None)
            model: Model to use (default: gemini-pro)
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
        
        if genai is None:
            raise ImportError(
                "google-generativeai package is required for Gemini provider. "
                "Install with: pip install google-generativeai"
            )
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            logger.warning("Google API key not provided. Provider may not work.")
    
    def summarize(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate summary using Google Gemini API.
        
        Args:
            prompt: User prompt for summarization
            system_prompt: System prompt (merged with user prompt for Gemini)
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
        
        if not self.api_key:
            raise RuntimeError("Google API key not configured")
        
        # Gemini combines system and user prompts
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature if temperature is not None else self.temperature
        
        def _call_api():
            try:
                model = genai.GenerativeModel(self.model_name)
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
                raise
        
        try:
            return self._retry_with_backoff(
                _call_api,
                retryable_errors=(Exception,),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {e}") from e
    
    def is_available(self) -> bool:
        """
        Check if Gemini provider is available.
        
        Returns:
            True if API key is configured
        """
        return self.api_key is not None and bool(self.api_key.strip())
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get Gemini provider metadata.
        
        Returns:
            Provider metadata dictionary
        """
        return {
            "name": "gemini",
            "type": "cloud",
            "version": "1.0.0",
            "models": [self.model_name],
            "is_available": self.is_available(),
        }

