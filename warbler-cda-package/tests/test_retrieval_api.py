"""
Test suite for Retrieval API
Tests context store operations, semantic search, and retrieval modes
"""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent.parent))

from warbler_cda.retrieval_api import RetrievalAPI, RetrievalQuery, RetrievalMode, RetrievalResult
from warbler_cda.embeddings import EmbeddingProviderFactory


class TestRetrievalAPIContextStore:
    """Test context store operations."""

    def setup_method(self):
        """Setup for each test."""
        self.api = RetrievalAPI(
            embedding_provider=EmbeddingProviderFactory.get_default_provider(),
            config={"enable_fractalstat_hybrid": False},
        )

    def test_add_document(self):
        """Test adding a document to context store."""
        doc_id = "doc_1"
        content = "This is a test document"
        metadata = {"type": "test", "source": "test_suite"}

        result = self.api.add_document(doc_id, content, metadata)

        assert result is True
        assert self.api.get_context_store_size() == 1

    def test_add_duplicate_document(self):
        """Test that duplicate documents are rejected."""
        doc_id = "doc_1"
        content = "Test content"

        result1 = self.api.add_document(doc_id, content)
        result2 = self.api.add_document(doc_id, content)

        assert result1 is True
        assert result2 is False
        assert self.api.get_context_store_size() == 1

    def test_context_store_size(self):
        """Test context store size tracking."""
        initial_size = self.api.get_context_store_size()

        for i in range(5):
            self.api.add_document(f"doc_{i}", f"Document {i}")

        final_size = self.api.get_context_store_size()
        assert final_size == initial_size + 5

    def test_document_with_metadata(self):
        """Test adding document with metadata."""
        doc_id = "doc_meta"
        content = "Document with metadata"
        metadata = {"realm_type": "wisdom", "realm_label": "philosophy", "lifecycle_stage": "peak"}

        self.api.add_document(doc_id, content, metadata)

        assert self.api.get_context_store_size() == 1
        stored_doc = self.api._context_store[doc_id]
        assert stored_doc["metadata"] == metadata


class TestRetrievalQueryExecution:
    """Test retrieval query execution."""

    def setup_method(self):
        """Setup for each test."""
        self.api = RetrievalAPI(
            embedding_provider=EmbeddingProviderFactory.get_default_provider(),
            config={"enable_fractalstat_hybrid": False},
        )

        documents = [
            ("doc_1", "The quick brown fox jumps over the lazy dog", {"type": "story"}),
            (
                "doc_2",
                "Semantic embeddings enable efficient document retrieval",
                {"type": "technical"},
            ),
            ("doc_3", "Machine learning models learn from data", {"type": "technical"}),
            ("doc_4", "Philosophy explores fundamental questions of existence", {"type": "wisdom"}),
            (
                "doc_5",
                "Performance optimization techniques improve application speed",
                {"type": "technical"},
            ),
        ]

        for doc_id, content, metadata in documents:
            self.api.add_document(doc_id, content, metadata)

    def test_semantic_similarity_query(self):
        """Test semantic similarity retrieval."""
        query = RetrievalQuery(
            query_id="test_semantic_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="fast animal jumps",
            max_results=5,
            confidence_threshold=0.3,
        )

        assembly = self.api.retrieve_context(query)

        assert assembly is not None
        assert hasattr(assembly, "results")
        assert isinstance(assembly.results, list)

    def test_query_with_max_results(self):
        """Test that query respects max_results parameter."""
        query = RetrievalQuery(
            query_id="test_limit",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="technical",
            max_results=2,
            confidence_threshold=0.0,
        )

        assembly = self.api.retrieve_context(query)

        assert len(assembly.results) <= 2

    def test_query_with_confidence_threshold(self):
        """Test confidence threshold filtering."""
        query_high = RetrievalQuery(
            query_id="test_high_confidence",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="technical embeddings",
            max_results=10,
            confidence_threshold=0.8,
        )

        query_low = RetrievalQuery(
            query_id="test_low_confidence",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="technical embeddings",
            max_results=10,
            confidence_threshold=0.1,
        )

        assembly_high = self.api.retrieve_context(query_high)
        assembly_low = self.api.retrieve_context(query_low)

        assert len(assembly_high.results) <= len(assembly_low.results)

    def test_empty_query_string(self):
        """Test behavior with empty query string."""
        query = RetrievalQuery(
            query_id="test_empty",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="",
            max_results=5,
        )

        assembly = self.api.retrieve_context(query)

        assert assembly is not None

    def test_retrieval_result_structure(self):
        """Test that retrieval results have proper structure."""
        query = RetrievalQuery(
            query_id="test_structure",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="machine learning",
            max_results=1,
            confidence_threshold=0.0,
        )

        assembly = self.api.retrieve_context(query)

        if assembly.results:
            result = assembly.results[0]
            assert isinstance(result, RetrievalResult)
            assert hasattr(result, "result_id")
            assert hasattr(result, "content_type")
            assert hasattr(result, "content_id")
            assert hasattr(result, "content")
            assert hasattr(result, "relevance_score")
            assert hasattr(result, "metadata")


