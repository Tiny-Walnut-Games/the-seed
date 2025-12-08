"""
Shared utilities for FractalStat validation experiments.


Successor to fractalstat with improved expressivity (100% vs 95%).
Added 8th dimension: 'alignment' for social/coordination dynamics.

Features:
- Hybrid encoding (maps legacy systems to FractalStat coordinates)
- Backward compatibility with existing pets/badges/entities
- LUCA-adjacent bootstrap tracing
- Deterministic coordinate assignment
- Entanglement detection and management
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import uuid
import hashlib
from abc import ABC, abstractmethod
import secrets
import random
from decimal import Decimal, ROUND_HALF_EVEN



def _utc_now() -> datetime:
    """Helper function for timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


# ============================================================================
# FractalStat Dimension Enums
# ============================================================================


class Realm(Enum):
    """Domain classification for FractalStat entities"""

    COMPANION = "companion"  # Pets, familiars, companions
    BADGE = "badge"  # Achievement badges
    SPONSOR_RING = "sponsor_ring"  # Sponsor tier badges
    ACHIEVEMENT = "achievement"  # Generic achievements
    PATTERN = "pattern"  # System patterns
    FACULTY = "faculty"  # Faculty-exclusive entities
    TEMPORAL = "temporal"  # Time-based entities
    VOID = "void"  # Null/empty realm


class Horizon(Enum):
    """Lifecycle stage in entity progression"""

    GENESIS = "genesis"  # Entity created, initial state
    EMERGENCE = "emergence"  # Entity becoming active
    PEAK = "peak"  # Entity at maximum activity
    DECAY = "decay"  # Entity waning
    CRYSTALLIZATION = "crystallization"  # Entity settled/permanent
    ARCHIVED = "archived"  # Historical record


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


class Alignment(Enum):
    """Social and coordination dynamics alignment"""

    # Classical alignment system (inspired by fantasy RPGs) - Law vs Chaos
    LAWFUL_GOOD = "lawful_good"  # Principled, helpful
    NEUTRAL_GOOD = "neutral_good"  # Helpful, flexible
    CHAOTIC_GOOD = "chaotic_good"  # Helpful, unconstrained

    LAWFUL_NEUTRAL = "lawful_neutral"  # Principled, pragmatic
    TRUE_NEUTRAL = "true_neutral"  # Balanced, pragmatic
    CHAOTIC_NEUTRAL = "chaotic_neutral"  # Flexible, pragmatic

    LAWFUL_EVIL = "lawful_evil"  # Principled, harmful
    NEUTRAL_EVIL = "neutral_evil"  # Self-serving
    CHAOTIC_EVIL = "chaotic_evil"  # Harmful, unconstrained

    # Special classifications for FractalStat
    HARMONIC = "harmonic"  # Naturally coordinated
    ENTROPIC = "entropic"  # Naturally disruptive
    SYMBIOTIC = "symbiotic"  # Mutually beneficial connections


# ============================================================================
# FractalStat Coordinate Data Class (8 Dimensions)
# ============================================================================


