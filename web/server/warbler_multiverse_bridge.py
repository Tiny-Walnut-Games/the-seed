"""
Warbler Multiverse Bridge: Player Context to NPC Dialogue

Bridges UniversalPlayerRouter state with Warbler NPC dialogue generation.
Enables NPCs to be aware of player's cross-realm journey, reputation, and achievements.

Key Features:
- Converts player multiverse state into Warbler personality/context injections
- Tracks NPC memories of player interactions
- Generates reputation-based dialogue modifiers
- Cross-realm event propagation for dialogue triggers
- Personality injection based on player standing with factions

Example:
    bridge = WarblerMultiverseBridge(player_router)
    
    # Generate dialogue context for NPC
    context = bridge.get_dialogue_context(player_id, npc_id)
    
    # Warbler uses this context for narrative-aware responses
    response = warbler.generate_dialogue(
        user_input="Who are you?",
        context=context
    )
    # NPC might respond: "Ah, the renowned traveler! Tales of your deeds have reached even here..."
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DialogueModifierType(Enum):
    """Types of dialogue modifiers based on player reputation."""
    REVERENT = "reverent"  # Extremely positive
    DEFERENTIAL = "deferential"  # Respectful
    FRIENDLY = "friendly"  # Warm and welcoming
    NEUTRAL = "neutral"  # No special treatment
    SUSPICIOUS = "suspicious"  # Wary
    HOSTILE = "hostile"  # Aggressive


@dataclass
class NPCDialoguePersonality:
    """NPC personality influenced by player state."""
    base_personality: str  # NPC's inherent personality
    reputation_modifiers: Dict[str, str]  # faction -> modifier type
    player_acknowledgment: str  # How NPC acknowledges player
    dialogue_formality: str  # "formal", "casual", "hostile", "reverent"
    emotional_tone: str  # mood the NPC should adopt
    physical_behavior: str  # How NPC treats player (bows, sneers, etc.)


@dataclass
class DialogueContext:
    """Complete context for Warbler to generate player-aware dialogue."""
    player_id: str
    player_name: str
    npc_id: str
    npc_name: str
    
    # Player state
    player_journey: str  # Narrative of player's travels
    player_reputation: Dict[str, str]  # faction -> standing
    player_achievements: List[str]  # Major accomplishments
    
    # NPC state
    npc_personality: NPCDialoguePersonality
    npc_memories: List[Dict[str, Any]]  # What NPC remembers about player
    
    # Dialogue context
    conversation_history: List[Tuple[str, str]]  # (role, text) pairs
    suggested_topics: List[str]  # Things NPC could ask about
    dialogue_style_hints: Dict[str, Any]  # Style guidance for Warbler


class WarblerMultiverseBridge:
    """
    Bridge between UniversalPlayerRouter and Warbler dialogue generation.
    
    Converts multiverse player state into context for NPC dialogue generation.
    """
    
    def __init__(self, player_router):
        """
        Initialize bridge.
        
        Args:
            player_router: UniversalPlayerRouter instance
        """
        self.router = player_router
        self.npc_registry: Dict[str, Dict[str, Any]] = {}  # npc_id -> NPC data
        self.dialogue_history: List[Dict[str, Any]] = []  # Full dialogue log
        self.personality_templates: Dict[str, str] = self._init_personality_templates()
    
    def _init_personality_templates(self) -> Dict[str, str]:
        """Initialize base personality templates for NPCs."""
        return {
            "scholar": "Intellectually curious, speaks formally, values knowledge and truth",
            "merchant": "Shrewd, talkative, values profit and reputation, gossip-prone",
            "warrior": "Honorable, direct, values strength and loyalty, respects capable fighters",
            "mystic": "Mysterious, poetic, speaks in riddles, values spiritual wisdom",
            "townsfolk": "Friendly, curious, gossips easily, values community and news",
            "guard": "Professional, cautious, values order and security, suspicious of strangers",
        }
    
    def register_npc(self, npc_id: str, npc_name: str, 
                     realm_id: str, personality_template: str,
                     faction_allegiance: str = "neutral") -> bool:
        """
        Register an NPC with the bridge.
        
        Args:
            npc_id: Unique NPC identifier
            npc_name: NPC display name
            realm_id: Which realm this NPC inhabits
            personality_template: Base personality type
            faction_allegiance: Which faction (if any) this NPC favors
            
        Returns:
            Success boolean
        """
        self.npc_registry[npc_id] = {
            "npc_id": npc_id,
            "npc_name": npc_name,
            "realm_id": realm_id,
            "personality_template": personality_template,
            "faction_allegiance": faction_allegiance,
            "last_player_interaction": {},
            "created_at": datetime.utcnow().isoformat(),
        }
        return True
    
    def set_npc_mood(self, npc_id: str, mood: str) -> bool:
        """
        Set the emotional mood of an NPC.
        
        Moods affect dialogue formality and tone.
        
        Args:
            npc_id: NPC identifier
            mood: Mood state ("cheerful", "neutral", "grumpy", "excited", "thoughtful")
            
        Returns:
            Success boolean
        """
        if npc_id not in self.npc_registry:
            raise ValueError(f"NPC {npc_id} not registered")
        
        valid_moods = ["cheerful", "neutral", "grumpy", "excited", "thoughtful"]
        if mood not in valid_moods:
            raise ValueError(f"Invalid mood '{mood}'. Must be one of: {valid_moods}")
        
        self.npc_registry[npc_id]["mood"] = mood
        self.npc_registry[npc_id]["mood_updated_at"] = datetime.utcnow().isoformat()
        return True
    
    def record_npc_player_transaction(self,
                                     npc_id: str,
                                     player_id: str,
                                     transaction_type: str,
                                     items: List[str] = None) -> bool:
        """
        Record a transaction between NPC and player (sale, purchase, quest reward, etc.).
        
        Builds history for npc_history slot: "sold you 5 items, received 3 items"
        
        Args:
            npc_id: NPC involved in transaction
            player_id: Player involved in transaction
            transaction_type: "sold", "bought", "gifted", "quest_reward"
            items: List of item names/ids involved
            
        Returns:
            Success boolean
        """
        if npc_id not in self.npc_registry:
            raise ValueError(f"NPC {npc_id} not registered")
        
        # Initialize transaction history if not present
        if "transactions" not in self.npc_registry[npc_id]:
            self.npc_registry[npc_id]["transactions"] = {}
        
        if player_id not in self.npc_registry[npc_id]["transactions"]:
            self.npc_registry[npc_id]["transactions"][player_id] = []
        
        # Record transaction
        transaction = {
            "type": transaction_type,
            "items": items or [],
            "timestamp": datetime.utcnow().isoformat(),
            "item_count": len(items) if items else 0
        }
        
        self.npc_registry[npc_id]["transactions"][player_id].append(transaction)
        return True
    
    def get_dialogue_context(self, 
                           player_id: str, 
                           npc_id: str,
                           conversation_history: List[Tuple[str, str]] = None) -> DialogueContext:
        """
        Generate complete dialogue context for Warbler.
        
        Combines player multiverse state with NPC memory to create personalized context.
        
        Args:
            player_id: Target player
            npc_id: Target NPC
            conversation_history: Current conversation so far
            
        Returns:
            DialogueContext suitable for Warbler dialogue generation
        """
        # Get player and NPC data
        player = self.router.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        npc_data = self.npc_registry.get(npc_id)
        if not npc_data:
            raise ValueError(f"NPC {npc_id} not registered")
        
        # Build player journey narrative
        journey = self._build_player_journey(player)
        
        # Build player reputation dict
        reputation = {
            rep.faction.value: rep.standing for rep in player.reputation
        }
        
        # Extract player achievements from narrative events
        player_achievements = self._extract_achievements(player_id)
        
        # Get NPC personality modified by player reputation
        npc_personality = self._calculate_npc_personality(
            npc_data,
            reputation,
            player.level
        )
        
        # Get NPC memories of this player
        npc_memories = self.router.get_npc_memory_about_player(npc_id, player_id)
        
        # Generate suggested dialogue topics
        suggested_topics = self._generate_dialogue_topics(
            player,
            npc_data,
            reputation,
            player_achievements
        )
        
        # Build dialogue context
        context = DialogueContext(
            player_id=player_id,
            player_name=player.player_name,
            npc_id=npc_id,
            npc_name=npc_data["npc_name"],
            player_journey=journey,
            player_reputation=reputation,
            player_achievements=player_achievements,
            npc_personality=npc_personality,
            npc_memories=npc_memories.get("memories", []),
            conversation_history=conversation_history or [],
            suggested_topics=suggested_topics,
            dialogue_style_hints={
                "acknowledging_player": True,
                "personality_modifiers": npc_personality.reputation_modifiers,
                "formality_level": npc_personality.dialogue_formality,
            }
        )
        
        return context
    
    def _build_player_journey(self, player) -> str:
        """Create narrative summary of player's cross-realm journey."""
        if not player.visited_realms:
            return f"{player.player_name} is new to the multiverse"
        
        journey_parts = [
            f"{player.player_name}, a {player.character_race.lower()} {player.character_class.lower()},"
        ]
        
        if len(player.visited_realms) == 1:
            journey_parts.append(f"is from {player.visited_realms[0]}")
        else:
            journey_parts.append(
                f"has traveled through {len(player.visited_realms)} realms: "
                f"{', '.join(player.visited_realms)}"
            )
        
        if player.level > 1:
            journey_parts.append(f"and has reached level {player.level}")
        
        return " ".join(journey_parts)
    
    def _extract_achievements(self, player_id: str) -> List[str]:
        """Extract major achievements from player's narrative events."""
        achievements = []
        player_events = [
            e for e in self.router.narrative_events 
            if e.get("player_id") == player_id
        ]
        
        for event in player_events[-10:]:  # Last 10 events
            if event.get("event_type") in ["achievement", "milestone", "discovery"]:
                achievements.append(event.get("title", "Unknown Achievement"))
        
        return achievements
    
    def _calculate_npc_personality(self,
                                  npc_data: Dict[str, Any],
                                  player_reputation: Dict[str, str],
                                  player_level: int) -> NPCDialoguePersonality:
        """
        Calculate NPC personality modified by player state.
        
        If NPC is from REALM_KEEPERS faction and player is "revered" by them,
        NPC should be deferential. If player is "despised" by them, NPC hostile.
        """
        npc_faction = npc_data.get("faction_allegiance", "neutral")
        base_personality = npc_data.get("personality_template", "townsfolk")
        
        # Determine how NPC should treat player based on reputation with NPC's faction
        player_standing_with_faction = player_reputation.get(npc_faction, "neutral")
        
        # Calculate modifier
        if player_standing_with_faction == "revered":
            modifier = DialogueModifierType.REVERENT
            formality = "reverent"
            tone = "awed"
            behavior = "bows respectfully"
        elif player_standing_with_faction == "liked":
            modifier = DialogueModifierType.FRIENDLY
            formality = "formal"
            tone = "warm"
            behavior = "nods respectfully"
        elif player_standing_with_faction == "neutral":
            modifier = DialogueModifierType.NEUTRAL
            formality = "casual"
            tone = "neutral"
            behavior = "greets normally"
        elif player_standing_with_faction == "disliked":
            modifier = DialogueModifierType.SUSPICIOUS
            formality = "casual"
            tone = "wary"
            behavior = "eyes suspiciously"
        else:  # despised
            modifier = DialogueModifierType.HOSTILE
            formality = "hostile"
            tone = "angry"
            behavior = "sneers at"
        
        # Level-based respect modifier (high-level players get more respect)
        if player_level >= 10:
            if modifier == DialogueModifierType.NEUTRAL:
                modifier = DialogueModifierType.DEFERENTIAL
            formality = "formal"  # Slightly more formal for high-level players
        
        # Build personality
        personality = NPCDialoguePersonality(
            base_personality=base_personality,
            reputation_modifiers={npc_faction: modifier.value},
            player_acknowledgment=f"You have {player_standing_with_faction} reputation",
            dialogue_formality=formality,
            emotional_tone=tone,
            physical_behavior=behavior,
        )
        
        return personality
    
    def _generate_dialogue_topics(self,
                                 player,
                                 npc_data: Dict[str, Any],
                                 reputation: Dict[str, str],
                                 achievements: List[str]) -> List[str]:
        """
        Generate dialogue topics NPC could ask about.
        
        Topics based on player's journey, reputation, and achievements.
        """
        topics = []
        
        # If player has traveled multiple realms, ask about that
        if len(player.visited_realms) > 1:
            topics.append(f"What was it like traveling through {', '.join(player.visited_realms[:-1])}?")
        
        # If player has achievements, ask about them
        if achievements:
            topics.append(f"I hear you've accomplished great things. Tell me about {achievements[-1]}?")
        
        # If player has specific reputation, reference it
        for faction, standing in reputation.items():
            if standing not in ["neutral", "unknown"]:
                topics.append(f"I've heard you're {standing} among the {faction.replace('_', ' ')}. How did you manage that?")
        
        # NPC-specific topics
        npc_personality = npc_data.get("personality_template", "townsfolk")
        if npc_personality == "merchant":
            topics.append("Any legendary items for trade?")
        elif npc_personality == "scholar":
            topics.append("What knowledge have you gathered in your travels?")
        elif npc_personality == "warrior":
            topics.append("Have you seen any worthy battles?")
        
        return topics or ["So, where are you from?", "What brings you here?"]
    
    def log_dialogue(self, 
                    player_id: str, 
                    npc_id: str,
                    player_message: str,
                    npc_response: str,
                    context_used: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Log a dialogue exchange for audit and memory.
        
        Args:
            player_id: Player in dialogue
            npc_id: NPC in dialogue
            player_message: What player said
            npc_response: What NPC responded
            context_used: Dialogue context that was used
            
        Returns:
            Dialogue record
        """
        record = {
            "dialogue_id": f"dlg_{player_id}_{npc_id}_{int(datetime.utcnow().timestamp() * 1000)}",
            "player_id": player_id,
            "npc_id": npc_id,
            "player_message": player_message,
            "npc_response": npc_response,
            "timestamp": datetime.utcnow().isoformat(),
            "context_used": context_used or {}
        }
        self.dialogue_history.append(record)
        
        # Store as NPC memory
        npc = self.npc_registry.get(npc_id)
        if npc:
            self.router.store_npc_memory(
                npc_id=npc_id,
                player_id=player_id,
                memory_type="dialogue",
                content=f"Player said: {player_message[:100]}...",
                metadata={"npc_response": npc_response[:100]}
            )
        
        return record
    
    def get_dialogue_history(self, player_id: str = None, npc_id: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve dialogue history, optionally filtered.
        
        Args:
            player_id: Optional player filter
            npc_id: Optional NPC filter
            
        Returns:
            List of dialogue records
        """
        history = self.dialogue_history
        
        if player_id:
            history = [d for d in history if d.get("player_id") == player_id]
        if npc_id:
            history = [d for d in history if d.get("npc_id") == npc_id]
        
        return history[-100:]  # Last 100 dialogues
    
    def broadcast_player_arrival(self, player_id: str, realm_id: str, arrival_type: str = "normal") -> List[str]:
        """
        When a player arrives in a realm, broadcast awareness to NPCs in that realm.
        
        This creates narrative opportunities - NPCs might comment on player's arrival.
        
        Args:
            player_id: Player arriving
            realm_id: Which realm
            arrival_type: Type of arrival (normal, portal, wounded, etc.)
            
        Returns:
            List of NPC IDs who were notified
        """
        player = self.router.get_player(player_id)
        if not player:
            return []
        
        # Find all NPCs in this realm
        npcs_in_realm = [
            npc for npc in self.npc_registry.values()
            if npc.get("realm_id") == realm_id
        ]
        
        # Notify each NPC
        notified = []
        for npc in npcs_in_realm:
            npc_id = npc["npc_id"]
            
            # Store arrival as memory
            self.router.store_npc_memory(
                npc_id=npc_id,
                player_id=player_id,
                memory_type="arrival",
                content=f"{player.player_name} arrived via {arrival_type}",
                metadata={"arrival_type": arrival_type}
            )
            
            notified.append(npc_id)
        
        return notified