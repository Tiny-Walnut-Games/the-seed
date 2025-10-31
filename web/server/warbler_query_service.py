"""
Warbler Query Service: Cross-Realm NPC Query Engine

Independent service for querying NPC state, generating responses, and managing
conversations across multiple game realms with narrative awareness.

Features:
- Query NPC responses to player input
- Track NPC state across realms
- Route queries to appropriate NPCs
- Manage conversation sessions
- Emit dialogue events for story propagation
- Cache NPC responses for performance

Example:
    query_svc = WarblerQueryService(player_router, warbler_bridge)
    
    # Query NPC response
    response = query_svc.query_npc(
        player_id="uuid...",
        npc_id="npc_merchant_001",
        user_input="Do you know of the legendary sword?",
        realm_id="sol_1"
    )
    
    # Returns: {
    #   "npc_response": "Aye, I've heard tales...",
    #   "dialogue_context": {...},
    #   "suggested_follow_ups": [...]
    # }
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid
from warbler_pack_loader import WarblerPackLoader


class QueryStatus(Enum):
    """Status of a dialogue query."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    CACHED = "cached"


@dataclass
class NPCQuery:
    """A query to an NPC."""
    query_id: str
    player_id: str
    npc_id: str
    realm_id: str
    user_input: str
    status: QueryStatus
    timestamp: str
    warbler_context: Dict[str, Any] = None
    response: str = ""
    follow_ups: List[str] = None


@dataclass
class ConversationSession:
    """A conversation between player and NPC."""
    session_id: str
    player_id: str
    npc_id: str
    realm_id: str
    start_time: str
    last_activity: str
    messages: List[Tuple[str, str]]  # (speaker, message) pairs
    narrative_weight: int = 0  # Importance of this conversation


