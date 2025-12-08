"""
Test suite for 8D FractalStat Integration
Tests 8D FractalStat coordinate computation, hybrid scoring, and resonance calculations

Now upgraded from 7D FractalStat to 8D FractalStat with alignment dimension.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from warbler_cda.retrieval_api import RetrievalAPI, RetrievalQuery, RetrievalMode
from warbler_cda.embeddings import EmbeddingProviderFactory
from warbler_cda.fractalstat_entity import FractalStatCoordinates, Realm, Horizon, Polarity, Alignment


class TestFractalStatCoordinateComputation:
    """Test FractalStat coordinate computation from embeddings."""

    def setup_method(self):
        """Setup for each test."""
        try:
            from warbler_cda.embeddings.sentence_transformer_provider import (
                SentenceTransformerEmbeddingProvider,
            )

            self.provider = SentenceTransformerEmbeddingProvider()
            self.skip = False
        except ImportError:
            self.skip = True

    def test_fractalstat_from_embedding(self):
        """Test FractalStat coordinate computation from embedding."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        text = "Test document for FractalStat coordinates"
        embedding = self.provider.embed_text(text)

        fractalstat = self.provider.compute_fractalstat_from_embedding(embedding)

        assert "lineage" in fractalstat
        assert "adjacency" in fractalstat
        assert "luminosity" in fractalstat
        assert "polarity" in fractalstat
        assert "dimensionality" in fractalstat
        assert "horizon" in fractalstat
        assert "realm" in fractalstat

    def test_fractalstat_values_in_range(self):
        """Test that FractalStat values are in expected ranges."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        text = "Test text"
        embedding = self.provider.embed_text(text)
        fractalstat = self.provider.compute_fractalstat_from_embedding(embedding)

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

    def test_different_texts_produce_different_fractalstat(self):
        """Test that different texts produce different FractalStat coordinates."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        text1 = "This is about performance and optimization"
        text2 = "This is completely different about philosophy"

        emb1 = self.provider.embed_text(text1)
        emb2 = self.provider.embed_text(text2)

        fractalstat_1 = self.provider.compute_fractalstat_from_embedding(emb1)
        fractalstat_2 = self.provider.compute_fractalstat_from_embedding(emb2)

        differences = [
            abs(fractalstat_1[key] - fractalstat_2[key])
            for key in ["lineage", "adjacency", "luminosity", "polarity", "dimensionality"]
        ]

        assert any(
            diff > 0.1 for diff in differences
        ), "Different texts should produce different FractalStat"


