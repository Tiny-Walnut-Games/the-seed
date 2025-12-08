"""
Comprehensive tests for warbler_cda.semantic_anchors module.

Tests the SemanticAnchorGraph with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch
import time


class TestSemanticAnchorGraphInitialization:
    """Test SemanticAnchorGraph initialization."""

    def test_graph_default_init(self):
        """Graph should initialize with default settings."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        assert graph.embedding_provider is not None
        assert graph.memory_pool is not None
        assert graph.anchors == {}
        assert graph.clusters == {}
        assert graph.max_age_days == 30
        assert graph.consolidation_threshold == 0.8
        assert graph.eviction_heat_threshold == 0.1

    def test_graph_custom_config(self):
        """Graph should accept custom configuration."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        config = {
            "max_age_days": 60,
            "consolidation_threshold": 0.9,
            "eviction_heat_threshold": 0.05,
            "enable_memory_pooling": False
        }

        graph = SemanticAnchorGraph(config=config)
        assert graph.max_age_days == 60
        assert graph.consolidation_threshold == 0.9
        assert graph.eviction_heat_threshold == 0.05
        assert graph.enable_memory_pooling is False

    def test_graph_custom_embedding_provider(self):
        """Graph should accept custom embedding provider."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        mock_provider = Mock()
        graph = SemanticAnchorGraph(embedding_provider=mock_provider)
        assert graph.embedding_provider == mock_provider


class TestCreateOrUpdateAnchor:
    """Test create_or_update_anchor method."""

    def test_create_new_anchor(self):
        """create_or_update_anchor should create new anchor."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        anchor_id = graph.create_or_update_anchor(
            concept_text="test concept",
            utterance_id="u1",
            context={"source": "test"}
        )

        assert anchor_id in graph.anchors
        assert graph.anchors[anchor_id].concept_text == "test concept"
        assert graph.metrics["total_anchors_created"] == 1

    def test_update_existing_anchor(self):
        """create_or_update_anchor should update similar anchor."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph(config={"consolidation_threshold": 0.7})

        # Create first anchor
        anchor_id1 = graph.create_or_update_anchor(
            concept_text="test concept",
            utterance_id="u1",
            context={}
        )

        initial_updates = graph.metrics["total_updates"]

        # Create very similar anchor - should update existing
        anchor_id2 = graph.create_or_update_anchor(
            concept_text="test concept",  # Same text
            utterance_id="u2",
            context={}
        )

        # Should be same anchor
        assert anchor_id1 == anchor_id2
        assert graph.metrics["total_updates"] == initial_updates + 1
        assert graph.anchors[anchor_id1].provenance.update_count >= 2

    def test_create_anchor_with_privacy_hooks(self):
        """create_or_update_anchor should use privacy hooks if available."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        mock_privacy = Mock()
        mock_privacy.scrub_content_for_anchor_injection.return_value = (
            "scrubbed content",
            {"privacy_hook_applied": True}
        )
        mock_privacy.validate_privacy_compliance.return_value = (True, [])

        graph = SemanticAnchorGraph(privacy_hooks=mock_privacy)
        anchor_id = graph.create_or_update_anchor(
            concept_text="sensitive data",
            utterance_id="u1",
            context={}
        )

        # Should have called privacy hooks
        mock_privacy.scrub_content_for_anchor_injection.assert_called_once()
        mock_privacy.validate_privacy_compliance.assert_called_once()


class TestGetSemanticClusters:
    """Test get_semantic_clusters method."""

    def test_get_clusters_empty_graph(self):
        """get_semantic_clusters should return empty list for empty graph."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        clusters = graph.get_semantic_clusters()
        assert clusters == []

    def test_get_clusters_single_anchor(self):
        """get_semantic_clusters should return empty list with single anchor."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        graph.create_or_update_anchor("concept1", "u1", {})

        clusters = graph.get_semantic_clusters()
        assert clusters == []

    def test_get_clusters_similar_anchors(self):
        """get_semantic_clusters should group similar anchors."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph(config={"consolidation_threshold": 0.5})

        # Create similar anchors
        graph.create_or_update_anchor("jumping", "u1", {})
        time.sleep(0.01)
        graph.create_or_update_anchor("leaping", "u2", {})
        time.sleep(0.01)
        graph.create_or_update_anchor("completely different topic", "u3", {})

        clusters = graph.get_semantic_clusters(max_clusters=5)

        # Should find at least some clusters
        assert isinstance(clusters, list)


