"""Unit tests for OpenAI provider."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from github_tools.summarizers.providers.openai_provider import OpenAIProvider


@pytest.fixture
def mock_openai():
    """Mock OpenAI module."""
    with patch("github_tools.summarizers.providers.openai_provider.openai") as mock:
        yield mock


@pytest.fixture
def provider(mock_openai):
    """Create OpenAI provider instance."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return OpenAIProvider(api_key="test-key")


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""
    
    def test_provider_initialization(self, mock_openai):
        """Test provider initialization."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.model == "gpt-3.5-turbo"
        assert provider.timeout == 60
        assert provider.max_retries == 3
    
    def test_provider_initialization_from_env(self, mock_openai):
        """Test provider initialization from environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            provider = OpenAIProvider()
            assert provider.api_key == "env-key"
    
    def test_provider_initialization_custom_values(self, mock_openai):
        """Test provider initialization with custom values."""
        provider = OpenAIProvider(
            api_key="test-key",
            model="gpt-4",
            timeout=120,
            max_retries=5,
        )
        assert provider.model == "gpt-4"
        assert provider.timeout == 120
        assert provider.max_retries == 5
    
    def test_is_available_with_key(self, mock_openai):
        """Test is_available returns True when API key is set."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.is_available() is True
    
    def test_is_available_without_key(self, mock_openai):
        """Test is_available returns False when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIProvider()
            assert provider.is_available() is False
    
    def test_get_metadata(self, mock_openai):
        """Test get_metadata returns correct information."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4")
        metadata = provider.get_metadata()
        assert metadata["name"] == "openai"
        assert metadata["type"] == "cloud"
        assert metadata["models"] == ["gpt-4"]
        assert metadata["is_available"] is True
    
    def test_summarize_success(self, provider, mock_openai):
        """Test successful summarization."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This PR adds a new feature."
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        result = provider.summarize("Test prompt")
        assert result == "This PR adds a new feature."
        mock_openai.ChatCompletion.create.assert_called_once()
    
    def test_summarize_empty_prompt(self, provider):
        """Test summarize raises error for empty prompt."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.summarize("")
    
    def test_summarize_no_api_key(self, mock_openai):
        """Test summarize raises error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIProvider()
            with pytest.raises(RuntimeError, match="API key not configured"):
                provider.summarize("test prompt")
    
    def test_summarize_uses_default_system_prompt(self, provider, mock_openai):
        """Test summarize uses default system prompt."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        provider.summarize("test prompt")
        
        call_args = mock_openai.ChatCompletion.create.call_args
        messages = call_args[1]["messages"]
        assert messages[0]["role"] == "system"
        assert "technical writer" in messages[0]["content"]
    
    def test_summarize_uses_custom_system_prompt(self, provider, mock_openai):
        """Test summarize uses custom system prompt when provided."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        provider.summarize("test prompt", system_prompt="Custom system prompt")
        
        call_args = mock_openai.ChatCompletion.create.call_args
        messages = call_args[1]["messages"]
        assert messages[0]["content"] == "Custom system prompt"
    
    def test_summarize_retries_on_error(self, provider, mock_openai):
        """Test summarize retries on transient errors."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary"
        
        # Fail first two times, succeed on third
        mock_openai.ChatCompletion.create.side_effect = [
            ConnectionError("Connection failed"),
            ConnectionError("Connection failed"),
            mock_response,
        ]
        
        with patch("time.sleep"):
            result = provider.summarize("test prompt")
            assert result == "Summary"
            assert mock_openai.ChatCompletion.create.call_count == 3
    
    def test_summarize_uses_instance_defaults(self, provider, mock_openai):
        """Test summarize uses instance default values."""
        provider = OpenAIProvider(
            api_key="test-key",
            max_tokens=200,
            temperature=0.5,
        )
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        provider.summarize("test prompt")
        
        call_args = mock_openai.ChatCompletion.create.call_args
        assert call_args[1]["max_tokens"] == 200
        assert call_args[1]["temperature"] == 0.5
    
    def test_summarize_overrides_instance_defaults(self, provider, mock_openai):
        """Test summarize can override instance defaults."""
        provider = OpenAIProvider(
            api_key="test-key",
            max_tokens=200,
            temperature=0.5,
        )
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        provider.summarize("test prompt", max_tokens=100, temperature=0.7)
        
        call_args = mock_openai.ChatCompletion.create.call_args
        assert call_args[1]["max_tokens"] == 100
        assert call_args[1]["temperature"] == 0.7

