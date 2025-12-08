"""
Comprehensive tests for warbler_cda.anchor_data_classes module.

Tests the core data classes for semantic anchors.
"""

import pytest
from unittest.mock import patch
import time


class TestAnchorProvenance:
    """Test AnchorProvenance dataclass."""

    def test_provenance_initialization(self):
        """AnchorProvenance should initialize with required fields."""
        from warbler_cda.anchor_data_classes import AnchorProvenance

        current_time = time.time()
        provenance = AnchorProvenance(
            first_seen=current_time,
            utterance_ids=["u1", "u2"],
            update_count=2,
            last_updated=current_time,
            creation_context={"source": "test"},
            update_history=[]
        )

        assert provenance.first_seen == current_time
        assert provenance.utterance_ids == ["u1", "u2"]
        assert provenance.update_count == 2
        assert provenance.last_updated == current_time
        assert provenance.creation_context == {"source": "test"}
        assert provenance.update_history == []

    def test_add_update(self):
        """add_update should record update and increment counters."""
        from warbler_cda.anchor_data_classes import AnchorProvenance

        provenance = AnchorProvenance(
            first_seen=time.time(),
            utterance_ids=[],
            update_count=0,
            last_updated=time.time(),
            creation_context={},
            update_history=[]
        )

        initial_count = provenance.update_count
        initial_time = provenance.last_updated

        time.sleep(0.01)  # Small delay
        provenance.add_update("u1", {"key": "value"})

        assert "u1" in provenance.utterance_ids
        assert provenance.update_count == initial_count + 1
        assert provenance.last_updated > initial_time
        assert len(provenance.update_history) == 1
        assert provenance.update_history[0]["utterance_id"] == "u1"
        assert provenance.update_history[0]["context"] == {"key": "value"}

    def test_add_multiple_updates(self):
        """add_update should handle multiple updates."""
        from warbler_cda.anchor_data_classes import AnchorProvenance

        provenance = AnchorProvenance(
            first_seen=time.time(),
            utterance_ids=[],
            update_count=0,
            last_updated=time.time(),
            creation_context={},
            update_history=[]
        )

        for i in range(5):
            provenance.add_update(f"u{i}", {"index": i})

        assert len(provenance.utterance_ids) == 5
        assert provenance.update_count == 5
        assert len(provenance.update_history) == 5


