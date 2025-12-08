"""Test suite for embedding providers.

Tests local provider, OpenAI provider, and SentenceTransformer provider.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from warbler_cda.embeddings import (
    EmbeddingProviderFactory,
    LocalEmbeddingProvider,
    EmbeddingProvider,
)


class TestEmbeddingProviderFactory:
    """Test embedding provider factory."""

    def test_factory_creates_local_provider(self):
        """Test that factory can create local provider."""
        provider = EmbeddingProviderFactory.create_provider("local", {"dimension": 64})
        assert isinstance(provider, LocalEmbeddingProvider)
        assert provider.get_dimension() == 64

    def test_factory_list_available_providers(self):
        """Test that factory lists available providers."""
        providers = EmbeddingProviderFactory.list_available_providers()
        assert "local" in providers
        assert "sentence_transformer" in providers

    def test_factory_default_provider(self):
        """Test that factory can create default provider."""
        try:
            provider = EmbeddingProviderFactory.get_default_provider()
            assert provider is not None
            assert hasattr(provider, "embed_text")
            assert hasattr(provider, "embed_batch")
        except ImportError:
            pytest.skip("SentenceTransformer not installed, " "testing with local fallback")


class TestLocalEmbeddingProvider:
    """Test local TF-IDF embedding provider."""

    def setup_method(self):
        """Setup for each test."""
        self.provider = LocalEmbeddingProvider({"dimension": 128})

    def test_embed_single_text(self):
        """Test embedding a single text."""
        text = "This is a test document about semantic embeddings"
        embedding = self.provider.embed_text(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 128
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_batch(self):
        """Test batch embedding."""
        texts = [
            "First document about embeddings",
            "Second document about semantics",
            "Third document about search",
        ]

        embeddings = self.provider.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 128 for emb in embeddings)

    def test_similarity_calculation(self):
        """Test cosine similarity calculation."""
        text1 = "performance optimization techniques"
        text2 = "performance and optimization"
        text3 = "completely unrelated weather report"

        emb1 = self.provider.embed_text(text1)
        emb2 = self.provider.embed_text(text2)
        emb3 = self.provider.embed_text(text3)

        sim_12 = self.provider.calculate_similarity(emb1, emb2)
        sim_13 = self.provider.calculate_similarity(emb1, emb3)

        assert 0.0 <= sim_12 <= 1.0
        assert 0.0 <= sim_13 <= 1.0
        assert sim_12 > sim_13, "Similar texts should have higher similarity"

    def test_provider_info(self):
        """Test provider info method."""
        info = self.provider.get_provider_info()

        assert "provider_id" in info
        assert "dimension" in info
        assert info["dimension"] == 128
        assert info["provider_id"] == "LocalEmbeddingProvider"


class TestSentenceTransformerProvider:
    """Test SentenceTransformer embedding provider."""

    def setup_method(self):
        """Setup for each test."""
        try:
            from warbler_cda.embeddings.sentence_transformer_provider import (
                SentenceTransformerEmbeddingProvider,
            )

            self.provider_class = SentenceTransformerEmbeddingProvider
            self.skip = False
        except ImportError:
            self.skip = True

    def test_provider_initialization(self):
        """Test SentenceTransformer provider initialization."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        provider = self.provider_class()
        assert provider.model is not None
        assert provider.device in ["cpu", "cuda"]
        assert provider.get_dimension() == 384

    def test_embed_text_with_cache(self):
        """Test embedding with caching."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        provider = self.provider_class()
        text = "Cache test document for embeddings"

        emb1 = provider.embed_text(text)
        hits_before = provider.cache_stats["hits"]

        emb2 = provider.embed_text(text)
        hits_after = provider.cache_stats["hits"]

        assert emb1 == emb2, "Same text should produce same embedding"
        assert hits_after > hits_before, "Cache should register hit"

    def test_batch_embedding(self):
        """Test batch embedding with SentenceTransformer."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        provider = self.provider_class()
        texts = [
            "First test document",
            "Second test document",
            "Third test document",
        ]

        embeddings = provider.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)

    def test_semantic_search(self):
        """Test semantic search functionality."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        provider = self.provider_class()

        documents = [
            "The quick brown fox jumps over the lazy dog",
            "Semantic embeddings enable efficient document retrieval",
            "Machine learning models process text data",
            "Neural networks learn from examples",
        ]

        embeddings = [provider.embed_text(doc) for doc in documents]

        query = "fast animal and jumping"
        results = provider.semantic_search(query, embeddings, top_k=2)

        assert len(results) == 2
        assert all(isinstance(idx, int) and isinstance(score, float) for idx, score in results)
        assert results[0][0] == 0, "First document should be most similar to jumping query"

    def test_fractalstat_computation(self):
        """Test FractalStat coordinate computation from embedding."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        provider = self.provider_class()
        text = "Test document for FractalStat computation"
        embedding = provider.embed_text(text)

        fractalstat = provider.compute_fractalstat_from_embedding(embedding)

        assert "lineage" in fractalstat
        assert "adjacency" in fractalstat
        assert "luminosity" in fractalstat
        assert "polarity" in fractalstat
        assert "dimensionality" in fractalstat
        assert "horizon" in fractalstat
        assert "realm" in fractalstat

        # Verify expected ranges for different dimensions:
        # lineage: unbounded positive (energy-based, generation/passage)
        # adjacency: [-1, 1] (semantic connectivity)
        # luminosity: [0, 100] (activity/coherence level)
        # polarity: [-1, 1] (resonance balance)
        # dimensionality: [1, 8] (complexity depth)
        assert fractalstat["lineage"] >= 0.0, "lineage should be non-negative"
        assert -1.0 <= fractalstat["adjacency"] <= 1.0, "adjacency should be between -1 and 1"
        assert 0.0 <= fractalstat["luminosity"] <= 100.0, "luminosity should be between 0 and 100"
        assert -1.0 <= fractalstat["polarity"] <= 1.0, "polarity should be between -1 and 1"
        assert 1 <= fractalstat["dimensionality"] <= 8, "dimensionality should be between 1 and 8"

    def test_provider_info(self):
        """Test provider info."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        provider = self.provider_class()
        info = provider.get_provider_info()

        assert "provider_id" in info
        assert "model_name" in info
        assert "device" in info
        assert "dimension" in info
        assert info["dimension"] == 384


class TestEmbeddingProviderInterface:
    """Test the EmbeddingProvider abstract interface."""

    def test_local_provider_implements_interface(self):
        """Test that LocalEmbeddingProvider implements full interface."""
        provider = LocalEmbeddingProvider()

        assert isinstance(provider, EmbeddingProvider)
        assert hasattr(provider, "embed_text")
        assert hasattr(provider, "embed_batch")
        assert hasattr(provider, "calculate_similarity")
        assert hasattr(provider, "get_dimension")
        assert hasattr(provider, "get_provider_info")

    def test_embedding_dimension_consistency(self):
        """Test that all embeddings have consistent dimension."""
        provider = LocalEmbeddingProvider({"dimension": 128})

        texts = ["First", "Second", "Third", "Fourth"]
        embeddings = provider.embed_batch(texts)

        expected_dim = provider.get_dimension()
        for emb in embeddings:
            assert len(emb) == expected_dim

    def test_similarity_bounds(self):
        """Test that similarity scores are in valid range."""
        provider = LocalEmbeddingProvider()

        text1 = "Test document one"
        text2 = "Test document two"

        emb1 = provider.embed_text(text1)
        emb2 = provider.embed_text(text2)

        similarity = provider.calculate_similarity(emb1, emb2)
        assert -1.0 <= similarity <= 1.0, "Similarity should be between -1 and 1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