@dataclass
class FractalStatCoordinates:
    """
    8-dimensional addressing space for all entities with 100% expressivity.

    Each dimension represents a different axis of entity existence:
      1. Realm: Domain/type classification
      2. Lineage: Generation or tier progression from LUCA
      3. Adjacency: Semantic/functional proximity score (0-100)
      4. Horizon: Lifecycle stage
      5. Luminosity: Activity level (0-100)
      6. Polarity: Resonance/affinity type
      7. Dimensionality: Fractal depth / detail level
      8. Alignment: Social/coordination dynamics (NEW - 100% expressivity boost)
    """

    realm: Realm  # Domain classification
    lineage: int  # 0-based generation from LUCA
    adjacency: float  # 0-100 proximity score
    horizon: Horizon  # lifecycle stage
    luminosity: float  # 0-100 activity level
    polarity: Polarity  # resonance/affinity type
    dimensionality: int  # 0+ fractal depth
    alignment: Alignment  # 8th dimension for social dynamics

    @property
    def address(self) -> str:
        """Generate canonical FractalStat address string"""
        return f"FractalStat-{self.realm.value[0].upper()}-{self.lineage:03d}-{int(self.adjacency):02d}-{self.horizon.value[0].upper()}-{int(self.luminosity):02d}-{self.polarity.value[0].upper()}-{self.dimensionality}-{self.alignment.value[0].upper()}"

    @staticmethod
    def from_address(address: str) -> "FractalStatCoordinates":
        """Parse FractalStat address back to coordinates"""
        # Format: FractalStat-R-LLL-AA-H-LL-P-D-A (9 parts total)
        parts = address.split("-")
        if len(parts) != 9 or parts[0] != "FractalStat":
            raise ValueError(f"Invalid FractalStat address: {address}")

        realm_map = {r.value[0].upper(): r for r in Realm}
        horizon_map = {h.value[0].upper(): h for h in Horizon}
        polarity_map = {p.value[0].upper(): p for p in Polarity}
        alignment_map = {a.value[0].upper(): a for a in Alignment}

        try:
            return FractalStatCoordinates(
                realm=realm_map[parts[1]],
                lineage=int(parts[2]),
                adjacency=float(parts[3]),
                horizon=horizon_map[parts[4]],
                luminosity=float(parts[5]),
                polarity=polarity_map[parts[6]],
                dimensionality=int(parts[7]),
                alignment=alignment_map[parts[8]],
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid FractalStat address: {address}") from e

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "realm": self.realm.value,
            "lineage": self.lineage,
            "adjacency": self.adjacency,
            "horizon": self.horizon.value,
            "luminosity": self.luminosity,
            "polarity": self.polarity.value,
            "dimensionality": self.dimensionality,
            "alignment": self.alignment.value,
            "address": self.address,
        }


# ============================================================================
# Lifecycle Event Tracking
# ============================================================================


@dataclass
class LifecycleEvent:
    """Record of significant moments in entity history"""

    timestamp: datetime
    event_type: str  # "birth", "evolution", "mint", etc.
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "description": self.description,
            "metadata": self.metadata,
        }


# ============================================================================
# FractalStat Entity Base Class
# ============================================================================


