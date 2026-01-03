"""Abstract base class for LLM providers."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

__all__ = ["LLMProvider"]


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    DEFAULT_MAX_TOKENS = 150
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_SYSTEM_PROMPT = (
        "You are a technical writer that creates concise, informative summaries "
        "of pull requests. Summaries should be 1-2 sentences and highlight the key changes."
    )
    
    def __init__(
        self,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """
        Initialize LLM provider.
        
        Args:
            max_tokens: Maximum tokens for summary
            temperature: Temperature for generation
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for transient errors
        """
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def summarize(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate summary using LLM.
        
        Args:
            prompt: User prompt for summarization
            system_prompt: System prompt (uses default if None)
            max_tokens: Override max_tokens (uses instance default if None)
            temperature: Override temperature (uses instance default if None)
        
        Returns:
            Generated summary string
        
        Raises:
            ValueError: If prompt is empty or invalid
            RuntimeError: If provider is unavailable or request fails after retries
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available.
        
        Returns:
            True if provider is available and ready to use, False otherwise
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get provider metadata.
        
        Returns:
            Dictionary containing provider metadata:
            - name: Provider name
            - type: Provider type (local/cloud)
            - version: Provider version (if available)
            - models: List of supported models
            - is_available: Current availability status
        """
        pass
    
    def _retry_with_backoff(
        self,
        func,
        retryable_errors: tuple = (),
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            retryable_errors: Tuple of exception types that should trigger retry
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
        
        Returns:
            Return value from func
        
        Raises:
            RuntimeError: If all retries exhausted
            Original exception: If error is not retryable
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Check if error is retryable
                is_retryable = (
                    isinstance(e, retryable_errors) or
                    (hasattr(e, "status_code") and e.status_code >= 500) or
                    (hasattr(e, "status_code") and e.status_code == 429) or
                    isinstance(e, (TimeoutError, ConnectionError))
                )
                
                if not is_retryable or attempt == self.max_retries - 1:
                    # Non-retryable error or last attempt
                    raise
                
                # Calculate exponential backoff delay: 1s, 2s, 4s
                delay = 2 ** attempt
                time.sleep(delay)
        
        # Should not reach here, but handle edge case
        if last_exception:
            raise RuntimeError(f"Failed after {self.max_retries} retries") from last_exception
        
        raise RuntimeError("Unexpected error in retry logic")

