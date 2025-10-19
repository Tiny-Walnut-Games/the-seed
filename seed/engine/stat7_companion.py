#!/usr/bin/env python3
"""
CompanionSTAT7Entity - Pet/Familiar entities in STAT7 space
Bridges legacy pet system (XP, species, stage) to new STAT7 addressing
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
# Companion-Specific Enums
# ============================================================================

class PetSpecies(Enum):
    """Available pet species mapped to STAT7 archetypes"""
    # Fantasy themed
    SCROLLHOUND = "scrollhound"           # Document companion - LOGIC polarity
    CHRONO_CAT = "chrono_cat"            # Time-tracking - ORDER polarity
    DEBUGGER_FERRET = "debugger_ferret"  # Bug-hunting - CREATIVITY polarity
    CODE_PHOENIX = "code_phoenix"        # Rebirth - BALANCE polarity
    WISDOM_OWL = "wisdom_owl"            # Knowledge keeper - LOGIC polarity
    
    # Cyberpunk themed
    DATA_SPRITE = "data_sprite"          # Information - LOGIC polarity
    HACK_HOUND = "hack_hound"           # Security - ORDER polarity
    CIPHER_CAT = "cipher_cat"           # Encryption - CREATIVITY polarity
    
    # Space Opera themed
    VOID_WHALE = "void_whale"           # Massive - BALANCE polarity
    STAR_FOX = "star_fox"               # Agile - CREATIVITY polarity
    QUANTUM_QUAIL = "quantum_quail"     # Probability - CHAOS polarity


class PetStage(Enum):
    """Legacy pet evolution stages, maps to Horizon"""
    EGG = "egg"                    # Horizon.GENESIS
    HATCHLING = "hatchling"        # Horizon.EMERGENCE
    JUVENILE = "juvenile"          # Horizon.PEAK (young peak)
    ADULT = "adult"               # Horizon.PEAK (mature peak)
    ELDER = "elder"               # Horizon.DECAY
    LEGENDARY = "legendary"        # Horizon.CRYSTALLIZATION


class CompanionTrait(Enum):
    """Personality traits developed through play"""
    CURIOUS = "curious"
    PERSISTENT = "persistent"
    CREATIVE = "creative"
    SOCIAL = "social"
    METHODICAL = "methodical"
    ADVENTUROUS = "adventurous"
    PROTECTIVE = "protective"
    ANALYTICAL = "analytical"


class CompanionRarity(Enum):
    """Collectible rarity tiers"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"  # 1/1 ultra-rare


# ============================================================================
# Companion STAT7 Entity
# ============================================================================

