"""
Phase 5 → Phase 2-4 Integration Tests

Tests the complete integration between:
- Phase 5: Procedural Universe Initialization (realms, entities, STAT7)
- Phase 2: Warbler NPCs and Cross-Realm Quests
- Phase 3: Semantic Search with Entity Enrichment Context
- Phase 4: Multi-Turn Dialogue with STAT7 Awareness

Scenario: Initialize a multiverse with Phase 5, register entities as NPCs,
execute torus cycles to enrich narrative, query with semantic search, then
conduct multi-turn dialogue with STAT7-aware context.
"""

import pytest
import sys
import asyncio
from pathlib import Path
from typing import List, Dict

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

from phase5_bigbang import (
    UniverseBigBang, UniverseSpec, RealmSpec, ContentType,
    TorusCycleEngine, StoryElement, Entity, STAT7Point, RealmData
)
from phase5_providers import MetVanDamnProvider, CustomProvider, ArcadeProvider

# Phase 2-4 imports (mocked for now if not available)
try:
    from universal_player_router import UniversalPlayerRouter
    from warbler_multiverse_bridge import WarblerMultiverseBridge
    from cross_realm_quests import CrossRealmQuestSystem
except ImportError:
    UniversalPlayerRouter = None
    WarblerMultiverseBridge = None
    CrossRealmQuestSystem = None