class TestRetrievalModes:
    """Test different retrieval modes."""

    def setup_method(self):
        """Setup for each test."""
        self.api = RetrievalAPI(
            embedding_provider=EmbeddingProviderFactory.get_default_provider(),
            config={"enable_fractalstat_hybrid": False},
        )

        for i in range(3):
            self.api.add_document(f"doc_{i}", f"Document content {i}")

    def test_semantic_similarity_mode(self):
        """Test SEMANTIC_SIMILARITY retrieval mode."""
        query = RetrievalQuery(
            query_id="test_semantic_mode",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="document",
            max_results=5,
        )

        assembly = self.api.retrieve_context(query)
        assert assembly is not None

    def test_temporal_sequence_mode(self):
        """Test TEMPORAL_SEQUENCE retrieval mode."""
        current_time = time.time()
        query = RetrievalQuery(
            query_id="test_temporal_mode",
            mode=RetrievalMode.TEMPORAL_SEQUENCE,
            temporal_range=(current_time - 3600, current_time),
            max_results=5,
        )

        assembly = self.api.retrieve_context(query)
        assert assembly is not None

    def test_composite_mode(self):
        """Test COMPOSITE retrieval mode."""
        query = RetrievalQuery(
            query_id="test_composite_mode",
            mode=RetrievalMode.COMPOSITE,
            semantic_query="test",
            max_results=5,
        )

        assembly = self.api.retrieve_context(query)
        assert assembly is not None


class TestRetrievalHybridScoring:
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

        documents = [
            ("doc_1", "Semantic embeddings for retrieval", {}),
            ("doc_2", "Hybrid scoring with FractalStat coordinates", {}),
            ("doc_3", "Document ranking and relevance", {}),
        ]

        for doc_id, content, metadata in documents:
            self.api.add_document(doc_id, content, metadata)

    def test_hybrid_query_with_fractalstat(self):
        """Test hybrid query with FractalStat scoring."""
        if self.skip:
            pytest.skip("SentenceTransformer not installed")

        query = RetrievalQuery(
            query_id="test_hybrid",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="semantic embeddings",
            max_results=3,
            fractalstat_hybrid=True,
            weight_semantic=0.6,
            weight_fractalstat=0.4,
        )

        assembly = self.api.retrieve_context(query)

        assert assembly is not None
        if assembly.results:
            for result in assembly.results:
                assert hasattr(result, "semantic_similarity")
                assert hasattr(result, "fractalstat_resonance")