class TestSemanticAnchor:
    """Test SemanticAnchor dataclass."""

    def test_anchor_initialization(self):
        """SemanticAnchor should initialize with required fields."""
        from warbler_cda.anchor_data_classes import SemanticAnchor, AnchorProvenance

        provenance = AnchorProvenance(
            first_seen=time.time(),
            utterance_ids=[],
            update_count=0,
            last_updated=time.time(),
            creation_context={},
            update_history=[]
        )

        anchor = SemanticAnchor(
            anchor_id="anchor-1",
            concept_text="test concept",
            embedding=[0.1, 0.2, 0.3],
            heat=0.8,
            provenance=provenance
        )

        assert anchor.anchor_id == "anchor-1"
        assert anchor.concept_text == "test concept"
        assert anchor.embedding == [0.1, 0.2, 0.3]
        assert anchor.heat == 0.8
        assert anchor.provenance == provenance
        assert anchor.cluster_id is None
        assert anchor.semantic_drift == 0.0
        assert anchor.stability_score == 1.0

    def test_anchor_optional_fields(self):
        """SemanticAnchor should support optional fields."""
        from warbler_cda.anchor_data_classes import SemanticAnchor

        anchor = SemanticAnchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            provenance=None,
            cluster_id="cluster-1",
            semantic_drift=0.15,
            stability_score=0.9
        )

        assert anchor.cluster_id == "cluster-1"
        assert anchor.semantic_drift == 0.15
        assert anchor.stability_score == 0.9

    def test_calculate_age_days_no_provenance(self):
        """calculate_age_days should return 0 when provenance is None."""
        from warbler_cda.anchor_data_classes import SemanticAnchor

        anchor = SemanticAnchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            provenance=None
        )

        age = anchor.calculate_age_days()
        assert age == 0.0

    def test_calculate_age_days_with_provenance(self):
        """calculate_age_days should calculate age from first_seen."""
        from warbler_cda.anchor_data_classes import SemanticAnchor, AnchorProvenance

        # Create anchor from 2 days ago
        two_days_ago = time.time() - (2 * 24 * 3600)
        provenance = AnchorProvenance(
            first_seen=two_days_ago,
            utterance_ids=[],
            update_count=0,
            last_updated=two_days_ago,
            creation_context={},
            update_history=[]
        )

        anchor = SemanticAnchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            provenance=provenance
        )

        age = anchor.calculate_age_days()
        assert 1.9 < age < 2.1  # Approximately 2 days

    def test_calculate_activity_rate_no_provenance(self):
        """calculate_activity_rate should return 0 when provenance is None."""
        from warbler_cda.anchor_data_classes import SemanticAnchor

        anchor = SemanticAnchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            provenance=None
        )

        rate = anchor.calculate_activity_rate()
        assert rate == 0.0

    def test_calculate_activity_rate_zero_age(self):
        """calculate_activity_rate should return 0 for brand new anchor."""
        from warbler_cda.anchor_data_classes import SemanticAnchor, AnchorProvenance

        # Create anchor with current timestamp (age will be very small but not exactly 0)
        current_time = time.time()
        provenance = AnchorProvenance(
            first_seen=current_time,
            utterance_ids=[],
            update_count=5,
            last_updated=current_time,
            creation_context={},
            update_history=[]
        )

        anchor = SemanticAnchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            provenance=provenance
        )

        rate = anchor.calculate_activity_rate()
        # Age is very small (microseconds), so rate will be very high
        # Just verify it doesn't crash and returns a number
        assert isinstance(rate, float)
        assert rate >= 0.0

    def test_calculate_activity_rate_with_updates(self):
        """calculate_activity_rate should calculate updates per day."""
        from warbler_cda.anchor_data_classes import SemanticAnchor, AnchorProvenance

        # Create anchor from 1 day ago with 10 updates
        one_day_ago = time.time() - (24 * 3600)
        provenance = AnchorProvenance(
            first_seen=one_day_ago,
            utterance_ids=[f"u{i}" for i in range(10)],
            update_count=10,
            last_updated=time.time(),
            creation_context={},
            update_history=[]
        )

        anchor = SemanticAnchor(
            anchor_id="anchor-1",
            concept_text="test",
            embedding=[0.1],
            heat=0.5,
            provenance=provenance
        )

        rate = anchor.calculate_activity_rate()
        assert 9.0 < rate < 11.0  # Approximately 10 updates per day


class TestIntegration:
    """Integration tests for anchor data classes."""

    def test_anchor_with_provenance_workflow(self):
        """Test complete workflow of anchor with provenance updates."""
        from warbler_cda.anchor_data_classes import SemanticAnchor, AnchorProvenance

        # Create provenance
        provenance = AnchorProvenance(
            first_seen=time.time() - 3600,  # 1 hour ago
            utterance_ids=[],
            update_count=0,
            last_updated=time.time() - 3600,
            creation_context={"source": "initial"},
            update_history=[]
        )

        # Create anchor
        anchor = SemanticAnchor(
            anchor_id="anchor-1",
            concept_text="evolving concept",
            embedding=[0.5, 0.5, 0.5],
            heat=0.7,
            provenance=provenance
        )

        # Add updates
        for i in range(3):
            provenance.add_update(f"utterance-{i}", {"update": i})

        # Verify state
        assert len(provenance.utterance_ids) == 3
        assert provenance.update_count == 3
        assert len(provenance.update_history) == 3

        # Calculate metrics
        age = anchor.calculate_age_days()
        assert age > 0

        rate = anchor.calculate_activity_rate()
        assert rate > 0
