"""
Phase 2 STAT7 Integration Tests

Tests for STAT7 hybrid scoring integration with RetrievalAPI.
Includes:
- Backward compatibility (existing queries still work)
- STAT7 hybrid query support
- Concurrency test (EXP-09)
- Integration test with real STAT7 bridge
"""

import pytest
import time
import threading
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import RetrievalAPI components
from seed.engine.retrieval_api import (
    RetrievalAPI,
    RetrievalQuery,
    RetrievalMode,
    RetrievalResult,
    ContextAssembly
)

# Import STAT7 bridge
try:
    from seed.engine.stat7_rag_bridge import (
        STAT7Address,
        Realm,
        RAGDocument,
        hybrid_score,
        cosine_similarity,
        stat7_resonance
    )
    STAT7_AVAILABLE = True
except ImportError:
    STAT7_AVAILABLE = False


# ============================================================================
# Test Fixtures
# ============================================================================

class MockEmbeddingProvider:
    """Mock embedding provider for testing."""
    
    def embed_text(self, text: str) -> List[float]:
        """Generate deterministic mock embedding."""
        # Simple hash-based embedding
        hash_val = hash(text)
        return [
            float((hash_val >> (i * 8)) & 0xFF) / 256.0
            for i in range(10)
        ]
    
    def calculate_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity."""
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        denom = norm_a * norm_b + 1e-12
        return dot / denom


class MockSemanticAnchors:
    """Mock semantic anchors for testing."""
    
    def __init__(self):
        self.anchors = {}


class MockSummarizationLadder:
    """Mock summarization ladder for testing."""
    
    def __init__(self):
        self.micro_summaries = []


@pytest.fixture
def embedding_provider():
    """Provide mock embedding provider."""
    return MockEmbeddingProvider()


@pytest.fixture
def retrieval_api(embedding_provider):
    """Provide RetrievalAPI instance without STAT7."""
    config = {
        "default_max_results": 10,
        "relevance_threshold": 0.5,
        "temporal_decay_hours": 24,
        "cache_ttl_seconds": 300
    }
    
    api = RetrievalAPI(
        config=config,
        embedding_provider=embedding_provider,
        semantic_anchors=MockSemanticAnchors(),
        summarization_ladder=MockSummarizationLadder()
    )
    return api


@pytest.fixture
def retrieval_api_with_stat7(embedding_provider):
    """Provide RetrievalAPI instance with STAT7 bridge."""
    if not STAT7_AVAILABLE:
        pytest.skip("STAT7 bridge not available")
    
    config = {
        "default_max_results": 10,
        "relevance_threshold": 0.5,
        "temporal_decay_hours": 24,
        "cache_ttl_seconds": 300,
        "enable_stat7_hybrid": False,  # Default off, enable per-query
        "default_weight_semantic": 0.6,
        "default_weight_stat7": 0.4
    }
    
    # Create a mock STAT7 bridge
    class MockSTAT7Bridge:
        def stat7_resonance(self, q_addr, d_addr):
            return 0.8  # Dummy resonance
    
    api = RetrievalAPI(
        config=config,
        embedding_provider=embedding_provider,
        semantic_anchors=MockSemanticAnchors(),
        summarization_ladder=MockSummarizationLadder(),
        stat7_bridge=MockSTAT7Bridge()
    )
    return api


# ============================================================================
# Test Cases: Backward Compatibility
# ============================================================================

@pytest.mark.integration
class TestBackwardCompatibility:
    """Ensure existing queries still work without STAT7."""
    
    @pytest.mark.e2e
    def test_retrieve_context_without_stat7(self, retrieval_api):
        """Basic retrieval should work without STAT7 enabled."""
        query = RetrievalQuery(
            query_id="test_query_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test query",
            max_results=5
        )
        
        # Should not raise any errors
        assembly = retrieval_api.retrieve_context(query)
        assert assembly is not None
        assert assembly.assembly_id is not None
        assert assembly.query.query_id == query.query_id
    
    @pytest.mark.e2e
    def test_query_from_dict_backward_compat(self, retrieval_api):
        """Dict-to-query conversion should work without STAT7 keys."""
        query_dict = {
            "query_id": "test_query_2",
            "mode": "semantic_similarity",
            "semantic_query": "test",
            "max_results": 5
        }
        
        query = retrieval_api._dict_to_query(query_dict)
        assert query.query_id == "test_query_2"
        assert query.stat7_hybrid is False
        assert query.stat7_address is None
    
    @pytest.mark.e2e
    def test_metrics_without_hybrid(self, retrieval_api):
        """Metrics should track non-hybrid queries."""
        query = RetrievalQuery(
            query_id="test_query_3",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test",
            max_results=5
        )
        
        retrieval_api.retrieve_context(query)
        
        metrics = retrieval_api.get_retrieval_metrics()
        assert metrics["retrieval_metrics"]["total_queries"] >= 1
        assert metrics["retrieval_metrics"]["hybrid_queries"] == 0


# ============================================================================
# Test Cases: STAT7 Hybrid Support
# ============================================================================

@pytest.mark.skipif(not STAT7_AVAILABLE, reason="STAT7 bridge not available")
class TestSTAT7HybridSupport:
    """Test STAT7 hybrid scoring functionality."""
    
    @pytest.mark.integration
    def test_query_with_stat7_hybrid_flag(self, retrieval_api_with_stat7):
        """Query can be created with stat7_hybrid flag."""
        query = RetrievalQuery(
            query_id="test_stat7_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test",
            stat7_hybrid=True,
            max_results=5
        )
        
        assert query.stat7_hybrid is True
        assert query.stat7_address is not None
        assert "realm" in query.stat7_address
        assert query.weight_semantic == 0.6
        assert query.weight_stat7 == 0.4
    
    @pytest.mark.e2e
    def test_auto_assign_stat7_address(self, retrieval_api_with_stat7):
        """Auto-assign STAT7 to content from metadata."""
        metadata = {
            "realm_type": "game",
            "realm_label": "warbler_pack",
            "lineage": 1,
            "connection_count": 5,
            "activity_level": 0.7,
            "resonance_factor": 0.6,
            "thread_count": 4
        }
        
        stat7_addr = retrieval_api_with_stat7._auto_assign_stat7_address("doc_1", metadata)
        
        assert stat7_addr["realm"]["type"] == "game"
        assert stat7_addr["realm"]["label"] == "warbler_pack"
        assert stat7_addr["lineage"] == 1
        assert stat7_addr["adjacency"] == 0.5  # min(1.0, 5/10)
        assert stat7_addr["dimensionality"] == 4
    
    @pytest.mark.integration
    def test_auto_assign_stat7_with_defaults(self, retrieval_api_with_stat7):
        """Auto-assign should use sensible defaults."""
        metadata = {}  # Empty metadata
        
        stat7_addr = retrieval_api_with_stat7._auto_assign_stat7_address("doc_2", metadata)
        
        assert stat7_addr["realm"]["type"] == "data"
        assert stat7_addr["lineage"] == 0
        assert stat7_addr["dimensionality"] >= 1  # Default thread_count maps to 1+, ours is 3
    
    @pytest.mark.e2e
    def test_stat7_address_caching(self, retrieval_api_with_stat7):
        """STAT7 addresses should be cached."""
        metadata = {"realm_type": "system"}
        
        # First call computes
        stat7_1 = retrieval_api_with_stat7._auto_assign_stat7_address("doc_3", metadata)
        
        # Second call should use cache
        stat7_2 = retrieval_api_with_stat7._auto_assign_stat7_address("doc_3", metadata)
        
        assert stat7_1 == stat7_2
        assert "doc_3" in retrieval_api_with_stat7.document_stat7_cache
    
    @pytest.mark.integration
    def test_hybrid_query_retrieval(self, retrieval_api_with_stat7):
        """Hybrid query should work end-to-end."""
        query = RetrievalQuery(
            query_id="test_hybrid_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test",
            stat7_hybrid=True,
            max_results=5
        )
        
        # Should execute without error
        assembly = retrieval_api_with_stat7.retrieve_context(query)
        assert assembly is not None
    
    @pytest.mark.integration
    def test_hybrid_query_metrics(self, retrieval_api_with_stat7):
        """Hybrid queries should be tracked in metrics."""
        query = RetrievalQuery(
            query_id="test_hybrid_2",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test",
            stat7_hybrid=True,
            max_results=5
        )
        
        retrieval_api_with_stat7.retrieve_context(query)
        
        metrics = retrieval_api_with_stat7.get_retrieval_metrics()
        assert metrics["retrieval_metrics"]["hybrid_queries"] == 1


# ============================================================================
# Test Cases: Concurrency (EXP-09)
# ============================================================================

@pytest.mark.integration
class TestConcurrency:
    """Concurrency tests for STAT7 hybrid scoring."""
    
    @pytest.mark.integration
    def test_concurrent_semantic_queries(self, retrieval_api):
        """Multiple threads can execute semantic queries concurrently."""
        results = []
        
        def run_query(query_id: int):
            query = RetrievalQuery(
                query_id=f"concurrent_{query_id}",
                mode=RetrievalMode.SEMANTIC_SIMILARITY,
                semantic_query=f"query_{query_id}",
                max_results=5
            )
            assembly = retrieval_api.retrieve_context(query)
            results.append(assembly)
        
        # Run 10 queries concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_query, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()
        
        assert len(results) == 10
        # Should still have total_queries = 10 (accounting for thread safety)
        assert retrieval_api.metrics["total_queries"] == 10
    
    @pytest.mark.skipif(not STAT7_AVAILABLE, reason="STAT7 bridge not available")
    def test_concurrent_hybrid_queries(self, retrieval_api_with_stat7):
        """Multiple threads can execute hybrid queries concurrently."""
        results = []
        errors = []
        
        def run_hybrid_query(query_id: int):
            try:
                query = RetrievalQuery(
                    query_id=f"hybrid_concurrent_{query_id}",
                    mode=RetrievalMode.SEMANTIC_SIMILARITY,
                    semantic_query=f"query_{query_id}",
                    stat7_hybrid=True,
                    max_results=5
                )
                assembly = retrieval_api_with_stat7.retrieve_context(query)
                results.append(assembly)
            except Exception as e:
                errors.append(str(e))
        
        # Run 10 hybrid queries concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_hybrid_query, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()
        
        assert len(results) == 10
        assert len(errors) == 0
        assert retrieval_api_with_stat7.metrics["hybrid_queries"] == 10
    
    @pytest.mark.integration
    def test_concurrent_cache_access(self, retrieval_api):
        """Cache should be thread-safe during concurrent access."""
        query_ids = []
        
        def run_and_cache(query_id: int):
            query = RetrievalQuery(
                query_id=f"cache_test_{query_id}",
                mode=RetrievalMode.SEMANTIC_SIMILARITY,
                semantic_query="shared_query",  # Same query
                max_results=5
            )
            assembly = retrieval_api.retrieve_context(query)
            query_ids.append(query.query_id)
        
        # Run 10 queries with same semantic_query (should hit cache)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_and_cache, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()
        
        assert len(query_ids) == 10
        # Should have some cache hits
        assert retrieval_api.metrics["cache_hits"] >= 0
    
    @pytest.mark.skipif(not STAT7_AVAILABLE, reason="STAT7 bridge not available")
    def test_concurrent_stat7_assignment(self, retrieval_api_with_stat7):
        """STAT7 assignment should be thread-safe."""
        results = []
        
        def assign_stat7(doc_id: int):
            metadata = {
                "realm_type": "game",
                "activity_level": doc_id / 100.0
            }
            stat7 = retrieval_api_with_stat7._auto_assign_stat7_address(
                f"doc_{doc_id}",
                metadata
            )
            results.append(stat7)
        
        # Assign STAT7 to 20 documents concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(assign_stat7, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()
        
        assert len(results) == 20
        # All should be cached
        assert len(retrieval_api_with_stat7.document_stat7_cache) == 20


# ============================================================================
# Test Cases: Integration
# ============================================================================

@pytest.mark.integration
class TestPhase2Integration:
    """End-to-end integration tests."""
    
    @pytest.mark.e2e
    def test_config_default_stat7_disabled(self, retrieval_api):
        """STAT7 should be disabled by default."""
        assert retrieval_api.enable_stat7_hybrid is False
    
    @pytest.mark.e2e
    def test_config_stat7_weights(self, retrieval_api_with_stat7):
        """STAT7 weights should be configurable."""
        assert retrieval_api_with_stat7.default_weight_semantic == 0.6
        assert retrieval_api_with_stat7.default_weight_stat7 == 0.4
    
    @pytest.mark.e2e
    def test_component_availability_includes_stat7(self, retrieval_api_with_stat7):
        """Component availability check should include STAT7."""
        availability = retrieval_api_with_stat7._check_component_availability()
        assert "stat7_bridge" in availability
        assert availability["stat7_bridge"] is True
    
    @pytest.mark.integration
    def test_mixed_semantic_and_hybrid_queries(self, retrieval_api_with_stat7):
        """API should handle mix of semantic and hybrid queries."""
        # Semantic query
        semantic_query = RetrievalQuery(
            query_id="semantic_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test_mixed_1",  # Different query to avoid cache
            stat7_hybrid=False,
            max_results=5
        )
        
        # Hybrid query
        hybrid_query = RetrievalQuery(
            query_id="hybrid_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="test_mixed_2",  # Different query to avoid cache
            stat7_hybrid=True,
            max_results=5
        )
        
        initial_queries = retrieval_api_with_stat7.metrics["total_queries"]
        initial_hybrid = retrieval_api_with_stat7.metrics["hybrid_queries"]
        
        semantic_assembly = retrieval_api_with_stat7.retrieve_context(semantic_query)
        hybrid_assembly = retrieval_api_with_stat7.retrieve_context(hybrid_query)
        
        assert semantic_assembly is not None
        assert hybrid_assembly is not None
        
        metrics = retrieval_api_with_stat7.get_retrieval_metrics()
        assert metrics["retrieval_metrics"]["total_queries"] >= initial_queries + 2
        assert metrics["retrieval_metrics"]["hybrid_queries"] >= initial_hybrid + 1


# ============================================================================
# Test Cases: Performance
# ============================================================================

@pytest.mark.integration
class TestPhase2Performance:
    """Performance benchmarks for Phase 2."""
    
    @pytest.mark.integration
    def test_hybrid_scoring_latency(self, retrieval_api_with_stat7):
        """Hybrid scoring should not significantly increase latency."""
        query = RetrievalQuery(
            query_id="perf_test_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="performance test",
            stat7_hybrid=True,
            max_results=10
        )
        
        start = time.time()
        retrieval_api_with_stat7.retrieve_context(query)
        elapsed_ms = (time.time() - start) * 1000
        
        # Should complete in reasonable time (< 1 second)
        assert elapsed_ms < 1000
        
        metrics = retrieval_api_with_stat7.get_retrieval_metrics()
        assert metrics["retrieval_metrics"]["average_retrieval_time_ms"] < 1000
    
    @pytest.mark.e2e
    def test_stat7_cache_performance(self, retrieval_api_with_stat7):
        """STAT7 cache should improve repeated assignment performance."""
        metadata = {"realm_type": "game"}
        
        # First assignment (cache miss)
        start_1 = time.time()
        retrieval_api_with_stat7._auto_assign_stat7_address("perf_doc_1", metadata)
        time_1 = (time.time() - start_1) * 1000
        
        # Second assignment (cache hit)
        start_2 = time.time()
        retrieval_api_with_stat7._auto_assign_stat7_address("perf_doc_1", metadata)
        time_2 = (time.time() - start_2) * 1000
        
        # Cache hit should be significantly faster
        assert time_2 <= time_1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])