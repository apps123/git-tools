"""Unit tests for Gemini provider."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from github_tools.summarizers.providers.gemini_provider import GeminiProvider


@pytest.fixture
def mock_genai():
    """Mock google.generativeai module."""
    with patch("github_tools.summarizers.providers.gemini_provider.genai") as mock:
        yield mock


@pytest.fixture
def provider(mock_genai):
    """Create Gemini provider instance."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
        return GeminiProvider(api_key="test-key")


class TestGeminiProvider:
    """Tests for GeminiProvider."""
    
    def test_provider_initialization(self, mock_genai):
        """Test provider initialization."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider(api_key="test-key")
            assert provider.api_key == "test-key"
            assert provider.model_name == "gemini-pro"
            assert provider.timeout == 60
            mock_genai.configure.assert_called_once_with(api_key="test-key")
    
    def test_provider_initialization_from_env(self, mock_genai):
        """Test provider initialization from environment variable."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key"}):
            provider = GeminiProvider()
            assert provider.api_key == "env-key"
    
    def test_is_available_with_key(self, mock_genai):
        """Test is_available returns True when API key is set."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider(api_key="test-key")
            assert provider.is_available() is True
    
    def test_is_available_without_key(self, mock_genai):
        """Test is_available returns False when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            provider = GeminiProvider()
            assert provider.is_available() is False
    
    def test_get_metadata(self, mock_genai):
        """Test get_metadata returns correct information."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider(api_key="test-key", model="gemini-ultra")
            metadata = provider.get_metadata()
            assert metadata["name"] == "gemini"
            assert metadata["type"] == "cloud"
            assert metadata["models"] == ["gemini-ultra"]
    
    def test_summarize_success(self, provider, mock_genai):
        """Test successful summarization."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This PR adds a new feature."
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        result = provider.summarize("Test prompt")
        assert result == "This PR adds a new feature."
        mock_genai.GenerativeModel.assert_called_once_with("gemini-pro")
    
    def test_summarize_empty_prompt(self, provider):
        """Test summarize raises error for empty prompt."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.summarize("")
    
    def test_summarize_no_api_key(self, mock_genai):
        """Test summarize raises error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            provider = GeminiProvider()
            with pytest.raises(RuntimeError, match="API key not configured"):
                provider.summarize("test prompt")
    
    def test_summarize_merges_system_prompt(self, provider, mock_genai):
        """Test summarize merges system prompt with user prompt."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Summary"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        provider.summarize("User prompt", system_prompt="System prompt")
        
        call_args = mock_model.generate_content.call_args
        full_prompt = call_args[0][0]
        assert "System prompt" in full_prompt
        assert "User prompt" in full_prompt

