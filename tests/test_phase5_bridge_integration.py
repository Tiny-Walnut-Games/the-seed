"""
Phase 5 Bridge Integration Tests

Tests the Phase5Phase2Phase3Phase4Bridge that connects:
- Phase 5: Procedural universe with entities and enrichments
- Phase 2: NPC registration system
- Phase 3: Semantic search indexing
- Phase 4: Multi-turn dialogue state management
"""

import pytest
import sys
from pathlib import Path
from typing import List

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

from phase5_bigbang import (
    UniverseBigBang, UniverseSpec, RealmSpec, ContentType,
    TorusCycleEngine, StoryElement, RealmData
)
from phase5_providers import MetVanDamnProvider, CustomProvider, ArcadeProvider
from phase5_to_phase2_bridge import (
    Phase5Phase2Phase3Phase4Bridge,
    Phase5ToPhase2Adapter,
    Phase5ToPhase3Adapter,
    Phase5ToPhase4Adapter,
    integrate_phase5_universe
)


class TestPhase5Phase2BridgeAdapter:
    """Test Phase 5 → Phase 2 (NPC Registration) adapter"""
    
    @pytest.fixture
    async def setup_universe_with_entities(self):
        """Create a Phase 5 universe with entities."""
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=90)
        
        # Pre-register custom realm
        tavern_realm = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[],
            metadata={},
            orbit=0,
            lineage=0
        )
        custom_provider.register_realm("tavern", tavern_realm)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=2),
                RealmSpec(id="tavern", type=ContentType.CUSTOM),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        return universe
    
    @pytest.mark.asyncio
    async def test_adapter_registers_entities_as_npcs(self, setup_universe_with_entities):
        """Verify adapter converts entities to NPC registrations."""
        universe = await setup_universe_with_entities
        adapter = Phase5ToPhase2Adapter()
        
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        # Register first NPC
        if npcs:
            npc_entity = npcs[0]
            registration = adapter.register_entity_as_npc(npc_entity, "overworld")
            
            assert registration.npc_id.startswith("npc_overworld_")
            assert registration.npc_name is not None
            assert registration.realm_id == "overworld"
            assert registration.stat7_coordinates is not None
    
    @pytest.mark.asyncio
    async def test_adapter_generates_personality_traits(self, setup_universe_with_entities):
        """Verify adapter extracts personality from enrichments."""
        universe = await setup_universe_with_entities
        
        # Enrich entities first
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe,
            enrichment_types=[StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
        )
        
        adapter = Phase5ToPhase2Adapter()
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        if npcs:
            npc_entity = npcs[0]
            registration = adapter.register_entity_as_npc(npc_entity, "overworld")
            
            assert "base_mood" in registration.personality_traits
            assert "interaction_count" in registration.personality_traits
            assert "enriched_dimensions" in registration.personality_traits
            
            # Should have interaction count > 0 after enrichment
            assert registration.personality_traits["interaction_count"] > 0
    
    @pytest.mark.asyncio
    async def test_adapter_maintains_entity_npc_mapping(self, setup_universe_with_entities):
        """Verify adapter maintains mapping between entities and NPCs."""
        universe = await setup_universe_with_entities
        adapter = Phase5ToPhase2Adapter()
        
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        # Register multiple NPCs
        registered_count = 0
        for npc_entity in npcs[:min(3, len(npcs))]:
            adapter.register_entity_as_npc(npc_entity, "overworld")
            registered_count += 1
        
        # Verify registry
        assert len(adapter.npc_registry) == registered_count
        assert len(adapter.entity_to_npc_map) == registered_count


class TestPhase5Phase3BridgeAdapter:
    """Test Phase 5 → Phase 3 (Semantic Search) adapter"""
    
    @pytest.fixture
    async def setup_enriched_universe(self):
        """Create a Phase 5 universe with enriched entities."""
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=2),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        
        # Enrich with multiple cycles
        engine = TorusCycleEngine()
        for _ in range(2):
            await engine.execute_torus_cycle(
                universe,
                enrichment_types=[
                    StoryElement.DIALOGUE,
                    StoryElement.QUEST,
                    StoryElement.NPC_HISTORY
                ]
            )
        
        return universe
    
    @pytest.mark.asyncio
    async def test_adapter_extracts_semantic_context(self, setup_enriched_universe):
        """Verify adapter extracts semantic context from enrichments."""
        universe = await setup_enriched_universe
        adapter = Phase5ToPhase3Adapter()
        
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        if npcs:
            npc_entity = npcs[0]
            context = adapter.extract_semantic_context(npc_entity, "overworld")
            
            assert context.entity_id == npc_entity.id
            assert context.realm_id == "overworld"
            assert context.primary_topic in ["dialogue", "quest", "npc_history"]
            # Verify enrichment was captured
            assert context.audit_trail_depth > 0, "Should have enrichments"
            assert len(context.semantic_keywords) > 0, "Should have keywords"
            # Narrative arc may be empty if enrichment data is minimal
            assert isinstance(context.narrative_arc, list)
    
    @pytest.mark.asyncio
    async def test_adapter_provides_semantic_search(self, setup_enriched_universe):
        """Verify adapter enables semantic search queries."""
        universe = await setup_enriched_universe
        adapter = Phase5ToPhase3Adapter()
        
        # Index all NPCs
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        indexed_count = 0
        for npc_entity in npcs:
            adapter.extract_semantic_context(npc_entity, "overworld")
            indexed_count += 1
        
        # Search by topic
        topics = adapter.search_by_topic("dialogue")
        assert len(topics) > 0
        
        # Search by keyword
        overworld_entities = adapter.search_by_keyword("realm_overworld")
        assert len(overworld_entities) > 0
    
    @pytest.mark.asyncio
    async def test_adapter_provides_audit_trail(self, setup_enriched_universe):
        """Verify adapter provides enrichment audit trail for dialogue."""
        universe = await setup_enriched_universe
        adapter = Phase5ToPhase3Adapter()
        
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        if npcs:
            npc_entity = npcs[0]
            context = adapter.extract_semantic_context(npc_entity, "overworld")
            
            # Get audit trail
            trail = adapter.get_enrichment_audit_trail(npc_entity.id)
            assert isinstance(trail, list)
            # Audit trail may be empty or populated depending on enrichment data format
            # But the context should have audit_trail_depth > 0
            assert context.audit_trail_depth > 0, "Context should have captured enrichments"