@dataclass
class FractalStatEntity(ABC):
    """
    Abstract base class for all FractalStat-addressed entities.

    8-dimensional successor to fractalstat with enhanced expressivity.

    Provides:
    - Hybrid encoding (bridge between legacy and FractalStat systems)
    - 8D coordinate assignment
    - Entanglement tracking
    - Temporal tracking
    - NFT metadata
    """

    # Identity
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""  # Overridden in subclasses

    # FractalStat Addressing (8D)
    fractalstat: Optional[FractalStatCoordinates] = None

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
    created_at: datetime = field(default_factory=_utc_now)
    last_activity: datetime = field(default_factory=_utc_now)
    lifecycle_events: List[LifecycleEvent] = field(default_factory=list)

    # Owner/User
    owner_id: str = ""

    # User Preferences
    opt_in_fractalstat_nft: bool = True  # Renamed from opt_in_fractalstat_nft
    opt_in_blockchain: bool = False
    preferred_zoom_level: int = 1  # Default display level

    def __post_init__(self):
        """Initialize FractalStat coordinates if not provided"""
        if self.fractalstat is None:
            self.fractalstat = self._compute_fractalstat_coordinates()
        self._record_event("genesis", "Entity initialized in FractalStat space")

    # ========================================================================
    # Abstract Methods (Implemented by Subclasses)
    # ========================================================================

    @abstractmethod
    def _compute_fractalstat_coordinates(self) -> FractalStatCoordinates:
        """
        Compute 8D FractalStat coordinates from entity data.
        Each subclass defines its own coordinate mapping.
        """

    @abstractmethod
    def to_collectible_card_data(self) -> Dict[str, Any]:
        """Convert entity to collectible card display format"""

    @abstractmethod
    def validate_hybrid_encoding(self) -> Tuple[bool, str]:
        """
        Validate that FractalStat coordinates correctly encode legacy data.
        Returns (is_valid, error_message_or_empty_string)
        """

    # ========================================================================
    # Event Tracking
    # ========================================================================

    def _record_event(
        self,
        event_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Record a lifecycle event"""
        event = LifecycleEvent(
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            description=description,
            metadata=metadata or {},
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
            self._record_event(
                "entanglement_added",
                f"Entangled with {other_entity_id}",
                {"strength": strength},
            )

    def remove_entanglement(self, other_entity_id: str):
        """Remove entanglement with another entity"""
        if other_entity_id in self.entangled_entities:
            idx = self.entangled_entities.index(other_entity_id)
            self.entangled_entities.pop(idx)
            self.entanglement_strength.pop(idx)
            self._record_event(
                "entanglement_removed", f"Untangled from {other_entity_id}"
            )

    def get_entanglements(self) -> List[Tuple[str, float]]:
        """Get all entangled entities with strength"""
        return list(zip(self.entangled_entities, self.entanglement_strength))

    def update_entanglement_strength(self, other_entity_id: str, new_strength: float):
        """Update entanglement strength with another entity"""
        if other_entity_id in self.entangled_entities:
            idx = self.entangled_entities.index(other_entity_id)
            old_strength = self.entanglement_strength[idx]
            self.entanglement_strength[idx] = new_strength
            self._record_event(
                "entanglement_updated",
                f"Entanglement strength changed {old_strength:.2f} -> {new_strength:.2f}",
            )

    # ========================================================================
    # LUCA Bootstrap
    # ========================================================================

    @property
    def luca_distance(self) -> int:
        """Distance from LUCA (Last Universal Common Ancestor)"""
        if self.fractalstat is None:
            raise ValueError("fractalstat coordinates must be initialized")
        return self.fractalstat.lineage

    def get_luca_trace(self) -> Dict[str, Any]:
        """
        Get path back to LUCA bootstrap origin.
        In a real system, this would trace parent entities.
        """
        if self.fractalstat is None:
            raise ValueError("fractalstat coordinates must be initialized")
        return {
            "entity_id": self.entity_id,
            "luca_distance": self.luca_distance,
            "realm": self.fractalstat.realm.value,
            "lineage": self.fractalstat.lineage,
            "created_at": self.created_at.isoformat(),
            "migration_source": self.migration_source,
            "event_count": len(self.lifecycle_events),
        }

    # ========================================================================
    # NFT Integration
    # ========================================================================

    def prepare_for_minting(self) -> Dict[str, Any]:
        """
        Generate NFT metadata for minting.
        Returns ERC-721/ERC-1155 compatible metadata object.
        """
        if not self.opt_in_fractalstat_nft:
            raise ValueError("Entity not opted in to FractalStat-NFT system")

        if self.fractalstat is None:
            raise ValueError("fractalstat coordinates must be initialized")
        card_data = self.to_collectible_card_data()

        return {
            "name": card_data.get("title", self.entity_id),
            "description": card_data.get("fluff_text", ""),
            "image": card_data.get("artwork_url", ""),
            "external_url": f"https://theseed.example.com/entity/{self.entity_id}",
            "attributes": [
                {"trait_type": "Entity Type", "value": self.entity_type},
                {"trait_type": "Realm", "value": self.fractalstat.realm.value},
                {"trait_type": "Lineage", "value": self.fractalstat.lineage},
                {"trait_type": "Horizon", "value": self.fractalstat.horizon.value},
                {
                    "trait_type": "Luminosity",
                    "value": int(self.fractalstat.luminosity),
                },
                {"trait_type": "Polarity", "value": self.fractalstat.polarity.value},
                {
                    "trait_type": "Dimensionality",
                    "value": self.fractalstat.dimensionality,
                },
                {"trait_type": "Alignment", "value": self.fractalstat.alignment.value},
                {
                    "trait_type": "FractalStat Address",
                    "value": self.fractalstat.address,
                },
            ],
            "properties": card_data.get("properties", {}),
        }

    def record_mint(self, contract_address: str, token_id: int, ipfs_hash: str):
        """Record successful NFT minting"""
        self.nft_minted = True
        self.nft_contract = contract_address
        self.nft_token_id = token_id
        self.nft_metadata_ipfs = ipfs_hash
        self._record_event(
            "nft_minted",
            f"Minted as ERC-721 token #{token_id}",
            {
                "contract": contract_address,
                "token_id": token_id,
                "ipfs_hash": ipfs_hash,
            },
        )

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON storage"""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "fractalstat": self.fractalstat.to_dict() if self.fractalstat else None,
            "legacy_data": self.legacy_data,
            "migration_source": self.migration_source,
            "nft_minted": self.nft_minted,
            "nft_contract": self.nft_contract,
            "nft_token_id": self.nft_token_id,
            "nft_metadata_ipfs": self.nft_metadata_ipfs,
            "entangled_entities": self.entangled_entities,
            "entanglement_strength": self.entanglement_strength,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "lifecycle_events": [e.to_dict() for e in self.lifecycle_events],
            "owner_id": self.owner_id,
            "opt_in_fractalstat_nft": self.opt_in_fractalstat_nft,
            "opt_in_blockchain": self.opt_in_blockchain,
            "preferred_zoom_level": self.preferred_zoom_level,
        }

    def save_to_file(self, path: Path):
        """Persist entity to JSON file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, path: Path) -> "FractalStatEntity":
        """Load entity from JSON file (must know concrete type)"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        entity_type = data.get("entity_type", "unknown")
        raise NotImplementedError(
            f"Use subclass load methods (detected entity_type: {entity_type}). "
            "Use factory pattern to instantiate correct subclass."
        )

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
        if level < 1 or level > 8:  # Increased max zoom level for 8D
            raise ValueError(f"Invalid zoom level: {level}")

        if self.fractalstat is None:
            raise ValueError("FractalStat coordinates must be initialized")
        card_data = self.to_collectible_card_data()

        base = {
            "zoom_level": level,
            "entity_id": self.entity_id,
            "fractalstat_address": self.fractalstat.address,
            "created_at": self.created_at.isoformat(),
        }

        if level == 1:
            # Badge: Just icon + rarity
            return {
                **base,
                "type": "badge",
                "icon": card_data.get("icon_url"),
                "rarity": card_data.get("rarity"),
            }

        elif level == 2:
            # Dog-tag: Icon, title, key stats
            return {
                **base,
                "type": "dog_tag",
                "icon": card_data.get("icon_url"),
                "title": card_data.get("title"),
                "stats": card_data.get("key_stats"),
            }

        elif level == 3:
            # Full card
            return {**base, "type": "collectible_card", **card_data}

        elif level == 4:
            # Profile panel
            return {
                **base,
                "type": "profile_panel",
                **card_data,
                "owner": self.owner_id,
                "entangled_count": len(self.entangled_entities),
                "events": len(self.lifecycle_events),
            }

        elif level == 5:
            # Full profile page
            return {
                **base,
                "type": "entity_profile",
                **card_data,
                "owner": self.owner_id,
                "lifecycle_events": [e.to_dict() for e in self.lifecycle_events],
                "entanglements": self.get_entanglements(),
                "luca_trace": self.get_luca_trace(),
            }

        elif level == 6:
            # 8th dimension awareness
            return {
                **base,
                "type": "fractal_descent",
                "fractalstat_dimensions": self.fractalstat.to_dict(),
                "alignment_dynamics": self._get_alignment_details(),
                "realm_details": self._get_realm_details(),
                "entanglement_network": self.get_entanglements(),
                "event_chronology": [e.to_dict() for e in self.lifecycle_events],
                "luca_trace": self.get_luca_trace(),
            }

        else:  # level 7+
            # Full fractal descent with 8D awareness
            return {
                **base,
                "type": "fractal_descent",
                "fractalstat_dimensions": self.fractalstat.to_dict(),
                "alignment_dynamics": self._get_alignment_details(),
                "realm_details": self._get_realm_details(),
                "entanglement_network": self.get_entanglements(),
                "event_chronology": [e.to_dict() for e in self.lifecycle_events],
                "luca_trace": self.get_luca_trace(),
            }

    def _get_realm_details(self) -> Dict[str, Any]:
        """Override in subclasses to provide realm-specific details"""
        return {}

    def _get_alignment_details(self) -> Dict[str, Any]:
        """Get alignment-based social/coordination analysis"""
        if self.fractalstat is None:
            return {}

        alignment = self.fractalstat.alignment
        # Analyze social coordination patterns based on alignment
        coordination_style = {
            Alignment.LAWFUL_GOOD: "structured_harmonious",
            Alignment.NEUTRAL_GOOD: "balanced_harmonious",
            Alignment.CHAOTIC_GOOD: "flexible_harmonious",
            Alignment.LAWFUL_NEUTRAL: "structured_pragmatic",
            Alignment.TRUE_NEUTRAL: "balanced_pragmatic",
            Alignment.CHAOTIC_NEUTRAL: "flexible_pragmatic",
            Alignment.LAWFUL_EVIL: "structured_destructive",
            Alignment.NEUTRAL_EVIL: "balanced_destructive",
            Alignment.CHAOTIC_EVIL: "flexible_destructive",
            Alignment.HARMONIC: "naturally_coordinating",
            Alignment.ENTROPIC: "naturally_disruptive",
            Alignment.SYMBIOTIC: "mutually_beneficial",
        }.get(alignment, "unknown")

        return {
            "alignment": alignment.value,
            "coordination_style": coordination_style,
            "social_dynamics": self._analyze_social_dynamics(),
        }

    def _analyze_social_dynamics(self) -> Dict[str, Any]:
        """Analyze social interaction patterns based on entanglement and alignment"""
        if self.fractalstat is None:
            return {}

        # Simplified social analysis based on alignment
        alignment = self.fractalstat.alignment

        if alignment in [Alignment.LAWFUL_GOOD, Alignment.HARMONIC]:
            social_pattern = "coordinating_harmonious"
        elif alignment in [Alignment.CHAOTIC_EVIL, Alignment.ENTROPIC]:
            social_pattern = "disruptive_chaotic"
        else:
            social_pattern = "pragmatic_balanced"

        return {
            "social_pattern": social_pattern,
            "entanglement_quality": len(self.entangled_entities)
            * 0.1,  # Simplified metric
            "coordination_potential": self._calculate_coordination_potential(),
        }

    def _calculate_coordination_potential(self) -> float:
        """Calculate coordination potential based on alignment and entanglements"""
        # Simplified calculation - would be more sophisticated in production
        base_potential = len(self.entangled_entities) * 0.1

        # Alignment modifiers
        alignment_bonus = {
            Alignment.HARMONIC: 1.5,
            Alignment.SYMBIOTIC: 1.3,
            Alignment.LAWFUL_GOOD: 1.2,
            Alignment.CHAOTIC_EVIL: -0.5,
            Alignment.ENTROPIC: -0.3,
        }.get(
            self.fractalstat.alignment if self.fractalstat else Alignment.TRUE_NEUTRAL,
            1.0,
        )

        return min(1.0, base_potential * alignment_bonus)


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


