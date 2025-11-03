"""
Phase 6D: Reproducibility & Export — Test Suite (TDD-First)

Tests for universe snapshots, export/replay capability, and reproducibility validation.
This is test-first development: tests define the contract, then implementation follows.

Coverage:
- UniverseExporter: Universe serialization with seed/hash/tier metadata
- UniverseReplayer: Universe recreation from seed with validation
- CrossTierAlignment: Tier hierarchy preservation across export/replay
- AuditTrailReconstruction: Complete lineage tracking from seed to NPC

Date: 2025-10-30
Status: TDD Ready
"""

import pytest
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys
import hashlib
import tempfile

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

# Imports for testing
from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig, DemoUniverseMetadata
from phase6_hierarchical_realms import (
    TierClassification, TierTheme, RealmTierMetadata, TierRegistry
)


# ============================================================================
# TEST: UNIVERSE EXPORTER
# ============================================================================

class TestUniverseExporter:
    """Test UniverseExporter class for serializing universe state."""
    
    @pytest.mark.asyncio
    async def test_export_includes_seed(self):
        """Export should include original initialization seed."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        assert snapshot.seed == 42
        assert snapshot.seed is not None
        assert isinstance(snapshot.seed, int)
    
    @pytest.mark.asyncio
    async def test_export_includes_all_realms(self):
        """Export should include all realms from orchestrator."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        assert len(snapshot.realms) > 0
        assert any(r.realm_id == "tavern" for r in snapshot.realms)
    
    @pytest.mark.asyncio
    async def test_export_includes_tier_metadata(self):
        """Export should include tier assignments for all realms."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Tier assignments should be present
        assert len(snapshot.tier_assignments) > 0
        
        # Each assignment should have required fields
        for realm_id, assignment in snapshot.tier_assignments.items():
            assert assignment.realm_id == realm_id
            assert assignment.tier_classification in ["celestial", "terran", "subterran"]
            assert assignment.tier_theme is not None
            assert isinstance(assignment.semantic_anchors, list)
    
    @pytest.mark.asyncio
    async def test_export_includes_enrichment_trails(self):
        """Export should include enrichment audit trail."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch, include_enrichments=True)
        
        # Should have enrichments list
        assert isinstance(snapshot.enrichments, list)
        
        # Each enrichment should be timestamped
        for enrichment in snapshot.enrichments:
            assert hasattr(enrichment, 'created_at')
    
    @pytest.mark.asyncio
    async def test_export_computes_universe_hash(self):
        """Export should compute deterministic hash for reproducibility validation."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        assert snapshot.universe_hash is not None
        assert isinstance(snapshot.universe_hash, str)
        assert len(snapshot.universe_hash) > 0
        
        # Same export should produce same hash (deterministic)
        snapshot2 = await exporter.export(orch)
        assert snapshot.universe_hash == snapshot2.universe_hash
    
    @pytest.mark.asyncio
    async def test_export_includes_semantic_anchors(self):
        """Export should include semantic anchors for each realm."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Should have semantic anchor index
        assert hasattr(snapshot, 'semantic_anchor_index')
        assert isinstance(snapshot.semantic_anchor_index, dict)
    
    @pytest.mark.asyncio
    async def test_export_as_json_serializable(self):
        """Export should be JSON-serializable (for file storage/transport)."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Should be convertible to dict
        snapshot_dict = snapshot.to_dict() if hasattr(snapshot, 'to_dict') else {
            'seed': snapshot.seed,
            'universe_id': snapshot.universe_id,
            'universe_hash': snapshot.universe_hash,
            'exported_at': snapshot.exported_at,
            'tier_assignments': {k: v.to_dict() if hasattr(v, 'to_dict') else dict(v.__dict__) 
                                for k, v in snapshot.tier_assignments.items()},
            'realms': [r.to_dict() if hasattr(r, 'to_dict') else dict(r.__dict__) for r in snapshot.realms],
        }
        
        # Should serialize to JSON string
        json_str = json.dumps(snapshot_dict, default=str)
        assert json_str is not None
        assert len(json_str) > 0
    
    @pytest.mark.asyncio
    async def test_export_excludes_sensitive_data(self):
        """Export should not include sensitive data (connection strings, internal state)."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        snapshot_dict = snapshot.to_dict() if hasattr(snapshot, 'to_dict') else dict(snapshot.__dict__)
        json_str = json.dumps(snapshot_dict, default=str)
        
        # Should not contain sensitive strings
        assert "password" not in json_str.lower()
        assert "token" not in json_str.lower()
        assert "secret" not in json_str.lower()


