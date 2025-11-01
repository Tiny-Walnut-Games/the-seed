"""
Phase 5: Procedural Universe Initialization (The BigBang) with Torus Cycle Refresh

Tests the complete Phase 5 system:
1. BigBang initialization — first orbit instantiates entire multiverse
2. Torus cycle mechanics — realms refresh on each orbital pass
3. Lineage increment — STAT7 temporal dimension shifts across orbits
4. Narrative enrichment — each cycle adds coherence, depth, and lore
5. Contradiction resolution — histories realigned during event horizon passage
6. Provider orchestration — MetVanDamn (3D), Custom (hand-crafted), Arcade (2D)

THE WARBLER SINGULARITY MODEL:
    At the heart of the-seed lies the Warbler singularity — a pulsar-like
    orchestrator that both emits data (dialogue, narratives) and attracts it back
    (narrative pull, coherence). Around it spins a torus event horizon that
    refreshes realms on each orbital pass. Realms (MetVanDamn worlds, custom
    content, arcade cabinets) orbit as sprinkles on the torus surface.
    
    Each cycle through the event horizon:
    - Lineage increments (STAT7 temporal dimension)
    - Stories deepen (narrative enrichment)
    - Contradictions reconcile (history realignment)
    - Realms emerge richer ("tastier than before")

Scenario: First Warbler boot triggers BigBang:
    - Orbit 0 (BigBang): Multiple providers generate initial realm content
      * MetVanDamn procedurally generates 3D MetroidVania worlds
      * Custom provider registers hand-crafted content
      * Arcade provider creates 2D game cabinets in 3D space
    - Torus spin begins: realms orbit around singularity
    - Orbit 1+: Each pass through event horizon enriches content
      * New dialogue generated contextually
      * Quest histories deepened
      * NPC relationships evolved
      * Lore contradictions detected and reconciled

Test Markers: @pytest.mark.exp05 (Phase 5 feature integration)
Test Count: 15+ comprehensive test cases covering all torus mechanics
"""

import pytest
import asyncio
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

# Add web/server to path for potential future integration
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))


# ============================================================================
# ENUMS AND DOMAIN MODELS
# ============================================================================

class ContentType(Enum):
    """Type of content a realm contains."""
    METVAN_3D = "metvan_3d"
    CUSTOM = "custom"
    ARCADE_2D = "arcade_2d"
    UNKNOWN = "unknown"


class StoryElement(Enum):
    """Types of narrative elements that can be enriched."""
    DIALOGUE = "dialogue"
    QUEST = "quest"
    NPC_HISTORY = "npc_history"
    CONTRADICTION = "contradiction"
    LORE = "lore"


@dataclass
class STAT7Point:
    """
    7-dimensional coordinate in STAT7 address space.
    
    Dimensions:
    - realm: Realm identifier (0 to 2^32-1)
    - lineage: Temporal lineage / orbit number (-inf to +inf, increments on refresh)
    - adjacency: Spatial adjacency index (0 to n)
    - horizon: Perceptual boundary / event horizon crossing (0 to horizon_max)
    - resonance: Harmonic frequency / narrative frequency (0 to 1000)
    - velocity: Change rate / narrative momentum (0 to max_velocity)
    - density: Concentration / entity density (0 to max_density)
    """
    realm: int
    lineage: int
    adjacency: int
    horizon: int
    resonance: int
    velocity: int
    density: int

    def __post_init__(self):
        """Validate 7D coordinate bounds."""
        assert 0 <= self.realm < 2**32, f"Realm {self.realm} out of bounds"
        assert -1000000 <= self.lineage <= 1000000, f"Lineage {self.lineage} out of bounds"
        assert self.adjacency >= 0, f"Adjacency {self.adjacency} must be non-negative"

    def advance_orbit(self) -> "STAT7Point":
        """Create next orbit coordinate (increment lineage, reset horizon)."""
        return STAT7Point(
            realm=self.realm,
            lineage=self.lineage + 1,
            adjacency=self.adjacency,
            horizon=0,
            resonance=self.resonance,
            velocity=self.velocity,
            density=self.density
        )

    def to_dict(self) -> Dict[str, int]:
        """Serialize to dictionary."""
        return {
            "realm": self.realm,
            "lineage": self.lineage,
            "adjacency": self.adjacency,
            "horizon": self.horizon,
            "resonance": self.resonance,
            "velocity": self.velocity,
            "density": self.density
        }


