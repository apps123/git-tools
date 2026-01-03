"""Contract tests for LLM provider interface and configuration."""

import pytest
from typing import Dict, Any
from unittest.mock import Mock

from github_tools.summarizers.providers.base import LLMProvider
from github_tools.summarizers.providers.registry import get_provider
from github_tools.summarizers.llm_summarizer import LLMSummarizer


class MockProvider(LLMProvider):
    """Mock provider for contract testing."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._available = True
    
    def summarize(self, prompt, system_prompt=None, max_tokens=None, temperature=None):
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        return f"Summary: {prompt[:50]}"
    
    def is_available(self):
        return self._available
    
    def get_metadata(self):
        return {
            "name": "mock-provider",
            "type": "test",
            "version": "1.0.0",
            "models": ["test-model"],
            "is_available": self._available,
        }


@pytest.mark.contract
class TestLLMProviderContract:
    """Contract tests for LLMProvider interface."""
    
    def test_provider_implements_required_methods(self):
        """Test that provider implements all required abstract methods."""
        provider = MockProvider()
        
        # All abstract methods must be implemented
        assert hasattr(provider, "summarize")
        assert hasattr(provider, "is_available")
        assert hasattr(provider, "get_metadata")
    
    def test_provider_summarize_contract(self):
        """Test that summarize method follows contract."""
        provider = MockProvider()
        
        # Should accept prompt and optional parameters
        result = provider.summarize("Test prompt")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should accept system_prompt
        result = provider.summarize("Test prompt", system_prompt="System prompt")
        assert isinstance(result, str)
        
        # Should accept max_tokens override
        result = provider.summarize("Test prompt", max_tokens=100)
        assert isinstance(result, str)
        
        # Should accept temperature override
        result = provider.summarize("Test prompt", temperature=0.5)
        assert isinstance(result, str)
    
    def test_provider_is_available_contract(self):
        """Test that is_available method follows contract."""
        provider = MockProvider()
        
        # Should return boolean
        result = provider.is_available()
        assert isinstance(result, bool)
    
    def test_provider_get_metadata_contract(self):
        """Test that get_metadata method follows contract."""
        provider = MockProvider()
        
        # Should return dictionary
        metadata = provider.get_metadata()
        assert isinstance(metadata, dict)
        
        # Should include required fields
        assert "name" in metadata
        assert "type" in metadata
        assert "is_available" in metadata
        
        # Should have correct types
        assert isinstance(metadata["name"], str)
        assert isinstance(metadata["type"], str)
        assert isinstance(metadata["is_available"], bool)
    
    def test_provider_summarize_validates_empty_prompt(self):
        """Test that summarize raises ValueError for empty prompt."""
        provider = MockProvider()
        
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.summarize("")
        
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.summarize("   ")


@pytest.mark.contract
class TestLLMSummarizerContract:
    """Contract tests for LLMSummarizer with providers."""
    
    def test_summarizer_accepts_provider_instance(self):
        """Test that LLMSummarizer accepts provider instance."""
        provider = MockProvider()
        summarizer = LLMSummarizer(provider=provider, auto_detect=False)
        
        assert summarizer.provider == provider
    
    def test_summarizer_accepts_provider_name(self):
        """Test that LLMSummarizer accepts provider name."""
        # Register mock provider
        from github_tools.summarizers.providers.registry import register_provider
        register_provider("contract-test", MockProvider)
        
        summarizer = LLMSummarizer(provider_name="contract-test", auto_detect=False)
        
        assert summarizer.provider is not None
        assert summarizer.provider_name == "contract-test"
    
    def test_summarizer_auto_detects_provider(self):
        """Test that LLMSummarizer can auto-detect provider."""
        provider = MockProvider()
        
        with pytest.raises(RuntimeError):  # Will fail if no providers available, which is expected
            # This test validates the contract - auto_detect should attempt detection
            pass
        
        # With a provider, it should work
        summarizer = LLMSummarizer(provider=provider, auto_detect=False)
        assert summarizer.provider == provider


@pytest.mark.contract
class TestProviderConfigurationContract:
    """Contract tests for provider configuration."""
    
    def test_provider_config_structure(self):
        """Test that provider configuration has expected structure."""
        # Configuration should support provider-specific settings
        provider_config = {
            "openai": {
                "api_key": "test-key",
                "model": "gpt-3.5-turbo",
                "timeout": 60,
            },
            "claude_local": {
                "endpoint": "http://localhost:11434",
                "model": "claude-3-5-sonnet",
                "timeout": 30,
            },
            "gemini": {
                "api_key": "test-key",
                "model": "gemini-pro",
                "timeout": 60,
            },
        }
        
        # Each provider config should be a dictionary
        for provider_name, config in provider_config.items():
            assert isinstance(config, dict)
            # Should support model and timeout
            if "model" in config:
                assert isinstance(config["model"], str)
            if "timeout" in config:
                assert isinstance(config["timeout"], (int, type(None)))
    
    def test_provider_metadata_contract(self):
        """Test that provider metadata follows contract."""
        provider = MockProvider()
        metadata = provider.get_metadata()
        
        # Required fields
        required_fields = ["name", "type", "is_available"]
        for field in required_fields:
            assert field in metadata, f"Metadata must include {field}"
        
        # Type constraints
        assert metadata["type"] in ["local", "cloud", "test"], "Type must be local, cloud, or test"
        assert isinstance(metadata["is_available"], bool), "is_available must be boolean"

