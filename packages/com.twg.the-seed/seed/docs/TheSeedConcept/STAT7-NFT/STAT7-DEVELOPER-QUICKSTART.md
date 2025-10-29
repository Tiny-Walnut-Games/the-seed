# STAT7 Entity System - Developer Quick Start

## Installation

```python
from seed.engine.stat7_companion import CompanionSTAT7Entity, PetSpecies, PetStage, CompanionTrait
from seed.engine.stat7_badge import BadgeSTAT7Entity, BadgeCategory, SponsorTier
from seed.engine.stat7_entity import STAT7Coordinates, Realm, Horizon, Polarity, LifecycleEvent
```

---

## Creating Companions

### Basic Creation
```python
companion = CompanionSTAT7Entity(
    species=PetSpecies.SCROLLHOUND,
    companion_name="Archie",
    owner_id="user_123",
    genre_theme="fantasy"
)
```

### With Legacy Data
```python
# Migrating from old system
companion = CompanionSTAT7Entity(
    species=PetSpecies.SCROLLHOUND,
    companion_name="Archie",
    owner_id="user_123",
    xp=1500,  # From old system
    stage=PetStage.ADULT,
    traits=[CompanionTrait.CURIOUS, CompanionTrait.ANALYTICAL],
    migration_source="legacy_pet_system"
)
```

### Progression
```python
# Gain XP
companion.gain_xp(100, source="documentation")

# Develop traits
companion.add_trait(CompanionTrait.PERSISTENT)

# Evolve to next stage
companion.evolve(PetStage.JUVENILE)

# Learn abilities
companion.teach_ability("Fast Learning")

# Modify stats
companion.mod_happiness(+10)
companion.mod_focus(-5)
companion.take_damage(5)
companion.heal(20)
```

### Checking Status
```python
# Get STAT7 address
print(companion.stat7.address)  # STAT7-C-002-55-P-75-C-1

# Get rarity
rarity = companion._compute_rarity()
print(rarity.value)  # "epic"

# Get lifecycle events
events = companion.get_event_history(limit=5)
for event in events:
    print(f"{event.timestamp}: {event.event_type} - {event.description}")

# Validate encoding
is_valid, error = companion.validate_hybrid_encoding()
print(f"Valid: {is_valid}, Error: {error or 'None'}")
```

### Card Rendering
```python
# Get collectible card data
card = companion.to_collectible_card_data()
print(card['title'])
print(card['stat7_details'])
print(card['traits'])

# Render at zoom level (1-7)
level_3_card = companion.render_zoom_level(3)  # Full card
level_5_profile = companion.render_zoom_level(5)  # Full profile
```

### Entanglement
```python
# Link to another entity
companion.add_entanglement("badge_123", strength=0.8)

# Get entangled entities
entanglements = companion.get_entanglements()
# Returns: [("badge_123", 0.8), ("companion_456", 0.5)]

# Update entanglement strength
companion.update_entanglement_strength("badge_123", 0.9)

# Remove entanglement
companion.remove_entanglement("badge_123")
```

### NFT Minting
```python
# Check if ready
if companion.opt_in_stat7_nft:
    # Prepare metadata
    metadata = companion.prepare_for_minting()
    print(metadata['name'])
    print(metadata['attributes'])
    
    # After blockchain minting
    companion.record_mint(
        contract_address="0x1234...abcd",
        token_id=42,
        ipfs_hash="QmXyz123..."
    )
    
    print(companion.nft_token_id)  # 42
```

### Persistence
```python
from pathlib import Path

# Save to JSON
companion.save_to_file(Path("companions/archie.json"))

# Load from JSON (manual process)
import json
with open("companions/archie.json") as f:
    data = json.load(f)
    # Use factory pattern to instantiate correct type
```

---

## Creating Badges

### Achievement Badge
```python
badge = BadgeSTAT7Entity(
    badge_type="first_contribution",
    category=BadgeCategory.CONTRIBUTION,
    owner_id="user_123",
    description="Congratulations on your first contribution!",
    unlock_criteria="Make at least 1 contribution",
    total_earners=127
)

# Repeat earn
badge.increment_earn_count()  # Now earn_count = 2

# Link related badges
badge.add_related_badge("badge_456")

# Lifecycle
badge.archive()  # Move to history
badge.crystallize()  # Permanent record
```

