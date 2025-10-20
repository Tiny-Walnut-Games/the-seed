#!/usr/bin/env python3
"""
BadgeSTAT7Entity - Achievement Badges and Sponsor Rings in STAT7 space
Bridges legacy badge system to new STAT7 addressing

Special support for Seed-Sponsor "tree ring" badges showing support tenure.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from enum import Enum

from stat7_entity import (
    STAT7Entity, STAT7Coordinates, LifecycleEvent,
    Realm, Horizon, Polarity,
    hash_for_coordinates, compute_adjacency_score
)


# ============================================================================
# Badge-Specific Enums
# ============================================================================

class BadgeCategory(Enum):
    """Achievement badge categories"""
    CONTRIBUTION = "contribution"  # Code, docs, ideas
    COMMUNITY = "community"        # Mentoring, helping, collaboration
    TECHNICAL = "technical"        # Deep technical expertise
    CREATIVE = "creative"          # Innovation, novel solutions
    ACHIEVEMENT = "achievement"    # Milestones, goals
    SPONSOR = "sponsor"            # Supporter badges
    FACULTY = "faculty"            # Faculty-exclusive


class BadgeRarity(Enum):
    """Badge rarity tiers"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class SponsorTier(Enum):
    """Seed-Sponsor supporter tiers (tree rings)"""
    RING_0 = 0          # No support / Regular user
    RING_1 = 1          # 1 year as supporter (Sapling)
    RING_2 = 2          # 2 years (Oak)
    RING_3 = 3          # 3 years (Ancient)
    RING_4 = 4          # 4 years
    RING_5_PLUS = 5     # 5+ years (Primordial)


# ============================================================================
# Badge STAT7 Entity
# ============================================================================