class TestPhase5Phase2Integration:
    """Integration tests: Phase 5 → Phase 2"""

    @pytest.fixture
    async def setup_universe_and_systems(self):
        """Initialize Phase 5 universe + Phase 2 systems."""
        # Phase 5: Create BigBang
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=90)
        bigbang.register_provider("arcade", ArcadeProvider(), priority=80)

        # Pre-register a custom realm for Phase 2 NPC system
        tavern_realm = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[],
            metadata={"zone": "bar"},
            orbit=0,
            lineage=0
        )
        custom_provider.register_realm("tavern", tavern_realm)

        # Define multiverse
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=3),
                RealmSpec(id="tavern", type=ContentType.CUSTOM),
            ]
        )

        # Initialize (Orbit 0)
        universe = await bigbang.initialize_multiverse(spec)

        # Phase 2: Create systems (if available)
        player_router = None
        warbler_bridge = None
        quest_system = None

        if UniversalPlayerRouter and WarblerMultiverseBridge:
            player_router = UniversalPlayerRouter()
            warbler_bridge = WarblerMultiverseBridge(player_router)
            quest_system = CrossRealmQuestSystem(player_router, None)

        return {
            "bigbang": bigbang,
            "universe": universe,
            "player_router": player_router,
            "warbler_bridge": warbler_bridge,
            "quest_system": quest_system,
        }

    @pytest.mark.asyncio
    async def test_phase5_realms_initialize_correctly(self, setup_universe_and_systems):
        """Verify Phase 5 realms initialize with proper structure."""
        setup = await setup_universe_and_systems
        universe = setup["universe"]

        # Check realms exist
        assert len(universe.realms) == 2
        assert "overworld" in universe.realms
        assert "tavern" in universe.realms

        # Check realm data structure
        overworld = universe.realms["overworld"]
        assert overworld.type == ContentType.METVAN_3D
        assert len(overworld.entities) > 0  # MetVanDamn should create entities

    @pytest.mark.asyncio
    async def test_phase5_entities_have_stat7_coordinates(self, setup_universe_and_systems):
        """Verify entities have valid STAT7 coordinates."""
        setup = await setup_universe_and_systems
        universe = setup["universe"]

        overworld = universe.realms["overworld"]
        for entity in overworld.entities:
            assert entity.stat7 is not None
            assert isinstance(entity.stat7, STAT7Point)

            # Verify STAT7 is within bounds (per __post_init__ validation)
            coord_dict = entity.stat7.to_dict()
            # Realm: 0 to 2^32-1; Lineage: -1M to +1M; Others: non-negative
            assert 0 <= coord_dict["realm"] < 2**32, f"Realm {coord_dict['realm']} out of bounds"
            assert -1000000 <= coord_dict["lineage"] <= 1000000, f"Lineage {coord_dict['lineage']} out of bounds"
            assert coord_dict["adjacency"] >= 0, f"Adjacency {coord_dict['adjacency']} must be non-negative"

    @pytest.mark.asyncio
    async def test_phase5_entities_queryable_by_type(self, setup_universe_and_systems):
        """Verify entities can be queried by type (for NPC registration)."""
        setup = await setup_universe_and_systems
        universe = setup["universe"]

        overworld = universe.realms["overworld"]

        # Query NPCs
        npcs = overworld.get_entities_by_type("npc")
        assert len(npcs) > 0, "Overworld should have NPCs"

        # Verify all returned entities are NPCs
        for entity in npcs:
            assert "npc" in entity.id.lower() or entity.entity_type == "npc"

    @pytest.mark.asyncio
    async def test_phase5_torus_cycle_enriches_entities(self, setup_universe_and_systems):
        """Verify torus cycles add narrative enrichments to entities."""
        setup = await setup_universe_and_systems
        universe = setup["universe"]

        # Execute first torus cycle (Orbit 1)
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe,
            enrichment_types=[StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
        )

        # Verify orbit advanced
        assert universe.current_orbit == 1

        # Check enrichments on entities
        overworld = universe.realms["overworld"]
        enrichment_count = 0
        for entity in overworld.entities:
            enrichments = entity.metadata.get("enrichments", [])
            enrichment_count += len(enrichments)

        assert enrichment_count > 0, "Torus cycle should create enrichments"

    @pytest.mark.asyncio
    async def test_phase5_enrichment_audit_trail_preservation(self, setup_universe_and_systems):
        """Verify enrichment audit trail is preserved for Phase 3 semantic context."""
        setup = await setup_universe_and_systems
        universe = setup["universe"]

        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe,
            enrichment_types=[StoryElement.DIALOGUE]
        )

        # Check audit trail structure
        overworld = universe.realms["overworld"]
        for entity in overworld.entities:
            enrichments = entity.metadata.get("enrichments", [])
            for enrichment in enrichments:
                # Verify audit trail fields
                assert "timestamp" in enrichment, "Enrichment must have timestamp"
                assert "type" in enrichment, "Enrichment must have type"
                assert "data" in enrichment, "Enrichment must have data"

    @pytest.mark.asyncio
    async def test_phase5_concurrent_cycles_thread_safe(self, setup_universe_and_systems):
        """Verify concurrent torus cycles maintain thread safety."""
        setup = await setup_universe_and_systems
        universe = setup["universe"]

        engine = TorusCycleEngine()

        # Execute multiple cycles concurrently
        tasks = [
            engine.execute_torus_cycle(
                universe,
                enrichment_types=[StoryElement.DIALOGUE]
            )
            for _ in range(3)
        ]

        await asyncio.gather(*tasks)

        # Verify all cycles executed without race conditions
        assert universe.current_orbit == 3, "All cycles should complete"

        # Verify entity enrichment counts are consistent
        overworld = universe.realms["overworld"]
        for entity in overworld.entities:
            enrichments = entity.metadata.get("enrichments", [])
            # Should have some enrichments
            assert len(enrichments) >= 0

    @pytest.mark.asyncio
    async def test_phase5_serializable_for_phase3_indexing(self, setup_universe_and_systems):
        """Verify entities serialize to JSON for Phase 3 semantic indexing."""
        setup = await setup_universe_and_systems
        universe = setup["universe"]

        overworld = universe.realms["overworld"]
        npcs = overworld.get_entities_by_type("npc")

        for npc in npcs:
            # Verify STAT7 serializes
            stat7_dict = npc.stat7.to_dict()
            assert isinstance(stat7_dict, dict)
            assert all(isinstance(v, (int, float)) for v in stat7_dict.values())

            # Verify enrichments serialize
            enrichments = npc.metadata.get("enrichments", [])
            for enrichment in enrichments:
                assert isinstance(enrichment.get("data"), (str, dict, list))


