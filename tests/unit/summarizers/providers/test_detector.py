"""Unit tests for provider detector."""

import os
import pytest
from unittest.mock import patch

from github_tools.summarizers.providers.detector import (
    check_claude_desktop,
    check_cursor_agent,
    check_gemini,
    check_openai,
    detect_available_providers,
    get_detection_status,
)


class TestProviderDetection:
    """Tests for provider detection functions."""
    
    def test_check_openai_with_key(self):
        """Test check_openai returns True when API key is set."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            assert check_openai() is True
    
    def test_check_openai_without_key(self):
        """Test check_openai returns False when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            assert check_openai() is False
    
    def test_check_gemini_with_key(self):
        """Test check_gemini returns True when API key is set."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            assert check_gemini() is True
    
    def test_check_gemini_without_key(self):
        """Test check_gemini returns False when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            assert check_gemini() is False
    
    def test_check_claude_desktop_available(self):
        """Test check_claude_desktop returns True when available."""
        with patch("github_tools.summarizers.providers.detector.check_http_endpoint", return_value=True):
            assert check_claude_desktop() is True
    
    def test_check_claude_desktop_unavailable(self):
        """Test check_claude_desktop returns False when unavailable."""
        with patch("github_tools.summarizers.providers.detector.check_http_endpoint", return_value=False):
            assert check_claude_desktop() is False
    
    def test_check_cursor_agent_available(self):
        """Test check_cursor_agent returns True when available."""
        with patch("github_tools.summarizers.providers.detector.check_http_endpoint", return_value=True):
            assert check_cursor_agent() is True


class TestDetectAvailableProviders:
    """Tests for detect_available_providers."""
    
    def test_detect_all_providers(self):
        """Test detecting all available providers."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "GOOGLE_API_KEY": "test"}):
            with patch("github_tools.summarizers.providers.detector.check_claude_desktop", return_value=True):
                with patch("github_tools.summarizers.providers.detector.check_cursor_agent", return_value=True):
                    providers = detect_available_providers()
                    assert "claude-local" in providers
                    assert "cursor" in providers
                    assert "gemini" in providers
                    assert "openai" in providers
    
    def test_detect_priority_ordering(self):
        """Test provider detection respects priority ordering."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "GOOGLE_API_KEY": "test"}):
            with patch("github_tools.summarizers.providers.detector.check_claude_desktop", return_value=True):
                providers = detect_available_providers()
                # Claude should come before others
                assert providers.index("claude-local") < providers.index("openai")


class TestGetDetectionStatus:
    """Tests for get_detection_status."""
    
    def test_get_detection_status_all_providers(self):
        """Test getting detection status for all providers."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "GOOGLE_API_KEY": "test"}):
            with patch("github_tools.summarizers.providers.detector.check_claude_desktop", return_value=True):
                status = get_detection_status()
                assert "claude-local" in status
                assert "gemini" in status
                assert "openai" in status
                assert status["openai"]["status"] == "available"
                assert status["gemini"]["status"] == "available"
    
    def test_get_detection_status_with_hints(self):
        """Test detection status includes configuration hints."""
        with patch.dict(os.environ, {}, clear=True):
            status = get_detection_status()
            assert status["openai"]["status"] == "unavailable"
            assert "hint" in status["openai"]
            assert "OPENAI_API_KEY" in status["openai"]["hint"]

