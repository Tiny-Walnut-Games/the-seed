"""
Phase 5 → Phase 2-4 Integration Bridge

Connects Phase 5 (Procedural Universe) with:
- Phase 2: Warbler NPCs and Cross-Realm Quests
- Phase 3: Semantic Search with Enrichment Context
- Phase 4: Multi-Turn Dialogue with STAT7 Location Awareness

This bridge:
1. Converts Phase 5 entities to Phase 2 NPC registrations
2. Extracts semantic context from Phase 5 enrichments for Phase 3 indexing
3. Provides STAT7-aware location and dialogue turn state for Phase 4

Architecture:
- Phase5ToPhase2Adapter: Entity → NPC registration
- Phase5ToPhase3Adapter: Enrichment audit trail → semantic context
- Phase5ToPhase4Adapter: STAT7 coordinates and orbits → dialogue state
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# Phase 2 ADAPTER: Convert Phase 5 Entities → NPCs
# ============================================================================

@dataclass
class NPCRegistration:
    """Registration for Phase 2 NPC system."""
    npc_id: str
    npc_name: str
    realm_id: str
    entity_type: str
    stat7_coordinates: Dict[str, int]
    personality_traits: Dict[str, Any]
    enrichment_history: List[Dict[str, Any]]


class Phase5ToPhase2Adapter:
    """Convert Phase 5 entities to Phase 2 NPC registrations."""
    
    def __init__(self):
        self.npc_registry: Dict[str, NPCRegistration] = {}
        self.entity_to_npc_map: Dict[str, str] = {}
    
    def register_entity_as_npc(
        self, 
        entity,  # Phase 5 Entity
        realm_id: str,
        npc_name: Optional[str] = None
    ) -> NPCRegistration:
        """
        Convert a Phase 5 entity to a Phase 2 NPC registration.
        
        Args:
            entity: Phase 5 Entity object
            realm_id: Realm the entity belongs to
            npc_name: Override auto-generated name
        
        Returns:
            NPCRegistration for Phase 2 systems
        """
        # Generate NPC ID from entity
        npc_id = f"npc_{realm_id}_{entity.id}"
        
        # Auto-generate name if not provided
        if not npc_name:
            npc_name = self._generate_npc_name(entity, realm_id)
        
        # Extract personality from metadata
        personality = self._extract_personality(entity.metadata)
        
        # Extract enrichment history
        enrichments = entity.metadata.get("enrichments", [])
        
        # Create registration
        registration = NPCRegistration(
            npc_id=npc_id,
            npc_name=npc_name,
            realm_id=realm_id,
            entity_type=entity.type,
            stat7_coordinates=entity.stat7.to_dict(),
            personality_traits=personality,
            enrichment_history=enrichments
        )
        
        self.npc_registry[npc_id] = registration
        self.entity_to_npc_map[entity.id] = npc_id
        
        logger.info(
            f"✅ Registered NPC: {npc_name} (ID: {npc_id}) in realm '{realm_id}'"
        )
        
        return registration
    
    def get_npc_registration(self, npc_id: str) -> Optional[NPCRegistration]:
        """Retrieve NPC registration by ID."""
        return self.npc_registry.get(npc_id)
    
    def get_realm_npcs(self, realm_id: str) -> List[NPCRegistration]:
        """Get all NPCs in a realm."""
        return [
            npc for npc in self.npc_registry.values()
            if npc.realm_id == realm_id
        ]
    
    def _generate_npc_name(self, entity, realm_id: str) -> str:
        """Generate a lore-appropriate NPC name."""
        entity_index = entity.id.split("_")[-1] if "_" in entity.id else "0"
        
        # Name patterns based on realm
        if "metvan" in realm_id.lower():
            names = ["District Guardian", "Realm Keeper", "Pathfinder"]
        elif "tavern" in realm_id.lower():
            names = ["Barkeep", "Innkeeper", "Storyteller"]
        elif "arcade" in realm_id.lower():
            names = ["Arcade Keeper", "Game Master", "Attendant"]
        else:
            names = ["Wanderer", "Sage", "Keeper"]
        
        name_base = names[int(entity_index) % len(names)]
        return f"{name_base} {entity_index}"
    
    def _extract_personality(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract personality traits from entity metadata."""
        enrichments = metadata.get("enrichments", [])
        
        personality = {
            "base_mood": "neutral",
            "interaction_count": len(enrichments),
            "enriched_dimensions": set()
        }
        
        # Infer personality from enrichments
        for enrichment in enrichments:
            enrichment_type = enrichment.get("type", "")
            if "dialogue" in enrichment_type:
                personality["base_mood"] = "talkative"
            if "history" in enrichment_type:
                personality["base_mood"] = "experienced"
            personality["enriched_dimensions"].add(enrichment_type)
        
        # Convert set to list for serialization
        personality["enriched_dimensions"] = list(personality["enriched_dimensions"])
        
        return personality


