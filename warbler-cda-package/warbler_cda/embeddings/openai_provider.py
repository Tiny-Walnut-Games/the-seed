"""
OpenAI Embedding Provider - Cloud-based Semantic Grounding
"""

import hashlib
import math
import struct
from typing import Any, Dict, List, Optional
from types import ModuleType

from .base_provider import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI API-based embedding provider."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key: Optional[str] = config.get("api_key") if config else None
        model_default = "text-embedding-ada-002"
        self.model: str = (
            config.get("model", model_default) if config else model_default
        )
        self.dimension: int = config.get("dimension", 1536) if config else 1536
        self._client: Optional[ModuleType] = None

    def _get_client(self) -> ModuleType:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                import openai

                if self.api_key:
                    openai.api_key = self.api_key
                self._client = openai
            except ImportError as exc:
                raise ImportError(
                    "OpenAI package not installed. Run: pip install openai"
                ) from exc
        return self._client

    def embed_text(self, text: str) -> List[float]:
        """Generate OpenAI embedding for text."""
        try:
            client = self._get_client()
            response: Dict[str, Any] = client.Embedding.create(  # pylint: disable=no-member
                model=self.model, input=text
            )
            return response["data"][0]["embedding"]
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Warning: OpenAI API failed ({e}), using mock embedding")
            return self._create_mock_embedding(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate OpenAI embeddings for multiple texts."""
        try:
            client = self._get_client()
            response: Dict[str, Any] = client.Embedding.create(  # pylint: disable=no-member
                model=self.model, input=texts
            )
            return [item["embedding"] for item in response["data"]]
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Warning: OpenAI API failed ({e}), using mock embeddings")
            return [self._create_mock_embedding(text) for text in texts]

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension

    def _create_mock_embedding(self, text: str) -> List[float]:
        """Create a mock embedding for development/testing."""
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        vector = []
        for i in range(0, min(len(hash_bytes), self.dimension // 4 * 4), 4):
            value = struct.unpack("f", hash_bytes[i : i + 4])[0]
            vector.append(value)

        while len(vector) < self.dimension:
            seed = len(vector) + hash(text)
            normalized_val = (seed % 1000) / 1000.0 - 0.5
            vector.append(normalized_val)

        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude > 0:
            vector = [x / magnitude for x in vector]

        return vector