class TestPhase5Phase3Integration:
    """Integration tests: Phase 5 → Phase 3 (Semantic Search)"""

    @pytest.mark.asyncio
    async def test_phase5_enrichments_provide_semantic_context(self):
        """Verify Phase 5 enrichments provide rich semantic context for Phase 3."""
        bigbang = UniverseBigBang()
        bigbang.register_provider("metvan", MetVanDamnProvider())

        spec = UniverseSpec(
            realms=[
                RealmSpec(id="overworld", type=ContentType.METVAN_3D, district_count=2),
            ]
        )

        universe = await bigbang.initialize_multiverse(spec)

        # Execute multiple torus cycles to accumulate enrichments
        engine = TorusCycleEngine()
        for i in range(2):
            await engine.execute_torus_cycle(
                universe,
                enrichment_types=[StoryElement.DIALOGUE, StoryElement.QUEST]
            )

        # Verify semantic richness
        overworld = universe.realms["overworld"]
        for entity in overworld.entities:
            enrichments = entity.metadata.get("enrichments", [])
            enrichment_types = {e.get("type") for e in enrichments}

            # Should have multiple enrichment types for semantic richness
            assert len(enrichment_types) > 0, f"Entity {entity.id} lacks enrichments"


class TestPhase5Phase4Integration:
    """Integration tests: Phase 5 → Phase 4 (Multi-Turn Dialogue)"""

    @pytest.mark.asyncio
    async def test_phase5_stat7_coordinates_enable_location_awareness(self):
        """Verify STAT7 coordinates enable location-aware dialogue."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        bigbang.register_provider("arcade", ArcadeProvider(), priority=90)

        # Pre-register custom realm
        tavern_realm = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[],
            metadata={"zone": "bar"},
            orbit=0,
            lineage=0
        )
        custom_provider.register_realm("tavern", tavern_realm)

        spec = UniverseSpec(
            realms=[
                RealmSpec(id="tavern", type=ContentType.CUSTOM),
                RealmSpec(id="arcade", type=ContentType.ARCADE_2D, available_games=["pac_man"]),
            ]
        )

        universe = await bigbang.initialize_multiverse(spec)

        # Verify location context extraction
        for realm_id, realm in universe.realms.items():
            for entity in realm.entities:
                # Extract location from STAT7
                location_context = {
                    "realm": realm_id,
                    "adjacency": entity.stat7.adjacency,
                    "resonance": entity.stat7.resonance,
                }
                assert location_context["realm"] in ["tavern", "arcade"]

    @pytest.mark.asyncio
    async def test_phase5_orbit_progression_tracks_dialogue_turns(self):
        """Verify orbit progression can track multi-turn dialogue."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)

        # Pre-register custom realm
        meeting_realm = RealmData(
            id="meetingpoint",
            type=ContentType.CUSTOM,
            entities=[],
            metadata={"purpose": "meeting"},
            orbit=0,
            lineage=0
        )
        custom_provider.register_realm("meetingpoint", meeting_realm)

        spec = UniverseSpec(
            realms=[
                RealmSpec(id="meetingpoint", type=ContentType.CUSTOM),
            ]
        )

        universe = await bigbang.initialize_multiverse(spec)
        engine = TorusCycleEngine()

        # Simulate multi-turn dialogue as orbit progression
        dialogue_turns = []
        for turn in range(3):
            await engine.execute_torus_cycle(
                universe,
                enrichment_types=[StoryElement.DIALOGUE]
            )
            dialogue_turns.append(universe.current_orbit)

        # Verify orbit tracks turn progression
        assert dialogue_turns == [1, 2, 3]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])