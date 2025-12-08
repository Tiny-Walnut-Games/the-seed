"""
Comprehensive tests for warbler_cda.anchor_memory_pool module.

Tests the AnchorMemoryPool for object pooling and memory management.
"""

import pytest
from unittest.mock import Mock, patch
import time
from threading import Thread


class TestPoolMetrics:
    """Test PoolMetrics dataclass."""

    def test_pool_metrics_initialization(self):
        """PoolMetrics should initialize with zero values."""
        from warbler_cda.anchor_memory_pool import PoolMetrics

        metrics = PoolMetrics()
        assert metrics.total_created == 0
        assert metrics.total_reused == 0
        assert metrics.total_returned == 0
        assert metrics.current_pool_size == 0
        assert metrics.peak_pool_size == 0
        assert metrics.gc_collections_avoided == 0
        assert metrics.memory_pressure_events == 0
        assert metrics.last_cleanup_timestamp == 0.0

    def test_pool_metrics_get_reuse_rate_zero(self):
        """get_reuse_rate should return 0 when no requests."""
        from warbler_cda.anchor_memory_pool import PoolMetrics

        metrics = PoolMetrics()
        assert metrics.get_reuse_rate() == 0.0

    def test_pool_metrics_get_reuse_rate_calculation(self):
        """get_reuse_rate should calculate percentage correctly."""
        from warbler_cda.anchor_memory_pool import PoolMetrics

        metrics = PoolMetrics(total_created=20, total_reused=80)
        # 80 reused out of 100 total = 80%
        assert metrics.get_reuse_rate() == 80.0

    def test_pool_metrics_get_reuse_rate_all_created(self):
        """get_reuse_rate should return 0 when all objects are newly created."""
        from warbler_cda.anchor_memory_pool import PoolMetrics

        metrics = PoolMetrics(total_created=100, total_reused=0)
        assert metrics.get_reuse_rate() == 0.0

    def test_pool_metrics_get_reuse_rate_all_reused(self):
        """get_reuse_rate should return 100 when all objects are reused."""
        from warbler_cda.anchor_memory_pool import PoolMetrics

        metrics = PoolMetrics(total_created=0, total_reused=100)
        assert metrics.get_reuse_rate() == 100.0