### Sponsor Ring (Preferred Method)
```python
ring = BadgeSTAT7Entity.create_sponsor_ring(
    owner_id="sponsor_jane_001",
    years_supported=3,
    tier=SponsorTier.RING_3,
    benefits=[
        "early_access_48h",
        "extra_pet_slots_2",
        "founder_badge"
    ]
)

# Sponsor ring properties
print(ring.sponsor_years)  # 3
print(ring.sponsor_tier)   # SponsorTier.RING_3
print(ring.stat7.luminosity)  # 100.0 (always)
print(ring.stat7.polarity)    # Polarity.UNITY
print(ring.stat7.realm)       # Realm.SPONSOR_RING
```

### Sponsor Ring Upgrade
```python
# After supporter has been with us for 4 years
ring.sponsor_years = 4
ring.sponsor_tier = SponsorTier.RING_4
ring.sponsor_benefits = [
    "early_access_48h",
    "extra_pet_slots_2",
    "founder_badge",
    "voting_rights"  # New benefit
]
ring.stat7 = ring._compute_stat7_coordinates()  # Update coords
ring._record_event("tier_upgraded", "Sponsor tier upgraded to RING_4")
```

---

## STAT7 Coordinate System

### Understanding Dimensions

```python
coord = companion.stat7

# 1. Realm: Domain classification
coord.realm  # Realm.COMPANION

# 2. Lineage: Generation from LUCA
coord.lineage  # 2 (Gen 2)

# 3. Adjacency: Semantic proximity (0-100)
coord.adjacency  # 55.0

# 4. Horizon: Lifecycle stage
coord.horizon  # Horizon.PEAK

# 5. Luminosity: Activity level (0-100)
coord.luminosity  # 75.0

# 6. Polarity: Resonance/affinity
coord.polarity  # Polarity.LOGIC

# 7. Dimensionality: Fractal depth
coord.dimensionality  # 1

# Full address
print(coord.address)  # STAT7-C-002-55-P-75-L-1

# Parse address back
parsed = STAT7Coordinates.from_address("STAT7-C-002-55-P-75-L-1")
```

### Mapping Examples

#### Companion XP → Lineage
```
0-500 XP     → Lineage 0
500-1500 XP  → Lineage 1
1500-5000    → Lineage 2
5000-15000   → Lineage 3
15000-30000  → Lineage 4
30000+       → Lineage 5+
```

#### Pet Stage → Horizon
```
EGG          → GENESIS
HATCHLING    → EMERGENCE
JUVENILE     → PEAK
ADULT        → PEAK
ELDER        → DECAY
LEGENDARY    → CRYSTALLIZATION
```

#### Species → Polarity
```
SCROLLHOUND  → LOGIC
CHRONO_CAT   → ORDER
DEBUGGER_FERRET → CREATIVITY
CODE_PHOENIX → BALANCE
WISDOM_OWL   → LOGIC
STAR_FOX     → CREATIVITY
QUANTUM_QUAIL → CHAOS
```

---

## Zoom Levels Reference

```python
# Level 1: Badge icon
data = companion.render_zoom_level(1)
# {zoom_level: 1, type: "badge", icon: "...", rarity: "epic"}

# Level 2: Dog-tag micro-card
data = companion.render_zoom_level(2)
# {zoom_level: 2, type: "dog_tag", icon: "...", title: "Archie", stats: {...}}

# Level 3: Collectible card
data = companion.render_zoom_level(3)
# {zoom_level: 3, type: "collectible_card", artwork_url: "...", stats: {...}, ...}

# Level 4: Profile panel
data = companion.render_zoom_level(4)
# {zoom_level: 4, type: "profile_panel", owner: "user_123", entangled_count: 3, ...}

# Level 5: Full entity page
data = companion.render_zoom_level(5)
# {zoom_level: 5, type: "entity_profile", lifecycle_events: [...], entanglements: [...], ...}

# Level 6+: Fractal descent
data = companion.render_zoom_level(6)
# {zoom_level: 6, type: "fractal_descent", stat7_dimensions: {...}, realm_details: {...}, ...}
```

---

## Common Patterns

