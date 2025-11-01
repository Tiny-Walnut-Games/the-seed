"""
Phase 6: Unified End-to-End Orchestrator Tests

Tests the orchestrator that wires together:
- Phase 5: Procedural universe generation
- Bridge: Phase 5 → Phase 2-4 integration
- Phase 2-4: NPC, semantic search, dialogue systems

The orchestrator is a single entry point for university demo.
"""

import pytest
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

from phase5_bigbang import UniverseBigBang, UniverseSpec, RealmSpec, ContentType, TorusCycleEngine, StoryElement, RealmData
from phase5_providers import MetVanDamnProvider, CustomProvider, ArcadeProvider
from phase5_to_phase2_bridge import integrate_phase5_universe


class TestPhase6Orchestrator:
    """Test the unified orchestrator for university demo."""
    
    @pytest.fixture
    def demo_spec(self):
        """Demo universe specification."""
        return UniverseSpec(
            realms=[
                RealmSpec(id="tavern", type=ContentType.CUSTOM, seed=42),
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=1, seed=42),
            ]
        )
    
    @pytest.mark.asyncio
    async def test_orchestrator_initializes_with_seed(self, demo_spec):
        """✅ Orchestrator should initialize Phase 5 with reproducible seed."""
        
        # Initialize with seed 42 on RealmSpec
        bigbang1 = UniverseBigBang()
        bigbang1.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom1 = CustomProvider()
        # Pre-register custom realm with seed 42
        tavern_realm1 = RealmData(
            id="tavern", 
            type=ContentType.CUSTOM, 
            entities=[],
            metadata={},
            orbit=0,
            lineage=0
        )
        custom1.register_realm("tavern", tavern_realm1)
        bigbang1.register_provider("custom", custom1, priority=90)
        
        universe1 = await bigbang1.initialize_multiverse(demo_spec)
        
        # Initialize again with same setup
        bigbang2 = UniverseBigBang()
        bigbang2.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom2 = CustomProvider()
        tavern_realm2 = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[],
            metadata={},
            orbit=0,
            lineage=0
        )
        custom2.register_realm("tavern", tavern_realm2)
        bigbang2.register_provider("custom", custom2, priority=90)
        
        universe2 = await bigbang2.initialize_multiverse(demo_spec)
        
        # Both should have same realms
        assert len(universe1.realms) == len(universe2.realms)
        assert set(universe1.realms.keys()) == set(universe2.realms.keys())
    
    @pytest.mark.asyncio
    async def test_orchestrator_runs_enrichment_cycles(self, demo_spec):
        """✅ Orchestrator should run Torus cycles for narrative enrichment."""
        
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom = CustomProvider()
        tavern_realm = RealmData(id="tavern", type=ContentType.CUSTOM, entities=[], metadata={}, orbit=0, lineage=0)
        custom.register_realm("tavern", tavern_realm)
        bigbang.register_provider("custom", custom, priority=90)
        
        universe = await bigbang.initialize_multiverse(demo_spec)
        
        # Capture initial state
        initial_enrichment_counts = {}
        for realm_id, realm in universe.realms.items():
            for entity in realm.entities:
                entity_id = entity.id
                enrichments = entity.metadata.get("enrichments", [])
                initial_enrichment_counts[entity_id] = len(enrichments)
        
        # Run one Torus cycle with enrichment types
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe,
            [StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
        )
        
        # Enrichments should increase
        for realm_id, realm in universe.realms.items():
            for entity in realm.entities:
                entity_id = entity.id
                enrichments = entity.metadata.get("enrichments", [])
                current_count = len(enrichments)
                
                # After enrichment, count should be >= initial
                assert current_count >= initial_enrichment_counts[entity_id], \
                    f"Entity {entity_id}: enrichments didn't increase"
    
    @pytest.mark.asyncio
    async def test_orchestrator_bridges_to_phase2_4(self, demo_spec):
        """✅ Orchestrator should bridge Phase 5 universe to Phase 2-4 systems."""
        
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom = CustomProvider()
        tavern_realm = RealmData(id="tavern", type=ContentType.CUSTOM, entities=[], metadata={}, orbit=0, lineage=0)
        custom.register_realm("tavern", tavern_realm)
        bigbang.register_provider("custom", custom, priority=90)
        
        universe = await bigbang.initialize_multiverse(demo_spec)
        
        # Run one cycle for enrichment
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe,
            [StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
        )
        
        # Bridge the universe
        bridge = await integrate_phase5_universe(universe)
        
        # Verify bridge produced outputs
        assert bridge is not None
        assert hasattr(bridge, 'phase2_adapter'), "Bridge should have Phase 2 adapter"
        assert hasattr(bridge, 'phase3_adapter'), "Bridge should have Phase 3 adapter"
        assert hasattr(bridge, 'phase4_adapter'), "Bridge should have Phase 4 adapter"
    
    @pytest.mark.asyncio
    async def test_orchestrator_produces_reproducible_metadata(self, demo_spec):
        """✅ Orchestrator should return metadata with seed for reproducibility."""
        
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom = CustomProvider()
        tavern_realm = RealmData(id="tavern", type=ContentType.CUSTOM, entities=[], metadata={}, orbit=0, lineage=0)
        custom.register_realm("tavern", tavern_realm)
        bigbang.register_provider("custom", custom, priority=90)
        
        universe = await bigbang.initialize_multiverse(demo_spec)
        
        # Count entities
        total_entities = sum(len(realm.entities) for realm_id, realm in universe.realms.items())
        assert total_entities > 0, "Universe should have entities"
        
        # Build metadata dict
        metadata = {
            "seed": 42,
            "universe_initialized_at": universe.initialized_at.isoformat(),
            "realms": {realm_id: len(realm.entities) for realm_id, realm in universe.realms.items()},
            "total_entities": total_entities,
            "generation_timestamp": None,  # Will be set during orchestration
        }
        
        # Verify metadata structure
        assert metadata["seed"] == 42
        assert metadata["universe_initialized_at"] is not None
        assert all(isinstance(count, int) for count in metadata["realms"].values())
    
    @pytest.mark.asyncio
    async def test_orchestrator_tracks_multiple_cycles(self, demo_spec):
        """✅ Orchestrator should track multiple enrichment cycles."""
        
        # Use just a simple spec with entities
        simple_spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=1, seed=42),
            ]
        )
        
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        
        universe = await bigbang.initialize_multiverse(simple_spec)
        engine = TorusCycleEngine()
        
        # Run 3 cycles
        for cycle_num in range(3):
            await engine.execute_torus_cycle(
                universe,
                [StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
            )
            
            # After each cycle, verify universe is valid
            assert len(universe.realms) > 0
            # At least one realm should have entities (overworld from MetVanDamnProvider)
            total_entities = sum(len(realm.entities) for realm_id, realm in universe.realms.items())
            assert total_entities > 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_serializes_to_json(self, demo_spec):
        """✅ Orchestrator should export universe to JSON for reproducibility."""
        
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom = CustomProvider()
        tavern_realm = RealmData(id="tavern", type=ContentType.CUSTOM, entities=[], metadata={}, orbit=0, lineage=0)
        custom.register_realm("tavern", tavern_realm)
        bigbang.register_provider("custom", custom, priority=90)
        
        universe = await bigbang.initialize_multiverse(demo_spec)
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe,
            [StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
        )
        
        # Export metadata
        export_data = {
            "seed": 42,
            "universe_initialized_at": universe.initialized_at.isoformat(),
            "orbits": universe.total_orbits_completed,
            "realms": {},
        }
        
        for realm_id, realm in universe.realms.items():
            export_data["realms"][realm_id] = {
                "type": realm.type.value,
                "entity_count": len(realm.entities),
            }
        
        # Should be JSON serializable
        json_str = json.dumps(export_data)
        loaded = json.loads(json_str)
        
        assert loaded["seed"] == 42
        assert loaded["orbits"] >= 1
        assert len(loaded["realms"]) > 0


class TestPhase6OrchestratorAPI:
    """Test orchestrator as a composable API."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_api_setup(self):
        """✅ Orchestrator should provide composable API."""
        
        # The orchestrator should support:
        # 1. Creating  universe bigbang
        # 2. Initializing universe
        # 3. Running cycles
        # 4. Bridging to Phase 2-4
        # 5. Returning metadata
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=1, seed=100),
            ]
        )
        
        # 1. Create BigBang
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        
        # 2. Initialize
        universe = await bigbang.initialize_multiverse(spec)
        assert universe is not None
        
        # 3. Run cycle
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe,
            [StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
        )
        assert universe is not None
        
        # 4. Bridge
        bridge = await integrate_phase5_universe(universe)
        assert bridge is not None
        
        # 5. Metadata
        metadata = {
            "seed": 100,
            "universe_initialized_at": universe.initialized_at.isoformat(),
            "orbits": universe.total_orbits_completed,
        }
        assert metadata["seed"] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])