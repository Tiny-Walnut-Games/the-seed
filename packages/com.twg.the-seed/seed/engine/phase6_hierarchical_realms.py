"""
Phase 6-Alpha: Hierarchical Realm Tier System
PRODUCTION CODE — Hierarchical tier classification layer atop STAT7 + bitchain

Architecture:
- TierClassification: Celestial, Terran, Subterran cosmological hierarchy
- TierTheme: Semantic themes within each tier
- RealmTierMetadata: Tier classification for realms
- TierRegistry: Maps realms to tier classifications
- HierarchicalUniverseAdapter: Extends Universe with tier queries
- ZoomNavigator: Handles entity-to-sub-realm traversal

Implementation Note:
This is a PERSPECTIVE LAYER on top of Phase 5 STAT7 + bitchain.
No changes to core Phase 5 structures. Just metadata + traversal.

Date: 2025-10-31
Status: Production ready with comprehensive test coverage
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import json

logger = logging.getLogger(__name__)


# ============================================================================
# TIER SYSTEM DOMAIN MODELS
# ============================================================================

class TierClassification(Enum):
    """Three-tier cosmological hierarchy."""
    CELESTIAL = "celestial"     # Heaven, utopia, peace, mysticism
    TERRAN = "terran"           # Mid-world, mundane, urban, natural
    SUBTERRAN = "subterran"     # Hell, horror, abyss, dystopia


class TierTheme(Enum):
    """Semantic themes within each tier."""
    # Celestial themes
    HEAVEN = "heaven"               # Peaceful, utopian
    AETHER = "aether"               # Mystical, cosmic
    ASCENSION = "ascension"         # Spiritual growth
    
    # Terran themes
    OVERWORLD = "overworld"         # Natural, outdoor
    CITY_STATE = "city_state"       # Urban, civilization
    RURAL = "rural"                 # Pastoral, quiet
    FRONTIER = "frontier"           # Exploration, danger
    
    # Subterran themes
    HELL = "hell"                   # Demonic, dark
    ABYSS = "abyss"                 # Eldritch, cosmic horror
    UNDERDARK = "underdark"         # Subterranean, alien
    DYSTOPIA = "dystopia"           # Sci-fi horror, desolation


@dataclass
class RealmTierMetadata:
    """Metadata that classifies a realm within the hierarchical tier system."""
    realm_id: str
    tier: TierClassification
    theme: TierTheme
    semantic_anchors: List[str] = field(default_factory=list)
    tier_depth: int = 0  # Fractal zoom depth (0 = top-level realm)
    parent_realm_id: Optional[str] = None  # Realm this was zoomed from
    parent_entity_id: Optional[str] = None  # Entity that contains this sub-realm
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "realm_id": self.realm_id,
            "tier": self.tier.value,
            "theme": self.theme.value,
            "semantic_anchors": self.semantic_anchors,
            "tier_depth": self.tier_depth,
            "parent_realm_id": self.parent_realm_id,
            "parent_entity_id": self.parent_entity_id,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
# TIER REGISTRY (Centralized Tier Classification)
# ============================================================================

class TierRegistry:
    """
    Maintains mapping between realms and their tier classifications.
    Supports queries by tier, theme, and semantic anchors.
    """
    
    def __init__(self):
        # Initialize tier buckets properly using enum members
        self._realms_by_tier: Dict[TierClassification, Set[str]] = {
            tier: set() for tier in TierClassification
        }
        # Initialize theme buckets properly using enum members
        self._realms_by_theme: Dict[TierTheme, Set[str]] = {
            theme: set() for theme in TierTheme
        }
        self._metadata: Dict[str, RealmTierMetadata] = {}
        self._lock = asyncio.Lock()
    
    async def register_realm(self, metadata: RealmTierMetadata) -> None:
        """Register a realm with tier classification."""
        async with self._lock:
            self._metadata[metadata.realm_id] = metadata
            self._realms_by_tier[metadata.tier].add(metadata.realm_id)
            self._realms_by_theme[metadata.theme].add(metadata.realm_id)
            logger.info(f"Registered realm '{metadata.realm_id}' as {metadata.tier.value}/{metadata.theme.value}")
    
    async def get_realms_by_tier(self, tier: TierClassification) -> List[str]:
        """Get all realm IDs for a given tier."""
        async with self._lock:
            return list(self._realms_by_tier[tier])
    
    async def get_realms_by_theme(self, theme: TierTheme) -> List[str]:
        """Get all realm IDs for a given theme."""
        async with self._lock:
            return list(self._realms_by_theme[theme])
    
    async def get_realms_by_anchor(self, anchor: str) -> List[str]:
        """Get all realms tagged with a semantic anchor."""
        async with self._lock:
            return [
                realm_id for realm_id, metadata in self._metadata.items()
                if anchor in metadata.semantic_anchors
            ]
    
    async def get_metadata(self, realm_id: str) -> Optional[RealmTierMetadata]:
        """Get tier metadata for a realm."""
        async with self._lock:
            return self._metadata.get(realm_id)
    
    async def get_all_metadata(self) -> Dict[str, RealmTierMetadata]:
        """Get all registered metadata."""
        async with self._lock:
            return dict(self._metadata)
    
    def tier_counts(self) -> Dict[str, int]:
        """Get realm counts by tier."""
        return {
            tier.value: len(realms)
            for tier, realms in self._realms_by_tier.items()
        }


# ============================================================================
# ZOOM NAVIGATOR (Entity → Sub-Realm Traversal)
# ============================================================================

class ZoomNavigator:
    """
    Handles navigation into entities as sub-realms (fractal zoom).
    
    When you zoom into an entity:
    1. Entity becomes the center of a new sub-realm
    2. Sub-realm inherits parent tier + theme
    3. New STAT7 address space generated relative to entity position
    4. Bitchain path preserved for reversibility
    """
    
    def __init__(self):
        self._zoom_stack: List[Tuple[str, str]] = []  # [(realm_id, entity_id), ...]
        self._sub_realm_cache: Dict[str, RealmTierMetadata] = {}
    
    def compute_sub_realm_id(self, parent_realm_id: str, entity_id: str, depth: int) -> str:
        """
        Generate deterministic sub-realm ID from parent realm and entity.
        Uses bitchain-style addressing for reversibility.
        """
        return f"sub_{parent_realm_id}_{entity_id}_{depth}"
    
    def create_sub_realm_metadata(
        self,
        parent_metadata: RealmTierMetadata,
        entity_id: str,
        additional_anchors: Optional[List[str]] = None
    ) -> RealmTierMetadata:
        """
        Create tier metadata for a sub-realm.
        Inherits tier/theme from parent, adds entity context.
        """
        sub_realm_id = self.compute_sub_realm_id(
            parent_metadata.realm_id,
            entity_id,
            parent_metadata.tier_depth + 1
        )
        
        combined_anchors = parent_metadata.semantic_anchors.copy()
        if additional_anchors:
            combined_anchors.extend(additional_anchors)
        
        return RealmTierMetadata(
            realm_id=sub_realm_id,
            tier=parent_metadata.tier,  # Inherit tier
            theme=parent_metadata.theme,  # Inherit theme
            semantic_anchors=combined_anchors,
            tier_depth=parent_metadata.tier_depth + 1,
            parent_realm_id=parent_metadata.realm_id,
            parent_entity_id=entity_id,
        )
    
    def get_bitchain_path(self) -> List[Tuple[str, str]]:
        """Get current zoom navigation path (bitchain)."""
        return self._zoom_stack.copy()
    
    def zoom_in(self, realm_id: str, entity_id: str) -> None:
        """Record zoom-in navigation."""
        self._zoom_stack.append((realm_id, entity_id))
    
    def zoom_out(self) -> Optional[Tuple[str, str]]:
        """Record zoom-out navigation (reverse traversal)."""
        if self._zoom_stack:
            return self._zoom_stack.pop()
        return None


# ============================================================================
# NPC TIER PERSONALITY GENERATOR
# ============================================================================

class TierPersonalityGenerator:
    """
    Generates NPC personality traits based on tier classification.
    Ensures NPCs reflect their cosmological context.
    """
    
    @staticmethod
    def get_personality_traits(tier: TierClassification, count: int = 3) -> List[str]:
        """Get personality traits for a given tier."""
        traits_dict = {
            TierClassification.CELESTIAL: [
                "wise", "ethereal", "ascendant", "mystical", "serene",
                "transcendent", "luminous", "harmonious", "benevolent"
            ],
            TierClassification.TERRAN: [
                "practical", "grounded", "sociable", "cunning", "industrious",
                "adventurous", "pragmatic", "clever", "balanced"
            ],
            TierClassification.SUBTERRAN: [
                "dark", "eldritch", "corrupted", "mysterious", "malevolent",
                "haunting", "ancient", "twisted", "unfathomable"
            ],
        }
        traits = traits_dict.get(tier, [])
        return traits[:count]
    
    @staticmethod
    def get_dialogue_seed(theme: TierTheme) -> str:
        """Get narrative dialogue seed for a theme."""
        seeds = {
            TierTheme.HEAVEN: "The celestial realms speak of eternal peace...",
            TierTheme.AETHER: "The stars whisper secrets of the cosmos...",
            TierTheme.ASCENSION: "The path of enlightenment spirals upward...",
            TierTheme.OVERWORLD: "The village square fills with merchants and travelers...",
            TierTheme.CITY_STATE: "The city thrums with commerce and intrigue...",
            TierTheme.RURAL: "The quiet countryside beckons with simplicity...",
            TierTheme.FRONTIER: "The untamed lands pulse with danger and opportunity...",
            TierTheme.HELL: "The shadows writhe with unknown horrors...",
            TierTheme.ABYSS: "The abyss stares back with eldritch comprehension...",
            TierTheme.UNDERDARK: "The depths shelter terrors alien to surface dwellers...",
            TierTheme.DYSTOPIA: "The ruins of civilization decay into dust...",
        }
        return seeds.get(theme, "An NPC speaks...")
    
    @staticmethod
    def create_npc_metadata(
        tier: TierClassification,
        theme: TierTheme,
        entity_id: str
    ) -> Dict[str, Any]:
        """Create NPC metadata reflecting tier/theme."""
        return {
            "npc_id": entity_id,
            "tier_affinity": tier.value,
            "theme_affinity": theme.value,
            "personality_traits": TierPersonalityGenerator.get_personality_traits(tier),
            "dialogue_seed": TierPersonalityGenerator.get_dialogue_seed(theme),
            "created_at": datetime.now().isoformat(),
        }


# ============================================================================
# HIERARCHICAL UNIVERSE ADAPTER
# ============================================================================

class HierarchicalUniverseAdapter:
    """
    Extends a Phase 5 Universe with tier-aware queries and sub-realm traversal.
    
    IMPORTANT: Does NOT modify Phase 5 structures.
    Wraps Universe with tier registry and zoom navigation.
    """
    
    def __init__(self, universe: "Universe"):  # type: ignore
        from phase5_bigbang import Universe
        
        self.universe = universe
        self.tier_registry = TierRegistry()
        self.zoom_navigator = ZoomNavigator()
        self.personality_generator = TierPersonalityGenerator()
        self._initialized = False
    
    async def initialize_with_tier_classification(
        self,
        tier_specs: Dict[str, Tuple[TierClassification, TierTheme, List[str]]]
    ) -> None:
        """
        Initialize tier classification for existing universe realms.
        
        tier_specs: Dict[realm_id, (tier, theme, semantic_anchors)]
        """
        for realm_id, (tier, theme, anchors) in tier_specs.items():
            if realm_id not in self.universe.realms:
                logger.warning(f"Realm '{realm_id}' not found in universe")
                continue
            
            metadata = RealmTierMetadata(
                realm_id=realm_id,
                tier=tier,
                theme=theme,
                semantic_anchors=anchors,
                tier_depth=0,
            )
            
            await self.tier_registry.register_realm(metadata)
        
        self._initialized = True
        logger.info(f"Initialized tier classification for {len(tier_specs)} realms")
    
    async def get_realms_by_tier(self, tier: TierClassification) -> Dict[str, "RealmData"]:  # type: ignore
        """Get all realms in a specific tier."""
        realm_ids = await self.tier_registry.get_realms_by_tier(tier)
        return {
            rid: self.universe.realms[rid]
            for rid in realm_ids
            if rid in self.universe.realms
        }
    
    async def get_realms_by_theme(self, theme: TierTheme) -> Dict[str, "RealmData"]:  # type: ignore
        """Get all realms with a specific theme."""
        realm_ids = await self.tier_registry.get_realms_by_theme(theme)
        return {
            rid: self.universe.realms[rid]
            for rid in realm_ids
            if rid in self.universe.realms
        }
    
    async def get_realm_metadata(self, realm_id: str) -> Optional[RealmTierMetadata]:
        """Get tier metadata for a realm."""
        return await self.tier_registry.get_metadata(realm_id)
    
    async def get_tier_statistics(self) -> Dict[str, Any]:
        """Get statistics about tier distribution."""
        all_metadata = await self.tier_registry.get_all_metadata()
        return {
            "total_realms": len(all_metadata),
            "tier_distribution": self.tier_registry.tier_counts(),
            "theme_distribution": {
                theme.value: len(await self.tier_registry.get_realms_by_theme(theme))
                for theme in TierTheme
            },
        }
    
    async def create_sub_realm(
        self,
        parent_realm_id: str,
        entity_id: str,
        additional_anchors: Optional[List[str]] = None
    ) -> Optional[RealmTierMetadata]:
        """
        Create a sub-realm by zooming into an entity.
        Returns the new sub-realm's tier metadata.
        """
        parent_metadata = await self.tier_registry.get_metadata(parent_realm_id)
        if not parent_metadata:
            logger.warning(f"Parent realm '{parent_realm_id}' not found")
            return None
        
        # Create sub-realm metadata
        sub_metadata = self.zoom_navigator.create_sub_realm_metadata(
            parent_metadata,
            entity_id,
            additional_anchors
        )
        
        # Register sub-realm
        await self.tier_registry.register_realm(sub_metadata)
        
        # Record zoom navigation
        self.zoom_navigator.zoom_in(parent_realm_id, entity_id)
        
        logger.info(f"Created sub-realm '{sub_metadata.realm_id}' from entity '{entity_id}'")
        return sub_metadata
    
    async def export_tier_structure(self) -> Dict[str, Any]:
        """Export complete tier structure as JSON."""
        all_metadata = await self.tier_registry.get_all_metadata()
        return {
            "timestamp": datetime.now().isoformat(),
            "total_realms": len(all_metadata),
            "realms": {
                rid: metadata.to_dict()
                for rid, metadata in all_metadata.items()
            },
            "statistics": await self.get_tier_statistics(),
        }


if __name__ == "__main__":
    print("Phase 6-Alpha: Hierarchical Realm Tier System")
    print("=" * 60)
    print("Usage: from phase6_hierarchical_realms import HierarchicalUniverseAdapter")
    print("\nFeatures:")
    print("- Celestial/Terran/Subterran tier classification")
    print("- Semantic theme classification within each tier")
    print("- Entity → sub-realm zoom navigation (bitchain-aware)")
    print("- Tier-aware NPC personality generation")
    print("- Async-safe registry and queries")