### Migrating Existing Pet
```python
def migrate_legacy_pet(legacy_pet_data):
    """Convert old pet to STAT7Entity"""
    companion = CompanionSTAT7Entity(
        species=PetSpecies(legacy_pet_data['species']),
        companion_name=legacy_pet_data['name'],
        owner_id=legacy_pet_data['owner_id'],
        xp=legacy_pet_data['xp'],
        stage=PetStage(legacy_pet_data['stage']),
        traits=[CompanionTrait(t) for t in legacy_pet_data.get('traits', [])],
        health=legacy_pet_data.get('health', 100),
        happiness=legacy_pet_data.get('happiness', 100),
        focus=legacy_pet_data.get('focus', 50),
        legacy_data=legacy_pet_data,
        migration_source="legacy_pet_system"
    )
    
    # Validate
    is_valid, error = companion.validate_hybrid_encoding()
    if not is_valid:
        raise ValueError(f"Migration validation failed: {error}")
    
    return companion
```

### Batch Operations
```python
companions = [
    CompanionSTAT7Entity(species=PetSpecies.SCROLLHOUND, owner_id="user_1"),
    CompanionSTAT7Entity(species=PetSpecies.CHRONO_CAT, owner_id="user_2"),
    CompanionSTAT7Entity(species=PetSpecies.DEBUGGER_FERRET, owner_id="user_3"),
]

# Process all
for companion in companions:
    companion.gain_xp(100)
    is_valid, _ = companion.validate_hybrid_encoding()
    assert is_valid
    
    # Export
    card = companion.to_collectible_card_data()
    print(f"{companion.companion_name}: {card['rarity']}")
```

### Finding Entangled Entities
```python
def get_entanglement_network(entity, visited=None):
    """Recursively trace entanglement network"""
    if visited is None:
        visited = set()
    
    if entity.entity_id in visited:
        return visited
    
    visited.add(entity.entity_id)
    
    for entangled_id, strength in entity.get_entanglements():
        print(f"  → {entangled_id} (strength: {strength})")
        # In real system, would load that entity and recurse
    
    return visited
```

### NFT Metadata Generation
```python
def prepare_nft_collection(companions):
    """Generate NFT metadata for batch minting"""
    metadatas = []
    
    for companion in companions:
        if not companion.opt_in_stat7_nft:
            continue  # Skip opted-out entities
        
        metadata = companion.prepare_for_minting()
        metadatas.append({
            'entity_id': companion.entity_id,
            'metadata': metadata,
            'stat7_address': companion.stat7.address,
            'rarity': companion._compute_rarity().value
        })
    
    return metadatas
```

---

## Event Tracking

### All Events Are Recorded
```python
companion.gain_xp(100)
companion.add_trait(CompanionTrait.CURIOUS)
companion.evolve(PetStage.JUVENILE)
companion.take_damage(10)
companion.heal(15)

# Get full history
for event in companion.get_event_history():
    print(f"{event.timestamp.isoformat()}: {event.event_type}")
    print(f"  Description: {event.description}")
    print(f"  Metadata: {event.metadata}")
```

### Lifecycle Events
```
EVENT TYPE              TRIGGERED BY
──────────────────────────────────────
genesis                 Entity initialization
xp_gained               gain_xp()
trait_acquired          add_trait()
evolution               evolve()
ability_learned         teach_ability()
happiness_changed       mod_happiness()
focus_changed           mod_focus()
damage_taken            take_damage()
healed                  heal()
entanglement_added      add_entanglement()
entanglement_removed    remove_entanglement()
entanglement_updated    update_entanglement_strength()
nft_minted              record_mint()
badge_earned            (for badges)
re_earned               increment_earn_count()
related_badge_added     add_related_badge()
badge_archived          archive()
badge_crystallized      crystallize()
```

---

## Error Handling

```python
try:
    companion.evolve(PetStage.LEGENDARY)
except ValueError as e:
    print(f"Evolution failed: {e}")

try:
    companion.take_damage(1000)  # Overkill
except Exception as e:
    print(f"Damage failed: {e}")

try:
    metadata = companion.prepare_for_minting()
except ValueError as e:
    print(f"Not opted in: {e}")

# Validation
is_valid, error = companion.validate_hybrid_encoding()
if not is_valid:
    print(f"Encoding validation failed: {error}")
```

---

## Best Practices

### 1. Always Validate After Migration
```python
companion = migrate_legacy_pet(old_data)
assert companion.validate_hybrid_encoding()[0], "Migration corrupted data!"
```

