"""Provider registry and factory for LLM providers."""

import os
from typing import Dict, List, Optional, Type

from github_tools.summarizers.providers.base import LLMProvider
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class ProviderRegistry:
    """Registry for LLM providers."""
    
    def __init__(self):
        """Initialize provider registry."""
        self._providers: Dict[str, Type[LLMProvider]] = {}
        self._instances: Dict[str, LLMProvider] = {}
    
    def register(self, name: str, provider_class: Type[LLMProvider]) -> None:
        """
        Register a provider class.
        
        Args:
            name: Provider name (e.g., "openai", "gemini")
            provider_class: Provider class that extends LLMProvider
        """
        if not issubclass(provider_class, LLMProvider):
            raise ValueError(f"{provider_class} must be a subclass of LLMProvider")
        
        self._providers[name] = provider_class
        logger.debug(f"Registered provider: {name}")
    
    def get(self, name: str, **kwargs) -> Optional[LLMProvider]:
        """
        Get a provider instance by name.
        
        Args:
            name: Provider name
            **kwargs: Arguments to pass to provider constructor
        
        Returns:
            Provider instance or None if not found
        """
        provider_class = self._providers.get(name)
        if not provider_class:
            logger.warning(f"Provider not found: {name}")
            return None
        
        # Create instance with provided kwargs
        try:
            instance = provider_class(**kwargs)
            return instance
        except Exception as e:
            logger.error(f"Failed to create provider {name}: {e}")
            return None
    
    def list_providers(self) -> List[str]:
        """
        List all registered provider names.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def is_registered(self, name: str) -> bool:
        """
        Check if a provider is registered.
        
        Args:
            name: Provider name
        
        Returns:
            True if provider is registered
        """
        return name in self._providers


# Global registry instance
_registry = ProviderRegistry()


def register_provider(name: str, provider_class: Type[LLMProvider]) -> None:
    """
    Register a provider in the global registry.
    
    Args:
        name: Provider name
        provider_class: Provider class
    """
    _registry.register(name, provider_class)


def get_provider(name: str, **kwargs) -> Optional[LLMProvider]:
    """
    Get a provider instance from the global registry.
    
    Args:
        name: Provider name
        **kwargs: Arguments to pass to provider constructor
    
    Returns:
        Provider instance or None if not found
    """
    return _registry.get(name, **kwargs)


def list_providers() -> List[str]:
    """
    List all registered providers.
    
    Returns:
        List of provider names
    """
    return _registry.list_providers()

