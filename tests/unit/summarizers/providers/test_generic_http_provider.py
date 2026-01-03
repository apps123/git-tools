"""Unit tests for Generic HTTP provider."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from github_tools.summarizers.providers.generic_http_provider import GenericHTTPProvider


@pytest.fixture
def mock_httpx():
    """Mock httpx module."""
    with patch("github_tools.summarizers.providers.generic_http_provider.httpx") as mock:
        yield mock


@pytest.fixture
def provider(mock_httpx):
    """Create Generic HTTP provider instance."""
    return GenericHTTPProvider(endpoint="http://localhost:11434", model="llama2")


class TestGenericHTTPProvider:
    """Tests for GenericHTTPProvider."""
    
    def test_provider_initialization(self, mock_httpx):
        """Test provider initialization."""
        provider = GenericHTTPProvider(endpoint="http://localhost:11434", model="llama2")
        assert provider.endpoint == "http://localhost:11434"
        assert provider.model == "llama2"
        assert provider.timeout == 30
    
    def test_provider_initialization_with_api_key(self, mock_httpx):
        """Test provider initialization with API key."""
        provider = GenericHTTPProvider(
            endpoint="http://localhost:11434",
            model="llama2",
            api_key="test-key",
        )
        assert provider.api_key == "test-key"
        assert "Authorization" in provider.headers
        assert provider.headers["Authorization"] == "Bearer test-key"
    
    def test_provider_initialization_with_custom_headers(self, mock_httpx):
        """Test provider initialization with custom headers."""
        custom_headers = {"X-Custom-Header": "value"}
        provider = GenericHTTPProvider(
            endpoint="http://localhost:11434",
            model="llama2",
            headers=custom_headers,
        )
        assert provider.headers["X-Custom-Header"] == "value"
    
    def test_is_available_true(self, provider):
        """Test is_available returns True when endpoint is reachable."""
        with patch("github_tools.summarizers.providers.generic_http_provider.check_http_endpoint", return_value=True):
            assert provider.is_available() is True
    
    def test_summarize_success(self, provider, mock_httpx):
        """Test successful summarization."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Summary"}}]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx.Client.return_value = mock_client
        
        result = provider.summarize("Test prompt")
        assert result == "Summary"
        
        # Verify correct endpoint was used
        call_args = mock_client.post.call_args
        assert "v1/chat/completions" in call_args[0][0] or "api/v1/chat/completions" in call_args[0][0]
    
    def test_summarize_empty_prompt(self, provider):
        """Test summarize raises error for empty prompt."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.summarize("")

