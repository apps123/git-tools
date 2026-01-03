"""Unit tests for Claude Local provider."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from github_tools.summarizers.providers.claude_local_provider import ClaudeLocalProvider


@pytest.fixture
def mock_httpx():
    """Mock httpx module."""
    with patch("github_tools.summarizers.providers.claude_local_provider.httpx") as mock:
        yield mock


@pytest.fixture
def provider(mock_httpx):
    """Create Claude Local provider instance."""
    return ClaudeLocalProvider(endpoint="http://localhost:11434")


class TestClaudeLocalProvider:
    """Tests for ClaudeLocalProvider."""
    
    def test_provider_initialization(self, mock_httpx):
        """Test provider initialization."""
        provider = ClaudeLocalProvider(endpoint="http://localhost:11434")
        assert provider.endpoint == "http://localhost:11434"
        assert provider.model == "claude-3-5-sonnet"
        assert provider.timeout == 30
        assert provider.max_retries == 3
    
    def test_provider_initialization_custom_values(self, mock_httpx):
        """Test provider initialization with custom values."""
        provider = ClaudeLocalProvider(
            endpoint="http://localhost:9999",
            model="claude-3-opus",
            timeout=60,
            max_retries=5,
        )
        assert provider.endpoint == "http://localhost:9999"
        assert provider.model == "claude-3-opus"
        assert provider.timeout == 60
        assert provider.max_retries == 5
    
    def test_is_available_true(self, provider):
        """Test is_available returns True when endpoint is reachable."""
        with patch("github_tools.summarizers.providers.claude_local_provider.check_claude_desktop", return_value=True):
            assert provider.is_available() is True
    
    def test_is_available_false(self, provider):
        """Test is_available returns False when endpoint is not reachable."""
        with patch("github_tools.summarizers.providers.claude_local_provider.check_claude_desktop", return_value=False):
            assert provider.is_available() is False
    
    def test_get_metadata(self, provider):
        """Test get_metadata returns correct information."""
        metadata = provider.get_metadata()
        assert metadata["name"] == "claude-local"
        assert metadata["type"] == "local"
        assert metadata["models"] == ["claude-3-5-sonnet"]
        assert metadata["endpoint"] == "http://localhost:11434"
    
    def test_summarize_success_httpx(self, provider, mock_httpx):
        """Test successful summarization with httpx."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This PR adds a new feature."}}]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx.Client.return_value = mock_client
        
        result = provider.summarize("Test prompt")
        assert result == "This PR adds a new feature."
        mock_client.post.assert_called_once()
    
    def test_summarize_success_requests(self, provider):
        """Test successful summarization with requests fallback."""
        with patch("github_tools.summarizers.providers.claude_local_provider.httpx", None):
            with patch("github_tools.summarizers.providers.claude_local_provider.requests") as mock_requests:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "This PR adds a new feature."}}]
                }
                mock_response.raise_for_status = Mock()
                
                mock_session = MagicMock()
                mock_session.post.return_value = mock_response
                mock_requests.Session.return_value = mock_session
                
                result = provider.summarize("Test prompt")
                assert result == "This PR adds a new feature."
    
    def test_summarize_empty_prompt(self, provider):
        """Test summarize raises error for empty prompt."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.summarize("")
    
    def test_summarize_retries_on_error(self, provider, mock_httpx):
        """Test summarize retries on transient errors."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Summary"}}]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.post.side_effect = [
            ConnectionError("Connection failed"),
            ConnectionError("Connection failed"),
            mock_response,
        ]
        mock_httpx.Client.return_value = mock_client
        
        with patch("time.sleep"):
            result = provider.summarize("test prompt")
            assert result == "Summary"
            assert mock_client.post.call_count == 3
    
    def test_summarize_uses_default_system_prompt(self, provider, mock_httpx):
        """Test summarize uses default system prompt."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Summary"}}]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx.Client.return_value = mock_client
        
        provider.summarize("test prompt")
        
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["messages"][0]["role"] == "system"
        assert "technical writer" in payload["messages"][0]["content"]

