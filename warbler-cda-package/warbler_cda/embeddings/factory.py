"""
Embedding Provider Factory - Dynamic Provider Creation
"""

from typing import Dict, Any, Optional, List

from .base_provider import EmbeddingProvider
from .local_provider import LocalEmbeddingProvider
from .openai_provider import OpenAIEmbeddingProvider
from .sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)


class EmbeddingProviderFactory:
    """Factory for creating embedding providers."""

    PROVIDERS = {
        "local": LocalEmbeddingProvider,
        "openai": OpenAIEmbeddingProvider,
        "sentence_transformer": SentenceTransformerEmbeddingProvider,
    }

    @classmethod
    def create_provider(
        cls,
        provider_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> EmbeddingProvider:
        """Create an embedding provider of the specified type."""
        if provider_type not in cls.PROVIDERS:
            available = list(cls.PROVIDERS.keys())
            raise ValueError(
                f"Unknown provider type '{provider_type}'. Available: {available}"
            )

        provider_class = cls.PROVIDERS[provider_type]
        return provider_class(config)  # type: ignore

    @classmethod
    def get_default_provider(
        cls, config: Optional[Dict[str, Any]] = None
    ) -> EmbeddingProvider:
        """Get the default embedding provider (SentenceTransformer with fallback)."""
        try:
            return cls.create_provider("sentence_transformer", config)
        except ImportError:
            print(
                "Warning: SentenceTransformer not available, "
                "falling back to LocalEmbeddingProvider"
            )
            return cls.create_provider("local", config)

    @classmethod
    def list_available_providers(cls) -> List[str]:
        """List all available provider types."""
        return list(cls.PROVIDERS.keys())

    @classmethod
    def create_from_config(cls, full_config: Dict[str, Any]) -> EmbeddingProvider:
        """Create provider from configuration dict."""
        provider_type = full_config.get("provider", "local")
        provider_config = full_config.get("config", {})

        return cls.create_provider(provider_type, provider_config)