# ============================================================================
# Phase 3 ADAPTER: Extract Semantic Context from Enrichments
# ============================================================================

@dataclass
class SemanticContext:
    """Semantic context extracted from Phase 5 enrichments."""
    entity_id: str
    realm_id: str
    primary_topic: str
    related_topics: List[str]
    narrative_arc: List[str]
    enrichment_density: float
    audit_trail_depth: int
    semantic_keywords: List[str]


class Phase5ToPhase3Adapter:
    """Extract semantic context from Phase 5 enrichments for Phase 3 indexing."""
    
    def __init__(self):
        self.semantic_index: Dict[str, SemanticContext] = {}
    
    def extract_semantic_context(
        self,
        entity,  # Phase 5 Entity
        realm_id: str
    ) -> SemanticContext:
        """
        Extract semantic context from Phase 5 entity enrichments.
        
        Args:
            entity: Phase 5 Entity with enrichment history
            realm_id: Realm the entity belongs to
        
        Returns:
            SemanticContext for Phase 3 semantic search indexing
        """
        enrichments = entity.metadata.get("enrichments", [])
        
        # Build narrative arc from enrichment timeline
        narrative_arc = []
        enrichment_types = {}
        
        for enrichment in enrichments:
            enrichment_type = enrichment.get("type", "unknown")
            enrichment_data = enrichment.get("data", "")
            
            enrichment_types[enrichment_type] = enrichment_types.get(enrichment_type, 0) + 1
            
            # Convert enrichment data to string representation
            if enrichment_data:
                if isinstance(enrichment_data, str):
                    data_str = enrichment_data[:50]
                elif isinstance(enrichment_data, dict):
                    data_str = str(enrichment_data).replace("'", "")[:50]
                else:
                    data_str = str(enrichment_data)[:50]
                
                narrative_arc.append(f"{enrichment_type}: {data_str}")
        
        # Extract primary topic from most common enrichment type
        primary_topic = max(
            enrichment_types.items(),
            key=lambda x: x[1]
        )[0] if enrichment_types else "unknown"
        
        # Generate semantic keywords
        keywords = list(enrichment_types.keys()) + [
            f"realm_{realm_id}",
            f"entity_{entity.type}"
        ]
        
        # Calculate enrichment density (enrichments per dimension)
        enrichment_density = len(enrichments) / 7.0  # 7 STAT7 dimensions
        
        context = SemanticContext(
            entity_id=entity.id,
            realm_id=realm_id,
            primary_topic=primary_topic,
            related_topics=list(enrichment_types.keys())[1:],
            narrative_arc=narrative_arc,
            enrichment_density=enrichment_density,
            audit_trail_depth=len(enrichments),
            semantic_keywords=keywords
        )
        
        self.semantic_index[entity.id] = context
        
        logger.debug(
            f"📊 Extracted semantic context for {entity.id}: "
            f"{len(keywords)} keywords, {len(narrative_arc)} narrative points"
        )
        
        return context
    
    def search_by_topic(self, topic: str) -> List[SemanticContext]:
        """Find entities by primary topic."""
        return [
            ctx for ctx in self.semantic_index.values()
            if ctx.primary_topic == topic
        ]
    
    def search_by_keyword(self, keyword: str) -> List[SemanticContext]:
        """Find entities by semantic keyword."""
        return [
            ctx for ctx in self.semantic_index.values()
            if keyword in ctx.semantic_keywords
        ]
    
    def get_enrichment_audit_trail(self, entity_id: str) -> List[str]:
        """Get narrative arc for an entity (for Phase 4 context)."""
        context = self.semantic_index.get(entity_id)
        return context.narrative_arc if context else []


# ============================================================================
# Phase 4 ADAPTER: Provide Dialogue State from STAT7 & Orbits
# ============================================================================

@dataclass
class DialogueState:
    """Dialogue state derived from Phase 5 STAT7 and orbit tracking."""
    entity_id: str
    npc_name: str
    realm_id: str
    current_orbit: int
    location_context: Dict[str, Any]
    dialogue_turn: int
    enrichment_progression: List[str]
    current_narrative_phase: str