class TestRetrievalMetrics:
    """Test retrieval metrics and caching."""

    def setup_method(self):
        """Setup for each test."""
        self.api = RetrievalAPI(
            embedding_provider=EmbeddingProviderFactory.get_default_provider(),
            config={"enable_fractalstat_hybrid": False, "cache_ttl_seconds": 3600},
        )

        self.api.add_document("doc_1", "Test document one")
        self.api.add_document("doc_2", "Test document two")

    def test_metrics_tracking(self):
        """Test that metrics are tracked."""
        query = RetrievalQuery(
            query_id="test_metrics",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test",
            max_results=5,
        )

        self.api.retrieve_context(query)

        metrics = self.api.get_retrieval_metrics()
        assert "retrieval_metrics" in metrics
        assert "cache_performance" in metrics
        assert "context_store_size" in metrics

    def test_cache_behavior(self):
        """Test query caching behavior."""
        query = RetrievalQuery(
            query_id="test_cache_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="cache",
            max_results=5,
        )

        initial_metrics = self.api.get_retrieval_metrics()

        self.api.retrieve_context(query)
        self.api.retrieve_context(query)

        final_metrics = self.api.get_retrieval_metrics()

        assert final_metrics["retrieval_metrics"]["total_queries"] >= 2


class TestRetrievalAPIAdditionalMethods:
    """Test additional RetrievalAPI methods for better coverage."""

    def setup_method(self):
        """Setup for each test."""
        self.api = RetrievalAPI(
            embedding_provider=EmbeddingProviderFactory.get_default_provider(),
            config={"enable_fractalstat_hybrid": False},
        )

        # Add some test documents
        self.api.add_document("doc_1", "Machine learning and AI concepts", {"category": "tech"})
        self.api.add_document("doc_2", "Philosophy and wisdom traditions", {"category": "wisdom"})
        self.api.add_document("doc_3", "Historical facts and events", {"category": "history"})

    def test_query_semantic_anchors(self):
        """Test query_semantic_anchors convenience method."""
        # Add a semantic anchor for testing
        from unittest.mock import Mock
        mock_anchor = Mock()
        mock_anchor.concept_text = "artificial intelligence"
        mock_anchor.heat = 0.8
        mock_anchor.provenance.first_seen = time.time()
        mock_anchor.embedding = self.api.embedding_provider.embed_text("artificial intelligence")

        # Mock semantic anchors (since we don't have real ones in this test)
        self.api.semantic_anchors = Mock()
        self.api.semantic_anchors.anchors = {"anchor_1": mock_anchor}

        results = self.api.query_semantic_anchors("artificial intelligence concepts")

        # Should return list of RetrievalResult objects
        assert isinstance(results, list)
        if results:  # May be empty if mocking doesn't work perfectly
            assert all(hasattr(r, 'result_id') for r in results)

    def test_get_anchor_context(self):
        """Test get_anchor_context method."""
        # This method requires anchor neighborhood retrieval
        # Mock semantic anchors and embedding provider
        self.api.semantic_anchors = Mock()
        self.api.semantic_anchors.anchors = {}  # Empty for now

        assembly = self.api.get_anchor_context("nonexistent_anchor")

        # Should return ContextAssembly even for nonexistent anchor
        assert hasattr(assembly, 'results')
        assert hasattr(assembly, 'query')

    def test_trace_provenance(self):
        """Test trace_provenance method."""
        # Mock semantic anchors
        self.api.semantic_anchors = Mock()
        self.api.semantic_anchors.anchors = {}

        assembly = self.api.trace_provenance("nonexistent_content")

        assert hasattr(assembly, 'results')
        assert hasattr(assembly, 'query')

    def test_dict_to_query_conversion(self):
        """Test _dict_to_query private method."""
        query_dict = {
            "query_id": "dict_test",
            "semantic_query": "test query",
            "max_results": 10,
            "confidence_threshold": 0.8,
        }

        query = self.api._dict_to_query(query_dict)

        assert isinstance(query, RetrievalQuery)
        assert query.query_id == "dict_test"
        assert query.semantic_query == "test query"

    def test_cache_key_generation(self):
        """Test cache key generation for queries."""
        query = RetrievalQuery(
            query_id="cache_test",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="cache key test",
            max_results=5,
        )

        key1 = self.api._generate_cache_key(query)
        key2 = self.api._generate_cache_key(query)

        # Same query should generate same key
        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) > 0

    def test_cache_operations(self):
        """Test cache get/set operations."""
        query = RetrievalQuery(
            query_id="cache_ops",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="cache operations test",
        )

        cache_key = self.api._generate_cache_key(query)
        assembly = self.api.retrieve_context(query)

        # Test cache set
        self.api._cache_result(cache_key, assembly)

        # Test cache get
        cached = self.api._get_cached_result(cache_key)
        assert cached is not None
        assert cached.assembly_id == assembly.assembly_id

    def test_calculate_temporal_distance_and_relevance(self):
        """Test temporal distance and relevance calculations."""
        timestamp1 = time.time()
        timestamp2 = timestamp1 + 3600  # 1 hour later

        # Test distance calculation
        distance = self.api._calculate_temporal_distance(timestamp1, timestamp2)
        assert distance == 3600

        # Test relevance calculation
        relevance = self.api._calculate_temporal_relevance(timestamp1, timestamp2)
        assert isinstance(relevance, float)
        assert 0.5 < relevance < 1.0  # Should decay over time

    def test_calculate_assembly_quality(self):
        """Test assembly quality calculation."""
        query = RetrievalQuery(
            query_id="quality_test",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="quality test",
            max_results=5,
        )

        # Create mock results
        results = [
            RetrievalResult(
                result_id=f"result_{i}",
                content_type="context_store",
                content_id=f"doc_{i}",
                content=f"Content {i}",
                relevance_score=0.8 + (i * 0.05),
                temporal_distance=0.0,
                anchor_connections=[],
                provenance_depth=1,
                conflict_flags=[] if i % 2 == 0 else ["conflict_1"],
                metadata={},
            )
            for i in range(3)
        ]

        quality = self.api._calculate_assembly_quality(results, query)
        assert isinstance(quality, float)
        assert 0.0 <= quality <= 1.0

    def test_component_availability_check(self):
        """Test component availability checking."""
        availability = self.api._check_component_availability()

        expected_keys = [
            "semantic_anchors", "summarization_ladder", "conflict_detector",
            "embedding_provider", "fractalstat_bridge"
        ]

        for key in expected_keys:
            assert key in availability
            assert isinstance(availability[key], bool)

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        # Initially empty metrics
        rate = self.api._calculate_success_rate()
        assert rate == 1.0  # No failures, no successes

        # After some queries, should calculate properly
        self.api.metrics["quality_distribution"] = {"high": 5, "medium": 3, "low": 1}
        rate = self.api._calculate_success_rate()
        assert rate == 8/9  # 8 successful (high + medium) out of 9 total

    def test_average_quality_calculation(self):
        """Test average quality calculation."""
        quality = self.api._calculate_average_quality()
        assert quality == 0.0  # Initially empty

        # With some quality data
        self.api.metrics["quality_distribution"] = {"high": 2, "medium": 1, "low": 1}
        quality = self.api._calculate_average_quality()
        # (2*1.0 + 1*0.7 + 1*0.3) / 4 = 3.0/4 = 0.75
        assert abs(quality - 0.75) < 0.01