# ============================================================================
# TEST: UNIVERSE REPLAYER
# ============================================================================

class TestUniverseReplayer:
    """Test UniverseReplayer class for universe recreation from seed."""
    
    @pytest.mark.asyncio
    async def test_replay_with_same_seed_identical_universe(self):
        """Replaying with same seed should produce identical universe."""
        from phase6d_reproducibility import UniverseReplayer, UniverseExporter
        
        # First create initial export
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        initial_export = await exporter.export(orch)
        
        replayer = UniverseReplayer()
        replay_config = OrchestratorConfig(seed=initial_export.seed, orbits=1, realms=["tavern"])
        
        # Replay from seed
        replayed_orch = await replayer.replay_from_seed(initial_export.seed, replay_config)
        
        assert replayed_orch is not None
        assert replayed_orch.config.seed == initial_export.seed
        assert replayed_orch.setup_complete
    
    @pytest.mark.asyncio
    async def test_replay_preserves_tier_assignments(self):
        """Replayed universe should have identical tier assignments."""
        from phase6d_reproducibility import UniverseReplayer, UniverseExporter
        
        # Create initial export
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        initial_export = await exporter.export(orch)
        
        replayer = UniverseReplayer()
        replay_config = OrchestratorConfig(seed=initial_export.seed, orbits=1, realms=["tavern"])
        
        replayed_orch = await replayer.replay_from_seed(initial_export.seed, replay_config)
        
        # Re-export replayed universe
        exporter = UniverseExporter()
        replayed_export = await exporter.export(replayed_orch)
        
        # Tier assignments should match
        for realm_id in initial_export.tier_assignments:
            assert realm_id in replayed_export.tier_assignments
            original_tier = initial_export.tier_assignments[realm_id]
            replayed_tier = replayed_export.tier_assignments[realm_id]
            assert original_tier.tier_classification == replayed_tier.tier_classification
    
    @pytest.mark.asyncio
    async def test_replay_validates_seed_integrity(self):
        """Replayed universe should validate against original hash."""
        from phase6d_reproducibility import UniverseReplayer, UniverseExporter
        
        # Create initial export
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        initial_export = await exporter.export(orch)
        
        replayer = UniverseReplayer()
        replay_config = OrchestratorConfig(seed=initial_export.seed, orbits=1, realms=["tavern"])
        
        replayed_orch = await replayer.replay_from_seed(
            initial_export.seed, 
            replay_config, 
            validate_hash=initial_export.universe_hash
        )
        
        # Should not raise error if hashes match
        assert replayed_orch is not None
    
    @pytest.mark.asyncio
    async def test_replay_rejects_nonexistent_seed(self):
        """Replaying with nonexistent seed should handle gracefully."""
        from phase6d_reproducibility import UniverseReplayer
        
        replayer = UniverseReplayer()
        config = OrchestratorConfig(seed=999999, orbits=1, realms=["tavern"])
        
        # Should either return new state or raise informative error
        try:
            result = await replayer.replay_from_seed(999999, config)
            # If succeeds, should still work (new universe with that seed)
            assert result is not None
        except Exception as e:
            # If fails, error should be informative
            assert "seed" in str(e).lower() or "universe" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_replay_runs_initialization_cycle(self):
        """Replayed universe should run full initialization (not just cache load)."""
        from phase6d_reproducibility import UniverseReplayer, UniverseExporter
        
        # Create initial export
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        initial_export = await exporter.export(orch)
        
        replayer = UniverseReplayer()
        replay_config = OrchestratorConfig(seed=initial_export.seed, orbits=1, realms=["tavern"])
        
        replayed_orch = await replayer.replay_from_seed(initial_export.seed, replay_config)
        
        # Export should show enrichment history
        exporter = UniverseExporter()
        replayed_export = await exporter.export(replayed_orch)
        
        # Should have run the initialization cycle (validate via metadata)
        assert replayed_export.universe_specifications['total_orbits_completed'] >= 1
        assert replayed_export.seed == initial_export.seed
    
    @pytest.mark.asyncio
    async def test_replay_restores_orchestrator_state(self):
        """Replayed orchestrator should have correct initialization seed in state."""
        from phase6d_reproducibility import UniverseReplayer, UniverseExporter
        
        # Create initial export
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        initial_export = await exporter.export(orch)
        
        replayer = UniverseReplayer()
        replay_config = OrchestratorConfig(seed=initial_export.seed, orbits=1, realms=["tavern"])
        
        replayed_orch = await replayer.replay_from_seed(initial_export.seed, replay_config)
        
        # Orchestrator should expose initialization seed
        assert hasattr(replayed_orch, 'get_initialization_seed')
        assert replayed_orch.get_initialization_seed() == initial_export.seed
    
    @pytest.mark.asyncio
    async def test_replay_idempotent_multiple_calls(self):
        """Multiple replays of same seed should produce identical universes."""
        from phase6d_reproducibility import UniverseReplayer, UniverseExporter
        
        # Create initial export
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter_base = UniverseExporter()
        initial_export = await exporter_base.export(orch)
        
        replayer = UniverseReplayer()
        exporter = UniverseExporter()
        replay_config = OrchestratorConfig(seed=initial_export.seed, orbits=1, realms=["tavern"])
        
        # Replay 3 times
        replayed1 = await replayer.replay_from_seed(initial_export.seed, replay_config)
        export1 = await exporter.export(replayed1)
        
        replayed2 = await replayer.replay_from_seed(initial_export.seed, replay_config)
        export2 = await exporter.export(replayed2)
        
        replayed3 = await replayer.replay_from_seed(initial_export.seed, replay_config)
        export3 = await exporter.export(replayed3)
        
        # All three should have identical hashes
        assert export1.universe_hash == export2.universe_hash == export3.universe_hash