@dataclass
class BadgeSTAT7Entity(STAT7Entity):
    """
    Represents an achievement badge or sponsor ring in STAT7 space.
    
    Hybrid encoding maps:
    - badge_type → Polarity (category resonance)
    - earn_count → Lineage (how many times earned)
    - related_badges → Adjacency (categorical proximity)
    - status → Horizon (active, crystallized, archived)
    - visibility → Luminosity (how prominently displayed)
    - For sponsor rings: tier/years → Lineage (support duration)
    """
    
    entity_type: str = "badge"
    
    # Badge Identity
    badge_type: str = ""  # "first_contribution", "100_ideas", "sponsor_founder", etc.
    category: BadgeCategory = BadgeCategory.ACHIEVEMENT
    is_sponsor_ring: bool = False  # Special flag for sponsor badges
    
    # Sponsor Ring Specific
    sponsor_tier: Optional[SponsorTier] = None
    sponsor_years: int = 0
    sponsor_benefits: List[str] = field(default_factory=list)  # Early access, slots, etc.
    
    # Achievement Tracking
    earn_count: int = 1  # How many times earned (if repeatable)
    total_earners: int = 0  # Total users with this badge
    max_earnable: Optional[int] = None  # None = unlimited, N = limit
    
    # Status
    earned_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"  # "active", "archived", "crystallized"
    
    # Display & Metadata
    icon_url: str = ""
    description: str = ""
    unlock_criteria: str = ""
    
    # Relations
    related_badge_ids: List[str] = field(default_factory=list)
    parent_companion_id: Optional[str] = None  # For earned badges from companion
    
    def _compute_stat7_coordinates(self) -> STAT7Coordinates:
        """
        Map badge data to STAT7 coordinates.
        
        Realm: BADGE or SPONSOR_RING
        Lineage: For badges = earn_count; for sponsors = years_supported
        Adjacency: Related badge proximity score
        Horizon: Maps from status
        Luminosity: Visibility/prominence level
        Polarity: From badge category (special UNITY for sponsors)
        Dimensionality: Recursion depth (related badges)
        """
        
        # 1. Realm: BADGE or SPONSOR_RING
        realm = Realm.SPONSOR_RING if self.is_sponsor_ring else Realm.BADGE
        
        # 2. Lineage: For sponsors, it's years; for badges, earn count
        if self.is_sponsor_ring:
            lineage = self.sponsor_years
        else:
            lineage = self.earn_count - 1  # 0-based
        
        # 3. Adjacency: Related badge proximity
        adjacency = self._compute_related_badge_adjacency()
        
        # 4. Horizon: From status
        horizon = self._map_status_to_horizon()
        
        # 5. Luminosity: Visibility/prominence
        luminosity = self._compute_luminosity()
        
        # 6. Polarity: From category (special UNITY for sponsors)
        if self.is_sponsor_ring:
            polarity = Polarity.UNITY  # Special polarity for sponsor support
        else:
            polarity = self._map_category_to_polarity()
        
        # 7. Dimensionality: Related badge depth
        dimensionality = len(self.related_badge_ids)
        
        return STAT7Coordinates(
            realm=realm,
            lineage=lineage,
            adjacency=adjacency,
            horizon=horizon,
            luminosity=luminosity,
            polarity=polarity,
            dimensionality=dimensionality
        )
    
    def _map_status_to_horizon(self) -> Horizon:
        """Map badge status to STAT7 Horizon"""
        mapping = {
            "active": Horizon.PEAK,
            "crystallized": Horizon.CRYSTALLIZATION,
            "archived": Horizon.DECAY,
        }
        return mapping.get(self.status, Horizon.PEAK)
    
    def _map_category_to_polarity(self) -> Polarity:
        """Map badge category to STAT7 Polarity"""
        mapping = {
            BadgeCategory.CONTRIBUTION: Polarity.CONTRIBUTION,
            BadgeCategory.COMMUNITY: Polarity.COMMUNITY,
            BadgeCategory.TECHNICAL: Polarity.TECHNICAL,
            BadgeCategory.CREATIVE: Polarity.CREATIVE,
            BadgeCategory.ACHIEVEMENT: Polarity.ACHIEVEMENT,
            BadgeCategory.SPONSOR: Polarity.UNITY,
            BadgeCategory.FACULTY: Polarity.VOID,  # Special void for faculty
        }
        return mapping.get(self.category, Polarity.VOID)
    
    def _compute_related_badge_adjacency(self) -> float:
        """
        Compute adjacency based on related badge connections.
        More related badges = higher adjacency (more entangled).
        """
        if not self.related_badge_ids:
            return 25.0  # Isolated badge
        
        # Each related badge adds to adjacency
        # Cap at 100 (fully entangled with other badges)
        return min(100.0, 25.0 + (len(self.related_badge_ids) * 10))
    
    def _compute_luminosity(self) -> float:
        """
        Compute luminosity (visibility/prominence).
        
        Factors:
        - Sponsor rings: Always high luminosity (100)
        - Rare badges: High luminosity
        - Recently earned: High luminosity
        - Common badges: Lower luminosity
        """
        if self.is_sponsor_ring:
            return 100.0  # Sponsor badges always maximally visible
        
        # Age affects luminosity (recent badges brighter)
        days_since_earned = (datetime.utcnow() - self.earned_at).days
        age_factor = max(30.0, 100.0 - (days_since_earned / 10))  # Decays over time
        
        # Rarity affects luminosity
        rarity = self._compute_rarity()
        rarity_luminosity = {
            BadgeRarity.COMMON: 40.0,
            BadgeRarity.UNCOMMON: 55.0,
            BadgeRarity.RARE: 70.0,
            BadgeRarity.EPIC: 85.0,
            BadgeRarity.LEGENDARY: 95.0,
            BadgeRarity.MYTHIC: 100.0,
        }.get(rarity, 50.0)
        
        # Average age and rarity factors
        return (age_factor + rarity_luminosity) / 2.0
    
    def validate_hybrid_encoding(self) -> Tuple[bool, str]:
        """Validate STAT7 coordinates correctly encode badge data"""
        computed = self._compute_stat7_coordinates()
        stored = self.stat7
        
        if computed.realm != stored.realm:
            return False, f"Realm mismatch: {computed.realm} != {stored.realm}"
        
        if computed.lineage != stored.lineage:
            return False, f"Lineage mismatch: {computed.lineage} != {stored.lineage}"
        
        if abs(computed.adjacency - stored.adjacency) > 2.0:
            return False, f"Adjacency mismatch: {computed.adjacency} != {stored.adjacency}"
        
        if computed.horizon != stored.horizon:
            return False, f"Horizon mismatch: {computed.horizon} != {stored.horizon}"
        
        if abs(computed.luminosity - stored.luminosity) > 10.0:
            return False, f"Luminosity mismatch: {computed.luminosity} != {stored.luminosity}"
        
        if computed.polarity != stored.polarity:
            return False, f"Polarity mismatch: {computed.polarity} != {stored.polarity}"
        
        if computed.dimensionality != stored.dimensionality:
            return False, f"Dimensionality mismatch: {computed.dimensionality} != {stored.dimensionality}"
        
        return True, ""
    
    def to_collectible_card_data(self) -> Dict[str, Any]:
        """Convert badge to collectible card display format"""
        rarity = self._compute_rarity()
        
        if self.is_sponsor_ring:
            title = f"Seed-Sponsor • {self.sponsor_tier.name}"
            subtitle = f"{self.sponsor_years} Year{'s' if self.sponsor_years != 1 else ''} of Support"
        else:
            title = self.badge_type.replace('_', ' ').title()
            subtitle = self.category.value.title()
        
        return {
            'title': title,
            'subtitle': subtitle,
            'type': 'Sponsor Ring' if self.is_sponsor_ring else 'Achievement Badge',
            'rarity': rarity.value,
            'rarity_stars': self._rarity_to_stars(rarity),
            
            # Artwork
            'artwork_url': self.icon_url or f"ipfs://badge-{self.entity_id}.png",
            'icon_url': self.icon_url or f"ipfs://icon-{self.entity_id}.png",
            
            # Key stats for zoom level 2
            'key_stats': {
                'Category': self.category.value.title(),
                'Earned': self.earned_at.strftime('%Y-%m-%d'),
                'Rarity': rarity.value.title(),
            },
            
            # Full stats for zoom level 3
            'stats': {
                'Category': self.category.value,
                'Earned Times': self.earn_count,
                'Total Earners': self.total_earners,
                'Status': self.status,
            },
            
            # For sponsor rings, add ring details
            'sponsor_ring_details': {
                'Years Supported': self.sponsor_years,
                'Tier': self.sponsor_tier.name if self.sponsor_tier else "Unknown",
                'Benefits': self.sponsor_benefits,
                'Visual Rings': self.sponsor_years,  # For SVG rendering
            } if self.is_sponsor_ring else None,
            
            # Description and criteria
            'description': self.description,
            'unlock_criteria': self.unlock_criteria,
            'fluff_text': self._generate_lore(),
            
            # STAT7 details
            'stat7_details': {
                'Realm': self.stat7.realm.value,
                'Lineage': f"Gen {self.stat7.lineage}",
                'Horizon': self.stat7.horizon.value,
                'Polarity': self.stat7.polarity.value,
                'Dimensionality': f"L{self.stat7.dimensionality}",
            },
            
            # Related badges
            'related_badges': self.related_badge_ids,
            
            # NFT metadata
            'mint_info': {
                'Serial': self.stat7.address,
                'Minted': self.nft_minted,
                'Contract': self.nft_contract or "Not minted",
                'TokenID': self.nft_token_id or "—",
            },
            
            # Properties for ERC-721
            'properties': {
                'category': {'type': 'string', 'description': 'Badge category'},
                'earn_count': {'type': 'integer', 'description': 'Times earned'},
                'sponsor': {'type': 'boolean', 'description': 'Is sponsor ring'},
            }
        }
    
    def _compute_rarity(self) -> BadgeRarity:
        """Compute rarity tier based on STAT7 and badge properties"""
        if self.is_sponsor_ring:
            # Sponsor rings scale with years
            if self.sponsor_years >= 5:
                return BadgeRarity.MYTHIC
            elif self.sponsor_years >= 3:
                return BadgeRarity.LEGENDARY
            else:
                return BadgeRarity.EPIC
        
        # Regular badges: based on luminosity + total earners
        score = self.stat7.luminosity
        if self.total_earners < 5:
            score += 30
        elif self.total_earners < 20:
            score += 15
        
        if score < 40:
            return BadgeRarity.COMMON
        elif score < 55:
            return BadgeRarity.UNCOMMON
        elif score < 70:
            return BadgeRarity.RARE
        elif score < 85:
            return BadgeRarity.EPIC
        else:
            return BadgeRarity.LEGENDARY
    
    def _rarity_to_stars(self, rarity: BadgeRarity) -> str:
        """Convert rarity to star rating"""
        mapping = {
            BadgeRarity.COMMON: "★",
            BadgeRarity.UNCOMMON: "★★",
            BadgeRarity.RARE: "★★★",
            BadgeRarity.EPIC: "★★★★",
            BadgeRarity.LEGENDARY: "★★★★★",
            BadgeRarity.MYTHIC: "★★★★★✨",
        }
        return mapping.get(rarity, "★")
    
    def _generate_lore(self) -> str:
        """Generate flavor text based on badge type"""
        if self.is_sponsor_ring:
            tier_descriptions = {
                SponsorTier.RING_1: "A young Sapling, just beginning its growth in The Seed",
                SponsorTier.RING_2: "An Oak-like supporter, deeply rooted in The Seed's foundation",
                SponsorTier.RING_3: "An Ancient tree of support, weathered by seasons of devotion",
                SponsorTier.RING_4: "A Primordial elder, witnessing epochs of The Seed's evolution",
                SponsorTier.RING_5_PLUS: "A cosmic tree reaching toward LUCA itself, support without end",
            }
            return tier_descriptions.get(
                self.sponsor_tier,
                f"A supporter's badge marking {self.sponsor_years} year{'s' if self.sponsor_years != 1 else ''} of devotion to The Seed."
            )
        
        return self.description or f"A testament to achievement: {self.badge_type.replace('_', ' ').lower()}"
    
    def _get_realm_details(self) -> Dict[str, Any]:
        """Provide badge-specific realm details for fractal descent"""
        details = {
            'badge_type': self.badge_type,
            'category': self.category.value,
            'status': self.status,
            'earn_count': self.earn_count,
            'total_earners': self.total_earners,
            'earned_at': self.earned_at.isoformat(),
            'related_badges': self.related_badge_ids,
        }
        
        if self.is_sponsor_ring:
            details['sponsor_ring'] = {
                'tier': self.sponsor_tier.name if self.sponsor_tier else None,
                'years': self.sponsor_years,
                'benefits': self.sponsor_benefits,
            }
        
        return details
    
    # ========================================================================
    # Badge-Specific Operations
    # ========================================================================
    
    def increment_earn_count(self):
        """Increment earn count (for repeatable badges)"""
        if self.max_earnable and self.earn_count >= self.max_earnable:
            raise ValueError(f"Badge {self.badge_type} reached max earnable limit: {self.max_earnable}")
        
        self.earn_count += 1
        self.stat7 = self._compute_stat7_coordinates()
        self._record_event("re_earned", f"Earned again (total: {self.earn_count})", {'earn_count': self.earn_count})
    
    def add_related_badge(self, badge_id: str):
        """Link to a related badge"""
        if badge_id not in self.related_badge_ids:
            self.related_badge_ids.append(badge_id)
            self.stat7 = self._compute_stat7_coordinates()
            self._record_event("related_badge_added", f"Linked to badge {badge_id}", {'related_badge': badge_id})
    
    def archive(self):
        """Archive badge (historical record)"""
        old_status = self.status
        self.status = "archived"
        self.stat7 = self._compute_stat7_coordinates()
        self._record_event("badge_archived", f"Status changed from {old_status} to archived")
    
    def crystallize(self):
        """Crystallize badge (permanent achievement)"""
        old_status = self.status
        self.status = "crystallized"
        self.stat7 = self._compute_stat7_coordinates()
        self._record_event("badge_crystallized", f"Status changed from {old_status} to crystallized")
    
    @classmethod
    def create_sponsor_ring(
        cls,
        owner_id: str,
        years_supported: int,
        tier: SponsorTier,
        benefits: List[str]
    ) -> 'BadgeSTAT7Entity':
        """Factory method to create a sponsor ring badge"""
        badge = cls(
            owner_id=owner_id,
            badge_type=f"sponsor_ring_{tier.name}",
            category=BadgeCategory.SPONSOR,
            is_sponsor_ring=True,
            sponsor_tier=tier,
            sponsor_years=years_supported,
            sponsor_benefits=benefits,
            description=f"Seed-Sponsor Badge ({years_supported} year{'s' if years_supported != 1 else ''})",
            unlock_criteria="Active Seed support subscription",
        )
        badge.status = "crystallized"  # Sponsor rings are permanent
        badge.stat7 = badge._compute_stat7_coordinates()
        return badge


if __name__ == "__main__":
    # Example: Regular achievement badge
    badge = BadgeSTAT7Entity(
        badge_type="first_contribution",
        category=BadgeCategory.CONTRIBUTION,
        owner_id="user_123",
        description="Congratulations on your first contribution!",
        unlock_criteria="Make at least 1 contribution",
        total_earners=127
    )
    
    print(f"Badge: {badge.badge_type}")
    print(f"STAT7 Address: {badge.stat7.address}")
    print(f"Rarity: {badge._compute_rarity().value}")
    
    # Example: Sponsor ring
    ring = BadgeSTAT7Entity.create_sponsor_ring(
        owner_id="sponsor_001",
        years_supported=3,
        tier=SponsorTier.RING_3,
        benefits=["early_access_48h", "extra_pet_slots_2", "founder_badge"]
    )
    
    print(f"\nSponsor Ring: {ring.badge_type}")
    print(f"STAT7 Address: {ring.stat7.address}")
    print(f"Rarity: {ring._compute_rarity().value}")
    print(f"Luminosity: {ring.stat7.luminosity}")