@dataclass
class CompanionSTAT7Entity(STAT7Entity):
    """
    Represents a pet/companion in STAT7 space.
    
    Hybrid encoding maps:
    - species → Polarity (elemental affinity)
    - XP + stage → Lineage (generation/evolution)
    - traits → Adjacency (trait synergy)
    - activity → Luminosity (engagement level)
    - pet_id → Dimensionality (depth of detail)
    """
    
    entity_type: str = "companion"
    
    # Companion Identity
    species: PetSpecies = PetSpecies.SCROLLHOUND
    stage: PetStage = PetStage.EGG
    traits: List[CompanionTrait] = field(default_factory=list)
    
    # Experience & Progression
    xp: int = 0
    xp_history: List[Tuple[datetime, int]] = field(default_factory=list)  # (timestamp, amount)
    
    # Stats
    health: float = 100.0
    happiness: float = 100.0
    focus: float = 50.0
    
    # Evolution & Abilities
    evolution_count: int = 0
    special_abilities: List[str] = field(default_factory=list)
    
    # Metadata
    companion_name: str = ""
    genre_theme: str = "fantasy"  # fantasy, cyberpunk, space_opera
    batch_generation_seed: Optional[str] = None  # For deterministic NFT art
    
    def _compute_stat7_coordinates(self) -> STAT7Coordinates:
        """
        Map companion data to STAT7 coordinates.
        
        Realm: COMPANION (always)
        Lineage: Based on XP (0 XP = gen 0, scales by stages)
        Adjacency: Trait synergy score (0-100)
        Horizon: Maps from PetStage
        Luminosity: Derived from happiness + activity
        Polarity: Mapped from species
        Dimensionality: Fractal depth based on evolution count
        """
        
        # 1. Realm: Always COMPANION
        realm = Realm.COMPANION
        
        # 2. Lineage: Compute generation from XP
        # 0-500 XP = Gen 0, 500-1500 = Gen 1, etc.
        stage_xp_caps = [0, 500, 1500, 5000, 15000, 30000]
        lineage = sum(1 for cap in stage_xp_caps if self.xp >= cap)
        
        # 3. Adjacency: Trait synergy
        adjacency = self._compute_trait_synergy()
        
        # 4. Horizon: From pet stage
        horizon = self._map_stage_to_horizon()
        
        # 5. Luminosity: Engagement level
        luminosity = (self.happiness + self.focus) / 2.0
        
        # 6. Polarity: From species
        polarity = self._map_species_to_polarity()
        
        # 7. Dimensionality: Fractal depth
        dimensionality = self.evolution_count
        
        return STAT7Coordinates(
            realm=realm,
            lineage=lineage,
            adjacency=adjacency,
            horizon=horizon,
            luminosity=luminosity,
            polarity=polarity,
            dimensionality=dimensionality
        )
    
    def _map_stage_to_horizon(self) -> Horizon:
        """Map PetStage to STAT7 Horizon"""
        mapping = {
            PetStage.EGG: Horizon.GENESIS,
            PetStage.HATCHLING: Horizon.EMERGENCE,
            PetStage.JUVENILE: Horizon.PEAK,
            PetStage.ADULT: Horizon.PEAK,
            PetStage.ELDER: Horizon.DECAY,
            PetStage.LEGENDARY: Horizon.CRYSTALLIZATION,
        }
        return mapping.get(self.stage, Horizon.GENESIS)
    
    def _map_species_to_polarity(self) -> Polarity:
        """Map species to elemental polarity"""
        mapping = {
            # Fantasy
            PetSpecies.SCROLLHOUND: Polarity.LOGIC,
            PetSpecies.CHRONO_CAT: Polarity.ORDER,
            PetSpecies.DEBUGGER_FERRET: Polarity.CREATIVITY,
            PetSpecies.CODE_PHOENIX: Polarity.BALANCE,
            PetSpecies.WISDOM_OWL: Polarity.LOGIC,
            # Cyberpunk
            PetSpecies.DATA_SPRITE: Polarity.LOGIC,
            PetSpecies.HACK_HOUND: Polarity.ORDER,
            PetSpecies.CIPHER_CAT: Polarity.CREATIVITY,
            # Space Opera
            PetSpecies.VOID_WHALE: Polarity.BALANCE,
            PetSpecies.STAR_FOX: Polarity.CREATIVITY,
            PetSpecies.QUANTUM_QUAIL: Polarity.CHAOS,
        }
        return mapping.get(self.species, Polarity.BALANCE)
    
    def _compute_trait_synergy(self) -> float:
        """
        Compute trait synergy score (adjacency).
        Different trait combinations have different synergy values.
        """
        if not self.traits:
            return 50.0  # Neutral
        
        # Define synergistic trait pairs (high adjacency)
        synergy_pairs = [
            (CompanionTrait.CURIOUS, CompanionTrait.ANALYTICAL),
            (CompanionTrait.PERSISTENT, CompanionTrait.METHODICAL),
            (CompanionTrait.CREATIVE, CompanionTrait.ADVENTUROUS),
            (CompanionTrait.SOCIAL, CompanionTrait.PROTECTIVE),
        ]
        
        trait_set = set(self.traits)
        synergy_count = 0
        
        for trait1, trait2 in synergy_pairs:
            if trait1 in trait_set and trait2 in trait_set:
                synergy_count += 1
        
        # Base adjacency on trait count + synergies
        base_score = len(self.traits) * 10
        synergy_bonus = synergy_count * 15
        return min(100.0, base_score + synergy_bonus)
    
    def validate_hybrid_encoding(self) -> Tuple[bool, str]:
        """
        Validate that STAT7 coordinates correctly encode pet data.
        """
        computed = self._compute_stat7_coordinates()
        stored = self.stat7
        
        if computed.realm != stored.realm:
            return False, f"Realm mismatch: {computed.realm} != {stored.realm}"
        
        if computed.lineage != stored.lineage:
            return False, f"Lineage mismatch: {computed.lineage} != {stored.lineage}"
        
        if abs(computed.adjacency - stored.adjacency) > 1.0:
            return False, f"Adjacency mismatch: {computed.adjacency} != {stored.adjacency}"
        
        if computed.horizon != stored.horizon:
            return False, f"Horizon mismatch: {computed.horizon} != {stored.horizon}"
        
        if abs(computed.luminosity - stored.luminosity) > 5.0:
            return False, f"Luminosity mismatch: {computed.luminosity} != {stored.luminosity}"
        
        if computed.polarity != stored.polarity:
            return False, f"Polarity mismatch: {computed.polarity} != {stored.polarity}"
        
        if computed.dimensionality != stored.dimensionality:
            return False, f"Dimensionality mismatch: {computed.dimensionality} != {stored.dimensionality}"
        
        return True, ""
    
    def to_collectible_card_data(self) -> Dict[str, Any]:
        """
        Convert companion to collectible card display format.
        
        Returns display data for all zoom levels.
        """
        rarity = self._compute_rarity()
        
        return {
            'title': self.companion_name or f"{self.species.value.title()}",
            'subtitle': f"{self.stage.value.title()} • {self.genre_theme.title()}",
            'type': 'Companion',
            'rarity': rarity.value,
            'rarity_stars': self._rarity_to_stars(rarity),
            
            # Artwork (deterministic from STAT7 seed)
            'artwork_url': f"ipfs://sprite-{self.stat7.address}.png",
            'icon_url': f"ipfs://icon-{self.entity_id}.png",
            
            # Key stats for zoom level 2
            'key_stats': {
                'Level': self.stage.value.title(),
                'XP': f"{self.xp}",
                'Luminosity': f"{int(self.stat7.luminosity)}%",
            },
            
            # Full stats for zoom level 3
            'stats': {
                'Health': int(self.health),
                'Happiness': int(self.happiness),
                'Focus': int(self.focus),
                'XP': self.xp,
                'Evolutions': self.evolution_count,
            },
            
            # Traits/abilities
            'traits': [t.value for t in self.traits],
            'abilities': self.special_abilities,
            
            # Lore/flavor text
            'fluff_text': self._generate_lore(),
            
            # STAT7 details
            'stat7_details': {
                'Realm': self.stat7.realm.value,
                'Lineage': f"Gen {self.stat7.lineage}",
                'Horizon': self.stat7.horizon.value,
                'Polarity': self.stat7.polarity.value,
                'Dimensionality': f"L{self.stat7.dimensionality}",
            },
            
            # NFT metadata
            'mint_info': {
                'Serial': self.stat7.address,
                'Minted': self.nft_minted,
                'Contract': self.nft_contract or "Not minted",
                'TokenID': self.nft_token_id or "—",
            },
            
            # Properties for ERC-721
            'properties': {
                'generation': {'type': 'integer', 'description': 'Generation from LUCA'},
                'traits': {'type': 'array', 'description': 'Personality traits'},
                'polarity': {'type': 'string', 'description': 'Elemental affinity'},
            }
        }
    
    def _compute_rarity(self) -> CompanionRarity:
        """Compute rarity tier based on STAT7 properties"""
        # Simple heuristic: based on luminosity + evolution count
        score = self.stat7.luminosity + (self.evolution_count * 10)
        
        if score < 30:
            return CompanionRarity.COMMON
        elif score < 50:
            return CompanionRarity.UNCOMMON
        elif score < 70:
            return CompanionRarity.RARE
        elif score < 85:
            return CompanionRarity.EPIC
        elif score < 100:
            return CompanionRarity.LEGENDARY
        else:
            return CompanionRarity.MYTHIC
    
    def _rarity_to_stars(self, rarity: CompanionRarity) -> str:
        """Convert rarity to star rating"""
        mapping = {
            CompanionRarity.COMMON: "★",
            CompanionRarity.UNCOMMON: "★★",
            CompanionRarity.RARE: "★★★",
            CompanionRarity.EPIC: "★★★★",
            CompanionRarity.LEGENDARY: "★★★★★",
            CompanionRarity.MYTHIC: "★★★★★✨",
        }
        return mapping.get(rarity, "★")
    
    def _generate_lore(self) -> str:
        """Generate flavor text based on companion state"""
        templates = {
            PetSpecies.SCROLLHOUND: f"This loyal {self.species.value.replace('_', ' ')} has documented {self.evolution_count} great chronicles. Its fur glows with the wisdom of {self.xp} compiled thoughts.",
            PetSpecies.CHRONO_CAT: f"A temporal familiar that has witnessed {self.evolution_count} cycles of creation. It measures eternity in the XP of experience: {self.xp}.",
            PetSpecies.DEBUGGER_FERRET: f"This relentless {self.species.value.replace('_', ' ')} has hunted {self.evolution_count} deep bugs. Its code-sense has grown with {self.xp} refinements.",
            PetSpecies.CODE_PHOENIX: f"Reborn {self.evolution_count} times from the ashes of refactoring. This phoenix burns brightest after {self.xp} compilations.",
            PetSpecies.WISDOM_OWL: f"An ancient keeper of {self.evolution_count} revelations. Its vast knowledge spans {self.xp} documented insights.",
        }
        
        return templates.get(
            self.species,
            f"A mysterious {self.species.value.replace('_', ' ')} of remarkable properties. Has undergone {self.evolution_count} transformations and collected {self.xp} experiences."
        )
    
    def _get_realm_details(self) -> Dict[str, Any]:
        """Provide companion-specific realm details for fractal descent"""
        return {
            'species': self.species.value,
            'stage': self.stage.value,
            'traits': [t.value for t in self.traits],
            'stats': {
                'health': self.health,
                'happiness': self.happiness,
                'focus': self.focus,
            },
            'evolution_count': self.evolution_count,
            'genre_theme': self.genre_theme,
        }
    
    # ========================================================================
    # Companion-Specific Operations
    # ========================================================================
    
    def gain_xp(self, amount: int, source: str = "activity"):
        """Award experience points and update coordinates"""
        self.xp += amount
        self.xp_history.append((datetime.utcnow(), amount))
        
        # Recompute STAT7 coordinates with new XP
        self.stat7 = self._compute_stat7_coordinates()
        
        self._record_event("xp_gained", f"Gained {amount} XP from {source}", {'amount': amount, 'source': source, 'total_xp': self.xp})
    
    def add_trait(self, trait: CompanionTrait):
        """Develop a new personality trait"""
        if trait not in self.traits:
            self.traits.append(trait)
            # Update adjacency with new trait synergy
            self.stat7 = self._compute_stat7_coordinates()
            self._record_event("trait_acquired", f"Developed trait: {trait.value}", {'trait': trait.value})
    
    def evolve(self, new_stage: PetStage):
        """Evolve to new stage"""
        old_stage = self.stage
        self.stage = new_stage
        self.evolution_count += 1
        
        # Update horizon-related coordinates
        self.stat7 = self._compute_stat7_coordinates()
        
        self._record_event("evolution", f"Evolved from {old_stage.value} to {new_stage.value}", {
            'old_stage': old_stage.value,
            'new_stage': new_stage.value,
            'evolution_number': self.evolution_count
        })
    
    def teach_ability(self, ability_name: str):
        """Learn a new special ability"""
        if ability_name not in self.special_abilities:
            self.special_abilities.append(ability_name)
            self._record_event("ability_learned", f"Learned ability: {ability_name}", {'ability': ability_name})
    
    def mod_happiness(self, delta: float):
        """Modify happiness level"""
        self.happiness = max(0, min(100, self.happiness + delta))
        self.stat7 = self._compute_stat7_coordinates()
        self._record_event("happiness_changed", f"Happiness adjusted by {delta:+.1f}", {'new_happiness': self.happiness})
    
    def mod_focus(self, delta: float):
        """Modify focus level"""
        self.focus = max(0, min(100, self.focus + delta))
        self.stat7 = self._compute_stat7_coordinates()
        self._record_event("focus_changed", f"Focus adjusted by {delta:+.1f}", {'new_focus': self.focus})
    
    def take_damage(self, amount: float):
        """Damage companion"""
        self.health = max(0, self.health - amount)
        self._record_event("damage_taken", f"Took {amount} damage", {'damage': amount, 'health_remaining': self.health})
        if self.health == 0:
            self._record_event("fainted", "Companion fainted")
    
    def heal(self, amount: float):
        """Heal companion"""
        self.health = min(100, self.health + amount)
        self._record_event("healed", f"Healed {amount} HP", {'health_restored': amount, 'health_total': self.health})


if __name__ == "__main__":
    # Example usage
    companion = CompanionSTAT7Entity(
        species=PetSpecies.SCROLLHOUND,
        companion_name="Archie",
        owner_id="user_123",
        genre_theme="fantasy"
    )
    
    companion.gain_xp(250, "documentation")
    companion.add_trait(CompanionTrait.CURIOUS)
    companion.add_trait(CompanionTrait.ANALYTICAL)
    
    print(f"Companion: {companion.companion_name}")
    print(f"XP: {companion.xp}")
    print(f"STAT7 Address: {companion.stat7.address}")
    print(f"Rarity: {companion._compute_rarity().value}")
    print(f"Valid encoding: {companion.validate_hybrid_encoding()}")
    
    card = companion.to_collectible_card_data()
    print(f"Card Title: {card['title']}")
    print(f"Card Traits: {card['traits']}")