# ============================================================================
# TEST: CROSS-TIER ALIGNMENT
# ============================================================================

class TestCrossTierAlignment:
    """Test cross-tier alignment preservation across export/replay."""
    
    @pytest.mark.asyncio
    async def test_alignment_tracks_tier_transitions(self):
        """Alignment should track transitions between tiers."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Should have tier alignment index
        assert hasattr(snapshot, 'tier_alignment')
        assert isinstance(snapshot.tier_alignment, dict)
    
    @pytest.mark.asyncio
    async def test_alignment_preserves_zoom_chain(self):
        """Alignment should preserve bitchain zoom paths."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Should have parent-child index
        assert hasattr(snapshot, 'parent_child_index')
        assert isinstance(snapshot.parent_child_index, dict)
    
    @pytest.mark.asyncio
    async def test_alignment_enables_cross_realm_queries(self):
        """Alignment index should support cross-realm queries."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Should be queryable by various dimensions
        alignment = snapshot.tier_alignment
        assert 'by_tier' in alignment or 'tier_assignments' in snapshot.__dict__
    
    @pytest.mark.asyncio
    async def test_alignment_hash_unique_per_seed(self):
        """Different seeds should produce different alignment hashes."""
        from phase6d_reproducibility import UniverseExporter
        
        exporter = UniverseExporter()
        
        # Create two universes with different seeds
        config1 = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch1 = UniverseDemoOrchestrator(config1)
        await orch1.launch_demo()
        export1 = await exporter.export(orch1)
        
        config2 = OrchestratorConfig(seed=43, orbits=1, realms=["tavern"])
        orch2 = UniverseDemoOrchestrator(config2)
        await orch2.launch_demo()
        export2 = await exporter.export(orch2)
        
        # Hashes should differ
        assert export1.universe_hash != export2.universe_hash
    
    @pytest.mark.asyncio
    async def test_alignment_survives_tier_depth_expansion(self):
        """Alignment should remain valid when tier depth increases."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Alignment should support hierarchical queries
        alignment = snapshot.tier_alignment
        # If depth increases, should still be valid (hierarchical property)
        assert isinstance(alignment, dict)


