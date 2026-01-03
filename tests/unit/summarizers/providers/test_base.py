"""Unit tests for LLM provider base class."""

import pytest
from unittest.mock import Mock, patch

from github_tools.summarizers.providers.base import LLMProvider


class ConcreteProvider(LLMProvider):
    """Concrete implementation for testing."""
    
    def summarize(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Test implementation."""
        return f"Summary: {prompt}"
    
    def is_available(self) -> bool:
        """Test implementation."""
        return True
    
    def get_metadata(self) -> dict:
        """Test implementation."""
        return {
            "name": "test-provider",
            "type": "test",
            "version": "1.0.0",
            "models": ["test-model"],
            "is_available": True,
        }


class TestLLMProvider:
    """Tests for LLMProvider abstract base class."""
    
    def test_provider_initialization(self):
        """Test provider initialization with default values."""
        provider = ConcreteProvider()
        assert provider.max_tokens == 150
        assert provider.temperature == 0.3
        assert provider.max_retries == 3
        assert provider.timeout is None
    
    def test_provider_initialization_with_custom_values(self):
        """Test provider initialization with custom values."""
        provider = ConcreteProvider(
            max_tokens=200,
            temperature=0.5,
            timeout=60,
            max_retries=5,
        )
        assert provider.max_tokens == 200
        assert provider.temperature == 0.5
        assert provider.timeout == 60
        assert provider.max_retries == 5
    
    def test_summarize_implementation(self):
        """Test that summarize method works."""
        provider = ConcreteProvider()
        result = provider.summarize("Test prompt")
        assert result == "Summary: Test prompt"
    
    def test_is_available_implementation(self):
        """Test that is_available method works."""
        provider = ConcreteProvider()
        assert provider.is_available() is True
    
    def test_get_metadata_implementation(self):
        """Test that get_metadata method works."""
        provider = ConcreteProvider()
        metadata = provider.get_metadata()
        assert metadata["name"] == "test-provider"
        assert metadata["type"] == "test"
        assert "is_available" in metadata
    
    def test_retry_with_backoff_success(self):
        """Test retry logic succeeds on first attempt."""
        provider = ConcreteProvider()
        
        def mock_func():
            return "success"
        
        result = provider._retry_with_backoff(mock_func)
        assert result == "success"
    
    def test_retry_with_backoff_retries_on_retryable_error(self):
        """Test retry logic retries on retryable errors."""
        provider = ConcreteProvider(max_retries=3)
        call_count = [0]
        
        def mock_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ConnectionError("Connection failed")
            return "success"
        
        with patch("time.sleep"):
            result = provider._retry_with_backoff(mock_func, retryable_errors=(ConnectionError,))
            assert result == "success"
            assert call_count[0] == 2
    
    def test_retry_with_backoff_fails_after_max_retries(self):
        """Test retry logic fails after max retries."""
        provider = ConcreteProvider(max_retries=2)
        
        def mock_func():
            raise ConnectionError("Connection failed")
        
        with patch("time.sleep"):
            with pytest.raises(ConnectionError):
                provider._retry_with_backoff(mock_func, retryable_errors=(ConnectionError,))
    
    def test_retry_with_backoff_no_retry_on_non_retryable_error(self):
        """Test retry logic doesn't retry on non-retryable errors."""
        provider = ConcreteProvider(max_retries=3)
        
        def mock_func():
            raise ValueError("Invalid input")
        
        with patch("time.sleep"):
            with pytest.raises(ValueError):
                provider._retry_with_backoff(mock_func, retryable_errors=(ConnectionError,))
    
    def test_retry_with_backoff_http_5xx_retries(self):
        """Test retry logic retries on HTTP 5xx errors."""
        provider = ConcreteProvider(max_retries=3)
        call_count = [0]
        
        class HTTPError(Exception):
            status_code = 500
        
        def mock_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise HTTPError()
            return "success"
        
        with patch("time.sleep"):
            result = provider._retry_with_backoff(mock_func)
            assert result == "success"
    
    def test_retry_with_backoff_http_429_retries(self):
        """Test retry logic retries on HTTP 429 (rate limit) errors."""
        provider = ConcreteProvider(max_retries=3)
        call_count = [0]
        
        class RateLimitError(Exception):
            status_code = 429
        
        def mock_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise RateLimitError()
            return "success"
        
        with patch("time.sleep"):
            result = provider._retry_with_backoff(mock_func)
            assert result == "success"
    
    def test_retry_with_backoff_timeout_error_retries(self):
        """Test retry logic retries on timeout errors."""
        provider = ConcreteProvider(max_retries=3)
        call_count = [0]
        
        def mock_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise TimeoutError("Request timed out")
            return "success"
        
        with patch("time.sleep"):
            result = provider._retry_with_backoff(mock_func)
            assert result == "success"