# ============================================================================
# BitChain Entity (moved from fractalstat_experiments to break circular import)
# ============================================================================

class DataClass(Enum):
    """Data sensitivity classification."""

    PUBLIC = "PUBLIC"  # Anyone can read
    SENSITIVE = "SENSITIVE"  # Authenticated users, role-based
    PII = "PII"  # Owner-only, requires 2FA


class Capability(Enum):
    """Recovery capability levels."""

    COMPRESSED = "compressed"  # Read-only mist form, no expansion
    PARTIAL = "partial"  # Anonymized expansion, limited fields
    FULL = "full"  # Complete recovery


# Coordinate data class for BitChain (different from FractalStatCoordinates)
@dataclass
class Coordinates:
    """FractalStat 8-dimensional coordinates with enhanced expressivity."""

    realm: str  # Domain: data, narrative, system, faculty, event, pattern, void, temporal
    lineage: int  # Generation from LUCA
    adjacency: List[str]  # Relational neighbors (append-only)
    horizon: str  # Lifecycle stage
    luminosity: float  # 0-100 activity level
    polarity: Polarity  # Resonance/affinity type
    dimensionality: int  # 0+ fractal depth
    alignment: Alignment  # Social alignment dynamics - NEW DIMENSION

    def to_dict(self) -> Dict[str, Any]:
        """Convert to canonical dict with normalized floats."""
        return {
            # Append-only, but stored sorted
            "realm": self.realm,
            "lineage": self.lineage,
            "adjacency": sorted(self.adjacency),
            "horizon": self.horizon,
            "luminosity": normalize_float(self.luminosity),
            "polarity": self.polarity.name,
            "dimensionality": self.dimensionality,
            "alignment": self.alignment.name,
        }