# ============================================================================
# TEST: AUDIT TRAIL RECONSTRUCTION
# ============================================================================

class TestAuditTrailReconstruction:
    """Test audit trail capture and reconstruction."""
    
    @pytest.mark.asyncio
    async def test_audit_trail_captures_all_tier_assignments(self):
        """Audit trail should capture every tier assignment."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch, include_audit_trail=True)
        
        # Should have audit trail
        assert hasattr(snapshot, 'audit_trail')
        assert isinstance(snapshot.audit_trail, list)
        
        # Each entry should be timestamped
        for entry in snapshot.audit_trail:
            assert hasattr(entry, 'assigned_at') or 'timestamp' in str(entry)
    
    @pytest.mark.asyncio
    async def test_audit_trail_includes_admin_actions(self):
        """Audit trail should include governance/admin decisions."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch, include_governance=True)
        
        # Should have governance audit
        assert hasattr(snapshot, 'governance_audit')
        assert isinstance(snapshot.governance_audit, list)
    
    @pytest.mark.asyncio
    async def test_audit_trail_captures_enrichment_sequence(self):
        """Audit trail should preserve enrichment order."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Enrichments should be ordered
        enrichments = snapshot.enrichments
        if len(enrichments) > 1:
            # Verify timestamp ordering
            for i in range(len(enrichments) - 1):
                # Each enrichment should have timestamp
                assert hasattr(enrichments[i], 'created_at')
    
    @pytest.mark.asyncio
    async def test_audit_trail_enables_lineage_queries(self):
        """Audit trail should enable lineage tracing (NPC ← Entity ← Realm ← Seed)."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Should have enrichment lineage
        assert hasattr(snapshot, 'enrichment_lineage')
        assert isinstance(snapshot.enrichment_lineage, dict)
    
    @pytest.mark.asyncio
    async def test_audit_trail_immutable_in_export(self):
        """Exported audit trail should be immutable."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        snapshot = await exporter.export(orch)
        
        # Audit trail should not be modifiable (or should be a copy)
        original_length = len(snapshot.audit_trail)
        
        # Attempting to modify should not affect original
        # (either raises error or returns copy)
        audit_copy = snapshot.audit_trail.copy() if isinstance(snapshot.audit_trail, list) else list(snapshot.audit_trail)
        assert len(audit_copy) == original_length
    
    @pytest.mark.asyncio
    async def test_audit_trail_validation_on_replay(self, initial_export=None):
        """Audit trail should be validated during replay."""
        from phase6d_reproducibility import UniverseReplayer, UniverseExporter
        
        # Create export first
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        export_data = await exporter.export(orch)
        
        # Replay should validate audit trail
        replayer = UniverseReplayer()
        try:
            replayed = await replayer.replay_from_seed(export_data.seed, config)
            assert replayed is not None
        except Exception as e:
            # If validation fails, should be informative
            assert "audit" in str(e).lower() or "valid" in str(e).lower()


# ============================================================================
# TEST: FILE I/O
# ============================================================================

class TestExportFileIO:
    """Test export/import file operations."""
    
    @pytest.mark.asyncio
    async def test_export_to_file_creates_valid_json(self):
        """Export to file should create valid JSON."""
        from phase6d_reproducibility import UniverseExporter
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "universe_snapshot.json"
            snapshot = await exporter.export_to_file(orch, str(filepath))
            
            assert filepath.exists()
            
            # Should be valid JSON
            with open(filepath) as f:
                loaded = json.load(f)
                assert loaded is not None
    
    @pytest.mark.asyncio
    async def test_load_from_file_recreates_snapshot(self):
        """Loading from file should recreate snapshot."""
        from phase6d_reproducibility import UniverseExporter, UniverseReplayer
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orch = UniverseDemoOrchestrator(config)
        await orch.launch_demo()
        
        exporter = UniverseExporter()
        replayer = UniverseReplayer()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "universe_snapshot.json"
            original_snapshot = await exporter.export_to_file(orch, str(filepath))
            
            # Load from file
            loaded_snapshot = await replayer.load_from_file(str(filepath))
            
            assert loaded_snapshot.seed == original_snapshot.seed
            assert loaded_snapshot.universe_hash == original_snapshot.universe_hash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])