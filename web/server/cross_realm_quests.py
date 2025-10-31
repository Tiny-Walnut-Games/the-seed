"""
Cross-Realm Quest System: Quests That Span Multiple Game Worlds

Enables quest chains and storylines that span multiple realms.
Players travel between game worlds to complete quest objectives.
Quests are synchronized via control-ticks and persist across sessions.

Features:
- Quest chains spanning multiple realms
- NPCs in different realms as quest givers/objective locations
- Multi-stage quests with branching paths
- Realm-specific quest variations
- Cross-realm rewards and reputation gains
- Quest discovery through player travel and NPC dialogue

Example:
    quest_system = CrossRealmQuestSystem(player_router, player_router, npc_integration)
    
    # Create multi-realm quest
    quest = quest_system.create_quest(
        quest_id="the_shattered_crown",
        title="The Shattered Crown",
        description="Find the pieces of an ancient crown scattered across realms",
        giver_npc="npc_sol_1_001",
        starting_realm="sol_1",
        quest_type="multi_realm_chain"
    )
    
    # Add objectives across realms
    quest_system.add_objective(quest_id, {
        "objective_id": "find_piece_1",
        "description": "Find Crown Piece in sol_1",
        "realm": "sol_1",
        "objective_type": "fetch_item",
        "target": "crown_shard_1"
    })
    
    # Player completes quest in multiple realms
    player_router.accept_quest(player_id, quest_id)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class QuestStatus(Enum):
    """Status of a quest."""
    AVAILABLE = "available"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"


class ObjectiveStatus(Enum):
    """Status of a quest objective."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QuestObjective:
    """Single objective in a quest."""
    objective_id: str
    description: str
    realm_id: str
    objective_type: str  # "fetch_item", "defeat_enemy", "talk_to_npc", "reach_location"
    target: str  # What to fetch/defeat/talk_to
    status: ObjectiveStatus = ObjectiveStatus.PENDING
    completion_count: int = 0
    required_count: int = 1  # How many of target needed
    
    # Rewards for completing this objective
    reward_xp: int = 0
    reward_items: List[str] = field(default_factory=list)


@dataclass
class Quest:
    """A multi-realm quest."""
    quest_id: str
    title: str
    description: str
    giver_npc: str
    starting_realm: str
    quest_type: str  # "linear", "branching", "multi_realm_chain"
    
    # Status
    status: QuestStatus = QuestStatus.AVAILABLE
    created_at: str = ""
    accepted_at: str = ""
    completed_at: str = ""
    
    # Objectives
    objectives: List[QuestObjective] = field(default_factory=list)
    current_objective_index: int = 0
    
    # Rewards
    reward_xp: int = 0
    reward_items: List[str] = field(default_factory=list)
    reward_reputation: Dict[str, int] = field(default_factory=dict)  # faction -> reputation change
    
    # Meta
    difficulty: str = "normal"  # "easy", "normal", "hard", "legendary"
    can_abandon: bool = True
    repeatable: bool = False
    prerequisites: List[str] = field(default_factory=list)  # Other quests that must be completed first