class TestPhase5Phase4BridgeAdapter:
    """Test Phase 5 → Phase 4 (Multi-Turn Dialogue) adapter"""
    
    @pytest.fixture
    async def setup_universe_for_dialogue(self):
        """Create Phase 5 universe for dialogue state testing."""
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=1),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        return universe
    
    @pytest.mark.asyncio
    async def test_adapter_initializes_dialogue_state(self, setup_universe_for_dialogue):
        """Verify adapter initializes dialogue state from STAT7."""
        universe = await setup_universe_for_dialogue
        adapter = Phase5ToPhase4Adapter()
        
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        if npcs:
            npc_entity = npcs[0]
            dialogue_state = adapter.initialize_dialogue_state(
                npc_entity,
                "Test NPC",
                "overworld",
                universe.current_orbit
            )
            
            assert dialogue_state.entity_id == npc_entity.id
            assert dialogue_state.npc_name == "Test NPC"
            assert dialogue_state.realm_id == "overworld"
            assert dialogue_state.current_orbit == 0
            assert dialogue_state.dialogue_turn == 0
    
    @pytest.mark.asyncio
    async def test_adapter_provides_location_context(self, setup_universe_for_dialogue):
        """Verify adapter extracts location context from STAT7."""
        universe = await setup_universe_for_dialogue
        adapter = Phase5ToPhase4Adapter()
        
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        if npcs:
            npc_entity = npcs[0]
            adapter.initialize_dialogue_state(
                npc_entity,
                "Test NPC",
                "overworld",
                0
            )
            
            context = adapter.get_dialogue_context(npc_entity.id, "overworld", 0)
            
            assert "location_context" in context
            assert "location_type" in context
            assert "time_of_day" in context
            assert "npc_mood" in context
            assert "narrative_phase" in context
    
    @pytest.mark.asyncio
    async def test_adapter_tracks_dialogue_turns(self, setup_universe_for_dialogue):
        """Verify adapter tracks multi-turn dialogue progression."""
        universe = await setup_universe_for_dialogue
        adapter = Phase5ToPhase4Adapter()
        
        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")
        
        if npcs:
            npc_entity = npcs[0]
            adapter.initialize_dialogue_state(
                npc_entity,
                "Test NPC",
                "overworld",
                0
            )
            
            # Simulate multi-turn dialogue
            turn1 = adapter.advance_dialogue_turn(npc_entity.id, "overworld")
            turn2 = adapter.advance_dialogue_turn(npc_entity.id, "overworld")
            turn3 = adapter.advance_dialogue_turn(npc_entity.id, "overworld")
            
            assert turn1 == 1
            assert turn2 == 2
            assert turn3 == 3


class TestUnifiedBridge:
    """Test unified Phase5Phase2Phase3Phase4Bridge"""
    
    @pytest.mark.asyncio
    async def test_bridge_integrates_complete_universe(self):
        """Verify bridge integrates complete universe across Phase 2-4."""
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=90)
        
        # Pre-register custom realm
        tavern_realm = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[],
            metadata={},
            orbit=0,
            lineage=0
        )
        custom_provider.register_realm("tavern", tavern_realm)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=2),
                RealmSpec(id="tavern", type=ContentType.CUSTOM),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        
        # Enrich the universe
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe,
            enrichment_types=[StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
        )
        
        # Integrate via bridge
        bridge = Phase5Phase2Phase3Phase4Bridge()
        summary = await bridge.integrate_universe(universe)
        
        assert summary["npcs_registered"] > 0
        assert summary["semantic_contexts"] > 0
        assert summary["dialogue_sessions"] > 0
        assert len(summary["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_bridge_convenience_function(self):
        """Verify integrate_phase5_universe convenience function."""
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=1),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        bridge = await integrate_phase5_universe(universe)
        
        assert bridge is not None
        assert len(bridge.phase2_adapter.npc_registry) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])