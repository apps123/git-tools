"""Integration tests for provider auto-detection."""

import os
import pytest
from unittest.mock import patch

from github_tools.summarizers.providers.detector import (
    detect_available_providers,
    get_detection_status,
)


@pytest.mark.integration
class TestProviderDetection:
    """Integration tests for provider detection."""
    
    def test_detect_with_all_providers_available(self):
        """Test detection when all providers are available."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "GOOGLE_API_KEY": "test"}):
            with patch("github_tools.summarizers.providers.detector.check_claude_desktop", return_value=True):
                with patch("github_tools.summarizers.providers.detector.check_cursor_agent", return_value=True):
                    providers = detect_available_providers()
                    # Should detect all providers
                    assert len(providers) >= 4
                    # Priority order: claude-local > cursor > gemini > openai
                    assert providers[0] == "claude-local"
                    assert "cursor" in providers
                    assert "gemini" in providers
                    assert "openai" in providers
    
    def test_detect_with_only_cloud_providers(self):
        """Test detection when only cloud providers are available."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "GOOGLE_API_KEY": "test"}):
            with patch("github_tools.summarizers.providers.detector.check_claude_desktop", return_value=False):
                with patch("github_tools.summarizers.providers.detector.check_cursor_agent", return_value=False):
                    providers = detect_available_providers()
                    # Should detect cloud providers only
                    assert "gemini" in providers
                    assert "openai" in providers
                    assert "claude-local" not in providers
                    assert "cursor" not in providers
    
    def test_detect_with_no_providers(self):
        """Test detection when no providers are available."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("github_tools.summarizers.providers.detector.check_claude_desktop", return_value=False):
                with patch("github_tools.summarizers.providers.detector.check_cursor_agent", return_value=False):
                    providers = detect_available_providers()
                    # Should return empty list
                    assert len(providers) == 0
    
    def test_get_detection_status_comprehensive(self):
        """Test getting comprehensive detection status."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
            with patch("github_tools.summarizers.providers.detector.check_claude_desktop", return_value=False):
                status = get_detection_status()
                
                # Should have status for all providers
                assert "openai" in status
                assert "claude-local" in status
                assert "gemini" in status
                assert "cursor" in status
                
                # Check status structure
                for provider_name, provider_status in status.items():
                    assert "status" in provider_status
                    assert "reason" in provider_status
                    assert "hint" in provider_status
                    assert provider_status["status"] in ["available", "unavailable"]
                
                # OpenAI should be available
                assert status["openai"]["status"] == "available"
                
                # Claude should be unavailable
                assert status["claude-local"]["status"] == "unavailable"
                assert "not running" in status["claude-local"]["reason"].lower()
    
    def test_detection_status_hints(self):
        """Test that detection status includes actionable hints."""
        with patch.dict(os.environ, {}, clear=True):
            status = get_detection_status()
            
            # Unavailable providers should have hints
            assert status["openai"]["status"] == "unavailable"
            assert "OPENAI_API_KEY" in status["openai"]["hint"]
            
            assert status["gemini"]["status"] == "unavailable"
            assert "GOOGLE_API_KEY" in status["gemini"]["hint"]