@dataclass
class Entity:
    """
    Game entity in STAT7 space.
    
    An entity is any object, NPC, or interactive element in the multiverse.
    Each entity occupies a unique STAT7 coordinate.
    """
    id: str
    type: str
    position: Tuple[float, float, float]
    stat7: STAT7Point
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_orbit: int = 0
    enrichment_count: int = 0

    def enrich(self, enrichment_type: StoryElement, data: Any) -> None:
        """Apply narrative enrichment during torus cycle."""
        if "enrichments" not in self.metadata:
            self.metadata["enrichments"] = []
        
        self.metadata["enrichments"].append({
            "type": enrichment_type.value,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        self.enrichment_count += 1

    def advance_to_orbit(self, new_orbit: int, new_stat7: STAT7Point) -> None:
        """Advance entity to next orbit with new STAT7 coordinate."""
        self.stat7 = new_stat7
        self.metadata["last_orbit_update"] = new_orbit


@dataclass
class RealmSpec:
    """Specification for a realm to generate or register."""
    id: str
    type: ContentType
    seed: int = 42
    size_extents: Tuple[float, float, float] = (100.0, 100.0, 100.0)
    district_count: int = 10
    biome_fade_distance: float = 5.0
    available_games: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RealmData:
    """
    Generated or registered realm content.
    
    A realm is a coherent collection of entities, each with STAT7 coordinates.
    """
    id: str
    type: ContentType
    entities: List[Entity] = field(default_factory=list)
    physics_constants: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    orbit: int = 0
    lineage: int = 0
    enrichments_applied: List[Tuple[int, StoryElement]] = field(default_factory=list)

    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Retrieve entity by ID."""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None

    def enrich_realm(self, enrichment_type: StoryElement, scope: str = "global") -> None:
        """Apply realm-wide enrichment."""
        self.enrichments_applied.append((self.orbit, enrichment_type))
        
        if scope == "global":
            # Enrich all entities in realm
            for entity in self.entities:
                entity.enrich(enrichment_type, {"scope": "global", "orbit": self.orbit})
        elif scope == "startswith":
            # Enrich specific subset
            for entity in self.entities:
                if entity.type.startswith("npc"):
                    entity.enrich(enrichment_type, {"scope": "npcs", "orbit": self.orbit})


@dataclass
class UniverseSpec:
    """Complete multiverse specification for BigBang initialization."""
    realms: List[RealmSpec] = field(default_factory=list)
    physics: Dict[str, float] = field(default_factory=dict)
    extents: Tuple[float, float, float] = (1000.0, 1000.0, 1000.0)
    cycle_duration_ms: float = 100.0  # How long each orbit cycle takes


@dataclass
class Universe:
    """
    Initialized multiverse.
    
    The Universe is the result of BigBang initialization plus torus cycles.
    It maintains all realms, their current orbit state, and enrichment history.
    """
    realms: Dict[str, RealmData] = field(default_factory=dict)
    physics_constants: Dict[str, float] = field(default_factory=dict)
    stat7_grid: Any = None
    current_orbit: int = 0
    total_orbits_completed: int = 0
    initialized_at: datetime = field(default_factory=datetime.now)
    initialization_time_ms: float = 0.0
    cycle_history: List[Dict[str, Any]] = field(default_factory=list)

    def advance_orbit(self) -> None:
        """Advance universe to next orbit (torus spin)."""
        self.current_orbit += 1
        self.total_orbits_completed += 1
        
        # Update all realm lineages
        for realm_id, realm in self.realms.items():
            realm.orbit = self.current_orbit
            realm.lineage += 1
            
            # Update all entity STAT7 coordinates
            for entity in realm.entities:
                new_stat7 = entity.stat7.advance_orbit()
                entity.advance_to_orbit(self.current_orbit, new_stat7)
        
        self.cycle_history.append({
            "orbit": self.current_orbit,
            "timestamp": datetime.now().isoformat(),
            "realms_updated": len(self.realms)
        })


# ============================================================================
# PROVIDER INTERFACE (Abstract Contract)
# ============================================================================

class ContentProvider(ABC):
    """
    Abstract interface for universe content providers.
    
    Implementations can provide 3D procedural content (MetVanDamn),
    hand-crafted realms (Custom), 2D arcade games (Arcade), or any
    future content type.
    """

    @abstractmethod
    def can_generate_realm(self, realm_spec: RealmSpec) -> bool:
        """Check if this provider can handle a realm type."""
        pass

    @abstractmethod
    async def generate_realm_content(self, realm_spec: RealmSpec) -> RealmData:
        """Generate/load/register content for a realm."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Human-readable provider name."""
        pass


# ============================================================================
# CONCRETE PROVIDERS (Test Implementations)
# ============================================================================

class MockMetVanDamnProvider(ContentProvider):
    """
    Mock MetVanDamn provider.
    
    Simulates procedural 3D MetroidVania world generation via Wave Function Collapse.
    Generates districts with biome distribution.
    """

    def can_generate_realm(self, realm_spec: RealmSpec) -> bool:
        return realm_spec.type == ContentType.METVAN_3D

    async def generate_realm_content(self, realm_spec: RealmSpec) -> RealmData:
        """Simulate MetVanDamn 3D world generation."""
        # Simulate procedural generation
        await asyncio.sleep(0.05)  # Simulate ~200ms actual generation
        
        entities = []
        
        # Generate districts
        for i in range(realm_spec.district_count):
            stat7 = STAT7Point(
                realm=hash(realm_spec.id) % (2**32),
                lineage=0,
                adjacency=i,
                horizon=0,
                resonance=500 + (i * 10),
                velocity=0,
                density=100 + (i * 5)
            )
            
            entities.append(
                Entity(
                    id=f"district_{i}",
                    type="district",
                    position=(i * 10.0, 0.0, 0.0),
                    stat7=stat7,
                    metadata={
                        "district_index": i,
                        "biome": "testbiome",
                        "wfc_seed": realm_spec.seed + i
                    },
                    created_at_orbit=0
                )
            )
        
        # Generate some NPCs in the first district
        for j in range(3):
            stat7 = STAT7Point(
                realm=hash(realm_spec.id) % (2**32),
                lineage=0,
                adjacency=100 + j,
                horizon=0,
                resonance=600,
                velocity=1,
                density=10
            )
            
            entities.append(
                Entity(
                    id=f"npc_metvan_{j}",
                    type="npc_merchant",
                    position=(0.0 + j * 2.0, 0.5, 0.0),
                    stat7=stat7,
                    metadata={"npc_role": "merchant", "personality": "gruff"},
                    created_at_orbit=0
                )
            )

        return RealmData(
            id=realm_spec.id,
            type=ContentType.METVAN_3D,
            entities=entities,
            physics_constants={"gravity": 9.8, "air_resistance": 0.02},
            metadata={"generated_by": "MetVanDamnProvider", "generation_time_ms": 200},
            orbit=0,
            lineage=0
        )

    def get_provider_name(self) -> str:
        return "MetVanDamnProvider"


class MockCustomProvider(ContentProvider):
    """
    Mock custom content provider.
    
    Allows developers to register pre-generated realms without procedural generation.
    """

    def __init__(self):
        self.custom_realms: Dict[str, RealmData] = {}

    def can_generate_realm(self, realm_spec: RealmSpec) -> bool:
        return realm_spec.type == ContentType.CUSTOM and realm_spec.id in self.custom_realms

    async def generate_realm_content(self, realm_spec: RealmSpec) -> RealmData:
        if realm_spec.id in self.custom_realms:
            return self.custom_realms[realm_spec.id]
        raise ValueError(f"Custom realm '{realm_spec.id}' not registered")

    def register_realm(self, realm_id: str, realm_data: RealmData) -> None:
        """Register a pre-generated realm."""
        self.custom_realms[realm_id] = realm_data

    def get_provider_name(self) -> str:
        return "CustomProvider"


class MockArcadeProvider(ContentProvider):
    """
    Mock arcade cabinet provider.
    
    Creates 2D arcade game cabinets as interactive entities in 3D space.
    Each cabinet can host a registered 2D game.
    """

    def __init__(self):
        self.arcade_games: Dict[str, Dict[str, Any]] = {}

    def can_generate_realm(self, realm_spec: RealmSpec) -> bool:
        return realm_spec.type == ContentType.ARCADE_2D

    async def generate_realm_content(self, realm_spec: RealmSpec) -> RealmData:
        """Create arcade lounge with cabinet entities."""
        await asyncio.sleep(0.02)  # Simulate generation
        
        cabinets = []
        
        for idx, game_id in enumerate(realm_spec.available_games):
            stat7 = STAT7Point(
                realm=hash(realm_spec.id) % (2**32),
                lineage=0,
                adjacency=idx,
                horizon=0,
                resonance=700,
                velocity=0,
                density=50
            )
            
            cabinets.append(
                Entity(
                    id=f"cabinet_{idx}",
                    type="arcade_cabinet",
                    position=(idx * 3.0, 0.0, 0.0),
                    stat7=stat7,
                    metadata={"game_id": game_id, "score_high": 0},
                    created_at_orbit=0
                )
            )

        return RealmData(
            id=realm_spec.id,
            type=ContentType.ARCADE_2D,
            entities=cabinets,
            metadata={"cabinet_count": len(cabinets)},
            orbit=0,
            lineage=0
        )

    def register_arcade_game(self, game_id: str, game_data: Dict[str, Any]) -> None:
        """Register a 2D arcade game."""
        self.arcade_games[game_id] = game_data

    def get_provider_name(self) -> str:
        return "ArcadeProvider"


# ============================================================================
# TORUS CYCLE ENGINE (Realm Refresh Mechanics)
# ============================================================================

class TorusCycleEngine:
    """
    Orchestrates realm refresh cycles through the event horizon.
    
    On each cycle:
    1. Realms orbit around singularity
    2. Entity STAT7 coordinates update (lineage increment)
    3. Narrative enrichment applied
    4. Contradictions resolved
    5. Lore deepens
    """

    def __init__(self):
        self.enrichment_handlers: Dict[StoryElement, callable] = {
            StoryElement.DIALOGUE: self._enrich_dialogue,
            StoryElement.QUEST: self._enrich_quest,
            StoryElement.NPC_HISTORY: self._enrich_npc_history,
            StoryElement.CONTRADICTION: self._resolve_contradiction,
            StoryElement.LORE: self._enrich_lore,
        }

    async def execute_torus_cycle(
        self, universe: Universe, enrichment_types: List[StoryElement]
    ) -> None:
        """Execute one complete torus cycle (event horizon passage)."""
        logger.info(f"🌀 TORUS CYCLE {universe.current_orbit} → {universe.current_orbit + 1}: "
                   f"Event horizon passage for {len(universe.realms)} realms")
        
        # Apply enrichments
        for enrichment_type in enrichment_types:
            for realm_id, realm in universe.realms.items():
                realm.enrich_realm(enrichment_type)
                logger.info(f"  ✓ Enriched realm '{realm_id}' with {enrichment_type.value}")
        
        # Advance orbit (lineage increment)
        universe.advance_orbit()
        logger.info(f"✅ TORUS CYCLE complete: Orbits={universe.total_orbits_completed}, "
                   f"Current lineage={universe.realms[list(universe.realms.keys())[0]].lineage}")

    def _enrich_dialogue(self, realm: RealmData) -> None:
        """Generate new dialogue during cycle."""
        for entity in realm.entities:
            if entity.type.startswith("npc"):
                entity.enrich(
                    StoryElement.DIALOGUE,
                    {"new_dialogue": f"I've seen much since last we spoke... (orbit {realm.orbit})"}
                )

    def _enrich_quest(self, realm: RealmData) -> None:
        """Evolve quest lines."""
        entity = realm.get_entity_by_id("npc_metvan_0")
        if entity:
            entity.enrich(
                StoryElement.QUEST,
                {"quest_progress": "escalated", "orbit": realm.orbit}
            )

    def _enrich_npc_history(self, realm: RealmData) -> None:
        """Deepen NPC-player relationships."""
        for entity in realm.entities:
            if entity.type.startswith("npc"):
                entity.enrich(
                    StoryElement.NPC_HISTORY,
                    {"relationship_depth": entity.enrichment_count * 0.1, "orbit": realm.orbit}
                )

    def _resolve_contradiction(self, realm: RealmData) -> None:
        """Detect and reconcile narrative contradictions."""
        # Simplified: mark contradiction as resolved
        for entity in realm.entities:
            if "contradictions" in entity.metadata:
                entity.metadata["contradictions_resolved"] = True

    def _enrich_lore(self, realm: RealmData) -> None:
        """Deepen world lore and history."""
        realm.metadata.setdefault("lore_depth", 0)
        realm.metadata["lore_depth"] += 0.1


# ============================================================================
# BIGBANG COORDINATOR (Main Orchestrator)
# ============================================================================

class UniverseBigBang:
    """
    Procedurally initializes entire multiverse on first boot.
    
    The BigBang is the first orbit — it uses all available providers
    to populate realms instantaneously. After BigBang, the torus cycle
    engine keeps realms fresh through continuous refresh.
    """

    def __init__(self):
        self.providers: Dict[str, ContentProvider] = {}

    def register_provider(self, name: str, provider: ContentProvider) -> None:
        """Register a content provider."""
        self.providers[name] = provider
        logger.info(f"📦 Registered content provider: {name}")

    def _select_provider(self, realm_spec: RealmSpec) -> ContentProvider:
        """Choose provider based on realm type."""
        for provider in self.providers.values():
            if provider.can_generate_realm(realm_spec):
                return provider
        raise ValueError(f"No provider available for realm type '{realm_spec.type}'")

    async def initialize_multiverse(self, universe_spec: UniverseSpec) -> Universe:
        """
        MAIN ENTRY POINT: Generate entire multiverse (BigBang - Orbit 0).
        
        Invokes all providers in sequence to populate realms with initial content.
        Each realm is assigned STAT7 coordinates. After BigBang completes,
        the torus cycle engine can refresh realms on demand.
        """
        logger.info("🌌 BIGBANG: Initializing multiverse (Orbit 0)...")
        start_time = datetime.now()

        universe = Universe(
            physics_constants=universe_spec.physics,
            stat7_grid={"dimensions": 7}  # Simplified for testing
        )

        for realm_spec in universe_spec.realms:
            try:
                provider = self._select_provider(realm_spec)
                logger.info(
                    f"🌍 Generating realm '{realm_spec.id}' "
                    f"via {provider.get_provider_name()}"
                )

                realm_data = await provider.generate_realm_content(realm_spec)
                universe.realms[realm_spec.id] = realm_data

                logger.info(
                    f"✅ Realm '{realm_spec.id}' initialized: "
                    f"{len(realm_data.entities)} entities, "
                    f"Lineage={realm_data.lineage}"
                )
            except Exception as e:
                logger.error(f"❌ Failed to initialize realm '{realm_spec.id}': {e}")
                raise

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        universe.initialization_time_ms = elapsed
        logger.info(f"🌌 BIGBANG complete: {len(universe.realms)} realms "
                   f"initialized in {elapsed:.1f}ms")
        return universe


# ============================================================================
# TESTS — THE SCROLLS
# ============================================================================

class TestPhase5BigBangInitialization:
    """Test BigBang initialization — Orbit 0."""

    @pytest.fixture
    def bigbang(self) -> UniverseBigBang:
        """Set up BigBang coordinator with mock providers."""
        bb = UniverseBigBang()
        bb.register_provider("metvan_3d", MockMetVanDamnProvider())
        bb.register_provider("custom", MockCustomProvider())
        bb.register_provider("arcade", MockArcadeProvider())
        return bb

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_bigbang_initializes_empty_multiverse(self, bigbang):
        """Verify BigBang handles empty universe spec."""
        spec = UniverseSpec(realms=[])
        universe = await bigbang.initialize_multiverse(spec)

        assert len(universe.realms) == 0
        assert universe.initialization_time_ms >= 0
        assert universe.current_orbit == 0
        logger.info("✅ Empty multiverse initialization passed")

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_bigbang_with_metvandamn_provider(self, bigbang):
        """Verify MetVanDamn provider generates 3D worlds."""
        spec = UniverseSpec(
            realms=[
                RealmSpec(
                    id="sol_system",
                    type=ContentType.METVAN_3D,
                    seed=42,
                    district_count=5
                )
            ]
        )

        universe = await bigbang.initialize_multiverse(spec)

        assert len(universe.realms) == 1
        assert "sol_system" in universe.realms
        
        realm = universe.realms["sol_system"]
        assert len(realm.entities) >= 5  # At least districts
        assert realm.lineage == 0  # First orbit
        assert realm.orbit == 0
        
        # Verify STAT7 coordinates are assigned
        for entity in realm.entities[:3]:
            assert entity.stat7.realm != 0
            assert entity.stat7.lineage == 0
            assert entity.stat7.adjacency >= 0
        
        logger.info("✅ MetVanDamn provider integration passed")

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_bigbang_with_custom_provider(self, bigbang):
        """Verify custom provider registers hand-crafted realms."""
        custom_provider = bigbang.providers["custom"]
        
        # Pre-register a custom realm
        custom_stat7 = STAT7Point(
            realm=999, lineage=0, adjacency=0, horizon=0,
            resonance=800, velocity=0, density=50
        )
        custom_realm = RealmData(
            id="custom_arena",
            type=ContentType.CUSTOM,
            entities=[
                Entity(
                    id="boss_entity",
                    type="boss",
                    position=(0.0, 0.0, 0.0),
                    stat7=custom_stat7
                )
            ]
        )
        custom_provider.register_realm("custom_arena", custom_realm)

        spec = UniverseSpec(
            realms=[
                RealmSpec(id="custom_arena", type=ContentType.CUSTOM)
            ]
        )

        universe = await bigbang.initialize_multiverse(spec)

        assert "custom_arena" in universe.realms
        assert len(universe.realms["custom_arena"].entities) == 1
        assert universe.realms["custom_arena"].entities[0].type == "boss"
        logger.info("✅ Custom provider integration passed")

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_bigbang_with_arcade_provider(self, bigbang):
        """Verify arcade provider creates 2D game cabinets in 3D space."""
        arcade_provider = bigbang.providers["arcade"]
        arcade_provider.register_arcade_game(
            "goblin_eater_v1",
            {"name": "Goblin Eater", "binary": "./games/goblin.exe"}
        )

        spec = UniverseSpec(
            realms=[
                RealmSpec(
                    id="arcade_lounge",
                    type=ContentType.ARCADE_2D,
                    available_games=["goblin_eater_v1"]
                )
            ]
        )

        universe = await bigbang.initialize_multiverse(spec)

        assert "arcade_lounge" in universe.realms
        cabinets = universe.realms["arcade_lounge"].entities
        assert len(cabinets) == 1
        assert cabinets[0].type == "arcade_cabinet"
        assert cabinets[0].stat7.lineage == 0
        logger.info("✅ Arcade provider integration passed")

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_bigbang_mixed_providers(self, bigbang):
        """Verify BigBang orchestrates multiple providers simultaneously."""
        custom_provider = bigbang.providers["custom"]
        custom_provider.register_realm(
            "custom_dungeon",
            RealmData(
                id="custom_dungeon",
                type=ContentType.CUSTOM,
                entities=[]
            )
        )

        arcade_provider = bigbang.providers["arcade"]
        arcade_provider.register_arcade_game(
            "pac_man_clone",
            {"name": "Goblin Eater", "binary": "./games/goblin.exe"}
        )

        spec = UniverseSpec(
            realms=[
                RealmSpec(
                    id="overworld",
                    type=ContentType.METVAN_3D,
                    district_count=8
                ),
                RealmSpec(id="custom_dungeon", type=ContentType.CUSTOM),
                RealmSpec(
                    id="tavern_arcade",
                    type=ContentType.ARCADE_2D,
                    available_games=["pac_man_clone"]
                ),
            ]
        )

        universe = await bigbang.initialize_multiverse(spec)

        assert len(universe.realms) == 3
        assert "overworld" in universe.realms
        assert "custom_dungeon" in universe.realms
        assert "tavern_arcade" in universe.realms
        
        # Verify lineages are consistent
        for realm_id, realm in universe.realms.items():
            assert realm.lineage == 0
            assert realm.orbit == 0
        
        logger.info("✅ Mixed provider orchestration passed")

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_bigbang_fails_on_unknown_realm_type(self, bigbang):
        """Verify BigBang raises error for unsupported realm types."""
        spec = UniverseSpec(
            realms=[
                RealmSpec(id="unknown_realm", type=ContentType.UNKNOWN)
            ]
        )

        with pytest.raises(ValueError) as exc_info:
            await bigbang.initialize_multiverse(spec)

        assert "No provider available" in str(exc_info.value)
        logger.info("✅ Error handling for unknown realm types passed")


class TestPhase5TorusCycleMechanics:
    """Test torus cycle refresh mechanics — realms evolve across orbits."""

    @pytest.fixture
    def universe_after_bigbang(self) -> Universe:
        """Fixture: Create a multiverse after BigBang."""
        # This is a mock universe for testing torus cycles
        return Universe(
            realms={
                "test_realm": RealmData(
                    id="test_realm",
                    type=ContentType.METVAN_3D,
                    entities=[
                        Entity(
                            id="npc_test_1",
                            type="npc_merchant",
                            position=(0.0, 0.0, 0.0),
                            stat7=STAT7Point(
                                realm=1, lineage=0, adjacency=0, horizon=0,
                                resonance=500, velocity=0, density=10
                            ),
                            created_at_orbit=0
                        )
                    ],
                    orbit=0,
                    lineage=0
                )
            },
            current_orbit=0
        )

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_torus_cycle_increments_lineage(self, universe_after_bigbang):
        """Verify torus cycle increments STAT7 lineage dimension."""
        engine = TorusCycleEngine()
        
        initial_lineage = universe_after_bigbang.realms["test_realm"].lineage
        assert initial_lineage == 0
        
        # Execute one torus cycle
        await engine.execute_torus_cycle(
            universe_after_bigbang,
            enrichment_types=[StoryElement.DIALOGUE]
        )
        
        final_lineage = universe_after_bigbang.realms["test_realm"].lineage
        assert final_lineage == 1
        assert universe_after_bigbang.current_orbit == 1
        logger.info("✅ Lineage increment passed")

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_torus_cycle_updates_stat7_coordinates(self, universe_after_bigbang):
        """Verify entity STAT7 coordinates update on orbit advance."""
        realm = universe_after_bigbang.realms["test_realm"]
        entity = realm.entities[0]
        
        initial_lineage = entity.stat7.lineage
        assert initial_lineage == 0
        
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe_after_bigbang,
            enrichment_types=[StoryElement.DIALOGUE]
        )
        
        final_lineage = entity.stat7.lineage
        assert final_lineage == 1
        logger.info("✅ STAT7 coordinate update passed")

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_torus_cycle_applies_enrichment(self, universe_after_bigbang):
        """Verify narrative enrichment applied during cycle."""
        realm = universe_after_bigbang.realms["test_realm"]
        entity = realm.entities[0]
        
        initial_enrichment_count = entity.enrichment_count
        assert initial_enrichment_count == 0
        
        engine = TorusCycleEngine()
        await engine.execute_torus_cycle(
            universe_after_bigbang,
            enrichment_types=[StoryElement.DIALOGUE, StoryElement.NPC_HISTORY]
        )
        
        # Entity should have enrichments applied
        assert entity.enrichment_count > initial_enrichment_count
        assert "enrichments" in entity.metadata
        logger.info("✅ Narrative enrichment passed")

    @pytest.mark.exp05
    @pytest.mark.asyncio
    async def test_multiple_torus_cycles(self, universe_after_bigbang):
        """Verify multiple torus cycles accumulate enrichment."""
        engine = TorusCycleEngine()
        
        # Execute 3 cycles
        for cycle_num in range(3):
            await engine.execute_torus_cycle(
                universe_after_bigbang,
                enrichment_types=[
                    StoryElement.DIALOGUE,
                    StoryElement.LORE,
                    StoryElement.NPC_HISTORY
                ]
            )
        
        realm = universe_after_bigbang.realms["test_realm"]
        assert realm.lineage == 3
        assert universe_after_bigbang.total_orbits_completed == 3
        
        entity = realm.entities[0]
        assert entity.enrichment_count > 0
        logger.info("✅ Multiple cycles passed")

    @pytest.mark.exp05
    def test_stat7_point_advance_orbit(self):
        """Verify STAT7Point.advance_orbit() mechanics."""
        point_orbit_0 = STAT7Point(
            realm=42, lineage=0, adjacency=5, horizon=1,
            resonance=600, velocity=2, density=15
        )
        
        point_orbit_1 = point_orbit_0.advance_orbit()
        
        assert point_orbit_1.realm == 42  # Unchanged
        assert point_orbit_1.lineage == 1  # Incremented
        assert point_orbit_1.adjacency == 5  # Unchanged
        assert point_orbit_1.horizon == 0  # Reset
        logger.info("✅ STAT7 advance_orbit passed")


class TestPhase5NarrativeEnrichment:
    """Test narrative enrichment and contradiction resolution."""

    @pytest.fixture
    def enriched_realm(self) -> RealmData:
        """Fixture: Create a realm ready for enrichment."""
        return RealmData(
            id="enrichment_test",
            type=ContentType.METVAN_3D,
            entities=[
                Entity(
                    id="npc_rich",
                    type="npc_scholar",
                    position=(0.0, 0.0, 0.0),
                    stat7=STAT7Point(
                        realm=1, lineage=0, adjacency=0, horizon=0,
                        resonance=700, velocity=0, density=5
                    )
                )
            ],
            orbit=0,
            lineage=0
        )

    @pytest.mark.exp05
    def test_entity_enrichment_tracking(self, enriched_realm):
        """Verify entities track enrichment history."""
        entity = enriched_realm.entities[0]
        
        assert entity.enrichment_count == 0
        assert "enrichments" not in entity.metadata
        
        entity.enrich(StoryElement.DIALOGUE, {"text": "Hello, friend!"})
        
        assert entity.enrichment_count == 1
        assert "enrichments" in entity.metadata
        assert len(entity.metadata["enrichments"]) == 1
        
        entity.enrich(StoryElement.NPC_HISTORY, {"relationship": "friendly"})
        
        assert entity.enrichment_count == 2
        assert len(entity.metadata["enrichments"]) == 2
        logger.info("✅ Entity enrichment tracking passed")

    @pytest.mark.exp05
    def test_realm_wide_enrichment(self, enriched_realm):
        """Verify realm-wide enrichment applies to all entities."""
        enriched_realm.enrich_realm(StoryElement.LORE, scope="global")
        
        for entity in enriched_realm.entities:
            assert entity.enrichment_count > 0
        
        # Add more entities and test selective enrichment
        enriched_realm.entities.append(
            Entity(
                id="npc_merchant",
                type="npc_merchant",
                position=(1.0, 0.0, 0.0),
                stat7=STAT7Point(
                    realm=1, lineage=0, adjacency=1, horizon=0,
                    resonance=600, velocity=0, density=5
                )
            )
        )
        
        initial_merchant_count = enriched_realm.entities[1].enrichment_count
        enriched_realm.enrich_realm(StoryElement.QUEST, scope="startswith")
        
        # NPCs should be enriched
        for entity in enriched_realm.entities:
            if entity.type.startswith("npc"):
                assert entity.enrichment_count > 0
        
        logger.info("✅ Realm-wide enrichment passed")

    @pytest.mark.exp05
    def test_enrichment_creates_audit_trail(self, enriched_realm):
        """Verify enrichments create audit trail for debugging."""
        entity = enriched_realm.entities[0]
        
        entity.enrich(StoryElement.DIALOGUE, {"turn": 1})
        entity.enrich(StoryElement.NPC_HISTORY, {"turns_spoken": 5})
        
        enrichments = entity.metadata["enrichments"]
        assert len(enrichments) == 2
        
        assert enrichments[0]["type"] == "dialogue"
        assert enrichments[0]["data"]["turn"] == 1
        assert "timestamp" in enrichments[0]
        
        logger.info("✅ Enrichment audit trail passed")


class TestPhase5ProviderContract:
    """Test provider interface contract and behavior."""

    @pytest.mark.exp05
    def test_provider_registration(self):
        """Verify providers can be registered and retrieved."""
        bigbang = UniverseBigBang()
        
        metvan = MockMetVanDamnProvider()
        custom = MockCustomProvider()
        arcade = MockArcadeProvider()
        
        bigbang.register_provider("metvan_3d", metvan)
        bigbang.register_provider("custom", custom)
        bigbang.register_provider("arcade", arcade)
        
        assert "metvan_3d" in bigbang.providers
        assert "custom" in bigbang.providers
        assert "arcade" in bigbang.providers
        
        assert bigbang.providers["metvan_3d"].get_provider_name() == "MetVanDamnProvider"
        logger.info("✅ Provider registration passed")

    @pytest.mark.exp05
    def test_provider_can_handle_realm_type(self):
        """Verify provider filtering by realm type."""
        metvan = MockMetVanDamnProvider()
        custom = MockCustomProvider()
        arcade = MockArcadeProvider()
        
        assert metvan.can_generate_realm(
            RealmSpec(id="test", type=ContentType.METVAN_3D)
        )
        assert not metvan.can_generate_realm(
            RealmSpec(id="test", type=ContentType.CUSTOM)
        )
        
        assert not custom.can_generate_realm(
            RealmSpec(id="test", type=ContentType.METVAN_3D)
        )
        
        assert arcade.can_generate_realm(
            RealmSpec(id="test", type=ContentType.ARCADE_2D)
        )
        logger.info("✅ Provider filtering passed")


class TestPhase5STAT7Integration:
    """Test STAT7 7D addressing across multiverse."""

    @pytest.mark.exp05
    def test_stat7_point_construction_and_validation(self):
        """Verify STAT7 coordinates are properly constructed."""
        point = STAT7Point(
            realm=42, lineage=5, adjacency=10, horizon=2,
            resonance=600, velocity=1, density=20
        )
        
        assert point.realm == 42
        assert point.lineage == 5
        assert point.adjacency == 10
        assert point.horizon == 2
        assert point.resonance == 600
        assert point.velocity == 1
        assert point.density == 20
        
        # Verify serialization
        as_dict = point.to_dict()
        assert as_dict["realm"] == 42
        assert as_dict["lineage"] == 5
        logger.info("✅ STAT7 construction passed")

    @pytest.mark.exp05
    def test_stat7_coordinates_unique_per_entity(self):
        """Verify each entity in realm has unique STAT7 coordinate."""
        stat7_coords = []
        
        for i in range(5):
            coord = STAT7Point(
                realm=1, lineage=0, adjacency=i, horizon=0,
                resonance=500, velocity=0, density=10 + i
            )
            stat7_coords.append(coord.to_dict())
        
        # Check adjacency uniqueness
        adjacencies = [c["adjacency"] for c in stat7_coords]
        assert len(set(adjacencies)) == len(adjacencies)
        logger.info("✅ STAT7 uniqueness passed")


# ============================================================================
# PYTEST MARKERS & MODULE SETUP
# ============================================================================

pytestmark = pytest.mark.exp05


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])