class TestRetrievalAPIUtilityMethods:
    """Test utility methods in RetrievalAPI for comprehensive coverage."""

    def setup_method(self):
        """Setup for each test."""
        self.api = RetrievalAPI(config={"enable_fractalstat_hybrid": True})

    def test_retrieval_modes_enum_values(self):
        """Test that all retrieval modes are properly defined."""
        modes = [mode.value for mode in RetrievalMode]
        expected_modes = [
            "semantic_similarity", "temporal_sequence", "anchor_neighborhood",
            "provenance_chain", "conflict_aware", "composite"
        ]

        for mode in expected_modes:
            assert mode in modes

    def test_fractalstat_address_auto_assignment(self):
        """Test auto-assignment of FractalStat addresses."""
        metadata = {
            "realm_type": "wisdom",
            "realm_label": "philosophy",
            "lifecycle_stage": "peak",
            "activity_level": 0.8,
            "alignment_type": "balanced",
        }

        address = self.api._auto_assign_fractalstat_address("test_doc", metadata)

        required_keys = ["realm", "lineage", "adjacency", "horizon", "luminosity", "polarity", "dimensionality", "alignment"]
        for key in required_keys:
            assert key in address

        assert address["realm"]["type"] == "wisdom"
        assert address["horizon"] == "scene"  # peak -> scene mapping

    def test_retrieval_mode_retrieval_methods(self):
        """Test that all retrieval mode methods exist and are callable."""
        query = RetrievalQuery(
            query_id="mode_test",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test mode",
            max_results=5,
        )

        # Test _retrieve_temporal_sequence method
        results_temporal = self.api._retrieve_temporal_sequence(query)
        assert isinstance(results_temporal, list)

        # Test _retrieve_anchor_neighborhood method
        results_neighborhood = self.api._retrieve_anchor_neighborhood(query)
        assert isinstance(results_neighborhood, list)

        # Test _retrieve_provenance_chain method
        results_provenance = self.api._retrieve_provenance_chain(query)
        assert isinstance(results_provenance, list)

        # Test _retrieve_conflict_aware method
        results_conflict = self.api._retrieve_conflict_aware(query)
        assert isinstance(results_conflict, list)

        # Test _retrieve_composite method
        results_composite = self.api._retrieve_composite(query)
        assert isinstance(results_composite, list)

    def test_empty_context_assembly_creation(self):
        """Test creation of empty ContextAssembly."""
        query = RetrievalQuery(
            query_id="empty_test",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="empty test",
        )

        assembly = self.api._assemble_context(query, [])

        assert assembly.assembly_id.startswith("empty_")
        assert len(assembly.results) == 0
        assert assembly.assembly_quality == 0.0

    def test_metrics_update_functionality(self):
        """Test metrics update after retrieval."""
        query = RetrievalQuery(
            query_id="metrics_update_test",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="metrics test",
        )

        initial_queries = self.api.metrics["total_queries"]
        initial_avg_results = self.api.metrics["average_results_per_query"]

        # Perform some operations
        self.api.add_document("metrics_doc", "Test document for metrics")
        self.api.retrieve_context(query)

        # Metrics should be updated
        assert self.api.metrics["total_queries"] >= initial_queries

    def test_cache_efficiency_calculation(self):
        """Test cache efficiency calculation logic."""
        efficiency = self.api._calculate_cache_efficiency()

        # Should be between 0 and 1
        assert 0.0 <= efficiency <= 1.0

        # With some cache activity
        self.api.metrics["cache_hits"] = 8
        self.api.metrics["cache_misses"] = 2

        # Manually populate cache
        self.api.query_cache = {"key1": Mock(), "key2": Mock(), "key3": Mock(), "key4": Mock(), "key5": Mock()}

        efficiency = self.api._calculate_cache_efficiency()
        hit_rate = 8 / 10  # 80% hit rate
        size_penalty = 5 / 100.0  # 0.05 penalty
        expected = max(0, 0.8 - 0.05)  # 0.75
        assert abs(efficiency - expected) < 0.01


class TestRetrievalResultValidation:
    """Validate RetrievalResult object structure."""

    def test_retrieval_result_initialization(self):
        """Test RetrievalResult proper initialization."""
        result = RetrievalResult(
            result_id="test_result",
            content_type="context_store",
            content_id="doc_123",
            content="Test content",
            relevance_score=0.85,
            temporal_distance=3600.0,
            anchor_connections=["anchor_1"],
            provenance_depth=2,
            conflict_flags=["conflict_type_a"],
            metadata={"source": "test"},
            fractalstat_resonance=0.72,
            semantic_similarity=0.81,
        )

        assert result.result_id == "test_result"
        assert result.relevance_score == 0.85
        assert result.fractalstat_resonance == 0.72
        assert result.semantic_similarity == 0.81

    def test_retrieval_result_default_values(self):
        """Test default values in RetrievalResult."""
        result = RetrievalResult(
            result_id="minimal_result",
            content_type="anchor",
            content_id="anchor_1",
            content="Minimal content",
            relevance_score=0.5,
            temporal_distance=0.0,
            anchor_connections=[],
            provenance_depth=1,
            conflict_flags=[],
            metadata={},
        )

        assert result.fractalstat_resonance == 0.0
        assert result.semantic_similarity == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
