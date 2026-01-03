"""Unit tests for provider registry."""

import pytest
from unittest.mock import Mock

from github_tools.summarizers.providers.registry import ProviderRegistry, register_provider, get_provider
from github_tools.summarizers.providers.base import LLMProvider


class MockProvider(LLMProvider):
    """Mock provider for testing."""
    
    def summarize(self, prompt, system_prompt=None, max_tokens=None, temperature=None):
        return "Summary"
    
    def is_available(self):
        return True
    
    def get_metadata(self):
        return {"name": "mock", "type": "test"}


class TestProviderRegistry:
    """Tests for ProviderRegistry."""
    
    def test_register_provider(self):
        """Test registering a provider."""
        registry = ProviderRegistry()
        registry.register("test", MockProvider)
        assert registry.is_registered("test")
    
    def test_register_invalid_provider(self):
        """Test registering invalid provider raises error."""
        registry = ProviderRegistry()
        with pytest.raises(ValueError, match="must be a subclass"):
            registry.register("test", str)
    
    def test_get_provider(self):
        """Test getting a provider instance."""
        registry = ProviderRegistry()
        registry.register("test", MockProvider)
        provider = registry.get("test", max_tokens=200)
        assert provider is not None
        assert isinstance(provider, MockProvider)
        assert provider.max_tokens == 200
    
    def test_get_nonexistent_provider(self):
        """Test getting nonexistent provider returns None."""
        registry = ProviderRegistry()
        provider = registry.get("nonexistent")
        assert provider is None
    
    def test_list_providers(self):
        """Test listing registered providers."""
        registry = ProviderRegistry()
        registry.register("test1", MockProvider)
        registry.register("test2", MockProvider)
        providers = registry.list_providers()
        assert "test1" in providers
        assert "test2" in providers


class TestRegistryFunctions:
    """Tests for module-level registry functions."""
    
    def test_register_provider_function(self):
        """Test register_provider function."""
        register_provider("test_func", MockProvider)
        provider = get_provider("test_func")
        assert provider is not None
        assert isinstance(provider, MockProvider)
    
    def test_get_provider_function(self):
        """Test get_provider function."""
        register_provider("test_get", MockProvider)
        provider = get_provider("test_get", temperature=0.5)
        assert provider.temperature == 0.5