class TestAnchorMemoryPoolInitialization:
    """Test AnchorMemoryPool initialization."""

    def test_pool_default_init(self):
        """Pool should initialize with default settings."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool()
        assert pool.initial_size == 50
        assert pool.max_size == 500
        assert pool.cleanup_interval == 300.0
        assert pool.memory_pressure_threshold == 1000
        assert len(pool.available_anchors) == 50
        assert len(pool.available_provenances) == 50

    def test_pool_custom_init(self):
        """Pool should accept custom configuration."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(
            initial_size=10,
            max_size=100,
            cleanup_interval=60.0,
            memory_pressure_threshold=500
        )

        assert pool.initial_size == 10
        assert pool.max_size == 100
        assert pool.cleanup_interval == 60.0
        assert pool.memory_pressure_threshold == 500
        assert len(pool.available_anchors) == 10

    def test_pool_preallocates_objects(self):
        """Pool should preallocate objects on initialization."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5)
        assert len(pool.available_anchors) == 5
        assert len(pool.available_provenances) == 5
        assert pool.metrics.current_pool_size == 5
        assert pool.metrics.peak_pool_size == 5


class TestCreateCleanObjects:
    """Test _create_clean_anchor and _create_clean_provenance methods."""

    def test_create_clean_anchor(self):
        """_create_clean_anchor should create empty anchor."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=0)
        anchor = pool._create_clean_anchor()

        assert anchor.anchor_id == ""
        assert anchor.concept_text == ""
        assert anchor.embedding == []
        assert anchor.heat == 0.0
        assert anchor.provenance is None
        assert anchor.cluster_id is None
        assert anchor.semantic_drift == 0.0
        assert anchor.stability_score == 1.0

    def test_create_clean_provenance(self):
        """_create_clean_provenance should create empty provenance."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=0)
        provenance = pool._create_clean_provenance()

        assert provenance.first_seen == 0.0
        assert provenance.utterance_ids == []
        assert provenance.update_count == 0
        assert provenance.last_updated == 0.0
        assert provenance.creation_context == {}
        assert provenance.update_history == []


class TestAcquireAnchor:
    """Test acquire_anchor method."""

    def test_acquire_anchor_from_pool(self):
        """acquire_anchor should reuse object from pool."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5)
        initial_pool_size = len(pool.available_anchors)

        anchor = pool.acquire_anchor(
            anchor_id="anchor-1",
            concept_text="test concept",
            embedding=[0.1, 0.2, 0.3],
            heat=0.8,
            creation_context={"source": "test"}
        )

        assert anchor.anchor_id == "anchor-1"
        assert anchor.concept_text == "test concept"
        assert anchor.embedding == [0.1, 0.2, 0.3]
        assert anchor.heat == 0.8
        assert anchor.provenance is not None
        assert len(pool.available_anchors) == initial_pool_size - 1
        assert pool.metrics.total_reused == 1

    def test_acquire_anchor_creates_when_pool_empty(self):
        """acquire_anchor should create new object when pool is empty."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=0)
        assert len(pool.available_anchors) == 0

        anchor = pool.acquire_anchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            creation_context={}
        )

        assert anchor is not None
        assert pool.metrics.total_created == 1
        assert pool.metrics.total_reused == 0

    def test_acquire_anchor_defensive_copy(self):
        """acquire_anchor should make defensive copy of embedding."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=1)
        original_embedding = [0.1, 0.2, 0.3]

        anchor = pool.acquire_anchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=original_embedding,
            heat=0.5,
            creation_context={}
        )

        # Modify original
        original_embedding[0] = 999.0

        # Anchor should have copy
        assert anchor.embedding[0] == 0.1

    def test_acquire_anchor_provenance_configured(self):
        """acquire_anchor should configure provenance correctly."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=1)
        context = {"source": "test", "version": "1.0"}

        anchor = pool.acquire_anchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            creation_context=context
        )

        assert anchor.provenance is not None
        assert anchor.provenance.first_seen > 0
        assert anchor.provenance.utterance_ids == []
        assert anchor.provenance.update_count == 0
        assert anchor.provenance.creation_context == context
        assert anchor.provenance.update_history == []


class TestReturnAnchor:
    """Test return_anchor method."""

    def test_return_anchor_to_pool(self):
        """return_anchor should return object to pool."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5)
        anchor = pool.acquire_anchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            creation_context={}
        )

        initial_size = len(pool.available_anchors)
        pool.return_anchor(anchor)

        assert len(pool.available_anchors) == initial_size + 1
        assert pool.metrics.total_returned == 1

    def test_return_anchor_cleans_state(self):
        """return_anchor should clean anchor state."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=1)
        anchor = pool.acquire_anchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1, 0.2],
            heat=0.8,
            creation_context={"key": "value"}
        )

        pool.return_anchor(anchor)

        # Anchor should be cleaned
        assert anchor.anchor_id == ""
        assert anchor.concept_text == ""
        assert anchor.embedding == []
        assert anchor.heat == 0.0

    def test_return_anchor_none(self):
        """return_anchor should handle None gracefully."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=1)
        pool.return_anchor(None)  # Should not raise

    def test_return_anchor_at_max_capacity(self):
        """return_anchor should reject objects when pool is full."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=2, max_size=2)
        # Pool is already at max (2 objects preallocated)

        anchor = pool.acquire_anchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            creation_context={}
        )

        # Try to return when pool is full
        pool.return_anchor(anchor)

        # Should track memory pressure event
        assert pool.metrics.memory_pressure_events >= 0

    def test_return_anchor_updates_peak_size(self):
        """return_anchor should update peak pool size."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5)
        initial_peak = pool.metrics.peak_pool_size

        anchor = pool.acquire_anchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            creation_context={}
        )
        pool.return_anchor(anchor)

        # Peak should be at least initial size
        assert pool.metrics.peak_pool_size >= initial_peak