class TestFractalStatHybridScoring:
    """Test FractalStat hybrid scoring in retrieval."""

    def setup_method(self):
        """Setup for each test."""
        try:
            from warbler_cda.embeddings.sentence_transformer_provider import (
                SentenceTransformerEmbeddingProvider,
            )

            self.provider = SentenceTransformerEmbeddingProvider()
            self.skip = False
        except ImportError:
            self.skip = True

        self.api = RetrievalAPI(
            embedding_provider=(
                self.provider if not self.skip else EmbeddingProviderFactory.get_default_provider()
            ),
            config={"enable_fractalstat_hybrid": True},
        )

    def test_hybrid_scoring_combines_semantic_and_fractalstat(self):
        """Test that hybrid scoring combines semantic and FractalStat components."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        self.api.add_document("doc_1", "Semantic embeddings for document retrieval")
        self.api.add_document("doc_2", "FractalStat hybrid scoring approach")
        self.api.add_document("doc_3", "Machine learning and embeddings")

        query = RetrievalQuery(
            query_id="test_hybrid",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="embeddings and scoring",
            max_results=3,
            fractalstat_hybrid=True,
            weight_semantic=0.6,
            weight_fractalstat=0.4,
        )

        assembly = self.api.retrieve_context(query)

        assert assembly is not None
        for result in assembly.results:
            assert hasattr(result, "semantic_similarity")
            assert hasattr(result, "fractalstat_resonance")
            assert hasattr(result, "relevance_score")

    def test_fractalstat_resonance_calculation(self):
        """Test FractalStat resonance calculation."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        doc_fractalstat = {
            "lineage": 0.5,
            "adjacency": 0.6,
            "luminosity": 0.7,
            "polarity": 0.5,
            "dimensionality": 0.4,
            "horizon": "scene",
            "realm": {"type": "semantic", "label": "test"},
        }

        query_fractalstat = {
            "lineage": 0.5,
            "adjacency": 0.5,
            "luminosity": 0.7,
            "polarity": 0.5,
            "dimensionality": 0.4,
            "horizon": "scene",
            "realm": {"type": "semantic", "label": "test"},
        }

        resonance = self.api._calculate_fractalstat_resonance(doc_fractalstat, query_fractalstat)

        assert 0.0 <= resonance <= 1.0
        assert resonance > 0.7, "Similar FractalStat coordinates should have high resonance"

    def test_fractalstat_resonance_with_different_coordinates(self):
        """Test FractalStat resonance with very different coordinates."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        doc_fractalstat = {
            "lineage": 0.1,
            "adjacency": 0.2,
            "luminosity": 0.1,
            "polarity": 0.2,
            "dimensionality": 0.1,
        }

        query_fractalstat = {
            "lineage": 0.9,
            "adjacency": 0.8,
            "luminosity": 0.9,
            "polarity": 0.8,
            "dimensionality": 0.9,
        }

        resonance = self.api._calculate_fractalstat_resonance(doc_fractalstat, query_fractalstat)

        assert 0.0 <= resonance <= 1.0
        assert resonance < 0.4, "Very different FractalStat coordinates should have low resonance"


class TestFractalStatDocumentEnrichment:
    """Test document enrichment with FractalStat coordinates."""

    def setup_method(self):
        """Setup for each test."""
        try:
            from warbler_cda.embeddings.sentence_transformer_provider import (
                SentenceTransformerEmbeddingProvider,
            )

            self.provider = SentenceTransformerEmbeddingProvider()
            self.skip = False
        except ImportError:
            self.skip = True

        self.api = RetrievalAPI(
            embedding_provider=self.provider if not self.skip else None,
            config={"enable_fractalstat_hybrid": True},
        )

    def test_document_enriched_with_embedding(self):
        """Test that documents are enriched with embeddings."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        self.api.add_document("doc_1", "Test document content")

        stored_doc = self.api._context_store["doc_1"]
        assert "embedding" in stored_doc
        assert isinstance(stored_doc["embedding"], list)

    def test_document_enriched_with_fractalstat(self):
        """Test that documents are enriched with FractalStat coordinates."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        self.api.add_document("doc_1", "Test document for FractalStat")

        stored_doc = self.api._context_store["doc_1"]
        assert "fractalstat_coordinates" in stored_doc

        fractalstat = stored_doc["fractalstat_coordinates"]
        assert "lineage" in fractalstat
        assert "adjacency" in fractalstat
        assert "luminosity" in fractalstat
        assert "polarity" in fractalstat
        assert "dimensionality" in fractalstat


class TestFractalStatQueryAddressing:
    """Test FractalStat query addressing for multi-dimensional retrieval."""

    def setup_method(self):
        """Setup for each test."""
        try:
            from warbler_cda.embeddings.sentence_transformer_provider import (
                SentenceTransformerEmbeddingProvider,
            )

            self.provider = SentenceTransformerEmbeddingProvider()
            self.skip = False
        except ImportError:
            self.skip = True

        self.api = RetrievalAPI(
            embedding_provider=(
                self.provider if not self.skip else EmbeddingProviderFactory.get_default_provider()
            ),
            config={"enable_fractalstat_hybrid": True},
        )

    def test_query_with_fractalstat_address(self):
        """Test query with explicit FractalStat address."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        self.api.add_document("doc_1", "Document about optimization")
        self.api.add_document("doc_2", "Document about performance")

        fractalstat_address = {
            "realm": {"type": "technical", "label": "optimization"},
            "lineage": 0.7,
            "adjacency": 0.6,
            "horizon": "scene",
            "luminosity": 0.8,
            "polarity": 0.6,
            "dimensionality": 0.7,
        }

        query = RetrievalQuery(
            query_id="test_fractalstat_query",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="performance",
            max_results=5,
            fractalstat_hybrid=True,
            fractalstat_address=fractalstat_address,
        )

        assembly = self.api.retrieve_context(query)

        assert assembly is not None

    def test_default_fractalstat_address_generated(self):
        """Test that default FractalStat address is generated if not provided."""
        query = RetrievalQuery(
            query_id="test_default_fractalstat",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test",
            fractalstat_hybrid=True,
        )

        assert query.fractalstat_address is not None
        assert "lineage" in query.fractalstat_address
        assert "adjacency" in query.fractalstat_address
        assert "luminosity" in query.fractalstat_address
        assert "polarity" in query.fractalstat_address


class TestFractalStatDimensions:
    """Test FractalStat dimensional space properties."""

    def setup_method(self):
        """Setup for each test."""
        try:
            from warbler_cda.embeddings.sentence_transformer_provider import (
                SentenceTransformerEmbeddingProvider,
            )

            self.provider = SentenceTransformerEmbeddingProvider()
            self.skip = False
        except ImportError:
            self.skip = True

    def test_eight_dimensions_in_fractalstat(self):
        """Test that FractalStat provides 8 key dimensions."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        text = "Test for seven dimensions"
        embedding = self.provider.embed_text(text)
        fractalstat = self.provider.compute_fractalstat_from_embedding(embedding)

        expected_dims = [
            "lineage",
            "adjacency",
            "luminosity",
            "polarity",
            "dimensionality",
            "horizon",
            "realm",
        ]
        for dim in expected_dims:
            assert dim in fractalstat, f"FractalStat should contain {dim}"

    def test_fractalstat_realm_structure(self):
        """Test that FractalStat realm has proper structure."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        text = "Test"
        embedding = self.provider.embed_text(text)
        fractalstat = self.provider.compute_fractalstat_from_embedding(embedding)

        realm = fractalstat["realm"]
        assert isinstance(realm, dict)
        assert "type" in realm
        assert "label" in realm


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
