"""
City Simulation Integration: NPCs as First-Class Multiverse Citizens

Integrates city simulations with MultiGameTickEngine so NPCs:
- Participate in control-ticks alongside game worlds
- Are aware of cross-realm events
- Remember player interactions across realms
- Generate dynamic dialogue based on multiverse state
- Trigger quests and narrative events

Architecture:
- Each city simulation registers with orchestrator
- NPCs synchronize during control-ticks
- Player transitions trigger NPC awareness events
- Warbler runs per control-tick to update NPC state

Example:
    integration = CitySimulationIntegration(orchestrator, player_router, warbler_bridge)
    
    # Register city simulation
    city_sim = CitySimulation(realm_id="sol_1", num_npcs=50)
    integration.register_city_simulation("sol_1", city_sim)
    
    # NPCs now participate in orchestrator ticks
    # When player travels, NPCs in destination get notified
    # When cross-game events propagate, NPCs react
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class NPCState(Enum):
    """NPC state during simulation."""
    IDLE = "idle"
    INTERACTING = "interacting"
    TRAVELING = "traveling"
    REACTING = "reacting"
    REMEMBERING = "remembering"


@dataclass
class CityNPC:
    """NPC entity in a city simulation."""
    npc_id: str
    npc_name: str
    role: str  # "merchant", "guard", "scholar", etc.
    realm_id: str
    location: str  # Current location in city
    
    # State
    state: NPCState = NPCState.IDLE
    current_activity: str = "idle"
    
    # Memory and personality
    personality_type: str = "neutral"
    faction_allegiance: str = "neutral"
    mood: str = "neutral"
    
    # Cross-realm awareness
    known_players: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # player_id -> memory
    cross_realm_knowledge: List[Dict[str, Any]] = field(default_factory=list)  # Events from other realms
    
    # Activity tracking
    last_interaction: str = ""
    interaction_count: int = 0


@dataclass
class NPCEvent:
    """Event that affects NPC state."""
    event_id: str
    event_type: str  # "player_arrival", "reputation_change", "cross_realm_event"
    npc_id: str
    data: Dict[str, Any]
    timestamp: str


class CitySimulationIntegration:
    """
    Integrates city simulations with the multiverse orchestrator.
    
    Manages NPC synchronization, event propagation, and narrative awareness.
    """
    
    def __init__(self, orchestrator, player_router, warbler_bridge, warbler_query_service=None):
        """
        Initialize integration.
        
        Args:
            orchestrator: MultiGameTickEngine instance
            player_router: UniversalPlayerRouter instance
            warbler_bridge: WarblerMultiverseBridge instance
            warbler_query_service: Optional WarblerQueryService instance
        """
        self.orchestrator = orchestrator
        self.router = player_router
        self.bridge = warbler_bridge
        self.query_service = warbler_query_service
        
        # City simulations
        self.city_simulations: Dict[str, Any] = {}  # realm_id -> city_sim
        self.npcs: Dict[str, CityNPC] = {}  # npc_id -> CityNPC
        self.realm_npcs: Dict[str, List[str]] = {}  # realm_id -> [npc_ids]
        
        # Event queue
        self.npc_event_queue: List[NPCEvent] = []
        self.processed_events: List[NPCEvent] = []
        
        # Statistics
        self.total_npc_ticks = 0
        self.total_npc_events_processed = 0
    
    def register_city_simulation(self, realm_id: str, city_simulation: Any, 
                               num_npcs: int = 50) -> List[str]:
        """
        Register a city simulation and create its NPCs.
        
        Args:
            realm_id: Which realm this city is in
            city_simulation: City simulation instance
            num_npcs: How many NPCs to create
            
        Returns:
            List of created NPC IDs
        """
        self.city_simulations[realm_id] = city_simulation
        
        # Create NPCs for this city
        npc_ids = []
        npc_roles = ["merchant", "guard", "scholar", "mystic", "townsfolk"]
        
        for i in range(num_npcs):
            npc_id = f"npc_{realm_id}_{i:03d}"
            role = npc_roles[i % len(npc_roles)]
            
            npc = CityNPC(
                npc_id=npc_id,
                npc_name=f"{role.title()} {npc_id[-3:]}",
                role=role,
                realm_id=realm_id,
                location=f"location_{i % 10}",
                personality_type=role,
                faction_allegiance=self._get_faction_for_role(role),
            )
            
            self.npcs[npc_id] = npc
            npc_ids.append(npc_id)
            
            # Register with Warbler bridge
            self.bridge.register_npc(npc_id, npc.npc_name, realm_id, role)
        
        # Track realm NPCs
        self.realm_npcs[realm_id] = npc_ids
        
        print(f"✅ Registered {num_npcs} NPCs in {realm_id}")
        return npc_ids
    
    def _get_faction_for_role(self, role: str) -> str:
        """Map NPC role to faction allegiance."""
        role_to_faction = {
            "merchant": "the_wanderers",
            "guard": "realm_keepers",
            "scholar": "realm_keepers",
            "mystic": "chaotic_forces",
            "townsfolk": "neutral",
        }
        return role_to_faction.get(role, "neutral")
    
    def synchronize_npc_tick(self, control_tick_id: int, elapsed_ms: float) -> Dict[str, Any]:
        """
        Synchronize NPCs during control-tick.
        
        Called by orchestrator during each control-tick.
        Updates NPC state and reactions to cross-realm events.
        
        Args:
            control_tick_id: Current control tick
            elapsed_ms: Milliseconds since last control-tick
            
        Returns:
            Metrics about NPC tick
        """
        events_processed = 0
        npc_reactions = 0
        
        # Process queued NPC events
        while self.npc_event_queue:
            event = self.npc_event_queue.pop(0)
            npc = self.npcs.get(event.npc_id)
            
            if npc:
                self._process_npc_event(npc, event)
                events_processed += 1
                self.total_npc_events_processed += 1
        
        # Update NPC states
        for npc_id, npc in self.npcs.items():
            old_state = npc.state
            self._update_npc_state(npc)
            
            if npc.state != old_state:
                npc_reactions += 1
        
        self.total_npc_ticks += 1
        
        return {
            "control_tick_id": control_tick_id,
            "npcs_synchronized": len(self.npcs),
            "npc_events_processed": events_processed,
            "npc_state_changes": npc_reactions,
            "elapsed_ms": elapsed_ms,
        }
    
    def _process_npc_event(self, npc: CityNPC, event: NPCEvent):
        """Process an event affecting an NPC."""
        if event.event_type == "player_arrival":
            # Player arrived in NPC's realm
            player_id = event.data.get("player_id")
            player = self.router.get_player(player_id)
            
            if player:
                # Store memory of player arrival
                npc.known_players[player_id] = {
                    "player_name": player.player_name,
                    "race": player.character_race,
                    "class": player.character_class,
                    "first_encounter": event.timestamp,
                    "encounter_count": 1,
                }
                
                npc.state = NPCState.REACTING
                npc.current_activity = f"notices arrival of {player.player_name}"
        
        elif event.event_type == "reputation_change":
            # Player reputation changed
            player_id = event.data.get("player_id")
            new_standing = event.data.get("standing")
            
            if player_id in npc.known_players:
                npc.known_players[player_id]["standing"] = new_standing
                
                # Adjust NPC mood based on player's reputation with NPC's faction
                player = self.router.get_player(player_id)
                if player:
                    rep = next(
                        (r for r in player.reputation if r.faction.value == npc.faction_allegiance),
                        None
                    )
                    if rep:
                        if rep.standing == "revered":
                            npc.mood = "deferential"
                        elif rep.standing == "liked":
                            npc.mood = "friendly"
                        elif rep.standing == "despised":
                            npc.mood = "hostile"
                        else:
                            npc.mood = "neutral"
        
        elif event.event_type == "cross_realm_event":
            # Event from another realm
            npc.cross_realm_knowledge.append(event.data)
            npc.state = NPCState.REMEMBERING
            npc.current_activity = "processing news from other realms"
        
        self.processed_events.append(event)
    
    def _update_npc_state(self, npc: CityNPC):
        """Update NPC state based on current conditions."""
        if npc.state == NPCState.REACTING:
            # NPC reacting - return to idle after reaction
            npc.state = NPCState.IDLE
        elif npc.state == NPCState.REMEMBERING:
            # NPC processing memories - return to idle
            npc.state = NPCState.IDLE
        elif npc.state == NPCState.IDLE:
            # NPCs cycle through activities
            npc.current_activity = "idle"
    
    def on_player_transition(self, 
                           player_id: str,
                           source_realm: str,
                           target_realm: str,
                           event_data: Dict[str, Any]):
        """
        Called when player transitions between realms.
        
        Notifies NPCs in both realms.
        
        Args:
            player_id: Player transitioning
            source_realm: Realm they left
            target_realm: Realm they entered
            event_data: Transition event data
        """
        player = self.router.get_player(player_id)
        if not player:
            return
        
        now = datetime.utcnow().isoformat()
        
        # Notify NPCs in source realm (player leaving)
        for npc_id in self.realm_npcs.get(source_realm, []):
            npc = self.npcs.get(npc_id)
            if npc and player_id in npc.known_players:
                npc.current_activity = f"notes departure of {player.player_name}"
                npc.state = NPCState.REACTING
        
        # Notify NPCs in target realm (player arriving)
        for npc_id in self.realm_npcs.get(target_realm, []):
            npc = self.npcs.get(npc_id)
            if npc:
                event = NPCEvent(
                    event_id=f"arrival_{player_id}_{now}",
                    event_type="player_arrival",
                    npc_id=npc_id,
                    data={
                        "player_id": player_id,
                        "player_name": player.player_name,
                        "source_realm": source_realm,
                        "target_realm": target_realm,
                    },
                    timestamp=now
                )
                self.npc_event_queue.append(event)
        
        # Emit NPC awareness event
        self.router.emit_narrative_event(
            player_id=player_id,
            event_type="npc_awareness",
            title=f"NPCs notice {player.player_name} in {target_realm}",
            description=f"Local NPCs in {target_realm} become aware of {player.player_name}'s arrival",
            metadata={"source_realm": source_realm, "target_realm": target_realm}
        )
    
    def on_cross_game_event(self, event: Dict[str, Any]):
        """
        Called when a cross-game event propagates.
        
        NPCs in affected realms react to the event.
        
        Args:
            event: Cross-game event
        """
        if event.get("event_type") == "world_event":
            # Broadcast to all NPCs
            for npc_id in self.npcs.keys():
                npc = self.npcs[npc_id]
                npc_event = NPCEvent(
                    event_id=f"cge_{event.get('event_id')}_{npc_id}",
                    event_type="cross_realm_event",
                    npc_id=npc_id,
                    data=event,
                    timestamp=datetime.utcnow().isoformat()
                )
                self.npc_event_queue.append(npc_event)
    
    def on_reputation_change(self, 
                           player_id: str,
                           faction: str,
                           new_standing: str):
        """
        Called when player reputation changes.
        
        NPCs aligned with that faction react.
        
        Args:
            player_id: Player whose reputation changed
            faction: Faction name
            new_standing: New standing level
        """
        now = datetime.utcnow().isoformat()
        player = self.router.get_player(player_id)
        
        if not player:
            return
        
        # Notify NPCs aligned with this faction
        for npc_id, npc in self.npcs.items():
            if npc.faction_allegiance == faction:
                event = NPCEvent(
                    event_id=f"repchange_{player_id}_{faction}_{now}",
                    event_type="reputation_change",
                    npc_id=npc_id,
                    data={
                        "player_id": player_id,
                        "player_name": player.player_name,
                        "faction": faction,
                        "standing": new_standing,
                    },
                    timestamp=now
                )
                self.npc_event_queue.append(event)
    
    def get_npc_dialogue(self, npc_id: str, player_id: str, 
                        user_input: str, realm_id: str) -> str:
        """
        Get dialogue from NPC.
        
        Delegates to Warbler Query Service if available.
        
        Args:
            npc_id: NPC responding
            player_id: Player asking
            user_input: What player said
            realm_id: Realm context
            
        Returns:
            NPC response
        """
        if not self.query_service:
            npc = self.npcs.get(npc_id)
            if npc:
                return f"{npc.npc_name} says: I'm not sure how to respond."
            return "No NPC response available"
        
        result = self.query_service.query_npc(
            player_id=player_id,
            npc_id=npc_id,
            user_input=user_input,
            realm_id=realm_id
        )
        
        return result.get("npc_response", "No response")
    
    def get_city_status(self, realm_id: str) -> Dict[str, Any]:
        """
        Get status of city in a realm.
        
        Args:
            realm_id: Realm to query
            
        Returns:
            City status including NPC distribution
        """
        npc_ids = self.realm_npcs.get(realm_id, [])
        npcs = [self.npcs[npc_id] for npc_id in npc_ids if npc_id in self.npcs]
        
        role_distribution = {}
        for npc in npcs:
            role_distribution[npc.role] = role_distribution.get(npc.role, 0) + 1
        
        mood_distribution = {}
        for npc in npcs:
            mood_distribution[npc.mood] = mood_distribution.get(npc.mood, 0) + 1
        
        return {
            "realm_id": realm_id,
            "total_npcs": len(npcs),
            "role_distribution": role_distribution,
            "mood_distribution": mood_distribution,
            "pending_npc_events": len(self.npc_event_queue),
            "total_npc_ticks": self.total_npc_ticks,
        }
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics."""
        return {
            "total_npcs": len(self.npcs),
            "total_realms": len(self.city_simulations),
            "total_npc_ticks": self.total_npc_ticks,
            "total_npc_events_processed": self.total_npc_events_processed,
            "pending_events": len(self.npc_event_queue),
            "processed_events": len(self.processed_events),
        }