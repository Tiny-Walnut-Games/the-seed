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
                 pack_loader: Optional[WarblerPackLoader] = None,
                 embedding_service: Optional[Any] = None):
        """
        Initialize query service.
        
        Args:
            player_router: UniversalPlayerRouter instance
            warbler_bridge: WarblerMultiverseBridge instance
            enable_cache: Whether to cache NPC responses
            pack_loader: Optional WarblerPackLoader for template-based dialogue.
                        If None, will use fallback template generation.
            embedding_service: Optional embedding service for semantic search (Phase 3).
                              If provided, enables semantic similarity matching.
        """
        self.router = player_router
        self.bridge = warbler_bridge
        self.enable_cache = enable_cache
        self.pack_loader = pack_loader
        self.embedding_service = embedding_service
        
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
        
        Phase 2: Reputation tier + keyword-based template selection
        Phase 3: Semantic similarity search with FAISS + embeddings
        
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
        
        # Phase 3: Try semantic search first if embeddings available
        if self.pack_loader.embedding_service:
            return self._generate_response_semantic(dialogue_context, user_input, npc_id, reputation_tier)
        
        # Phase 2: Fall back to keyword-based template selection
        return self._generate_response_keyword_based(dialogue_context, user_input, npc_id, reputation_tier)
    
    def _generate_response_semantic(self, dialogue_context, user_input: str, npc_id: str, reputation_tier: str) -> str:
        """
        Generate response using semantic similarity search (Phase 3).
        
        Finds semantically similar templates/documents using FAISS embeddings
        and reputation tier filtering.
        """
        # Search for semantically similar templates
        search_results = self.pack_loader.search_semantic(
            query=user_input,
            top_k=5,
            reputation_tier=reputation_tier
        )
        
        if not search_results:
            # Fall back to keyword-based if no semantic results
            return self._generate_response_keyword_based(dialogue_context, user_input, npc_id, reputation_tier)
        
        # Get best match
        template_id, similarity, template = search_results[0]
        
        npc_data = self.bridge.npc_registry.get(npc_id, {})
        
        # Extract location from player journey
        location = "unknown lands"
        if dialogue_context.player_journey:
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
            "time_of_day": "day",
            "item_types": "wondrous items",
        }
        
        # Handle template object vs document dict
        if hasattr(template, 'content'):
            # ConversationTemplate object
            response = self.pack_loader.fill_slots(template, slot_values)
        else:
            # JSONL document dict
            content = template.get("content", "")
            # Fill basic slots in content
            for key, value in slot_values.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
            response = content
        
        self.pack_templates_used += 1
        return response
    
    def _generate_response_keyword_based(self, dialogue_context, user_input: str, npc_id: str, reputation_tier: str) -> str:
        """
        Generate response using keyword-based template selection (Phase 2).
        
        Determines dialogue context tags from user input keywords and selects
        templates based on reputation tier + tags.
        """
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
            
            npc_data = self.bridge.npc_registry.get(npc_id, {})
            
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
    
    def create_conversation_session(self, player_id: str, npc_id: str, realm_id: str) -> str:
        """
        Create a new conversation session (Phase 4).
        
        Args:
            player_id: Player ID
            npc_id: NPC ID
            realm_id: Realm ID
            
        Returns:
            Session ID
        """
        session = self.start_conversation(player_id, npc_id, realm_id)
        
        # Extend session with Phase 4 metadata
        session.conversation_history = []
        session.turn_count = 0
        session.created_at = datetime.utcnow().isoformat()
        session.last_modified_at = session.created_at
        
        return session.session_id
    
    def get_conversation_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve conversation session by ID (Phase 4).
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data dict
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        result = {
            "session_id": session.session_id,
            "player_id": session.player_id,
            "npc_id": session.npc_id,
            "realm_id": session.realm_id,
            "created_at": getattr(session, "created_at", session.start_time),
            "last_modified_at": getattr(session, "last_modified_at", session.last_activity),
            "conversation_history": getattr(session, "conversation_history", []),
            "turn_count": getattr(session, "turn_count", len(session.messages) // 2),
            "messages": session.messages,
        }
        
        # Include full history length if tracked
        if hasattr(session, "full_history_count"):
            result["full_history_length"] = session.full_history_count
        
        return result
    
    def query_npc_with_session(self, session_id: str, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        Query NPC within a conversation session (Phase 4 multi-turn).
        
        Args:
            session_id: Conversation session ID
            user_input: Player message
            **kwargs: Extended slot parameters (include_extended_slots, weather, location_type, etc.)
            
        Returns:
            Response dict with turn_number, npc_response, context info
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        turn_number = getattr(session, "turn_count", len(session.messages) // 2) + 1
        
        # Get context
        dialogue_context = self.bridge.get_dialogue_context(session.player_id, session.npc_id)
        
        # Prepare extended slots if requested
        extended_slots = {}
        if kwargs.get("include_extended_slots"):
            extended_slots = self._prepare_extended_slots(
                session.player_id, session.npc_id, **kwargs
            )
        
        # Generate NPC response
        npc_response = self._generate_npc_response(
            dialogue_context,
            user_input,
            session.npc_id
        )
        
        # Fill extended slots in response if needed
        if extended_slots:
            for slot_name, slot_value in extended_slots.items():
                placeholder = f"{{{{{slot_name}}}}}"
                npc_response = npc_response.replace(placeholder, str(slot_value))
        
        # Update session
        session.messages.append(("player", user_input))
        session.messages.append(("npc", npc_response))
        session.turn_count = turn_number
        session.last_modified_at = datetime.utcnow().isoformat()
        session.last_activity = session.last_modified_at
        
        # Build history from messages
        if not hasattr(session, "conversation_history"):
            session.conversation_history = []
        
        if not hasattr(session, "full_history_count"):
            session.full_history_count = 0
        
        turn_data = {
            "turn_number": turn_number,
            "player_input": user_input,
            "npc_response": npc_response,
            "timestamp": session.last_modified_at,
        }
        
        session.conversation_history.append(turn_data)
        session.full_history_count += 1
        
        # Truncate history to last 10 turns for memory efficiency
        # But keep full count for reference
        MAX_HISTORY_LENGTH = 10
        if len(session.conversation_history) > MAX_HISTORY_LENGTH:
            session.conversation_history = session.conversation_history[-MAX_HISTORY_LENGTH:]
        
        # Prepare response
        response = {
            "turn_number": turn_number,
            "npc_response": npc_response,
            "session_id": session_id,
            "context_history_length": max(0, turn_number - 1),
            "context_messages": [msg for msg in session.messages if turn_number > 1],
            "slots_used": list(extended_slots.keys()) if extended_slots else [],
        }
        
        return response
    
    def _prepare_extended_slots(self, player_id: str, npc_id: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare Phase 4 extended slots (inventory, faction, time, mood, etc.).
        
        Args:
            player_id: Player ID
            npc_id: NPC ID
            **kwargs: Slot parameters
            
        Returns:
            Dict of slot_name -> slot_value
        """
        slots = {}
        player = self.router.get_player(player_id)
        
        if not player:
            return slots
        
        # {{inventory_summary}} - categorized inventory
        if "include_extended_slots" in kwargs:
            inventory_items = player.inventory
            if inventory_items:
                categories = {}
                for item in inventory_items:
                    cat = item.item_type
                    categories[cat] = categories.get(cat, 0) + item.quantity
                
                summary_parts = [f"{count} {cat}{'s' if count > 1 else ''}" 
                                for cat, count in categories.items()]
                slots["inventory_summary"] = ", ".join(summary_parts) if summary_parts else "No items"
        
        # {{faction_standing}} - reputation mapping
        if "include_extended_slots" in kwargs and player.reputation:
            primary_rep = player.reputation[0]  # Get primary reputation
            standing_text = f"{primary_rep.standing.title()} with The {primary_rep.faction.value.replace('_', ' ').title()}"
            slots["faction_standing"] = standing_text
        
        # {{time_of_day}} - from kwargs or default
        if "time_of_day" in kwargs:
            slots["time_of_day"] = kwargs["time_of_day"]
        else:
            slots["time_of_day"] = "day"
        
        # {{npc_mood}} - from kwargs
        if "npc_mood" in kwargs:
            slots["npc_mood"] = kwargs["npc_mood"]
        else:
            slots["npc_mood"] = "neutral"
        
        # {{quest_context}} - active quest
        if player.active_quests:
            first_quest = list(player.active_quests.values())[0]
            slots["quest_context"] = first_quest.get("title", "Active Quest")
        else:
            slots["quest_context"] = "No active quest"
        
        # {{weather}} - from kwargs
        if "weather" in kwargs:
            slots["weather"] = kwargs["weather"]
        else:
            slots["weather"] = "clear"
        
        # {{location_type}} - from kwargs
        if "location_type" in kwargs:
            slots["location_type"] = kwargs["location_type"]
        else:
            slots["location_type"] = "unknown"
        
        # {{npc_history}} - transaction count
        npc_memory = self.router.npc_memory_store.get(npc_id, [])
        player_transactions = [m for m in npc_memory if m.get("player_id") == player_id]
        if player_transactions:
            slots["npc_history"] = f"Traded {len(player_transactions)} times"
        else:
            slots["npc_history"] = "We haven't traded yet"
        
        return slots
    
    def set_session_modified_time(self, session_id: str, timestamp):
        """
        Set session's last modified time (for testing/cleanup).
        
        Args:
            session_id: Session ID
            timestamp: New timestamp (datetime object)
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_modified_at = timestamp.isoformat()
            session.last_activity = session.last_modified_at
    
    def cleanup_stale_sessions(self, timeout_minutes: int = 60) -> int:
        """
        Clean up sessions older than timeout (Phase 4 state management).
        
        Args:
            timeout_minutes: Sessions idle longer than this are archived
            
        Returns:
            Number of sessions archived
        """
        from datetime import timedelta
        
        now = datetime.utcnow()
        timeout_delta = timedelta(minutes=timeout_minutes)
        archived_count = 0
        
        sessions_to_delete = []
        for session_id, session in self.sessions.items():
            last_activity = datetime.fromisoformat(session.last_activity)
            if now - last_activity > timeout_delta:
                sessions_to_delete.append(session_id)
                archived_count += 1
        
        for session_id in sessions_to_delete:
            del self.sessions[session_id]
        
        return archived_count
    
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