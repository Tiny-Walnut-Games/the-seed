"""
Universal Player Router: Cross-Realm Player Management

Manages player state, transitions between realms, and persistent inventory/reputation
across multiverse simulations.

Features:
- Universal player IDs (global UUID)
- Active realm tracking (which game world player is in)
- Cross-realm inventory and reputation
- Realm transition mechanics (portals/travel)
- Narrative state persistence (affects story generation)
- Event emission for player transitions (feeds into Warbler context)

Example:
    router = UniversalPlayerRouter()
    
    # Create player
    player = router.create_player("alice", "human", starting_realm="sol_1")
    
    # Player travels to different realm
    router.transition_player("player_uuid_1", "sol_1", "sol_2")
    
    # Query player state for Warbler context
    context = router.get_warbler_context("player_uuid_1")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
from datetime import datetime, timedelta


class ReputationFaction(Enum):
    """Major reputation factions across multiverse."""
    THE_WANDERERS = "the_wanderers"  # Travelers' guild
    REALM_KEEPERS = "realm_keepers"  # Protectors of stability
    CHAOTIC_FORCES = "chaotic_forces"  # Narrative agitators
    NEUTRAL = "neutral"  # Unaligned


@dataclass
class InventoryItem:
    """Item in player inventory."""
    item_id: str
    name: str
    item_type: str  # "weapon", "armor", "quest", "cosmetic", "currency"
    rarity: str  # "common", "rare", "legendary"
    source_realm: str  # Which game this came from
    transferable: bool = True  # Can be taken between realms
    quantity: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReputationScore:
    """Reputation with a faction."""
    faction: ReputationFaction
    score: int  # -1000 to +1000
    standing: str  # "despised", "disliked", "neutral", "liked", "revered"
    last_modified: str = ""


@dataclass
class UniversalPlayer:
    """Player state persistent across realms."""
    
    # Identity
    player_id: str  # Global UUID
    player_name: str
    character_race: str
    character_class: str  # Optional: can vary per realm
    
    # Current state
    active_realm: str  # Which game world player is currently in
    active_location: str  # Where in that realm (optional)
    
    # Cross-realm persistence
    inventory: List[InventoryItem] = field(default_factory=list)
    reputation: List[ReputationScore] = field(default_factory=list)
    level: int = 1
    experience: int = 0
    
    # Timeline tracking (for narrative)
    realm_history: List[Tuple[str, str]] = field(default_factory=list)  # [(realm, timestamp), ...]
    visited_realms: List[str] = field(default_factory=list)
    
    # Narrative context
    active_quests: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # quest_id -> quest_data
    completed_quests: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: str = ""
    last_realm_transition: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "player_id": self.player_id,
            "player_name": self.player_name,
            "character_race": self.character_race,
            "character_class": self.character_class,
            "active_realm": self.active_realm,
            "active_location": self.active_location,
            "inventory": [
                {
                    "item_id": item.item_id,
                    "name": item.name,
                    "type": item.item_type,
                    "rarity": item.rarity,
                    "quantity": item.quantity,
                }
                for item in self.inventory
            ],
            "reputation": [
                {
                    "faction": rep.faction.value,
                    "score": rep.score,
                    "standing": rep.standing,
                }
                for rep in self.reputation
            ],
            "level": self.level,
            "experience": self.experience,
            "visited_realms": self.visited_realms,
            "created_at": self.created_at,
        }


class UniversalPlayerRouter:
    """
    Manages player state across multiverse realms.
    
    Responsible for:
    - Creating/loading universal players
    - Handling realm transitions
    - Maintaining cross-realm inventory
    - Tracking reputation across realms
    - Generating narrative context for Warbler
    """
    
    def __init__(self):
        self.players: Dict[str, UniversalPlayer] = {}
        self.player_by_name: Dict[str, str] = {}  # name -> player_id
        self.realm_players: Dict[str, List[str]] = {}  # realm_id -> [player_ids]
        self.transition_history: List[Dict[str, Any]] = []
        self.transition_events: List[Dict[str, Any]] = []  # Events for cross-game propagation
        self.narrative_events: List[Dict[str, Any]] = []  # Major story milestones
        self.npc_memory_store: Dict[str, List[Dict[str, Any]]] = {}  # npc_id -> memories about players
    
    def create_player(self, 
                      player_name: str,
                      character_race: str,
                      starting_realm: str,
                      character_class: str = "Wanderer") -> UniversalPlayer:
        """
        Create new universal player.
        
        Args:
            player_name: Human-readable name
            character_race: "human", "elf", "dwarf", etc.
            starting_realm: Initial realm ID (e.g., "sol_1")
            character_class: Optional character class
            
        Returns:
            UniversalPlayer instance
        """
        player_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        player = UniversalPlayer(
            player_id=player_id,
            player_name=player_name,
            character_race=character_race,
            character_class=character_class,
            active_realm=starting_realm,
            active_location="entry_point",
            created_at=now,
            last_realm_transition=now,
            visited_realms=[starting_realm],
            realm_history=[(starting_realm, now)],
        )
        
        # Initialize reputation with all factions
        for faction in ReputationFaction:
            reputation_score = ReputationScore(
                faction=faction,
                score=0,
                standing="neutral",
                last_modified=now,
            )
            player.reputation.append(reputation_score)
        
        # Store player
        self.players[player_id] = player
        self.player_by_name[player_name] = player_id
        
        # Add to realm roster
        if starting_realm not in self.realm_players:
            self.realm_players[starting_realm] = []
        self.realm_players[starting_realm].append(player_id)
        
        print(f"👤 Created player: {player_name} (ID: {player_id}) in {starting_realm}")
        
        return player
    
    def get_player(self, player_id: str) -> Optional[UniversalPlayer]:
        """Retrieve player by ID."""
        return self.players.get(player_id)
    
    def get_player_by_name(self, player_name: str) -> Optional[UniversalPlayer]:
        """Retrieve player by name."""
        player_id = self.player_by_name.get(player_name)
        return self.players.get(player_id) if player_id else None
    
    def transition_player(self, 
                         player_id: str,
                         source_realm: str,
                         target_realm: str,
                         narrative_context: str = "traveled") -> Tuple[bool, str]:
        """
        Transition player from one realm to another.
        
        Args:
            player_id: Player to transition
            source_realm: Current realm
            target_realm: Destination realm
            narrative_context: How they traveled (affects Warbler narration)
            
        Returns:
            (success: bool, message: str)
        """
        player = self.get_player(player_id)
        if not player:
            return False, f"Player {player_id} not found"
        
        if player.active_realm != source_realm:
            return False, f"Player not in {source_realm}"
        
        # Validation: can player travel?
        if not self._can_player_travel(player):
            return False, "Player cannot travel at this time"
        
        # Execute transition
        now = datetime.utcnow().isoformat()
        old_realm = player.active_realm
        
        # Update player state
        player.active_realm = target_realm
        player.active_location = "arrival_point"
        player.last_realm_transition = now
        
        if target_realm not in player.visited_realms:
            player.visited_realms.append(target_realm)
        
        player.realm_history.append((target_realm, now))
        
        # Update realm rosters
        if old_realm in self.realm_players:
            self.realm_players[old_realm].remove(player_id)
        if target_realm not in self.realm_players:
            self.realm_players[target_realm] = []
        self.realm_players[target_realm].append(player_id)
        
        # Record transition
        transition_record = {
            "player_id": player_id,
            "player_name": player.player_name,
            "source_realm": old_realm,
            "target_realm": target_realm,
            "context": narrative_context,
            "timestamp": now,
        }
        self.transition_history.append(transition_record)
        
        # Emit event for cross-game propagation
        event = {
            "event_type": "player_traveled",
            "event_id": f"travel_{player_id}_{int(datetime.utcnow().timestamp() * 1000)}",
            "data": {
                "player_id": player_id,
                "player_name": player.player_name,
                "source_realm": old_realm,
                "target_realm": target_realm,
                "context": narrative_context,
            }
        }
        self.transition_events.append(event)
        
        print(f"🚀 {player.player_name} traveled: {old_realm} → {target_realm}")
        
        return True, f"Player transitioned to {target_realm}"
    
    def _can_player_travel(self, player: UniversalPlayer) -> bool:
        """Validate if player can travel (basic checks)."""
        # Can expand with cooldowns, level requirements, etc.
        return True
    
    def modify_reputation(self,
                         player_id: str,
                         faction: ReputationFaction,
                         change: int) -> bool:
        """
        Modify player reputation with a faction.
        
        Args:
            player_id: Target player
            faction: Faction to modify
            change: Reputation change (-1000 to +1000)
            
        Returns:
            Success boolean
        """
        player = self.get_player(player_id)
        if not player:
            return False
        
        # Find reputation score for this faction
        rep_score = next(
            (r for r in player.reputation if r.faction == faction),
            None
        )
        if not rep_score:
            return False
        
        # Apply change
        rep_score.score = max(-1000, min(1000, rep_score.score + change))
        rep_score.last_modified = datetime.utcnow().isoformat()
        
        # Update standing
        if rep_score.score < -500:
            rep_score.standing = "despised"
        elif rep_score.score < -200:
            rep_score.standing = "disliked"
        elif rep_score.score < 200:
            rep_score.standing = "neutral"
        elif rep_score.score < 500:
            rep_score.standing = "liked"
        else:
            rep_score.standing = "revered"
        
        # Emit event
        event = {
            "event_type": "reputation_change",
            "event_id": f"rep_{player_id}_{faction.value}_{int(datetime.utcnow().timestamp() * 1000)}",
            "data": {
                "player_id": player_id,
                "player_name": player.player_name,
                "faction": faction.value,
                "change": change,
                "new_score": rep_score.score,
                "standing": rep_score.standing,
            }
        }
        self.transition_events.append(event)
        
        return True
    
    def add_item_to_inventory(self,
                              player_id: str,
                              item: InventoryItem) -> bool:
        """Add item to player inventory."""
        player = self.get_player(player_id)
        if not player:
            return False
        
        # Check if item already exists (stack)
        existing = next(
            (i for i in player.inventory if i.item_id == item.item_id),
            None
        )
        if existing:
            existing.quantity += item.quantity
        else:
            player.inventory.append(item)
        
        return True
    
    def get_warbler_context(self, player_id: str) -> Dict[str, Any]:
        """
        Generate Warbler context for NPC dialogue based on player state.
        
        This is what gets passed to Warbler for narrative generation.
        Warbler uses this to make NPCs aware of player's journey, reputation, etc.
        
        Returns:
            Dict suitable for Warbler context injection
        """
        player = self.get_player(player_id)
        if not player:
            return {}
        
        # Build world state based on player journey
        world_state = {
            "player_traveled_realms": len(player.visited_realms),
            "player_reputation_standing": {
                rep.faction.value: rep.standing for rep in player.reputation
            },
            "player_level": player.level,
            "player_has_legendary_items": any(
                item.rarity == "legendary" for item in player.inventory
            ),
            "player_experience": player.experience,
            "player_realm_count": len(set([entry[0] for entry in player.realm_history])),
        }
        
        # Narrative context
        narrative_context = {
            "character_journey": f"{player.player_name} has journeyed through {len(player.visited_realms)} realms",
            "reputation_arc": self._summarize_reputation(player),
            "inventory_summary": f"{len(player.inventory)} items",
            "quest_status": f"{len(player.active_quests)} active, {len(player.completed_quests)} completed",
        }
        
        return {
            "player_id": player_id,
            "player_name": player.player_name,
            "character_race": player.character_race,
            "character_class": player.character_class,
            "active_realm": player.active_realm,
            "world_state": world_state,
            "narrative_context": narrative_context,
            "visited_realms": player.visited_realms,
        }
    
    def _summarize_reputation(self, player: UniversalPlayer) -> str:
        """Create narrative summary of player reputation."""
        standings = [rep.standing for rep in player.reputation if rep.standing != "neutral"]
        if not standings:
            return "Unknown to the factions"
        return f"Known as {', '.join(set(standings))}"
    
    def get_realm_roster(self, realm_id: str) -> List[UniversalPlayer]:
        """Get all players currently in a realm."""
        player_ids = self.realm_players.get(realm_id, [])
        return [self.players[pid] for pid in player_ids if pid in self.players]
    
    def get_multiverse_stats(self) -> Dict[str, Any]:
        """Get statistics about player distribution across multiverse."""
        return {
            "total_players": len(self.players),
            "total_realms_visited": len(set(self.realm_players.keys())),
            "realm_distribution": {
                realm: len(player_ids)
                for realm, player_ids in self.realm_players.items()
            },
            "total_transitions": len(self.transition_history),
            "avg_realms_per_player": sum(len(p.visited_realms) for p in self.players.values()) / len(self.players) if self.players else 0,
        }
    
    def dump_audit_trail(self) -> Dict[str, Any]:
        """Full audit trail for player transitions."""
        return {
            "total_transitions": len(self.transition_history),
            "total_events": len(self.transition_events),
            "transitions": self.transition_history[-100:],  # Last 100 transitions
        }
    
    def emit_narrative_event(self,
                            player_id: str,
                            event_type: str,
                            title: str,
                            description: str,
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Emit a major narrative event for player (milestone, achievement, etc).
        
        These events are used by Warbler to build narrative awareness.
        NPCs can reference these milestones in dialogue.
        
        Args:
            player_id: Player who experienced the event
            event_type: Type of event (achievement, milestone, discovery, conflict)
            title: Short title of event
            description: Longer narrative description
            metadata: Additional context
            
        Returns:
            Event record that was emitted
        """
        player = self.get_player(player_id)
        if not player:
            return {}
        
        now = datetime.utcnow().isoformat()
        event = {
            "event_id": f"narrative_{player_id}_{event_type}_{int(datetime.utcnow().timestamp() * 1000)}",
            "player_id": player_id,
            "player_name": player.player_name,
            "event_type": event_type,
            "title": title,
            "description": description,
            "active_realm": player.active_realm,
            "timestamp": now,
            "metadata": metadata or {}
        }
        self.narrative_events.append(event)
        return event
    
    def get_npc_memory_about_player(self, npc_id: str, player_id: str) -> Dict[str, Any]:
        """
        What does this NPC 'know' about this player based on their journey?
        
        Returns dict with player info suitable for NPC personality/dialogue generation.
        
        Args:
            npc_id: NPC entity ID
            player_id: Player to query
            
        Returns:
            Memory context for NPC dialogue generation
        """
        player = self.get_player(player_id)
        if not player:
            return {}
        
        # Get memories about this player from NPC store
        memories = self.npc_memory_store.get(npc_id, [])
        player_memories = [m for m in memories if m.get("player_id") == player_id]
        
        # Build narrative awareness for NPC
        reputation_standing = {
            rep.faction.value: rep.standing for rep in player.reputation
        }
        
        return {
            "player_id": player_id,
            "player_name": player.player_name,
            "player_race": player.character_race,
            "player_class": player.character_class,
            "realms_visited": player.visited_realms,
            "current_realm": player.active_realm,
            "reputation_standing": reputation_standing,
            "level": player.level,
            "memories": player_memories,
            "legendary_items": [
                item.name for item in player.inventory 
                if item.rarity == "legendary"
            ],
            "personality_modifiers": self._calculate_personality_modifiers(reputation_standing),
        }
    
    def _calculate_personality_modifiers(self, reputation_standing: Dict[str, str]) -> Dict[str, str]:
        """
        Based on player reputation, what personality should NPC adopt?
        
        Example:
            If player is "revered" by THE_WANDERERS but "despised" by REALM_KEEPERS,
            Wanderer NPCs should be deferential, Keepers should be hostile.
        """
        modifiers = {}
        for faction, standing in reputation_standing.items():
            if standing == "revered":
                modifiers[faction] = "deferential"
            elif standing == "liked":
                modifiers[faction] = "friendly"
            elif standing == "neutral":
                modifiers[faction] = "neutral"
            elif standing == "disliked":
                modifiers[faction] = "suspicious"
            elif standing == "despised":
                modifiers[faction] = "hostile"
        return modifiers
    
    def store_npc_memory(self, npc_id: str, player_id: str, 
                        memory_type: str, content: str, 
                        metadata: Dict[str, Any] = None) -> bool:
        """
        Store a memory about a player in NPC's memory.
        
        Used by city simulation to track NPC awareness of player actions.
        
        Args:
            npc_id: NPC who is remembering
            player_id: Player being remembered
            memory_type: Type of memory (encounter, rumor, achievement)
            content: Memory content
            metadata: Additional data
            
        Returns:
            Success boolean
        """
        if npc_id not in self.npc_memory_store:
            self.npc_memory_store[npc_id] = []
        
        memory = {
            "memory_id": f"mem_{npc_id}_{player_id}_{int(datetime.utcnow().timestamp() * 1000)}",
            "player_id": player_id,
            "memory_type": memory_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.npc_memory_store[npc_id].append(memory)
        return True
    
    def get_warbler_dialogue_context(self, player_id: str, npc_id: str = None) -> Dict[str, Any]:
        """
        Enhanced Warbler context for dialogue generation.
        
        Includes both player state and NPC memory to create personalized dialogue.
        
        Args:
            player_id: Player to generate context for
            npc_id: Optional NPC ID - if provided, includes NPC-specific memories
            
        Returns:
            Complete context dict for Warbler dialogue generation
        """
        base_context = self.get_warbler_context(player_id)
        
        if npc_id:
            npc_memory = self.get_npc_memory_about_player(npc_id, player_id)
            base_context["npc_memory"] = npc_memory
        
        # Add narrative events for context
        player_narrative_events = [
            e for e in self.narrative_events 
            if e.get("player_id") == player_id
        ]
        base_context["recent_narrative_events"] = player_narrative_events[-5:]  # Last 5 events
        
        return base_context