@dataclass
class BitChain:
    """
    Minimal addressable unit in FractalStat space.
    Represents a single entity instance (manifestation).

    Security fields (Phase 1 Doctrine: Authentication + Access Control):
    - data_classification: Sensitivity level (PUBLIC, SENSITIVE, PII)
    - access_control_list: Roles allowed to recover this bitchain
    - owner_id: User who owns this bitchain
    - encryption_key_id: Optional key for encrypted-at-rest data
    """

    id: str  # Unique entity ID
    entity_type: str  # Type: concept, artifact, agent, etc.
    realm: str  # Domain classification
    coordinates: Coordinates  # FractalStat 8D position
    created_at: str  # ISO8601 UTC timestamp
    state: Dict[str, Any]  # Mutable state data

    # Security fields (Phase 1)
    data_classification: DataClass = DataClass.PUBLIC
    access_control_list: List[str] = field(default_factory=lambda: ["owner"])
    owner_id: Optional[str] = None
    encryption_key_id: Optional[str] = None

    def __post_init__(self):
        """Normalize timestamps."""
        self.created_at = normalize_timestamp(self.created_at)

    def to_canonical_dict(self) -> Dict[str, Any]:
        """Convert to canonical form for hashing."""
        return {
            "created_at": self.created_at,
            "entity_type": self.entity_type,
            "id": self.id,
            "realm": self.realm,
            "fractalstat_coordinates": self.coordinates.to_dict(),
            "state": sort_json_keys(self.state),
        }

    def compute_address(self) -> str:
        """Compute this bit-chain's FractalStat address (hash)."""
        return compute_address_hash(self.to_canonical_dict())

    def get_fractalstat_uri(self) -> str:
        """Generate FractalStat URI address format."""
        coords = self.coordinates
        adjacency_hash = compute_address_hash({"adjacency": sorted(coords.adjacency)})[
            :8
        ]

        uri = (
            f"fractalstat://{coords.realm}/{coords.lineage}/{adjacency_hash}/{coords.horizon}"
        )
        uri += f"?r={normalize_float(coords.luminosity)}&p={coords.polarity.name}"
        uri += f"&d={coords.dimensionality}&s={self.id}&a={coords.alignment.name}"

        return uri


