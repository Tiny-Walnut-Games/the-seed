"""
Mock tests for OpenAI Embedding Provider.

These tests mock OpenAI API calls to ensure coverage without requiring network access.
"""

from unittest.mock import MagicMock, patch
import sys
from pathlib import Path
import pytest
from warbler_cda.embeddings.openai_provider import OpenAIEmbeddingProvider

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestOpenAIEmbeddingProvider:
    """Mock tests for OpenAI embedding provider."""

    def setup_method(self):
        """Setup for each test."""
        self.provider = OpenAIEmbeddingProvider({ # pylint: disable=W0201
            "api_key": "test_key",
            "model": "text-embedding-ada-002",
            "dimension": 1536
        })

    def test_init(self):
        """Test provider initialization."""
        config = {
            "api_key": "test_api_key",
            "model": "text-embedding-3-small",
            "dimension": 1536
        }
        provider = OpenAIEmbeddingProvider(config)

        assert provider.api_key == "test_api_key"
        assert provider.model == "text-embedding-3-small"
        assert provider.dimension == 1536
        assert provider._client is None # pylint: disable=W0212

    def test_init_default_values(self):
        """Test initialization with default values."""
        provider = OpenAIEmbeddingProvider()

        assert provider.api_key is None
        assert provider.model == "text-embedding-ada-002"
        assert provider.dimension == 1536
        assert provider._client is None # pylint: disable=W0212

    @patch("builtins.__import__")
    def test_get_client_lazy_initialization(self, mock_import):
        """Test lazy initialization of OpenAI client."""
        mock_openai = MagicMock()
        mock_import.return_value = mock_openai

        client = self.provider._get_client() # pylint: disable=W0212

        assert client == mock_openai
        assert self.provider._client == mock_openai # pylint: disable=W0212
        # Test that API key is set
        assert mock_openai.api_key == "test_key"

        # Test that second call returns cached client (client stays the same)
        client2 = self.provider._get_client() # pylint: disable=W0212
        assert client2 == mock_openai

    @patch("builtins.__import__")
    def test_get_client_import_error(self, mock_import):
        """Test ImportError when openai is not installed."""
        mock_import.side_effect = ImportError("OpenAI package not installed")

        with pytest.raises(ImportError, match="OpenAI package not installed"):
            self.provider._get_client() # pylint: disable=W0212

    @patch("builtins.__import__")
    def test_embed_text_success(self, mock_import):
        """Test successful text embedding."""
        mock_openai = MagicMock()
        mock_openai.Embedding.create.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3]}]
        }
        mock_import.return_value = mock_openai

        result = self.provider.embed_text("test text")

        assert result == [0.1, 0.2, 0.3]
        mock_openai.Embedding.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input="test text"
        )

    @patch("builtins.__import__")
    def test_embed_text_fallback_on_failure(self, mock_import):
        """Test fallback to mock embedding when API fails."""
        mock_openai = MagicMock()
        mock_openai.Embedding.create.side_effect = Exception("API error")
        mock_import.return_value = mock_openai

        result = self.provider.embed_text("test text")

        assert isinstance(result, list)
        assert len(result) == 1536
        assert all(isinstance(x, float) for x in result)

    @patch("builtins.__import__")
    def test_embed_batch_success(self, mock_import):
        """Test successful batch embedding."""
        mock_openai = MagicMock()
        mock_openai.Embedding.create.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
                {"embedding": [0.7, 0.8, 0.9]}
            ]
        }
        mock_import.return_value = mock_openai

        texts = ["text1", "text2", "text3"]
        result = self.provider.embed_batch(texts)

        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        mock_openai.Embedding.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input=texts
        )

    @patch("builtins.__import__")
    def test_embed_batch_fallback_on_failure(self, mock_import):
        """Test fallback to mock embeddings when batch API fails."""
        mock_openai = MagicMock()
        mock_openai.Embedding.create.side_effect = Exception("API error")
        mock_import.return_value = mock_openai

        texts = ["text1", "text2", "text3"]
        result = self.provider.embed_batch(texts)

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(len(emb) == 1536 for emb in result)
        assert all(all(isinstance(x, float) for x in emb) for emb in result)

    def test_get_dimension(self):
        """Test getting embedding dimension."""
        assert self.provider.get_dimension() == 1536

    def test_create_mock_embedding(self):
        """Test creation of mock embedding."""
        result = self.provider._create_mock_embedding("test text") # pylint: disable=W0212

        assert isinstance(result, list)
        assert len(result) == 1536
        assert all(isinstance(x, float) for x in result)

        # Test that same text produces same embedding
        result2 = self.provider._create_mock_embedding("test text") # pylint: disable=W0212
        assert result == result2

        # Test that different text produces different embedding
        result3 = self.provider._create_mock_embedding("different text") # pylint: disable=W0212
        assert result != result3

    def test_create_mock_embedding_normalization(self):
        """Test that mock embeddings are normalized."""
        result = self.provider._create_mock_embedding("test") # pylint: disable=W0212

        # Calculate magnitude
        magnitude = sum(x * x for x in result) ** 0.5
        # Should be close to 1.0 (normalized)
        assert abs(magnitude - 1.0) < 0.01

    def test_provider_id(self):
        """Test provider ID."""
        assert self.provider.provider_id == "OpenAIEmbeddingProvider"

    def test_provider_info(self):
        """Test provider info method."""
        info = self.provider.get_provider_info()

        assert info["provider_id"] == "OpenAIEmbeddingProvider"
        assert info["dimension"] == 1536
        assert "created_at" in info
        assert "config_keys" in info