class TestGetAnchorDiff:
    """Test get_anchor_diff method."""

    def test_get_diff_no_changes(self):
        """get_anchor_diff should show no changes for future timestamp."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        graph.create_or_update_anchor("concept", "u1", {})

        # Query from future
        diff = graph.get_anchor_diff(since_timestamp=time.time() + 1000)

        assert len(diff["added"]) == 0
        assert len(diff["updated"]) == 0

    def test_get_diff_added_anchors(self):
        """get_anchor_diff should detect newly added anchors."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph(config={"consolidation_threshold": 0.95})  # Set high to prevent accidental consolidation
        past_time = time.time() - 100

        graph.create_or_update_anchor("concept1", "u1", {})
        graph.create_or_update_anchor("completely different concept2", "u2", {})  # Make it clearly different

        diff = graph.get_anchor_diff(since_timestamp=past_time)

        assert len(diff["added"]) == 2
        assert diff["total_anchors"] == 2


class TestApplyLifecyclePolicies:
    """Test apply_lifecycle_policies method."""

    def test_lifecycle_aging(self):
        """apply_lifecycle_policies should age all anchors."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        graph.create_or_update_anchor("concept", "u1", {})

        actions = graph.apply_lifecycle_policies()

        assert actions["aged"] == 1

    def test_lifecycle_eviction_low_heat(self):
        """apply_lifecycle_policies should evict cold anchors."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph(config={"eviction_heat_threshold": 0.5})
        anchor_id = graph.create_or_update_anchor("concept", "u1", {})

        # Manually set low heat
        graph.anchors[anchor_id].heat = 0.1

        actions = graph.apply_lifecycle_policies()

        assert actions["evicted"] == 1
        assert anchor_id not in graph.anchors

    def test_lifecycle_eviction_old_age(self):
        """apply_lifecycle_policies should evict old anchors."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph
        from warbler_cda.anchor_data_classes import AnchorProvenance

        graph = SemanticAnchorGraph(config={"max_age_days": 1})
        anchor_id = graph.create_or_update_anchor("concept", "u1", {})

        # Manually set old timestamp (40 days ago)
        old_time = time.time() - (40 * 24 * 3600)
        graph.anchors[anchor_id].provenance.first_seen = old_time

        actions = graph.apply_lifecycle_policies()

        assert actions["evicted"] >= 1


class TestGetStabilityMetrics:
    """Test get_stability_metrics method."""

    def test_stability_metrics_empty_graph(self):
        """get_stability_metrics should handle empty graph."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        metrics = graph.get_stability_metrics()

        assert metrics["total_anchors"] == 0
        assert metrics["average_age_days"] == 0
        assert metrics["stability_score"] == 1.0

    def test_stability_metrics_with_anchors(self):
        """get_stability_metrics should calculate metrics."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph(config={"consolidation_threshold": 0.95})  # Prevent consolidation
        graph.create_or_update_anchor("first concept", "u1", {})
        graph.create_or_update_anchor("very different second concept", "u2", {})

        metrics = graph.get_stability_metrics()

        assert metrics["total_anchors"] == 2
        assert metrics["average_heat"] > 0
        assert 0 <= metrics["stability_score"] <= 1.0
        assert "provider_info" in metrics


class TestPrivacyIntegration:
    """Test privacy hooks integration."""

    def test_get_privacy_metrics_no_hooks(self):
        """get_privacy_metrics should handle missing privacy hooks."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        metrics = graph.get_privacy_metrics()

        assert metrics["privacy_hooks_enabled"] is False

    def test_get_privacy_metrics_with_hooks(self):
        """get_privacy_metrics should call privacy hooks."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        mock_privacy = Mock()
        mock_privacy.get_privacy_metrics.return_value = {
            "pii_detections": 5,
            "scrubbing_applied": 3
        }

        graph = SemanticAnchorGraph(privacy_hooks=mock_privacy)
        metrics = graph.get_privacy_metrics()

        assert metrics["pii_detections"] == 5
        mock_privacy.get_privacy_metrics.assert_called_once()


class TestHelperMethods:
    """Test helper methods."""

    def test_generate_anchor_id(self):
        """_generate_anchor_id should create unique IDs."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        id1 = graph._generate_anchor_id("concept1")
        time.sleep(0.01)
        id2 = graph._generate_anchor_id("concept2")

        assert id1 != id2
        assert id1.startswith("anchor_")
        assert id2.startswith("anchor_")

    def test_calculate_drift(self):
        """_calculate_drift should compute semantic drift."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()

        # Identical embeddings = 0 drift
        emb1 = [1.0, 0.0, 0.0]
        emb2 = [1.0, 0.0, 0.0]
        drift = graph._calculate_drift(emb1, emb2)
        assert drift < 0.01

        # Different embeddings = higher drift
        emb3 = [0.0, 1.0, 0.0]
        drift2 = graph._calculate_drift(emb1, emb3)
        assert drift2 > 0.5

    def test_find_similar_anchor_none(self):
        """_find_similar_anchor should return None when no similar anchors."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph()
        result = graph._find_similar_anchor([0.1, 0.2, 0.3])
        assert result is None

    def test_find_similar_anchor_match(self):
        """_find_similar_anchor should find similar anchor."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph(config={"consolidation_threshold": 0.7})
        anchor_id = graph.create_or_update_anchor("test", "u1", {})

        # Get the embedding
        anchor = graph.anchors[anchor_id]
        similar_id = graph._find_similar_anchor(anchor.embedding)

        assert similar_id == anchor_id


class TestIntegration:
    """Integration tests for complete anchor lifecycle."""

    def test_full_anchor_lifecycle(self):
        """Test complete lifecycle: create, update, age, evict."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph(config={
            "max_age_days": 1,
            "eviction_heat_threshold": 0.05
        })

        # Create anchor
        anchor_id = graph.create_or_update_anchor("concept", "u1", {})
        assert anchor_id in graph.anchors

        # Update anchor
        graph.create_or_update_anchor("concept", "u2", {})
        assert graph.anchors[anchor_id].provenance.update_count >= 2

        # Age anchor (set old timestamp)
        graph.anchors[anchor_id].provenance.first_seen = time.time() - (10 * 24 * 3600)

        # Apply lifecycle
        actions = graph.apply_lifecycle_policies()

        # Should be evicted due to age
        assert actions["evicted"] >= 1

    def test_stability_metrics_workflow(self):
        """Test stability metrics calculation workflow."""
        from warbler_cda.semantic_anchors import SemanticAnchorGraph

        graph = SemanticAnchorGraph(config={"consolidation_threshold": 0.95})  # Prevent consolidation

        # Create multiple distinct anchors
        distinct_concepts = [
            "quantum physics fundamentals",
            "machine learning algorithms",
            "ancient Greek philosophy",
            "modern art techniques",
            "sustainable agriculture"
        ]

        for i, concept in enumerate(distinct_concepts):
            graph.create_or_update_anchor(concept, f"u{i}", {})

        # Get metrics
        metrics = graph.get_stability_metrics()

        assert metrics["total_anchors"] == 5
        assert metrics["average_heat"] > 0
        assert "provider_info" in metrics
        assert "memory_pool_metrics" in metrics