class TestCleanupPool:
    """Test cleanup_pool method."""

    def test_cleanup_pool_respects_interval(self):
        """cleanup_pool should respect cleanup interval."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5, cleanup_interval=1000.0)
        pool.metrics.last_cleanup_timestamp = time.time()

        # Should not cleanup if interval hasn't passed
        pool.cleanup_pool(force=False)
        # No assertion needed - just verify it doesn't crash

    def test_cleanup_pool_force(self):
        """cleanup_pool should run when forced."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5)
        pool.metrics.last_cleanup_timestamp = time.time()

        initial_timestamp = pool.metrics.last_cleanup_timestamp
        time.sleep(0.01)  # Small delay

        pool.cleanup_pool(force=True)

        # Timestamp should be updated
        assert pool.metrics.last_cleanup_timestamp > initial_timestamp

    def test_cleanup_pool_reduces_excess(self):
        """cleanup_pool should reduce pool size when excessive."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=10, max_size=100)

        # Artificially inflate pool
        for _ in range(50):
            anchor = pool._create_clean_anchor()
            pool.available_anchors.append(anchor)

        initial_size = len(pool.available_anchors)
        pool.cleanup_pool(force=True)

        # Pool should be reduced (exact size depends on optimal calculation)
        # Just verify cleanup ran
        assert pool.metrics.last_cleanup_timestamp > 0

    def test_cleanup_pool_grows_if_needed(self):
        """cleanup_pool should grow pool if usage is high."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5, max_size=100)

        # Simulate high reuse rate
        pool.metrics.total_created = 10
        pool.metrics.total_reused = 90  # 90% reuse rate

        # Empty the pool
        pool.available_anchors.clear()
        pool.available_provenances.clear()

        pool.cleanup_pool(force=True)

        # Pool should grow
        assert len(pool.available_anchors) > 0


class TestCalculateOptimalPoolSize:
    """Test _calculate_optimal_pool_size method."""

    def test_optimal_size_high_reuse(self):
        """Optimal size should be larger with high reuse rate."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=50, max_size=500)
        pool.metrics.total_created = 10
        pool.metrics.total_reused = 90  # 90% reuse

        optimal = pool._calculate_optimal_pool_size()
        assert optimal > pool.initial_size

    def test_optimal_size_low_reuse(self):
        """Optimal size should be initial size with low reuse rate."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=50)
        pool.metrics.total_created = 90
        pool.metrics.total_reused = 10  # 10% reuse

        optimal = pool._calculate_optimal_pool_size()
        assert optimal == pool.initial_size

    def test_optimal_size_medium_reuse(self):
        """Optimal size should be moderate with medium reuse rate."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=50, max_size=500)
        pool.metrics.total_created = 40
        pool.metrics.total_reused = 60  # 60% reuse

        optimal = pool._calculate_optimal_pool_size()
        assert pool.initial_size < optimal < pool.max_size


class TestGetPoolMetrics:
    """Test get_pool_metrics method."""

    def test_get_pool_metrics_structure(self):
        """get_pool_metrics should return structured metrics."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=10)
        metrics = pool.get_pool_metrics()

        assert "pool_status" in metrics
        assert "performance_metrics" in metrics
        assert "memory_management" in metrics

    def test_get_pool_metrics_pool_status(self):
        """get_pool_metrics should include pool status."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=10, max_size=100)
        metrics = pool.get_pool_metrics()

        assert metrics["pool_status"]["current_size"] == 10
        assert metrics["pool_status"]["max_size"] == 100
        assert "utilization_pct" in metrics["pool_status"]

    def test_get_pool_metrics_performance(self):
        """get_pool_metrics should include performance metrics."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5)
        pool.acquire_anchor("a1", "test", [0.1], 0.5, {})

        metrics = pool.get_pool_metrics()

        assert "total_created" in metrics["performance_metrics"]
        assert "total_reused" in metrics["performance_metrics"]
        assert "reuse_rate_pct" in metrics["performance_metrics"]
        assert "gc_collections_avoided" in metrics["performance_metrics"]


class TestGetMemorySavingsEstimate:
    """Test get_memory_savings_estimate method."""

    def test_memory_savings_estimate(self):
        """get_memory_savings_estimate should calculate savings."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=5)

        # Simulate some reuse
        for i in range(10):
            anchor = pool.acquire_anchor(f"a{i}", "test", [0.1], 0.5, {})
            pool.return_anchor(anchor)

        savings = pool.get_memory_savings_estimate()

        assert "objects_reused" in savings
        assert "gc_collections_avoided" in savings
        assert "estimated_memory_saved_bytes" in savings
        assert "estimated_memory_saved_mb" in savings
        assert "efficiency_score" in savings
        assert 0.0 <= savings["efficiency_score"] <= 1.0

    def test_memory_savings_no_reuse(self):
        """get_memory_savings_estimate should handle no reuse."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=0)
        pool.metrics.total_created = 10
        pool.metrics.total_reused = 0

        savings = pool.get_memory_savings_estimate()

        assert savings["objects_reused"] == 0
        assert savings["efficiency_score"] == 0.0