class CrossRealmQuestSystem:
    """
    Manages quests that span multiple game realms.
    
    Quests can have objectives in different game worlds,
    requiring players to travel and coordinate across realms.
    """
    
    def __init__(self, player_router, city_integration):
        """
        Initialize quest system.
        
        Args:
            player_router: UniversalPlayerRouter instance
            city_integration: CitySimulationIntegration instance
        """
        self.router = player_router
        self.city_integration = city_integration
        
        # Quest storage
        self.quests: Dict[str, Quest] = {}  # quest_id -> Quest
        self.player_quests: Dict[str, List[str]] = {}  # player_id -> [quest_ids]
        self.completed_quests: Dict[str, List[str]] = {}  # player_id -> [quest_ids]
        
        # Quest templates (for creating variations)
        self.quest_templates: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.total_quests_created = 0
        self.total_quests_completed = 0
        
        self._init_default_quests()
    
    def _init_default_quests(self):
        """Initialize some example quests."""
        # Multi-realm quest example
        quest_id = "the_scattered_artifacts"
        quest = Quest(
            quest_id=quest_id,
            title="The Scattered Artifacts",
            description="Ancient artifacts have been scattered across the realms. "
                       "Collect them all and bring them to the Archive.",
            giver_npc="npc_sol_1_001",
            starting_realm="sol_1",
            quest_type="multi_realm_chain",
            reward_xp=5000,
            reward_items=["artifact_case_legendary"],
            reward_reputation={"the_wanderers": 500, "realm_keepers": 300},
            difficulty="hard",
            created_at=datetime.utcnow().isoformat(),
        )
        
        # Add objectives across realms
        for i, realm in enumerate(["sol_1", "sol_2", "sol_3"]):
            objective = QuestObjective(
                objective_id=f"scatter_artifact_{i+1}",
                description=f"Find Artifact {i+1} in {realm}",
                realm_id=realm,
                objective_type="fetch_item",
                target=f"ancient_artifact_{i+1}",
                reward_xp=1500,
                required_count=1,
            )
            quest.objectives.append(objective)
        
        self.quests[quest_id] = quest
        self.total_quests_created += 1
    
    def create_quest(self,
                    quest_id: str,
                    title: str,
                    description: str,
                    giver_npc: str,
                    starting_realm: str,
                    quest_type: str = "multi_realm_chain",
                    difficulty: str = "normal",
                    reward_xp: int = 1000,
                    repeatable: bool = False) -> Quest:
        """
        Create a new quest.
        
        Args:
            quest_id: Unique quest identifier
            title: Quest title
            description: Quest description
            giver_npc: NPC who gives the quest
            starting_realm: Starting realm
            quest_type: Type of quest
            difficulty: Difficulty level
            reward_xp: XP reward for completion
            repeatable: Can player repeat this quest
            
        Returns:
            Quest object
        """
        quest = Quest(
            quest_id=quest_id,
            title=title,
            description=description,
            giver_npc=giver_npc,
            starting_realm=starting_realm,
            quest_type=quest_type,
            difficulty=difficulty,
            reward_xp=reward_xp,
            repeatable=repeatable,
            created_at=datetime.utcnow().isoformat(),
        )
        
        self.quests[quest_id] = quest
        self.total_quests_created += 1
        
        return quest
    
    def add_objective(self, quest_id: str, objective_data: Dict[str, Any]) -> bool:
        """
        Add an objective to a quest.
        
        Args:
            quest_id: Quest to add objective to
            objective_data: Objective configuration
            
        Returns:
            Success boolean
        """
        quest = self.quests.get(quest_id)
        if not quest:
            return False
        
        objective = QuestObjective(
            objective_id=objective_data.get("objective_id", str(uuid.uuid4())),
            description=objective_data.get("description", ""),
            realm_id=objective_data.get("realm", "sol_1"),
            objective_type=objective_data.get("objective_type", "fetch_item"),
            target=objective_data.get("target", ""),
            reward_xp=objective_data.get("reward_xp", 0),
            required_count=objective_data.get("required_count", 1),
        )
        
        quest.objectives.append(objective)
        return True
    
    def accept_quest(self, player_id: str, quest_id: str) -> Tuple[bool, str]:
        """
        Player accepts a quest.
        
        Args:
            player_id: Player accepting
            quest_id: Quest to accept
            
        Returns:
            (success, message)
        """
        player = self.router.get_player(player_id)
        if not player:
            return False, f"Player {player_id} not found"
        
        quest = self.quests.get(quest_id)
        if not quest:
            return False, f"Quest {quest_id} not found"
        
        # Check prerequisites
        completed = self.completed_quests.get(player_id, [])
        for prereq in quest.prerequisites:
            if prereq not in completed:
                return False, f"Prerequisites not met. Must complete {prereq} first."
        
        # Add to player's active quests
        if player_id not in self.player_quests:
            self.player_quests[player_id] = []
        
        if quest_id not in self.player_quests[player_id]:
            self.player_quests[player_id].append(quest_id)
            
            # Update quest status
            quest.status = QuestStatus.ACCEPTED
            quest.accepted_at = datetime.utcnow().isoformat()
            
            # Update player
            player.active_quests[quest_id] = {
                "title": quest.title,
                "status": quest.status.value,
                "accepted_at": quest.accepted_at,
            }
            
            # Emit narrative event
            self.router.emit_narrative_event(
                player_id=player_id,
                event_type="quest_accepted",
                title=f"Accepted quest: {quest.title}",
                description=f"{player.player_name} accepted '{quest.title}' from {quest.giver_npc}",
                metadata={"quest_id": quest_id, "difficulty": quest.difficulty}
            )
            
            return True, f"Quest '{quest.title}' accepted"
        
        return False, f"Quest already in progress"
    
    def progress_objective(self, 
                          player_id: str, 
                          quest_id: str, 
                          objective_id: str,
                          progress: int = 1) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Progress a quest objective.
        
        Args:
            player_id: Player progressing
            quest_id: Quest to progress
            objective_id: Objective to progress
            progress: How much to progress (default 1)
            
        Returns:
            (success, message, context)
        """
        player = self.router.get_player(player_id)
        if not player:
            return False, "Player not found", {}
        
        quest = self.quests.get(quest_id)
        if not quest:
            return False, "Quest not found", {}
        
        # Find objective
        objective = next(
            (o for o in quest.objectives if o.objective_id == objective_id),
            None
        )
        if not objective:
            return False, "Objective not found", {}
        
        # Progress objective
        objective.completion_count += progress
        
        context = {
            "objective_id": objective_id,
            "progress": objective.completion_count,
            "required": objective.required_count,
            "completed": objective.completion_count >= objective.required_count,
        }
        
        # Check if objective complete
        if objective.completion_count >= objective.required_count:
            objective.status = ObjectiveStatus.COMPLETED
            context["objective_completed"] = True
            
            # Award XP for objective
            player.experience += objective.reward_xp
            
            # Check if this was the last objective
            all_complete = all(
                o.status == ObjectiveStatus.COMPLETED 
                for o in quest.objectives
            )
            
            if all_complete:
                return self.complete_quest(player_id, quest_id)
            else:
                # Move to next objective
                quest.current_objective_index += 1
                return True, f"Objective complete! {len([o for o in quest.objectives if o.status == ObjectiveStatus.COMPLETED])}/{len(quest.objectives)}", context
        
        return True, f"Objective progressed: {objective.completion_count}/{objective.required_count}", context
    
    def complete_quest(self, player_id: str, quest_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Complete a quest.
        
        Awards player with XP, items, and reputation.
        
        Args:
            player_id: Player completing
            quest_id: Quest to complete
            
        Returns:
            (success, message, rewards)
        """
        player = self.router.get_player(player_id)
        if not player:
            return False, "Player not found", {}
        
        quest = self.quests.get(quest_id)
        if not quest:
            return False, "Quest not found", {}
        
        # Award XP
        player.experience += quest.reward_xp
        
        # Award items
        for item_id in quest.reward_items:
            from universal_player_router import InventoryItem
            item = InventoryItem(
                item_id=item_id,
                name=item_id.replace("_", " ").title(),
                item_type="quest_reward",
                rarity="rare",
                source_realm=player.active_realm,
                transferable=True,
            )
            self.router.add_item_to_inventory(player_id, item)
        
        # Award reputation
        for faction_name, rep_change in quest.reward_reputation.items():
            from universal_player_router import ReputationFaction
            faction = ReputationFaction(faction_name)
            self.router.modify_reputation(player_id, faction, rep_change)
        
        # Update quest status
        quest.status = QuestStatus.COMPLETED
        quest.completed_at = datetime.utcnow().isoformat()
        
        # Move from active to completed
        if player_id in self.player_quests:
            if quest_id in self.player_quests[player_id]:
                self.player_quests[player_id].remove(quest_id)
        
        if player_id not in self.completed_quests:
            self.completed_quests[player_id] = []
        self.completed_quests[player_id].append(quest_id)
        
        # Update player record
        if quest_id in player.active_quests:
            del player.active_quests[quest_id]
        player.completed_quests.append(quest_id)
        
        # Emit narrative event
        self.router.emit_narrative_event(
            player_id=player_id,
            event_type="quest_completed",
            title=f"Completed quest: {quest.title}",
            description=f"{player.player_name} completed '{quest.title}' across {len(set(o.realm_id for o in quest.objectives))} realms",
            metadata={
                "quest_id": quest_id,
                "xp_awarded": quest.reward_xp,
                "difficulty": quest.difficulty,
            }
        )
        
        self.total_quests_completed += 1
        
        rewards = {
            "xp": quest.reward_xp,
            "items": quest.reward_items,
            "reputation": quest.reward_reputation,
        }
        
        return True, f"Quest '{quest.title}' completed!", rewards
    
    def get_player_quests(self, player_id: str) -> Dict[str, Any]:
        """Get all quests for a player."""
        active = self.player_quests.get(player_id, [])
        completed = self.completed_quests.get(player_id, [])
        
        active_quests = [
            {
                "quest_id": qid,
                "title": self.quests[qid].title,
                "status": self.quests[qid].status.value,
                "progress": f"{len([o for o in self.quests[qid].objectives if o.status == ObjectiveStatus.COMPLETED])}/{len(self.quests[qid].objectives)}",
            }
            for qid in active if qid in self.quests
        ]
        
        return {
            "active_quests": active_quests,
            "completed_count": len(completed),
            "total_quests_completed": len(completed),
        }
    
    def get_available_quests_in_realm(self, realm_id: str) -> List[Dict[str, Any]]:
        """Get all quests available in a realm."""
        available = []
        
        for quest in self.quests.values():
            if quest.starting_realm == realm_id and quest.status == QuestStatus.AVAILABLE:
                available.append({
                    "quest_id": quest.quest_id,
                    "title": quest.title,
                    "description": quest.description,
                    "difficulty": quest.difficulty,
                    "reward_xp": quest.reward_xp,
                    "giver_npc": quest.giver_npc,
                })
        
        return available
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get quest system statistics."""
        return {
            "total_quests_created": self.total_quests_created,
            "total_quests_completed": self.total_quests_completed,
            "active_quests_count": sum(len(q) for q in self.player_quests.values()),
            "total_players_with_quests": len(self.player_quests),
            "difficulty_distribution": {
                "easy": len([q for q in self.quests.values() if q.difficulty == "easy"]),
                "normal": len([q for q in self.quests.values() if q.difficulty == "normal"]),
                "hard": len([q for q in self.quests.values() if q.difficulty == "hard"]),
                "legendary": len([q for q in self.quests.values() if q.difficulty == "legendary"]),
            }
        }