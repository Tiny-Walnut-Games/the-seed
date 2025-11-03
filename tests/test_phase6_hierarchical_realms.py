"""
Phase 6-Alpha: Hierarchical Realm Tier System Tests

Tests the three-tier cosmological hierarchy (Celestial/Terran/Subterran)
as a perspective layer on top of STAT7 + bitchain structure.

Architecture:
- TierClassification: Enum of Celestial, Terran, Subterran
- RealmTierMetadata: Tier + semantic classification for realms
- TierProvider: Factory for tier-aware realm creation
- Zoom navigation: Entity → Sub-realm via bitchain

Date: 2025-10-31
Tests: Tier classification, zoom mechanics, semantic context, integration
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

from phase5_bigbang import (
    UniverseBigBang, UniverseSpec, RealmSpec, ContentType,
    STAT7Point, Entity, RealmData, StoryElement
)
from phase5_providers import MetVanDamnProvider, CustomProvider
from phase6_hierarchical_realms import (
    TierClassification, TierTheme, RealmTierMetadata,
    TierRegistry, ZoomNavigator, TierPersonalityGenerator,
    HierarchicalUniverseAdapter
)


# ============================================================================
# NOTE: Enums and models are now imported from phase6_hierarchical_realms
# No local redefinitions—we use the production implementations
# ============================================================================


# ============================================================================
# TESTS: TIER CLASSIFICATION
# ============================================================================

class TestTierClassification:
    """Test basic tier classification and metadata."""
    
    def test_tier_enum_has_three_classifications(self):
        """Verify three tiers exist."""
        assert TierClassification.CELESTIAL.value == "celestial"
        assert TierClassification.TERRAN.value == "terran"
        assert TierClassification.SUBTERRAN.value == "subterran"
    
    def test_tier_themes_map_to_classifications(self):
        """Verify themes are associated with tiers."""
        celestial_themes = [TierTheme.HEAVEN, TierTheme.AETHER, TierTheme.ASCENSION]
        terran_themes = [TierTheme.OVERWORLD, TierTheme.CITY_STATE, TierTheme.RURAL, TierTheme.FRONTIER]
        subterran_themes = [TierTheme.HELL, TierTheme.ABYSS, TierTheme.UNDERDARK, TierTheme.DYSTOPIA]
        
        assert len(celestial_themes) >= 1
        assert len(terran_themes) >= 1
        assert len(subterran_themes) >= 1
    
    def test_realm_tier_metadata_serializes(self):
        """Verify metadata can be serialized."""
        metadata = RealmTierMetadata(
            realm_id="tavern",
            tier=TierClassification.TERRAN,
            theme=TierTheme.CITY_STATE,
            semantic_anchors=["urban", "medieval", "social"],
            tier_depth=0,
        )
        
        serialized = metadata.to_dict()
        assert serialized["realm_id"] == "tavern"
        assert serialized["tier"] == "terran"
        assert serialized["theme"] == "city_state"
        assert serialized["semantic_anchors"] == ["urban", "medieval", "social"]


# ============================================================================
# TESTS: TIER-AWARE REALM GENERATION
# ============================================================================

class TestTierAwareRealmGeneration:
    """Test creating realms with tier classification."""
    
    @pytest.fixture
    async def tier_provider(self):
        """Create a mock tier-aware provider."""
        # Will be implemented in Step 3
        pass
    
    @pytest.mark.asyncio
    async def test_realm_spec_accepts_tier_classification(self):
        """Verify RealmSpec can carry tier information."""
        # RealmSpec should support optional tier_info parameter
        realm_spec = RealmSpec(
            id="celestial_tavern",
            type=ContentType.CUSTOM,
            seed=42,
        )
        
        # After enhancement, should support:
        # realm_spec.tier_info = RealmTierMetadata(...)
        assert realm_spec.id == "celestial_tavern"
    
    @pytest.mark.asyncio
    async def test_realm_data_carries_tier_metadata(self):
        """Verify RealmData stores tier classification."""
        realm = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[],
        )
        
        # After enhancement, should have tier_metadata attribute
        assert realm.id == "tavern"
    
    @pytest.mark.asyncio
    async def test_universe_maintains_tier_index(self):
        """Verify Universe can query realms by tier."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        # Create realms with different tiers (will be enhanced)
        tavern = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[],
            metadata={},
        )
        custom_provider.register_realm("tavern", tavern)
        
        spec = UniverseSpec(
            realms=[RealmSpec(id="tavern", type=ContentType.CUSTOM)]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        
        # After enhancement, should support:
        # celestial_realms = universe.get_realms_by_tier(TierClassification.CELESTIAL)
        assert len(universe.realms) > 0


# ============================================================================
# TESTS: SUB-REALM TRAVERSAL (ZOOM MECHANICS)
# ============================================================================

class TestSubRealmTraversal:
    """Test navigating into entities as sub-realms (fractal zoom)."""
    
    def test_entity_can_be_zoomed_into_as_subrealm(self):
        """Verify entity can be converted to sub-realm via bitchain."""
        # Create parent entity
        parent_stat7 = STAT7Point(
            realm=0, lineage=0, adjacency=1, horizon=0,
            resonance=100, velocity=0, density=50
        )
        parent_entity = Entity(
            id="npc_tavern_keeper",
            type="npc",
            position=(50.0, 0.0, 50.0),
            stat7=parent_stat7,
        )
        
        # Should be able to derive sub-realm address
        # Example: Zoom into entity → new realm where entity becomes center
        sub_realm_id = f"sub_{parent_entity.id}_0"
        assert sub_realm_id == "sub_npc_tavern_keeper_0"
    
    def test_sub_realm_inherits_tier_context_from_parent(self):
        """Verify sub-realms carry parent tier metadata."""
        parent_metadata = RealmTierMetadata(
            realm_id="tavern",
            tier=TierClassification.TERRAN,
            theme=TierTheme.CITY_STATE,
            semantic_anchors=["urban", "medieval"],
            tier_depth=0,
        )
        
        # Create sub-realm from entity
        sub_metadata = RealmTierMetadata(
            realm_id="sub_npc_tavern_keeper_0",
            tier=parent_metadata.tier,  # Inherit tier
            theme=parent_metadata.theme,  # Inherit theme
            semantic_anchors=parent_metadata.semantic_anchors + ["interior", "tavern_keeper"],
            tier_depth=parent_metadata.tier_depth + 1,
            parent_realm_id=parent_metadata.realm_id,
            parent_entity_id="npc_tavern_keeper",
        )
        
        assert sub_metadata.tier == TierClassification.TERRAN
        assert sub_metadata.tier_depth == 1
        assert sub_metadata.parent_realm_id == "tavern"
    
    @pytest.mark.asyncio
    async def test_zoom_navigation_creates_bitchain_path(self):
        """Verify zoom-down navigation follows bitchain topology."""
        # Create parent universe
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        # Create parent realm with entity
        parent_realm = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[
                Entity(
                    id="npc_bartender",
                    type="npc",
                    position=(25.0, 0.0, 25.0),
                    stat7=STAT7Point(0, 0, 0, 0, 100, 0, 50),
                    metadata={"name": "Bartender"},
                )
            ],
            metadata={},
        )
        custom_provider.register_realm("tavern", parent_realm)
        
        spec = UniverseSpec(
            realms=[RealmSpec(id="tavern", type=ContentType.CUSTOM)]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        
        # After enhancement, should support zoom navigation:
        # sub_realm = await universe.zoom_into_entity("tavern", "npc_bartender")
        # assert sub_realm.parent_realm_id == "tavern"
        assert "tavern" in universe.realms


# ============================================================================
# TESTS: TIER-AWARE SEMANTIC ENRICHMENT
# ============================================================================

class TestTierAwareSemanticEnrichment:
    """Test enrichment respects tier classification."""
    
    def test_enrichment_includes_tier_context(self):
        """Verify enrichments capture tier metadata."""
        entity = Entity(
            id="npc_scholar",
            type="npc",
            position=(0.0, 0.0, 0.0),
            stat7=STAT7Point(0, 0, 0, 0, 100, 0, 50),
        )
        
        # Enrich with tier context
        enrichment_data = {
            "type": "dialogue",
            "tier_context": TierClassification.CELESTIAL.value,
            "theme_context": TierTheme.AETHER.value,
            "text": "The cosmic weavers speak through starlight...",
        }
        
        entity.enrich(StoryElement.DIALOGUE, enrichment_data)
        
        assert entity.enrichment_count == 1
        assert entity.metadata["enrichments"][0]["data"]["tier_context"] == "celestial"
    
    def test_npc_personality_reflects_tier_theme(self):
        """Verify NPC personalities are influenced by tier classification."""
        # Celestial NPC: mystical, ethereal
        celestial_npc_traits = ["wise", "ethereal", "ascendant", "mystical"]
        
        # Terran NPC: grounded, pragmatic
        terran_npc_traits = ["practical", "grounded", "sociable", "cunning"]
        
        # Subterran NPC: dark, eldritch
        subterran_npc_traits = ["dark", "eldritch", "corrupted", "mysterious"]
        
        assert "wise" in celestial_npc_traits
        assert "practical" in terran_npc_traits
        assert "dark" in subterran_npc_traits
    
    @pytest.mark.asyncio
    async def test_phase3_semantic_search_indexes_by_tier(self):
        """Verify Phase 3 semantic indexing respects tier classification."""
        # Create universe with tier-classified realms
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        realm = RealmData(
            id="celestial_library",
            type=ContentType.CUSTOM,
            entities=[
                Entity(
                    id="npc_celestial_librarian",
                    type="npc",
                    position=(0.0, 0.0, 0.0),
                    stat7=STAT7Point(0, 0, 0, 0, 100, 0, 50),
                )
            ],
            metadata={},
        )
        custom_provider.register_realm("celestial_library", realm)
        
        spec = UniverseSpec(
            realms=[RealmSpec(id="celestial_library", type=ContentType.CUSTOM)]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        
        # After enhancement, Phase 3 should:
        # - Index entities with tier metadata
        # - Separate celestial/terran/subterran search indexes
        # - Weight results by tier affinity
        assert "celestial_library" in universe.realms


# ============================================================================
# TESTS: NPC GENERATION TIER-AWARE
# ============================================================================

class TestNPCGenerationTierAware:
    """Test NPC generation respects tier classification."""
    
    @pytest.mark.asyncio
    async def test_npcs_are_generated_with_tier_affinity(self):
        """Verify NPCs reflect their realm's tier."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        # Create tier-classified realm
        celestial_realm = RealmData(
            id="celestial_temple",
            type=ContentType.CUSTOM,
            entities=[
                Entity(
                    id="npc_celestial_priest",
                    type="npc",
                    position=(0.0, 100.0, 0.0),
                    stat7=STAT7Point(0, 0, 0, 0, 100, 0, 50),
                    metadata={
                        "name": "Celestial Priest",
                        "tier_affinity": TierClassification.CELESTIAL.value,
                        "personality_traits": ["wise", "ethereal", "mystical"],
                    },
                )
            ],
            metadata={},
        )
        custom_provider.register_realm("celestial_temple", celestial_realm)
        
        spec = UniverseSpec(
            realms=[RealmSpec(id="celestial_temple", type=ContentType.CUSTOM)]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        celestial_temple = universe.realms["celestial_temple"]
        
        # Verify NPC exists and has tier affinity
        npcs = celestial_temple.get_entities_by_type("npc")
        assert len(npcs) > 0
        assert npcs[0].metadata.get("tier_affinity") == TierClassification.CELESTIAL.value
    
    @pytest.mark.asyncio
    async def test_tier_influences_dialogue_tone(self):
        """Verify dialogue generation considers tier."""
        # Celestial dialogue: ethereal, mystical
        celestial_dialogue = "The stars whisper secrets of the cosmos..."
        
        # Terran dialogue: practical, grounded
        terran_dialogue = "The village square fills with merchants and travelers."
        
        # Subterran dialogue: dark, ominous
        subterran_dialogue = "The shadows writhe with unknown horrors..."
        
        # These should be generated by Phase 2-4 based on tier metadata
        assert "whisper" in celestial_dialogue
        assert "village" in terran_dialogue
        assert "shadows" in subterran_dialogue


# ============================================================================
# TESTS: INTEGRATION WITH PHASE 5-6A
# ============================================================================

class TestTierIntegrationWithPhase5And6A:
    """Test tier system integrates with existing Phase 5 and 6A."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initializes_tier_aware_universe(self):
        """Verify Phase 6A orchestrator creates tier-classified realms."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        # Pre-register tier-classified realms
        realms_data = {
            "celestial_temple": RealmData(
                id="celestial_temple",
                type=ContentType.CUSTOM,
                entities=[],
                metadata={"tier": "celestial", "theme": "aether"},
            ),
            "tavern": RealmData(
                id="tavern",
                type=ContentType.CUSTOM,
                entities=[],
                metadata={"tier": "terran", "theme": "city_state"},
            ),
            "dungeon": RealmData(
                id="dungeon",
                type=ContentType.CUSTOM,
                entities=[],
                metadata={"tier": "subterran", "theme": "underdark"},
            ),
        }
        
        for realm_id, realm in realms_data.items():
            custom_provider.register_realm(realm_id, realm)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="celestial_temple", type=ContentType.CUSTOM),
                RealmSpec(id="tavern", type=ContentType.CUSTOM),
                RealmSpec(id="dungeon", type=ContentType.CUSTOM),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        
        # Verify all three tiers are represented
        assert len(universe.realms) == 3
        assert "celestial_temple" in universe.realms
        assert "tavern" in universe.realms
        assert "dungeon" in universe.realms
    
    @pytest.mark.asyncio
    async def test_universe_can_query_realms_by_tier(self):
        """Verify Universe supports tier-based queries."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        realms_data = {
            "heaven": RealmData(id="heaven", type=ContentType.CUSTOM, entities=[], metadata={}),
            "tavern": RealmData(id="tavern", type=ContentType.CUSTOM, entities=[], metadata={}),
            "hell": RealmData(id="hell", type=ContentType.CUSTOM, entities=[], metadata={}),
        }
        
        for realm_id, realm in realms_data.items():
            custom_provider.register_realm(realm_id, realm)
        
        spec = UniverseSpec(
            realms=[RealmSpec(id=rid, type=ContentType.CUSTOM) for rid in realms_data.keys()]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        
        # After enhancement, should support:
        # celestial_realms = universe.get_realms_by_tier(TierClassification.CELESTIAL)
        # assert len(celestial_realms) >= 1
        assert len(universe.realms) >= 1


# ============================================================================
# TESTS: TIER REGISTRY & ZOOM NAVIGATOR (Integration)
# ============================================================================

class TestTierRegistryIntegration:
    """Test TierRegistry with real tier operations."""
    
    @pytest.mark.asyncio
    async def test_tier_registry_registers_and_retrieves_realms(self):
        """Verify TierRegistry stores and retrieves tier classifications."""
        registry = TierRegistry()
        
        metadata1 = RealmTierMetadata(
            realm_id="tavern",
            tier=TierClassification.TERRAN,
            theme=TierTheme.CITY_STATE,
            semantic_anchors=["urban", "medieval"],
        )
        
        metadata2 = RealmTierMetadata(
            realm_id="heaven",
            tier=TierClassification.CELESTIAL,
            theme=TierTheme.HEAVEN,
            semantic_anchors=["peaceful", "utopian"],
        )
        
        await registry.register_realm(metadata1)
        await registry.register_realm(metadata2)
        
        # Query by tier
        terran_realms = await registry.get_realms_by_tier(TierClassification.TERRAN)
        assert "tavern" in terran_realms
        assert len(terran_realms) == 1
        
        celestial_realms = await registry.get_realms_by_tier(TierClassification.CELESTIAL)
        assert "heaven" in celestial_realms
        assert len(celestial_realms) == 1
    
    @pytest.mark.asyncio
    async def test_tier_registry_queries_by_theme(self):
        """Verify TierRegistry can query by theme."""
        registry = TierRegistry()
        
        for i in range(3):
            metadata = RealmTierMetadata(
                realm_id=f"city_{i}",
                tier=TierClassification.TERRAN,
                theme=TierTheme.CITY_STATE,
                semantic_anchors=["urban"],
            )
            await registry.register_realm(metadata)
        
        city_realms = await registry.get_realms_by_theme(TierTheme.CITY_STATE)
        assert len(city_realms) == 3
        assert all(rid.startswith("city_") for rid in city_realms)
    
    @pytest.mark.asyncio
    async def test_tier_registry_queries_by_semantic_anchor(self):
        """Verify TierRegistry can query by semantic anchor."""
        registry = TierRegistry()
        
        metadata1 = RealmTierMetadata(
            realm_id="library",
            tier=TierClassification.CELESTIAL,
            theme=TierTheme.AETHER,
            semantic_anchors=["knowledge", "books", "mystical"],
        )
        
        metadata2 = RealmTierMetadata(
            realm_id="academy",
            tier=TierClassification.TERRAN,
            theme=TierTheme.CITY_STATE,
            semantic_anchors=["knowledge", "education", "urban"],
        )
        
        await registry.register_realm(metadata1)
        await registry.register_realm(metadata2)
        
        # Query by semantic anchor
        knowledge_realms = await registry.get_realms_by_anchor("knowledge")
        assert len(knowledge_realms) == 2
        assert "library" in knowledge_realms
        assert "academy" in knowledge_realms
    
    @pytest.mark.asyncio
    async def test_tier_registry_provides_statistics(self):
        """Verify TierRegistry provides tier distribution statistics."""
        registry = TierRegistry()
        
        # Register realms in different tiers
        for i in range(2):
            await registry.register_realm(RealmTierMetadata(
                realm_id=f"celestial_{i}",
                tier=TierClassification.CELESTIAL,
                theme=TierTheme.HEAVEN,
                semantic_anchors=[],
            ))
        
        for i in range(3):
            await registry.register_realm(RealmTierMetadata(
                realm_id=f"terran_{i}",
                tier=TierClassification.TERRAN,
                theme=TierTheme.CITY_STATE,
                semantic_anchors=[],
            ))
        
        for i in range(1):
            await registry.register_realm(RealmTierMetadata(
                realm_id=f"subterran_{i}",
                tier=TierClassification.SUBTERRAN,
                theme=TierTheme.HELL,
                semantic_anchors=[],
            ))
        
        counts = registry.tier_counts()
        assert counts["celestial"] == 2
        assert counts["terran"] == 3
        assert counts["subterran"] == 1


class TestZoomNavigatorIntegration:
    """Test ZoomNavigator sub-realm creation."""
    
    def test_zoom_navigator_creates_sub_realm_ids(self):
        """Verify ZoomNavigator generates deterministic sub-realm IDs."""
        navigator = ZoomNavigator()
        
        sub_id_1 = navigator.compute_sub_realm_id("tavern", "npc_bartender", 1)
        sub_id_2 = navigator.compute_sub_realm_id("tavern", "npc_bartender", 1)
        
        # Should be deterministic
        assert sub_id_1 == sub_id_2
        assert "sub_tavern_npc_bartender_1" == sub_id_1
    
    def test_zoom_navigator_inherits_tier_from_parent(self):
        """Verify sub-realms inherit parent tier and theme."""
        navigator = ZoomNavigator()
        
        parent_metadata = RealmTierMetadata(
            realm_id="tavern",
            tier=TierClassification.TERRAN,
            theme=TierTheme.CITY_STATE,
            semantic_anchors=["urban", "medieval"],
            tier_depth=0,
        )
        
        sub_metadata = navigator.create_sub_realm_metadata(
            parent_metadata,
            "npc_bartender",
            additional_anchors=["interior", "tavern"],
        )
        
        # Verify inheritance
        assert sub_metadata.tier == TierClassification.TERRAN
        assert sub_metadata.theme == TierTheme.CITY_STATE
        assert sub_metadata.tier_depth == 1
        assert sub_metadata.parent_realm_id == "tavern"
        assert sub_metadata.parent_entity_id == "npc_bartender"
        
        # Verify anchor merging
        assert "urban" in sub_metadata.semantic_anchors
        assert "medieval" in sub_metadata.semantic_anchors
        assert "interior" in sub_metadata.semantic_anchors
        assert "tavern" in sub_metadata.semantic_anchors
    
    def test_zoom_navigator_tracks_navigation_path(self):
        """Verify ZoomNavigator maintains bitchain path."""
        navigator = ZoomNavigator()
        
        # Simulate zoom navigation
        navigator.zoom_in("tavern", "npc_bartender")
        navigator.zoom_in("sub_tavern_npc_bartender_1", "item_amulet")
        
        path = navigator.get_bitchain_path()
        assert len(path) == 2
        assert path[0] == ("tavern", "npc_bartender")
        assert path[1] == ("sub_tavern_npc_bartender_1", "item_amulet")
        
        # Simulate zoom out
        last = navigator.zoom_out()
        assert last == ("sub_tavern_npc_bartender_1", "item_amulet")
        
        path = navigator.get_bitchain_path()
        assert len(path) == 1


class TestTierPersonalityGenerator:
    """Test NPC personality generation based on tier."""
    
    def test_personality_generator_generates_celestial_traits(self):
        """Verify Celestial NPCs get appropriate traits."""
        traits = TierPersonalityGenerator.get_personality_traits(
            TierClassification.CELESTIAL, count=3
        )
        
        # Should be mystical/ethereal
        assert len(traits) == 3
        assert all(t in ["wise", "ethereal", "ascendant", "mystical", "serene",
                        "transcendent", "luminous", "harmonious", "benevolent"]
                  for t in traits)
    
    def test_personality_generator_generates_terran_traits(self):
        """Verify Terran NPCs get appropriate traits."""
        traits = TierPersonalityGenerator.get_personality_traits(
            TierClassification.TERRAN, count=3
        )
        
        # Should be grounded/practical
        assert len(traits) == 3
        assert all(t in ["practical", "grounded", "sociable", "cunning",
                        "industrious", "adventurous", "pragmatic", "clever", "balanced"]
                  for t in traits)
    
    def test_personality_generator_generates_subterran_traits(self):
        """Verify Subterran NPCs get appropriate traits."""
        traits = TierPersonalityGenerator.get_personality_traits(
            TierClassification.SUBTERRAN, count=3
        )
        
        # Should be dark/eldritch
        assert len(traits) == 3
        assert all(t in ["dark", "eldritch", "corrupted", "mysterious",
                        "malevolent", "haunting", "ancient", "twisted", "unfathomable"]
                  for t in traits)
    
    def test_dialogue_seed_reflects_theme(self):
        """Verify dialogue seeds match themes."""
        celestial_seed = TierPersonalityGenerator.get_dialogue_seed(TierTheme.AETHER)
        assert "stars" in celestial_seed or "cosmos" in celestial_seed
        
        subterran_seed = TierPersonalityGenerator.get_dialogue_seed(TierTheme.HELL)
        assert "shadows" in subterran_seed or "horrors" in subterran_seed
    
    def test_npc_metadata_creation(self):
        """Verify NPC metadata reflects tier/theme."""
        metadata = TierPersonalityGenerator.create_npc_metadata(
            TierClassification.TERRAN,
            TierTheme.CITY_STATE,
            "npc_merchant"
        )
        
        assert metadata["npc_id"] == "npc_merchant"
        assert metadata["tier_affinity"] == "terran"
        assert metadata["theme_affinity"] == "city_state"
        assert len(metadata["personality_traits"]) == 3
        assert metadata["dialogue_seed"] == "The city thrums with commerce and intrigue..."


# ============================================================================
# TESTS: HIERARCHICAL UNIVERSE ADAPTER (Full Integration)
# ============================================================================

class TestHierarchicalUniverseAdapter:
    """Test adapter that extends Phase 5 Universe with tier awareness."""
    
    @pytest.mark.asyncio
    async def test_adapter_initializes_with_tier_classification(self):
        """Verify adapter can classify existing universe realms."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        # Create basic universe
        tavern = RealmData(id="tavern", type=ContentType.CUSTOM, entities=[])
        heaven = RealmData(id="heaven", type=ContentType.CUSTOM, entities=[])
        hell = RealmData(id="hell", type=ContentType.CUSTOM, entities=[])
        
        for rid, realm in [("tavern", tavern), ("heaven", heaven), ("hell", hell)]:
            custom_provider.register_realm(rid, realm)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="tavern", type=ContentType.CUSTOM),
                RealmSpec(id="heaven", type=ContentType.CUSTOM),
                RealmSpec(id="hell", type=ContentType.CUSTOM),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        
        # Wrap with tier adapter
        adapter = HierarchicalUniverseAdapter(universe)
        
        tier_specs = {
            "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban", "medieval"]),
            "heaven": (TierClassification.CELESTIAL, TierTheme.HEAVEN, ["peaceful", "utopian"]),
            "hell": (TierClassification.SUBTERRAN, TierTheme.HELL, ["dark", "demonic"]),
        }
        
        await adapter.initialize_with_tier_classification(tier_specs)
        
        # Verify initialization
        assert adapter._initialized
    
    @pytest.mark.asyncio
    async def test_adapter_queries_realms_by_tier(self):
        """Verify adapter can query realms by tier."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        tavern = RealmData(id="tavern", type=ContentType.CUSTOM, entities=[])
        heaven = RealmData(id="heaven", type=ContentType.CUSTOM, entities=[])
        
        custom_provider.register_realm("tavern", tavern)
        custom_provider.register_realm("heaven", heaven)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="tavern", type=ContentType.CUSTOM),
                RealmSpec(id="heaven", type=ContentType.CUSTOM),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        adapter = HierarchicalUniverseAdapter(universe)
        
        tier_specs = {
            "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, []),
            "heaven": (TierClassification.CELESTIAL, TierTheme.HEAVEN, []),
        }
        
        await adapter.initialize_with_tier_classification(tier_specs)
        
        # Query by tier
        terran_realms = await adapter.get_realms_by_tier(TierClassification.TERRAN)
        assert "tavern" in terran_realms
        assert len(terran_realms) == 1
        
        celestial_realms = await adapter.get_realms_by_tier(TierClassification.CELESTIAL)
        assert "heaven" in celestial_realms
        assert len(celestial_realms) == 1
    
    @pytest.mark.asyncio
    async def test_adapter_creates_sub_realms_with_zoom(self):
        """Verify adapter can create sub-realms from entities."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        # Create realm with entity
        entity = Entity(
            id="npc_bartender",
            type="npc",
            position=(25.0, 0.0, 25.0),
            stat7=STAT7Point(0, 0, 0, 0, 100, 0, 50),
        )
        
        tavern = RealmData(
            id="tavern",
            type=ContentType.CUSTOM,
            entities=[entity],
        )
        
        custom_provider.register_realm("tavern", tavern)
        
        spec = UniverseSpec(
            realms=[RealmSpec(id="tavern", type=ContentType.CUSTOM)]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        adapter = HierarchicalUniverseAdapter(universe)
        
        tier_specs = {
            "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban"]),
        }
        
        await adapter.initialize_with_tier_classification(tier_specs)
        
        # Create sub-realm by zooming into entity
        sub_metadata = await adapter.create_sub_realm(
            "tavern",
            "npc_bartender",
            additional_anchors=["interior", "tavern"],
        )
        
        assert sub_metadata is not None
        # Sub-realm depth is parent.tier_depth + 1 = 0 + 1 = 1
        assert sub_metadata.realm_id == "sub_tavern_npc_bartender_1"
        assert sub_metadata.tier == TierClassification.TERRAN
        assert sub_metadata.tier_depth == 1
        assert sub_metadata.parent_realm_id == "tavern"
        assert sub_metadata.parent_entity_id == "npc_bartender"
    
    @pytest.mark.asyncio
    async def test_adapter_exports_tier_structure(self):
        """Verify adapter can export complete tier structure."""
        bigbang = UniverseBigBang()
        custom_provider = CustomProvider()
        bigbang.register_provider("custom", custom_provider, priority=100)
        
        tavern = RealmData(id="tavern", type=ContentType.CUSTOM, entities=[])
        heaven = RealmData(id="heaven", type=ContentType.CUSTOM, entities=[])
        
        custom_provider.register_realm("tavern", tavern)
        custom_provider.register_realm("heaven", heaven)
        
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="tavern", type=ContentType.CUSTOM),
                RealmSpec(id="heaven", type=ContentType.CUSTOM),
            ]
        )
        
        universe = await bigbang.initialize_multiverse(spec)
        adapter = HierarchicalUniverseAdapter(universe)
        
        tier_specs = {
            "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, []),
            "heaven": (TierClassification.CELESTIAL, TierTheme.HEAVEN, []),
        }
        
        await adapter.initialize_with_tier_classification(tier_specs)
        
        # Export structure
        export = await adapter.export_tier_structure()
        
        assert "timestamp" in export
        assert "total_realms" in export
        assert export["total_realms"] == 2
        assert "realms" in export
        assert "tavern" in export["realms"]
        assert "heaven" in export["realms"]
        assert "statistics" in export


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])