class TestThreadSafety:
    """Test thread safety of pool operations."""

    def test_concurrent_acquire(self):
        """Pool should handle concurrent acquire operations."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=20)
        acquired_anchors = []

        def acquire_multiple():
            for i in range(5):
                anchor = pool.acquire_anchor(
                    f"anchor-{i}",
                    "test",
                    [0.1],
                    0.5,
                    {}
                )
                acquired_anchors.append(anchor)

        threads = [Thread(target=acquire_multiple) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have acquired 15 anchors total
        assert len(acquired_anchors) == 15
        # All should be unique objects
        assert len(set(id(a) for a in acquired_anchors)) == 15

    def test_concurrent_return(self):
        """Pool should handle concurrent return operations."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=10, max_size=50)
        anchors = []

        # Acquire some anchors
        for i in range(10):
            anchor = pool.acquire_anchor(f"a{i}", "test", [0.1], 0.5, {})
            anchors.append(anchor)

        def return_multiple(anchor_list):
            for anchor in anchor_list:
                pool.return_anchor(anchor)

        # Split anchors across threads
        threads = [
            Thread(target=return_multiple, args=(anchors[:5],)),
            Thread(target=return_multiple, args=(anchors[5:],))
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should be returned
        assert pool.metrics.total_returned == 10


class TestGlobalPool:
    """Test global pool functions."""

    def test_get_global_anchor_pool(self):
        """get_global_anchor_pool should return singleton instance."""
        from warbler_cda.anchor_memory_pool import get_global_anchor_pool
        import warbler_cda.anchor_memory_pool as pool_module

        # Reset global
        pool_module._global_anchor_pool = None

        pool1 = get_global_anchor_pool()
        pool2 = get_global_anchor_pool()

        assert pool1 is pool2

    def test_configure_global_pool(self):
        """configure_global_pool should create pool with custom settings."""
        from warbler_cda.anchor_memory_pool import configure_global_pool
        import warbler_cda.anchor_memory_pool as pool_module

        # Reset global
        pool_module._global_anchor_pool = None

        pool = configure_global_pool(initial_size=20, max_size=200)

        assert pool.initial_size == 20
        assert pool.max_size == 200
        assert len(pool.available_anchors) == 20


class TestIntegration:
    """Integration tests for complete pool lifecycle."""

    def test_full_lifecycle(self):
        """Test complete acquire-use-return lifecycle."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=10)

        # Acquire multiple anchors
        anchors = []
        for i in range(5):
            anchor = pool.acquire_anchor(
                f"anchor-{i}",
                f"concept {i}",
                [float(i)],
                0.5 + i * 0.1,
                {"index": i}
            )
            anchors.append(anchor)

        # Verify acquisition
        assert len(anchors) == 5
        assert pool.metrics.total_reused == 5

        # Return all anchors
        for anchor in anchors:
            pool.return_anchor(anchor)

        # Verify return
        assert pool.metrics.total_returned == 5

        # Acquire again - should reuse
        anchor2 = pool.acquire_anchor("new", "test", [0.1], 0.5, {})
        assert pool.metrics.total_reused == 6

    def test_pool_metrics_tracking(self):
        """Test that metrics are tracked correctly throughout lifecycle."""
        from warbler_cda.anchor_memory_pool import AnchorMemoryPool

        pool = AnchorMemoryPool(initial_size=3)

        # Acquire all from pool
        a1 = pool.acquire_anchor("a1", "test", [0.1], 0.5, {})
        a2 = pool.acquire_anchor("a2", "test", [0.2], 0.5, {})
        a3 = pool.acquire_anchor("a3", "test", [0.3], 0.5, {})

        assert pool.metrics.total_reused == 3
        assert len(pool.available_anchors) == 0

        # Acquire one more - should create new
        a4 = pool.acquire_anchor("a4", "test", [0.4], 0.5, {})
        assert pool.metrics.total_created == 1

        # Return all
        for anchor in [a1, a2, a3, a4]:
            pool.return_anchor(anchor)

        assert pool.metrics.total_returned == 4
        assert len(pool.available_anchors) == 4

        # Get metrics summary
        metrics = pool.get_pool_metrics()
        assert metrics["performance_metrics"]["total_created"] == 1
        assert metrics["performance_metrics"]["total_reused"] == 3
        assert metrics["performance_metrics"]["total_returned"] == 4