class Phase5ToPhase4Adapter:
    """Provide Phase 4 dialogue state from Phase 5 STAT7 coordinates and orbits."""
    
    def __init__(self):
        self.dialogue_sessions: Dict[str, DialogueState] = {}
        self.turn_counter: Dict[str, int] = {}
    
    def initialize_dialogue_state(
        self,
        entity,  # Phase 5 Entity
        npc_name: str,
        realm_id: str,
        current_orbit: int
    ) -> DialogueState:
        """
        Initialize dialogue state from Phase 5 entity and orbit.
        
        Args:
            entity: Phase 5 Entity with STAT7 coordinates
            npc_name: NPC name (from Phase 2 registration)
            realm_id: Realm the entity belongs to
            current_orbit: Current universe orbit
        
        Returns:
            DialogueState for Phase 4 multi-turn dialogue
        """
        # Extract location context from STAT7
        stat7 = entity.stat7.to_dict()
        location_context = {
            "realm": realm_id,
            "realm_coordinate": stat7["realm"],
            "adjacency": stat7["adjacency"],
            "horizon": stat7["horizon"],
            "resonance": stat7["resonance"],
            "narrative_density": stat7["density"] / 100.0,
            "change_momentum": stat7["velocity"]
        }
        
        # Extract enrichment progression
        enrichments = entity.metadata.get("enrichments", [])
        enrichment_progression = [
            e.get("type", "unknown") for e in enrichments
        ]
        
        # Determine narrative phase based on orbit and enrichments
        narrative_phase = self._determine_narrative_phase(
            current_orbit,
            len(enrichments)
        )
        
        dialogue_state = DialogueState(
            entity_id=entity.id,
            npc_name=npc_name,
            realm_id=realm_id,
            current_orbit=current_orbit,
            location_context=location_context,
            dialogue_turn=0,
            enrichment_progression=enrichment_progression,
            current_narrative_phase=narrative_phase
        )
        
        session_id = f"{entity.id}_{realm_id}"
        self.dialogue_sessions[session_id] = dialogue_state
        self.turn_counter[session_id] = 0
        
        logger.info(
            f"🗣️ Initialized dialogue state for {npc_name} at orbit {current_orbit}, "
            f"phase: {narrative_phase}"
        )
        
        return dialogue_state
    
    def advance_dialogue_turn(self, entity_id: str, realm_id: str) -> int:
        """
        Advance dialogue turn counter for an entity.
        
        Used to track multi-turn conversation progression.
        """
        session_id = f"{entity_id}_{realm_id}"
        
        if session_id not in self.turn_counter:
            return 0
        
        self.turn_counter[session_id] += 1
        turn = self.turn_counter[session_id]
        
        # Update dialogue state
        if session_id in self.dialogue_sessions:
            self.dialogue_sessions[session_id].dialogue_turn = turn
        
        logger.debug(f"📝 Dialogue turn advanced: {session_id} → turn {turn}")
        
        return turn
    
    def get_dialogue_context(
        self,
        entity_id: str,
        realm_id: str,
        current_orbit: int
    ) -> Dict[str, Any]:
        """
        Get complete dialogue context for Phase 4 slot filling.
        
        Returns context dict suitable for template interpolation:
        - {{location_type}}: Extracted from realm ID
        - {{time_of_day}}: Derived from orbit progression
        - {{npc_mood}}: Based on enrichment types
        - {{narrative_phase}}: From orbit and enrichment count
        """
        session_id = f"{entity_id}_{realm_id}"
        dialogue_state = self.dialogue_sessions.get(session_id)
        
        if not dialogue_state:
            return {}
        
        return {
            "location_context": dialogue_state.location_context,
            "location_type": self._extract_location_type(realm_id),
            "time_of_day": self._derive_time_of_day(current_orbit),
            "npc_mood": self._infer_npc_mood(dialogue_state.enrichment_progression),
            "narrative_phase": dialogue_state.current_narrative_phase,
            "dialogue_turn": dialogue_state.dialogue_turn,
            "enrichment_depth": len(dialogue_state.enrichment_progression),
            "stat7_signature": dialogue_state.location_context["realm_coordinate"],
        }
    
    def _determine_narrative_phase(self, orbit: int, enrichment_count: int) -> str:
        """Determine narrative phase based on orbit and enrichment depth."""
        if orbit < 2:
            return "introduction"
        elif orbit < 5 and enrichment_count < 3:
            return "context"
        elif enrichment_count >= 3:
            return "deepening"
        else:
            return "resolution"
    
    def _extract_location_type(self, realm_id: str) -> str:
        """Extract location type from realm ID."""
        if "tavern" in realm_id.lower():
            return "tavern"
        elif "arcade" in realm_id.lower():
            return "arcade"
        elif "metvan" in realm_id.lower():
            return "dungeon"
        else:
            return "neutral_ground"
    
    def _derive_time_of_day(self, orbit: int) -> str:
        """Derive time of day from orbit progression."""
        times = ["dawn", "morning", "noon", "afternoon", "dusk", "night", "midnight"]
        return times[orbit % len(times)]
    
    def _infer_npc_mood(self, enrichment_progression: List[str]) -> str:
        """Infer NPC mood from enrichment history."""
        mood_map = {
            "dialogue": "talkative",
            "quest": "motivated",
            "npc_history": "nostalgic",
            "contradiction": "confused",
            "lore": "knowledgeable"
        }
        
        if not enrichment_progression:
            return "neutral"
        
        # Use most common enrichment type to infer mood
        most_common = max(set(enrichment_progression), key=enrichment_progression.count)
        return mood_map.get(most_common, "contemplative")