### 2. Opt-In Is Explicit
```python
# Don't assume users want NFTs
if not companion.opt_in_stat7_nft:
    # Can still use in games, just not on-chain
    pass
```

### 3. Preserve Legacy Data
```python
# Keep original data for audit trail
companion.legacy_data = {
    'original_species': old_pet.species,
    'original_xp': old_pet.xp,
    'migration_timestamp': datetime.utcnow().isoformat()
}
```

### 4. Track Events Consistently
```python
# Always use _record_event for custom actions
companion._record_event(
    "custom_event",
    "Something happened",
    metadata={'important': 'data'}
)
```

### 5. Use Factory Methods for Special Entities
```python
# Prefer factory method for sponsor rings
ring = BadgeSTAT7Entity.create_sponsor_ring(...)
# Rather than manually setting fields
```

---

## Testing Example

```python
def test_companion_stat7_encoding():
    """Verify hybrid encoding works correctly"""
    companion = CompanionSTAT7Entity(
        species=PetSpecies.SCROLLHOUND,
        xp=1200,
        stage=PetStage.JUVENILE,
        traits=[CompanionTrait.CURIOUS, CompanionTrait.ANALYTICAL]
    )
    
    # Should be valid
    is_valid, error = companion.validate_hybrid_encoding()
    assert is_valid, f"Encoding failed: {error}"
    
    # STAT7 should be computed
    assert companion.stat7.realm == Realm.COMPANION
    assert companion.stat7.lineage == 2  # 1200 XP = Gen 2
    assert companion.stat7.horizon == Horizon.PEAK
    assert companion.stat7.polarity == Polarity.LOGIC
    
    # Should generate valid card data
    card = companion.to_collectible_card_data()
    assert card['rarity'] in ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic']
    assert card['stat7_details']['Realm'] == 'companion'
    
    print("✅ All tests passed")

if __name__ == "__main__":
    test_companion_stat7_encoding()
```

---

## Troubleshooting

### "Invalid STAT7 address format"
```python
# Wrong format
parsed = STAT7Coordinates.from_address("STAT7-C-2-55-P-75-C-1")  # ❌ Should be 3-digit

# Correct format
parsed = STAT7Coordinates.from_address("STAT7-C-002-55-P-75-L-1")  # ✅
```

### "Encoding validation failed"
```python
# Might happen if you manually modify stat7
companion.stat7.luminosity = 150  # ❌ Out of range

# Recompute instead
companion.stat7 = companion._compute_stat7_coordinates()  # ✅
```

### "Entity not opted in"
```python
# Check opt-in status before minting
if not companion.opt_in_stat7_nft:
    companion.opt_in_stat7_nft = True  # Explicitly opt-in

metadata = companion.prepare_for_minting()  # Now works
```

---

## API Reference Summary

### CompanionSTAT7Entity Methods
- `gain_xp(amount, source)` - Award experience
- `add_trait(trait)` - Develop personality
- `evolve(new_stage)` - Progress lifecycle
- `teach_ability(ability_name)` - Learn move
- `mod_happiness/focus(delta)` - Adjust stats
- `take_damage(amount)` - Reduce health
- `heal(amount)` - Restore health
- `to_collectible_card_data()` - Card rendering
- `validate_hybrid_encoding()` - Verify STAT7
- `render_zoom_level(level)` - Display at zoom

### BadgeSTAT7Entity Methods
- `increment_earn_count()` - Re-earn badge
- `add_related_badge(badge_id)` - Link badges
- `archive()` - Move to history
- `crystallize()` - Permanent achievement
- `create_sponsor_ring()` - Factory method
- [All inherited from STAT7Entity]

### STAT7Entity Base Methods (All Entities)
- `add_entanglement(entity_id, strength)` - Create link
- `remove_entanglement(entity_id)` - Delete link
- `update_entanglement_strength(entity_id, strength)` - Modify link
- `get_entanglements()` - List links
- `get_event_history(limit)` - Chronology
- `get_luca_trace()` - Bootstrap path
- `prepare_for_minting()` - ERC-721 metadata
- `record_mint(contract, token_id, ipfs)` - Record minting
- `to_dict()` - Serialize to JSON
- `save_to_file(path)` - Persist

---

**Last Updated**: 2025-01-[current]  
**Version**: 1.0.0  
**Status**: Ready for development