# ============================================================================
# Constants and utilities for BitChain (moved from fractalstat_experiments)
# ============================================================================

# Use cryptographically secure random number generator
secure_random = secrets.SystemRandom()

REALMS = ["data", "narrative", "system", "faculty", "event", "pattern", "void"]
HORIZONS = ["genesis", "emergence", "peak", "decay", "crystallization"]
POLARITY_LIST = ["logic", "creativity", "order", "chaos", "balance", "achievement",
            "contribution", "community", "technical", "creative", "unity", "void"]
ALIGNMENT_LIST = ["lawful_good", "neutral_good", "chaotic_good", "lawful_neutral",
            "true_neutral", "chaotic_neutral", "lawful_evil", "neutral_evil"]
ENTITY_TYPES = [
    "concept",
    "artifact",
    "agent",
    "lineage",
    "adjacency",
    "horizon",
    "fragment",
]


def normalize_float(value: float, decimal_places: int = 8) -> str:
    """
    Normalize floating point to 8 decimal places using banker's rounding.
    """
    if isinstance(value, float):
        if value != value or value == float("inf") or value == float("-inf"):
            raise ValueError(f"NaN and Inf not allowed: {value}")

    # Use Decimal for precise rounding
    d = Decimal(str(value))
    quantized = d.quantize(Decimal(10) ** -decimal_places, rounding=ROUND_HALF_EVEN)

    # Convert to string and strip trailing zeros
    result = str(quantized)
    if "." in result:
        result = result.rstrip("0")
        if result.endswith("."):
            result += "0"
    elif "E" in result or "e" in result:
        # Handle scientific notation
        result = "0.0"

    return result