# ============================================================================
# UNIFIED BRIDGE: Orchestrate All Adapters
# ============================================================================

class Phase5Phase2Phase3Phase4Bridge:
    """
    Master integration bridge connecting Phase 5 to Phase 2-4 systems.
    
    Orchestrates:
    - NPC registration (Phase 2)
    - Semantic indexing (Phase 3)
    - Dialogue state management (Phase 4)
    """
    
    def __init__(self):
        self.phase2_adapter = Phase5ToPhase2Adapter()
        self.phase3_adapter = Phase5ToPhase3Adapter()
        self.phase4_adapter = Phase5ToPhase4Adapter()
    
    async def integrate_universe(self, universe) -> Dict[str, Any]:
        """
        Integrate a Phase 5 universe with Phase 2-4 systems.
        
        Args:
            universe: Phase 5 Universe object
        
        Returns:
            Integration summary with registration counts and indices built
        """
        logger.info("🌉 Starting Phase 5→Phase 2-4 integration...")
        
        summary = {
            "realms_integrated": 0,
            "npcs_registered": 0,
            "semantic_contexts": 0,
            "dialogue_sessions": 0,
            "errors": []
        }
        
        # Iterate over all realms and entities
        for realm_id, realm in universe.realms.items():
            try:
                for entity in realm.entities:
                    # Phase 2: Register as NPC
                    try:
                        self.phase2_adapter.register_entity_as_npc(entity, realm_id)
                        summary["npcs_registered"] += 1
                    except Exception as e:
                        summary["errors"].append(
                            f"Phase 2 registration failed for {entity.id}: {e}"
                        )
                    
                    # Phase 3: Extract semantic context
                    try:
                        self.phase3_adapter.extract_semantic_context(entity, realm_id)
                        summary["semantic_contexts"] += 1
                    except Exception as e:
                        summary["errors"].append(
                            f"Phase 3 semantic extraction failed for {entity.id}: {e}"
                        )
                    
                    # Phase 4: Initialize dialogue state
                    try:
                        npc_name = self.phase2_adapter.get_npc_registration(
                            f"npc_{realm_id}_{entity.id}"
                        ).npc_name
                        self.phase4_adapter.initialize_dialogue_state(
                            entity,
                            npc_name,
                            realm_id,
                            universe.current_orbit
                        )
                        summary["dialogue_sessions"] += 1
                    except Exception as e:
                        summary["errors"].append(
                            f"Phase 4 dialogue state failed for {entity.id}: {e}"
                        )
                
                summary["realms_integrated"] += 1
            except Exception as e:
                summary["errors"].append(f"Realm integration failed for {realm_id}: {e}")
        
        logger.info(f"✅ Integration complete: {summary['npcs_registered']} NPCs, "
                   f"{summary['semantic_contexts']} semantic contexts, "
                   f"{summary['dialogue_sessions']} dialogue sessions")
        
        return summary


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def integrate_phase5_universe(universe) -> Phase5Phase2Phase3Phase4Bridge:
    """
    Initialize and integrate a Phase 5 universe with Phase 2-4 systems.
    
    Returns the bridge for querying NPCs, semantic contexts, and dialogue state.
    """
    bridge = Phase5Phase2Phase3Phase4Bridge()
    await bridge.integrate_universe(universe)
    return bridge