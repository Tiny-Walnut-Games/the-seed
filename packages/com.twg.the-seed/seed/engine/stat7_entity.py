#!/usr/bin/env python3
"""
STAT7 Entity System - Core Infrastructure
Unified backbone for Companions, Badges, and all collectible entities using STAT7 addressing

Features:
- Hybrid encoding (maps legacy systems to STAT7 coordinates)
- Backward compatibility with existing pets/badges
- LUCA-adjacent bootstrap tracing
- Deterministic coordinate assignment
- Entanglement detection and management
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import uuid
import hashlib
from abc import ABC, abstractmethod


# ============================================================================
# STAT7 Dimension Enums
# ============================================================================

class Realm(Enum):
    """Domain classification for STAT7 entities"""
    COMPANION = "companion"        # Pets, familiars, companions
    BADGE = "badge"                # Achievement badges
    SPONSOR_RING = "sponsor_ring"  # Sponsor tier badges
    ACHIEVEMENT = "achievement"    # Generic achievements
    PATTERN = "pattern"            # System patterns
    FACULTY = "faculty"            # Faculty-exclusive entities
    VOID = "void"                  # Null/empty realm


class Horizon(Enum):
    """Lifecycle stage in entity progression"""
    GENESIS = "genesis"            # Entity created, initial state
    EMERGENCE = "emergence"        # Entity becoming active
    PEAK = "peak"                  # Entity at maximum activity
    DECAY = "decay"                # Entity waning
    CRYSTALLIZATION = "crystallization"  # Entity settled/permanent
    ARCHIVED = "archived"          # Historical record


class Polarity(Enum):
    """Resonance/affinity classification"""
    # Companion polarities (elemental)
    LOGIC = "logic"
    CREATIVITY = "creativity"
    ORDER = "order"
    CHAOS = "chaos"
    BALANCE = "balance"
    
    # Badge polarities (category)
    ACHIEVEMENT = "achievement"
    CONTRIBUTION = "contribution"
    COMMUNITY = "community"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    UNITY = "unity"  # Special for sponsor rings
    
    # Neutral
    VOID = "void"


# ============================================================================
# STAT7 Coordinate Data Class
# ============================================================================

@dataclass
class STAT7Coordinates:
    """
    7-dimensional addressing space for all entities.
    
    Each dimension represents a different axis of entity existence:
      1. Realm: Domain/type classification
      2. Lineage: Generation or tier progression
      3. Adjacency: Semantic/functional proximity score
      4. Horizon: Lifecycle stage
      5. Luminosity: Activity level (0-100)
      6. Polarity: Resonance/affinity type
      7. Dimensionality: Fractal depth / detail level
    """
    realm: Realm
    lineage: int                    # 0-based generation from LUCA
    adjacency: float                # 0-100 proximity score
    horizon: Horizon
    luminosity: float               # 0-100 activity level
    polarity: Polarity
    dimensionality: int             # 0+ fractal depth
    
    @property
    def address(self) -> str:
        """Generate canonical STAT7 address string"""
        return f"STAT7-{self.realm.value[0].upper()}-{self.lineage:03d}-{int(self.adjacency):02d}-{self.horizon.value[0].upper()}-{int(self.luminosity):02d}-{self.polarity.value[0].upper()}-{self.dimensionality}"
    
    @staticmethod
    def from_address(address: str) -> 'STAT7Coordinates':
        """Parse STAT7 address back to coordinates"""
        # Format: STAT7-R-000-00-H-00-P-0
        parts = address.split('-')
        if len(parts) != 8 or parts[0] != 'STAT7':
            raise ValueError(f"Invalid STAT7 address: {address}")
        
        realm_map = {r.value[0].upper(): r for r in Realm}
        horizon_map = {h.value[0].upper(): h for h in Horizon}
        polarity_map = {p.value[0].upper(): p for p in Polarity}
        
        return STAT7Coordinates(
            realm=realm_map[parts[1]],
            lineage=int(parts[2]),
            adjacency=float(parts[3]),
            horizon=horizon_map[parts[4]],
            luminosity=float(parts[5]),
            polarity=polarity_map[parts[6]],
            dimensionality=int(parts[7])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'realm': self.realm.value,
            'lineage': self.lineage,
            'adjacency': self.adjacency,
            'horizon': self.horizon.value,
            'luminosity': self.luminosity,
            'polarity': self.polarity.value,
            'dimensionality': self.dimensionality,
            'address': self.address
        }


# ============================================================================
# Lifecycle Event Tracking
# ============================================================================

@dataclass
class LifecycleEvent:
    """Record of significant moments in entity history"""
    timestamp: datetime
    event_type: str                 # "birth", "evolution", "mint", etc.
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'description': description,
            'metadata': self.metadata
        }


# ============================================================================
# STAT7 Entity Base Class
# ============================================================================

@dataclass
class STAT7Entity(ABC):
    """
    Abstract base class for all STAT7-addressed entities.
    
    Provides:
    - Hybrid encoding (bridge between legacy and STAT7 systems)
    - Coordinate assignment
    - Entanglement tracking
    - Temporal tracking
    - NFT metadata
    """
    
    # Identity
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""  # Overridden in subclasses
    
    # STAT7 Addressing
    stat7: STAT7Coordinates = None
    
    # Legacy Fields (backward compatibility)
    legacy_data: Dict[str, Any] = field(default_factory=dict)
    migration_source: Optional[str] = None  # "pet", "badge", etc.
    
    # NFT Status
    nft_minted: bool = False
    nft_contract: Optional[str] = None
    nft_token_id: Optional[int] = None
    nft_metadata_ipfs: Optional[str] = None
    
    # Entanglement
    entangled_entities: List[str] = field(default_factory=list)
    entanglement_strength: List[float] = field(default_factory=list)
    
    # Temporal
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    lifecycle_events: List[LifecycleEvent] = field(default_factory=list)
    
    # Owner/User
    owner_id: str = ""
    
    # User Preferences
    opt_in_stat7_nft: bool = True
    opt_in_blockchain: bool = False
    preferred_zoom_level: int = 1  # Default display level
    
    def __post_init__(self):
        """Initialize STAT7 coordinates if not provided"""
        if self.stat7 is None:
            self.stat7 = self._compute_stat7_coordinates()
        self._record_event("genesis", "Entity initialized in STAT7 space")
    
    # ========================================================================
    # Abstract Methods (Implemented by Subclasses)
    # ========================================================================
    
    @abstractmethod
    def _compute_stat7_coordinates(self) -> STAT7Coordinates:
        """
        Compute STAT7 coordinates from entity data.
        Each subclass defines its own coordinate mapping.
        """
        pass
    
    @abstractmethod
    def to_collectible_card_data(self) -> Dict[str, Any]:
        """Convert entity to collectible card display format"""
        pass
    
    @abstractmethod
    def validate_hybrid_encoding(self) -> Tuple[bool, str]:
        """
        Validate that STAT7 coordinates correctly encode legacy data.
        Returns (is_valid, error_message_or_empty_string)
        """
        pass
    
    # ========================================================================
    # Event Tracking
    # ========================================================================
    
    def _record_event(self, event_type: str, description: str, metadata: Dict[str, Any] = None):
        """Record a lifecycle event"""
        event = LifecycleEvent(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            description=description,
            metadata=metadata or {}
        )
        self.lifecycle_events.append(event)
        self.last_activity = event.timestamp
    
    def get_event_history(self, limit: Optional[int] = None) -> List[LifecycleEvent]:
        """Get lifecycle events, optionally limited to most recent"""
        events = sorted(self.lifecycle_events, key=lambda e: e.timestamp, reverse=True)
        return events[:limit] if limit else events
    
    # ========================================================================
    # Entanglement Management
    # ========================================================================
    
    def add_entanglement(self, other_entity_id: str, strength: float = 1.0):
        """
        Link to another entity via resonance/entanglement.
        Strength: 0-1.0 (1.0 = maximum entanglement)
        """
        if other_entity_id not in self.entangled_entities:
            self.entangled_entities.append(other_entity_id)
            self.entanglement_strength.append(strength)
            self._record_event("entanglement_added", f"Entangled with {other_entity_id}", {"strength": strength})
    
    def remove_entanglement(self, other_entity_id: str):
        """Remove entanglement with another entity"""
        if other_entity_id in self.entangled_entities:
            idx = self.entangled_entities.index(other_entity_id)
            self.entangled_entities.pop(idx)
            self.entanglement_strength.pop(idx)
            self._record_event("entanglement_removed", f"Untangled from {other_entity_id}")
    
    def get_entanglements(self) -> List[Tuple[str, float]]:
        """Get all entangled entities with strength"""
        return list(zip(self.entangled_entities, self.entanglement_strength))
    
    def update_entanglement_strength(self, other_entity_id: str, new_strength: float):
        """Update entanglement strength with another entity"""
        if other_entity_id in self.entangled_entities:
            idx = self.entangled_entities.index(other_entity_id)
            old_strength = self.entanglement_strength[idx]
            self.entanglement_strength[idx] = new_strength
            self._record_event("entanglement_updated", f"Entanglement strength changed {old_strength:.2f} → {new_strength:.2f}")
    
    # ========================================================================
    # LUCA Bootstrap
    # ========================================================================
    
    @property
    def luca_distance(self) -> int:
        """Distance from LUCA (Last Universal Common Ancestor)"""
        return self.stat7.lineage
    
    def get_luca_trace(self) -> Dict[str, Any]:
        """
        Get path back to LUCA bootstrap origin.
        In a real system, this would trace parent entities.
        """
        return {
            'entity_id': self.entity_id,
            'luca_distance': self.luca_distance,
            'realm': self.stat7.realm.value,
            'lineage': self.stat7.lineage,
            'created_at': self.created_at.isoformat(),
            'migration_source': self.migration_source,
            'event_count': len(self.lifecycle_events)
        }
    
    # ========================================================================
    # NFT Integration
    # ========================================================================
    
    def prepare_for_minting(self) -> Dict[str, Any]:
        """
        Generate NFT metadata for minting.
        Returns ERC-721/ERC-1155 compatible metadata object.
        """
        if not self.opt_in_stat7_nft:
            raise ValueError("Entity not opted in to STAT7-NFT system")
        
        card_data = self.to_collectible_card_data()
        
        return {
            'name': card_data.get('title', self.entity_id),
            'description': card_data.get('fluff_text', ''),
            'image': card_data.get('artwork_url', ''),
            'external_url': f"https://theseed.example.com/entity/{self.entity_id}",
            'attributes': [
                {'trait_type': 'Entity Type', 'value': self.entity_type},
                {'trait_type': 'Realm', 'value': self.stat7.realm.value},
                {'trait_type': 'Lineage', 'value': self.stat7.lineage},
                {'trait_type': 'Horizon', 'value': self.stat7.horizon.value},
                {'trait_type': 'Luminosity', 'value': int(self.stat7.luminosity)},
                {'trait_type': 'Polarity', 'value': self.stat7.polarity.value},
                {'trait_type': 'Dimensionality', 'value': self.stat7.dimensionality},
                {'trait_type': 'STAT7 Address', 'value': self.stat7.address},
            ],
            'properties': card_data.get('properties', {})
        }
    
    def record_mint(self, contract_address: str, token_id: int, ipfs_hash: str):
        """Record successful NFT minting"""
        self.nft_minted = True
        self.nft_contract = contract_address
        self.nft_token_id = token_id
        self.nft_metadata_ipfs = ipfs_hash
        self._record_event("nft_minted", f"Minted as ERC-721 token #{token_id}", {
            'contract': contract_address,
            'token_id': token_id,
            'ipfs_hash': ipfs_hash
        })
    
    # ========================================================================
    # Serialization
    # ========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON storage"""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'stat7': self.stat7.to_dict() if self.stat7 else None,
            'legacy_data': self.legacy_data,
            'migration_source': self.migration_source,
            'nft_minted': self.nft_minted,
            'nft_contract': self.nft_contract,
            'nft_token_id': self.nft_token_id,
            'nft_metadata_ipfs': self.nft_metadata_ipfs,
            'entangled_entities': self.entangled_entities,
            'entanglement_strength': self.entanglement_strength,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'lifecycle_events': [e.to_dict() for e in self.lifecycle_events],
            'owner_id': self.owner_id,
            'opt_in_stat7_nft': self.opt_in_stat7_nft,
            'opt_in_blockchain': self.opt_in_blockchain,
            'preferred_zoom_level': self.preferred_zoom_level,
        }
    
    def save_to_file(self, path: Path):
        """Persist entity to JSON file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
    
    @classmethod
    def load_from_file(cls, path: Path) -> 'STAT7Entity':
        """Load entity from JSON file (must know concrete type)"""
        with open(path, 'r') as f:
            data = json.load(f)
        # Note: In practice, would need factory pattern to instantiate correct subclass
        raise NotImplementedError("Use subclass load methods")
    
    # ========================================================================
    # Display Levels
    # ========================================================================
    
    def render_zoom_level(self, level: int) -> Dict[str, Any]:
        """
        Render entity at specific zoom level.
        
        Level 1: Badge (20x20px icon)
        Level 2: Dog-tag (100x150px micro-card)
        Level 3: Collectible Card (300x400px full card)
        Level 4: Profile panel (350x500px interactive)
        Level 5: Entity profile page (full details)
        Level 6+: Fractal descent (dimension breakdown)
        """
        if level < 1 or level > 7:
            raise ValueError(f"Invalid zoom level: {level}")
        
        card_data = self.to_collectible_card_data()
        
        base = {
            'zoom_level': level,
            'entity_id': self.entity_id,
            'stat7_address': self.stat7.address,
            'created_at': self.created_at.isoformat(),
        }
        
        if level == 1:
            # Badge: Just icon + rarity
            return {**base, 'type': 'badge', 'icon': card_data.get('icon_url'), 'rarity': card_data.get('rarity')}
        
        elif level == 2:
            # Dog-tag: Icon, title, key stats
            return {**base, 'type': 'dog_tag', 'icon': card_data.get('icon_url'), 'title': card_data.get('title'), 'stats': card_data.get('key_stats')}
        
        elif level == 3:
            # Full card
            return {**base, 'type': 'collectible_card', **card_data}
        
        elif level == 4:
            # Profile panel
            return {
                **base,
                'type': 'profile_panel',
                **card_data,
                'owner': self.owner_id,
                'entangled_count': len(self.entangled_entities),
                'events': len(self.lifecycle_events)
            }
        
        elif level == 5:
            # Full profile page
            return {
                **base,
                'type': 'entity_profile',
                **card_data,
                'owner': self.owner_id,
                'lifecycle_events': [e.to_dict() for e in self.lifecycle_events],
                'entanglements': self.get_entanglements(),
                'luca_trace': self.get_luca_trace()
            }
        
        else:  # level 6+
            # Fractal descent
            return {
                **base,
                'type': 'fractal_descent',
                'stat7_dimensions': self.stat7.to_dict(),
                'realm_details': self._get_realm_details(),
                'entanglement_network': self.get_entanglements(),
                'event_chronology': [e.to_dict() for e in self.lifecycle_events]
            }
    
    def _get_realm_details(self) -> Dict[str, Any]:
        """Override in subclasses to provide realm-specific details"""
        return {}


# ============================================================================
# Helper Functions
# ============================================================================

def hash_for_coordinates(data: Dict[str, Any]) -> str:
    """Deterministic hashing for coordinate assignment"""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


def compute_adjacency_score(tags1: List[str], tags2: List[str]) -> float:
    """
    Compute adjacency (similarity) score between two tag sets.
    Returns 0-100 score.
    """
    if not tags1 or not tags2:
        return 0.0
    
    common = len(set(tags1) & set(tags2))
    total = len(set(tags1) | set(tags2))
    return (common / total) * 100 if total > 0 else 0.0


if __name__ == "__main__":
    print("STAT7 Entity system loaded. Use as base class for Companion and Badge entities.")