def normalize_timestamp(ts: Optional[str] = None) -> str:
    """
    Normalize timestamp to ISO8601 UTC with millisecond precision.
    """
    if ts is None:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    else:
        # Parse input timestamp and convert to UTC
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        now = datetime.fromisoformat(ts).astimezone(timezone.utc)

    # Format with millisecond precision
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def sort_json_keys(obj: Any) -> Any:
    """
    Recursively sort all JSON object keys in ASCII order (case-sensitive).
    """
    if isinstance(obj, dict):
        return {k: sort_json_keys(obj[k]) for k in sorted(obj.keys())}
    elif isinstance(obj, list):
        return [sort_json_keys(item) for item in obj]
    else:
        return obj


def canonical_serialize(data: Dict[str, Any]) -> str:
    """
    Serialize to canonical form for deterministic hashing.
    """
    sorted_data = sort_json_keys(data)
    canonical = json.dumps(
        sorted_data, separators=(",", ":"), ensure_ascii=True, sort_keys=False
    )
    return canonical


def compute_address_hash(data: Dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of canonical serialization.
    """
    canonical = canonical_serialize(data)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def generate_random_bitchain(seed: Optional[int] = None) -> BitChain:
    """
    Generate a random bit-chain for testing and validation experiments.
    """
    
    # Use seedable random when seed is provided, otherwise use secure random
    if seed is not None:
        rng = random.Random(seed)
        base_id = hashlib.sha256(str(seed).encode()).hexdigest()[:32]
        id_str = f"{base_id[:8]}-{base_id[8:12]}-{base_id[12:16]}-{base_id[16:20]}"
        id_str += f"-{base_id[20:32]}"
        created_at_str = f"2024-01-01T{seed % 24:02d}:{(seed // 24) % 60:02d}"
        created_at_str += f":{(seed // 1440) % 60:02d}.000Z"
    else:
        rng = secure_random
        id_str = str(uuid.uuid4())
        created_at_str = datetime.now(timezone.utc).isoformat()

    # Replace all instances of `secure_random.` with `rng.` in the rest of the function
    adjacency_ids = [
        (
            hashlib.sha256(f"{seed}-adj-{i}".encode()).hexdigest()[:32]
            if seed is not None
            else str(uuid.uuid4())
        )
        for i in range(rng.randint(0, 5))  # Changed from secure_random.randint
    ]

    if seed is not None and adjacency_ids:
        adjacency_ids = [
            f"{uuid_hex[:8]}-{uuid_hex[8:12]}-{uuid_hex[12:16]}-{uuid_hex[16:20]}"
            f"-{uuid_hex[20:32]}"
            for uuid_hex in adjacency_ids
        ]

    # Generate coordinates with alignment
    luminosity_val = rng.uniform(0, 100)  # Changed from secure_random.uniform
    polarity_val = rng.choice(POLARITY_LIST)  # Changed from secure_random.choice
    dimensionality_val = rng.randint(0, 5)  # Changed from secure_random.randint
    alignment_val = rng.choice(list(Alignment))  # Changed from secure_random.choice

    return BitChain(
        id=id_str,
        entity_type=rng.choice(ENTITY_TYPES),  # Changed from secure_random.choice
        realm=rng.choice(REALMS),  # Changed from secure_random.choice
        coordinates=Coordinates(
            realm=rng.choice(REALMS),  # Changed from secure_random.choice
            lineage=rng.randint(1, 100),  # Changed from secure_random.randint
            adjacency=adjacency_ids,
            horizon=rng.choice(HORIZONS),  # Changed from secure_random.choice
            luminosity=luminosity_val,
            polarity=Polarity[polarity_val.upper()],
            dimensionality=dimensionality_val,
            alignment=alignment_val,
        ),
        created_at=created_at_str,
        state={"value": rng.randint(0, 1000)},  # Changed from secure_random.randint
    )
