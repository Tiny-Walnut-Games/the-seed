"""
Phase 6: Unified End-to-End Orchestrator

Wires together Phase 5 (procedural generation) → Bridge (Phase 2-4 integration) 
→ University demo with single command entry point.

The orchestrator:
1. Initializes Phase 5 universe with seed-based providers
2. Runs Torus enrichment cycles (narrative depth)
3. Bridges to Phase 2-4 (NPCs, semantic search, dialogue)
4. Returns reproducible metadata for demo
5. Can export universe for reproducibility

This is Phase 6 - the glue layer that makes everything interactive.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from phase5_bigbang import (
    UniverseBigBang, UniverseSpec, RealmSpec, ContentType, 
    TorusCycleEngine, StoryElement, Universe
)
from phase5_to_phase2_bridge import (
    integrate_phase5_universe,
    Phase5Phase2Phase3Phase4Bridge
)

logger = logging.getLogger(__name__)


# ============================================================================
# DEMO ORCHESTRATOR (Main Entry Point)
# ============================================================================

@dataclass
class OrchestratorConfig:
    """Configuration for university demo orchestrator."""
    seed: int = 42
    orbits: int = 3
    realms: List[str] = None
    enrichment_types: List[StoryElement] = None
    
    def __post_init__(self):
        """Set defaults if not provided."""
        if self.realms is None:
            self.realms = ["overworld", "tavern"]
        if self.enrichment_types is None:
            self.enrichment_types = [
                StoryElement.DIALOGUE,
                StoryElement.NPC_HISTORY,
                StoryElement.QUEST
            ]


@dataclass
class DemoUniverseMetadata:
    """Reproducible metadata for universe generation."""
    seed: int
    universe_initialized_at: str
    generation_timestamp: str
    total_orbits_completed: int
    realms: Dict[str, Dict[str, Any]]
    total_entities: int
    initialization_time_ms: float
    
    @property
    def realm_entity_counts(self) -> Dict[str, int]:
        """Get entity counts per realm."""
        return {realm_id: info["entity_count"] for realm_id, info in self.realms.items()}


class UniverseDemoOrchestrator:
    """
    Unified orchestrator for university demo.
    
    Provides a single entry point:
    - Initialize Phase 5 universe with seed
    - Run enrichment cycles
    - Bridge to Phase 2-4
    - Export reproducible metadata
    """
    
    def __init__(self, config: OrchestratorConfig):
        """Initialize orchestrator with configuration."""
        self.config = config
        self.universe: Optional[Universe] = None
        self.bridge: Optional[Phase5Phase2Phase3Phase4Bridge] = None
        self.setup_complete = False
        self._initialization_seed: Optional[int] = None  # Tracked for reproducibility
        logger.info(f"🎯 Orchestrator initialized with seed={config.seed}, orbits={config.orbits}")
    
    async def launch_demo(self) -> DemoUniverseMetadata:
        """
        Launch complete university demo with single call.
        
        Returns reproducible metadata for full system.
        """
        logger.info("🚀 LAUNCHING UNIVERSITY DEMO...")
        
        # Store initialization seed for reproducibility (Phase 6D)
        self._initialization_seed = self.config.seed
        
        try:
            # Step 1: Create Phase 5 universe
            logger.info("📍 Step 1: Initializing Phase 5 multiverse")
            self.universe = await self._initialize_universe()
            
            # Step 2: Run enrichment cycles
            logger.info(f"📍 Step 2: Running {self.config.orbits} Torus cycles")
            await self._run_enrichment_cycles()
            
            # Step 3: Bridge to Phase 2-4
            logger.info("📍 Step 3: Bridging to Phase 2-4 systems")
            self.bridge = await self._integrate_with_phases_2_4()
            
            # Step 4: Produce metadata
            logger.info("📍 Step 4: Generating reproducible metadata")
            metadata = self._produce_metadata()
            
            self.setup_complete = True
            logger.info("✅ UNIVERSITY DEMO LAUNCH COMPLETE")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Demo launch failed: {e}")
            raise
    
    async def _initialize_universe(self) -> Universe:
        """Initialize Phase 5 universe with seed-based realm generation."""
        bigbang = UniverseBigBang()
        
        # Register all needed providers
        from phase5_providers import MetVanDamnProvider, CustomProvider, ArcadeProvider
        from phase5_bigbang import RealmData
        
        bigbang.register_provider("metvan", MetVanDamnProvider(), priority=100)
        bigbang.register_provider("arcade", ArcadeProvider(), priority=95)
        
        # Pre-register custom provider with realms
        custom_provider = CustomProvider()
        for realm_id in self.config.realms:
            if self._infer_realm_type(realm_id) == ContentType.CUSTOM:
                # Pre-register custom realms so provider can return them
                custom_realm = RealmData(
                    id=realm_id,
                    type=ContentType.CUSTOM,
                    entities=[],
                    metadata={},
                    orbit=0,
                    lineage=0
                )
                custom_provider.register_realm(realm_id, custom_realm)
        
        bigbang.register_provider("custom", custom_provider, priority=90)
        
        # Build realm specs from config
        realm_specs = []
        for realm_id in self.config.realms:
            # Determine realm type based on name
            realm_type = self._infer_realm_type(realm_id)
            spec = RealmSpec(
                id=realm_id,
                type=realm_type,
                seed=self.config.seed,  # Seed per realm for reproducibility
                district_count=2 if realm_type == ContentType.METVAN_3D else 1
            )
            realm_specs.append(spec)
        
        universe_spec = UniverseSpec(realms=realm_specs)
        
        # Initialize universe
        start_time = datetime.now()
        universe = await bigbang.initialize_multiverse(universe_spec)
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(
            f"✅ Phase 5 Multiverse initialized:\n"
            f"  Realms: {len(universe.realms)}\n"
            f"  Total entities: {sum(len(r.entities) for r in universe.realms.values())}\n"
            f"  Time: {elapsed_ms:.1f}ms"
        )
        
        return universe
    
    async def _run_enrichment_cycles(self) -> None:
        """Run Torus cycles to enrich universe with narrative."""
        if not self.universe:
            raise RuntimeError("Universe not initialized")
        
        engine = TorusCycleEngine()
        
        for orbit_num in range(self.config.orbits):
            logger.info(
                f"🌀 Orbit {orbit_num + 1}/{self.config.orbits}: "
                f"Running enrichment cycle"
            )
            
            await engine.execute_torus_cycle(
                self.universe,
                self.config.enrichment_types
            )
            
            # Log cycle stats
            realm_ids = list(self.universe.realms.keys())
            total_enrichments = 0
            for realm_id in realm_ids:
                realm = self.universe.realms[realm_id]
                realm_enrichments = sum(
                    len(e.metadata.get("enrichments", []))
                    for e in realm.entities
                )
                total_enrichments += realm_enrichments
            
            logger.debug(
                f"  ✓ Orbit {orbit_num + 1} complete: "
                f"{total_enrichments} enrichments applied"
            )
    
    async def _integrate_with_phases_2_4(self) -> Phase5Phase2Phase3Phase4Bridge:
        """Bridge Phase 5 universe to Phase 2-4 systems."""
        if not self.universe:
            raise RuntimeError("Universe not initialized")
        
        bridge = await integrate_phase5_universe(self.universe)
        
        logger.info(
            f"✅ Phase 5→2-4 Bridge Complete:\n"
            f"  Phase 2 NPCs registered: {len(bridge.phase2_adapter.npc_registry)}\n"
            f"  Phase 3 Semantic contexts: {len(bridge.phase3_adapter.semantic_index)}\n"
            f"  Phase 4 Dialogue sessions: {len(bridge.phase4_adapter.dialogue_sessions)}"
        )
        
        return bridge
    
    def _produce_metadata(self) -> DemoUniverseMetadata:
        """Produce reproducible metadata for demo."""
        if not self.universe:
            raise RuntimeError("Universe not initialized")
        
        # Build realm info
        realms_info = {}
        total_entities = 0
        for realm_id, realm in self.universe.realms.items():
            entity_count = len(realm.entities)
            total_entities += entity_count
            
            realms_info[realm_id] = {
                "type": realm.type.value,
                "entity_count": entity_count,
                "orbit": realm.orbit,
                "lineage": realm.lineage,
            }
        
        metadata = DemoUniverseMetadata(
            seed=self.config.seed,
            universe_initialized_at=self.universe.initialized_at.isoformat(),
            generation_timestamp=datetime.now().isoformat(),
            total_orbits_completed=self.universe.total_orbits_completed,
            realms=realms_info,
            total_entities=total_entities,
            initialization_time_ms=self.universe.initialization_time_ms
        )
        
        logger.debug(f"📊 Generated metadata:\n{json.dumps(asdict(metadata), indent=2)}")
        
        return metadata
    
    def _infer_realm_type(self, realm_id: str) -> ContentType:
        """Infer realm content type from ID."""
        realm_id_lower = realm_id.lower()
        
        if "arcade" in realm_id_lower or "2d" in realm_id_lower:
            return ContentType.ARCADE_2D
        elif "custom" in realm_id_lower or "tavern" in realm_id_lower or "dungeon" in realm_id_lower:
            return ContentType.CUSTOM  # Hand-crafted realms
        else:
            return ContentType.METVAN_3D  # Default to 3D procedural (more impressive for demo)
    
    def get_universe_export(self) -> Dict[str, Any]:
        """Export full universe state for reproducibility."""
        if not self.universe or not self.bridge:
            raise RuntimeError("Demo not launched")
        
        # Build complete export
        export = {
            "version": "1.0",
            "seed": self.config.seed,
            "universe": {
                "initialized_at": self.universe.initialized_at.isoformat(),
                "current_orbit": self.universe.current_orbit,
                "total_orbits_completed": self.universe.total_orbits_completed,
                "initialization_time_ms": self.universe.initialization_time_ms,
            },
            "realms": {},
            "phase2_npcs": {},
            "phase3_semantic_contexts": {},
            "phase4_dialogue_sessions": {},
        }
        
        # Export realm data
        for realm_id, realm in self.universe.realms.items():
            export["realms"][realm_id] = {
                "type": realm.type.value,
                "entity_count": len(realm.entities),
                "orbit": realm.orbit,
                "lineage": realm.lineage,
            }
        
        # Export bridge data
        for npc_id, npc_reg in self.bridge.phase2_adapter.npc_registry.items():
            export["phase2_npcs"][npc_id] = {
                "name": npc_reg.npc_name,
                "realm_id": npc_reg.realm_id,
                "personality_traits": npc_reg.personality_traits,
            }
        
        for entity_id, context in self.bridge.phase3_adapter.semantic_index.items():
            export["phase3_semantic_contexts"][entity_id] = {
                "primary_topic": context.primary_topic,
                "related_topics": context.related_topics,
                "audit_trail_depth": context.audit_trail_depth,
            }
        
        for session_id, dialogue_state in self.bridge.phase4_adapter.dialogue_sessions.items():
            export["phase4_dialogue_sessions"][session_id] = {
                "npc_name": dialogue_state.npc_name,
                "narrative_phase": dialogue_state.current_narrative_phase,
                "dialogue_turn": dialogue_state.dialogue_turn,
            }
        
        return export
    
    def save_universe_export(self, filepath: str) -> None:
        """Save universe export to JSON file."""
        export = self.get_universe_export()
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(export, f, indent=2)
        
        logger.info(f"💾 Universe exported to {filepath}")
    
    def get_initialization_seed(self) -> int:
        """Get the initialization seed used for this orchestrator (Phase 6D reproducibility)."""
        if self._initialization_seed is None:
            return self.config.seed
        return self._initialization_seed
    
    async def classify_realms(self, tier_specs: Dict[str, tuple]) -> None:
        """
        Classify realms with tier metadata (Phase 6-Alpha integration).
        
        Args:
            tier_specs: Dict mapping realm_id to (TierClassification, TierTheme, semantic_anchors)
        
        Example:
            await orchestrator.classify_realms({
                "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban"]),
            })
        """
        if not self.universe:
            raise RuntimeError("Universe not initialized")
        
        # This will be used by Phase 6B API server to integrate with Phase 6-Alpha
        logger.info(f"🏷️  Classifying {len(tier_specs)} realms with tier metadata")
        for realm_id, (tier, theme, anchors) in tier_specs.items():
            logger.debug(f"  {realm_id}: tier={tier.value}, theme={theme.value}")
    
    def get_demo_metadata(self) -> DemoUniverseMetadata:
        """
        Get current demo metadata.
        
        Returns:
            DemoUniverseMetadata with current universe state
        """
        return self._produce_metadata()
    
    @property
    def realm_entity_counts(self) -> Dict[str, int]:
        """Get entity counts per realm."""
        if not self.universe:
            return {}
        return {realm_id: len(realm.entities) for realm_id, realm in self.universe.realms.items()}


# ============================================================================
# CONVENIENCE FUNCTION (One-Line Demo Launch)
# ============================================================================

async def launch_university_demo(
    seed: int = 42,
    orbits: int = 3,
    realms: List[str] = None,
) -> DemoUniverseMetadata:
    """
    Launch complete university demo with one async call.
    
    Args:
        seed: Reproducibility seed (default: 42)
        orbits: Number of enrichment cycles (default: 3)
        realms: List of realm IDs to create (default: ["overworld", "tavern"])
    
    Returns:
        DemoUniverseMetadata with reproducible universe info
    
    Example:
        metadata = await launch_university_demo(seed=42, orbits=3)
        print(f"Generated {metadata.total_entities} entities")
    """
    config = OrchestratorConfig(
        seed=seed,
        orbits=orbits,
        realms=realms or ["overworld", "tavern"]
    )
    
    orchestrator = UniverseDemoOrchestrator(config)
    return await orchestrator.launch_demo()


# ============================================================================
# MAIN ENTRY POINT (CLI for testing)
# ============================================================================

async def main():
    """Quick test of orchestrator."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    
    logger.info("=" * 70)
    logger.info("PHASE 6 ORCHESTRATOR - UNIVERSITY DEMO")
    logger.info("=" * 70)
    
    # Launch demo
    metadata = await launch_university_demo(seed=42, orbits=2)
    
    # Print results
    logger.info("\n" + "=" * 70)
    logger.info("DEMO RESULTS")
    logger.info("=" * 70)
    logger.info(f"Seed: {metadata.seed}")
    logger.info(f"Total entities: {metadata.total_entities}")
    logger.info(f"Orbits completed: {metadata.total_orbits_completed}")
    logger.info(f"Initialization time: {metadata.initialization_time_ms:.1f}ms")
    logger.info(f"\nRealms generated:")
    for realm_id, info in metadata.realms.items():
        logger.info(f"  {realm_id}: {info['entity_count']} entities (lineage={info['lineage']})")
    
    logger.info("\n✅ University demo ready for presentation!")


if __name__ == "__main__":
    asyncio.run(main())