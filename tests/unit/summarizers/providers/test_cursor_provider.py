"""Unit tests for Cursor provider."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from github_tools.summarizers.providers.cursor_provider import CursorProvider


@pytest.fixture
def mock_httpx():
    """Mock httpx module."""
    with patch("github_tools.summarizers.providers.cursor_provider.httpx") as mock:
        yield mock


@pytest.fixture
def provider(mock_httpx):
    """Create Cursor provider instance."""
    return CursorProvider(endpoint="http://localhost:8080")


class TestCursorProvider:
    """Tests for CursorProvider."""
    
    def test_provider_initialization(self, mock_httpx):
        """Test provider initialization."""
        provider = CursorProvider(endpoint="http://localhost:8080")
        assert provider.endpoint == "http://localhost:8080"
        assert provider.model == "cursor-model"
        assert provider.timeout == 30
    
    def test_is_available_true(self, provider):
        """Test is_available returns True when endpoint is reachable."""
        with patch("github_tools.summarizers.providers.cursor_provider.check_cursor_agent", return_value=True):
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