class WarblerQueryService:
    """
    Independent service for querying Warbler across realms.
    
    Handles NPC query routing, response generation, and conversation management.
    """
    
    def __init__(self, player_router, warbler_bridge, enable_cache: bool = True, 
                 pack_loader: Optional[WarblerPackLoader] = None):
        """
        Initialize query service.
        
        Args:
            player_router: UniversalPlayerRouter instance
            warbler_bridge: WarblerMultiverseBridge instance
            enable_cache: Whether to cache NPC responses
            pack_loader: Optional WarblerPackLoader for template-based dialogue.
                        If None, will use fallback template generation.
        """
        self.router = player_router
        self.bridge = warbler_bridge
        self.enable_cache = enable_cache
        self.pack_loader = pack_loader
        
        # Storage
        self.queries: Dict[str, NPCQuery] = {}  # query_id -> NPCQuery
        self.sessions: Dict[str, ConversationSession] = {}  # session_id -> ConversationSession
        self.response_cache: Dict[str, str] = {}  # cache_key -> response
        
        # Statistics
        self.total_queries = 0
        self.cache_hits = 0
        self.avg_response_time_ms = 0.0
        self.pack_templates_used = 0  # Track pack usage
    
    def start_conversation(self, 
                          player_id: str, 
                          npc_id: str,
                          realm_id: str) -> ConversationSession:
        """
        Start a new conversation session between player and NPC.
        
        Args:
            player_id: Player initiating conversation
            npc_id: NPC being spoken to
            realm_id: Realm where conversation occurs
            
        Returns:
            ConversationSession
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        session = ConversationSession(
            session_id=session_id,
            player_id=player_id,
            npc_id=npc_id,
            realm_id=realm_id,
            start_time=now,
            last_activity=now,
            messages=[],
            narrative_weight=0
        )
        
        self.sessions[session_id] = session
        
        # Broadcast player arrival to NPC
        self.bridge.broadcast_player_arrival(player_id, realm_id)
        
        return session
    
    def query_npc(self,
                 player_id: str,
                 npc_id: str,
                 user_input: str,
                 realm_id: str,
                 session_id: str = None) -> Dict[str, Any]:
        """
        Query an NPC for response to player input.
        
        This is the main entry point for dialogue generation.
        
        Args:
            player_id: Player asking question
            npc_id: NPC being queried
            user_input: What player said
            realm_id: Realm context
            session_id: Optional conversation session
            
        Returns:
            Dict with response and context
        """
        import time
        start_time = time.time()
        
        query_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Check cache first
        cache_key = f"{npc_id}:{user_input[:50]}"
        if self.enable_cache and cache_key in self.response_cache:
            self.cache_hits += 1
            cached_response = self.response_cache[cache_key]
            return {
                "query_id": query_id,
                "status": "cached",
                "npc_response": cached_response,
                "response_time_ms": 0,
            }
        
        try:
            # Generate dialogue context
            dialogue_context = self.bridge.get_dialogue_context(player_id, npc_id)
            
            # In production, this would call actual Warbler
            # For now, generate a response based on context
            npc_response = self._generate_npc_response(
                dialogue_context,
                user_input,
                npc_id
            )
            
            # Cache response
            if self.enable_cache:
                self.response_cache[cache_key] = npc_response
            
            # Create query record
            query = NPCQuery(
                query_id=query_id,
                player_id=player_id,
                npc_id=npc_id,
                realm_id=realm_id,
                user_input=user_input,
                status=QueryStatus.COMPLETE,
                timestamp=now,
                warbler_context=dialogue_context.__dict__ if dialogue_context else {},
                response=npc_response,
                follow_ups=self._generate_follow_ups(dialogue_context, npc_response)
            )
            self.queries[query_id] = query
            
            # Update session if provided
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
                session.messages.append(("player", user_input))
                session.messages.append(("npc", npc_response))
                session.last_activity = now
                session.narrative_weight += 1
            
            # Log dialogue for memory
            self.bridge.log_dialogue(player_id, npc_id, user_input, npc_response)
            
            # Emit narrative event if significant
            self._emit_dialogue_event(player_id, npc_id, user_input, npc_response, realm_id)
            
            response_time_ms = (time.time() - start_time) * 1000
            self.total_queries += 1
            self.avg_response_time_ms = (
                (self.avg_response_time_ms * (self.total_queries - 1) + response_time_ms) 
                / self.total_queries
            )
            
            return {
                "query_id": query_id,
                "status": "complete",
                "npc_response": npc_response,
                "follow_ups": query.follow_ups,
                "response_time_ms": response_time_ms,
                "dialogue_context": {
                    "player_journey": dialogue_context.player_journey,
                    "player_reputation": dialogue_context.player_reputation,
                    "npc_personality": dialogue_context.npc_personality.__dict__,
                }
            }
            
        except Exception as e:
            return {
                "query_id": query_id,
                "status": "error",
                "error": str(e),
                "npc_response": f"[NPC cannot respond: {str(e)}]"
            }
    
    def _generate_npc_response(self, 
                               dialogue_context, 
                               user_input: str,
                               npc_id: str) -> str:
        """
        Generate NPC response based on dialogue context.
        
        If pack_loader is available, uses real Warbler pack templates with slot-filling
        and reputation-aware selection. Otherwise, falls back to template generation.
        
        Args:
            dialogue_context: DialogueContext from bridge
            user_input: Player's input
            npc_id: NPC generating response
            
        Returns:
            NPC response text
        """
        npc_data = self.bridge.npc_registry.get(npc_id, {})
        personality = dialogue_context.npc_personality
        
        # Try to use real Warbler pack templates if available
        if self.pack_loader:
            return self._generate_response_from_packs(dialogue_context, user_input, npc_id)
        
        # Fallback: Generate hardcoded template-based responses
        return self._generate_fallback_response(dialogue_context, user_input, npc_id)
    
    def _generate_response_from_packs(self, dialogue_context, user_input: str, npc_id: str) -> str:
        """
        Generate response using loaded Warbler pack templates.
        
        Uses reputation tier to select appropriate templates, then fills slots
        with dialogue context variables.
        
        Args:
            dialogue_context: DialogueContext from bridge
            user_input: Player's input
            npc_id: NPC generating response
            
        Returns:
            Slot-filled template response
        """
        npc_data = self.bridge.npc_registry.get(npc_id, {})
        personality = dialogue_context.npc_personality
        
        # Map dialogue formality to reputation tier for template selection
        formality_to_tier = {
            "reverent": "revered",
            "friendly": "trusted",
            "neutral": "neutral",
            "suspicious": "suspicious",
            "hostile": "hostile",
        }
        
        reputation_tier = formality_to_tier.get(personality.dialogue_formality, "neutral")
        
        # Determine context tags (what kind of dialogue is this?)
        context_tags = self._determine_dialogue_tags(user_input, dialogue_context)
        
        # Select template based on reputation tier
        template = self.pack_loader.select_template_for_reputation(
            reputation_tier=reputation_tier,
            context_tags=context_tags
        )
        
        if template:
            # Extract location from player journey (first realm mentioned)
            location = "unknown lands"
            if dialogue_context.player_journey:
                # Try to extract realm name from journey
                journey_lower = dialogue_context.player_journey.lower()
                for realm in ["sol_1", "sol_2", "sol_3", "realm", "kingdom"]:
                    if realm in journey_lower:
                        location = realm.replace("_", " ").title()
                        break
            
            # Build slot values from dialogue context
            slot_values = {
                "user_name": dialogue_context.player_name,
                "user_title": self._get_player_title(dialogue_context),
                "location": location,
                "location_type": "realm",
                "npc_name": dialogue_context.npc_name or npc_data.get("npc_name", "NPC"),
                "npc_role": npc_data.get("npc_role", "traveler"),
                "time_of_day": "day",  # Could be expanded from game state
                "item_types": "wondrous items",  # Could be expanded from NPC inventory
            }
            
            # Fill template slots
            response = self.pack_loader.fill_slots(template, slot_values)
            self.pack_templates_used += 1
            return response
        
        # If no template found, use fallback
        return self._generate_fallback_response(dialogue_context, user_input, npc_id)
    
    def _generate_fallback_response(self, dialogue_context, user_input: str, npc_id: str) -> str:
        """
        Generate hardcoded template-based response (fallback).
        
        Used when pack loader is unavailable or no matching templates found.
        """
        personality = dialogue_context.npc_personality
        
        # Generate response template based on personality
        openings = {
            "reverent": [
                f"Ah, {dialogue_context.player_name}! Your fame precedes you.",
                f"Greetings, legendary one! I am honored.",
                f"The great {dialogue_context.player_name} speaks to me?",
            ],
            "friendly": [
                f"Well met, {dialogue_context.player_name}!",
                f"Good to see you again, friend!",
                f"Hello there, traveler!",
            ],
            "neutral": [
                f"You've got my attention.",
                f"What can I do for you?",
                f"Hmm, what brings you here?",
            ],
            "hostile": [
                f"I know who you are, {dialogue_context.player_name}.",
                f"What do you want?",
                f"Don't cause trouble here.",
            ],
        }
        
        key = personality.dialogue_formality
        opening = openings.get(key, openings["neutral"])[0]
        
        # Add context-aware content
        if dialogue_context.player_achievements:
            content = f"I've heard of your {dialogue_context.player_achievements[-1]}."
        elif dialogue_context.player_reputation:
            reps = [f"{stand}" for stand in dialogue_context.player_reputation.values() if stand != "neutral"]
            if reps:
                content = f"You are known as {reps[0]} in these parts."
            else:
                content = "What brings you to my realm?"
        else:
            content = "What brings you here?"
        
        return f"{opening} {content}"
    
    def _determine_dialogue_tags(self, user_input: str, dialogue_context) -> List[str]:
        """
        Determine dialogue context tags based on user input and context.
        
        Returns tags like ["greeting", "help_request", "trade_inquiry", etc.
        """
        tags = []
        user_lower = user_input.lower()
        
        # Simple keyword-based tagging
        if any(word in user_lower for word in ["hello", "hi", "greet", "meet"]):
            tags.append("greeting")
        if any(word in user_lower for word in ["help", "assist", "need", "can you"]):
            tags.append("help_request")
        if any(word in user_lower for word in ["trade", "sell", "buy", "merchant", "item"]):
            tags.append("trade_inquiry")
        if any(word in user_lower for word in ["quest", "mission", "task", "objective"]):
            tags.append("quest")
        if any(word in user_lower for word in ["goodbye", "farewell", "bye", "leave"]):
            tags.append("farewell")
        
        # Default to general_conversation if nothing specific
        if not tags:
            tags.append("general_conversation")
        
        return tags
    
    def _get_player_title(self, dialogue_context) -> str:
        """Get formal title for player."""
        # Could be based on achievements, faction standing, etc.
        if dialogue_context.player_achievements:
            return "Renowned One"
        return "Traveler"
    
    def _generate_follow_ups(self, dialogue_context, npc_response: str) -> List[str]:
        """Generate suggested follow-up questions for player."""
        follow_ups = dialogue_context.suggested_topics[:3] if dialogue_context else []
        return follow_ups or ["Tell me more.", "What else?", "And then?"]
    
    def _emit_dialogue_event(self, player_id: str, npc_id: str, 
                            user_input: str, response: str, realm_id: str):
        """
        Emit narrative event from significant dialogue.
        
        Major conversations can trigger narrative events.
        """
        # Determine if this is significant
        if len(response) > 100:  # Longer response = significant
            npc_data = self.bridge.npc_registry.get(npc_id, {})
            npc_name = npc_data.get("npc_name", "Unknown NPC")
            
            self.router.emit_narrative_event(
                player_id=player_id,
                event_type="dialogue",
                title=f"Met with {npc_name}",
                description=f"Had a meaningful conversation with {npc_name} in {realm_id}",
                metadata={"npc_id": npc_id, "realm_id": realm_id}
            )
    
    def end_conversation(self, session_id: str) -> Dict[str, Any]:
        """
        End a conversation session.
        
        Args:
            session_id: Session to end
            
        Returns:
            Session summary
        """
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        now = datetime.utcnow().isoformat()
        
        duration_str = f"Session lasted from {session.start_time} to {now}"
        
        summary = {
            "session_id": session_id,
            "player_id": session.player_id,
            "npc_id": session.npc_id,
            "message_count": len(session.messages),
            "narrative_weight": session.narrative_weight,
            "summary": duration_str,
        }
        
        # Emit end-of-conversation event
        npc_data = self.bridge.npc_registry.get(session.npc_id, {})
        npc_name = npc_data.get("npc_name", "Unknown")
        self.router.emit_narrative_event(
            player_id=session.player_id,
            event_type="conversation_end",
            title=f"Parted ways with {npc_name}",
            description=f"Had {len(session.messages) // 2} exchanges with {npc_name}",
            metadata={"session_id": session_id}
        )
        
        del self.sessions[session_id]
        return summary
    
    def get_realm_npc_list(self, realm_id: str) -> List[Dict[str, str]]:
        """
        Get all NPCs in a given realm.
        
        Args:
            realm_id: Realm to query
            
        Returns:
            List of NPC info dicts
        """
        npcs = [
            {
                "npc_id": npc["npc_id"],
                "npc_name": npc["npc_name"],
                "personality": npc.get("personality_template", "unknown"),
                "faction": npc.get("faction_allegiance", "neutral"),
            }
            for npc in self.bridge.npc_registry.values()
            if npc.get("realm_id") == realm_id
        ]
        return npcs
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get query service statistics.
        
        Returns:
            Service performance metrics
        """
        return {
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits if self.enable_cache else 0,
            "cache_hit_rate": (self.cache_hits / max(self.total_queries, 1)) * 100 if self.enable_cache else 0,
            "avg_response_time_ms": self.avg_response_time_ms,
            "active_sessions": len(self.sessions),
            "cached_responses": len(self.response_cache) if self.enable_cache else 0,
        }