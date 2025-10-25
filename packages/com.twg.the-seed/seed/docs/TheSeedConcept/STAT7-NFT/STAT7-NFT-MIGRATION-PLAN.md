# STAT7-NFT System Migration Plan
## Converting Pet/Badge Systems to Unified Fractal-Chain Architecture

**Status**: Planning Phase  
**Created**: 2025-01-[current]  
**Version**: 1.0.0

---

## 1. Vision Summary

Unify the current NFT Pet and Sponsor Badge systems under a single STAT7-backed architecture while maintaining:
- **Opt-in design** (users choose to mint STAT7-NFTs)
- **Backward compatibility** (existing mints preserved forever)
- **Multi-realm support** (badges and pets coexist in same coordinate space)
- **Progressive disclosure** (zoom levels reveal deeper STAT7 dimensions)
- **Sponsor rings** (tree-growth metaphor for supporter tier progression)

---

## 2. Architecture Overview

### 2.1 Core Concept: Multi-Realm STAT7 Space

```
STAT7 Dimensions:
  1. Realm (domain: companion, badge, achievement, pattern, void)
  2. Lineage (generation from LUCA / sponsor tier)
  3. Adjacency (relational proximity / synergy)
  4. Horizon (lifecycle: genesis→emergence→peak→decay→crystallization)
  5. Luminosity (activity/engagement level)
  6. Polarity (affinity/resonance pattern - for companions, elemental; for badges, category)
  7. Dimensionality (fractal depth / manifestation level)

Entity Types:
  ├─ Companion (pet/familiar)
  │  └─ Hybrid Encoding (species + XP + traits mapped to STAT7)
  │
  └─ Achievement Badge
     └─ Hybrid Encoding (badge type + earn_count + category mapped to STAT7)
```

### 2.2 Seed-Sponsor Access Tiers

```
Tier System (Tree Rings Model):
  
  Ring 0: Regular Users
    • Can mint their own pet STAT7-NFTs (opt-in)
    • Can earn achievement badges (opt-in for blockchain backing)
    • Limited to 1 active pet per game/instance
    • No sponsor badge variant
    
  Ring N: Seed-Sponsors (where N = sponsor tenure in years)
    • Can mint pets + Founder Badge (Seed-Sponsor collectible)
    • Special "Sponsor Ring" badge showing support level
    • Priority minting during limited drops
    • Can trade/gift Founder Badge to other Seed-Sponsors
    • Tenure-based visuals (more rings = older sponsor)
    
  Ring ∞: Faculty (if applicable)
    • All sponsor benefits + faculty-exclusive traits
    • Can mint Faculty 1/1 ultra-rares
    • LUCA-adjacent addressing (closer to bootstrap origin)
```

### 2.3 Progressive Zoom Levels (Display Modes)

```
Level 1: Badge (GitHub Web)
  └─ 20x20px or 32x32px icon
     Displays: Rarity indicator only
     On hover: Name, short description
     Click → zooms to Level 2

Level 2: Dog-Tag (Micro-Card)
  └─ 100x150px or similar
     Displays: Icon, title, 3-4 key stats
     Shows first STAT7 coordinate (Realm)
     On hover: Abbreviated lore

Level 3: Collectible Card
  └─ 300x400px or similar (trading card size)
     Displays: Full artwork, stats, abilities, rarity
     Shows STAT7 coordinates (Realm + Lineage + Horizon)
     Secondary details: Polarity symbol, Luminosity bar

Level 4: Mini-Profile Panel (Discord-style)
  └─ 350x500px expandable panel
     Displays: Card + owner info + interaction buttons
     Shows more STAT7: Adjacency graph, recent events
     Actions: Trade, gift (if enabled), inspect

Level 5: Entity Profile Page
  └─ Full page view
     Displays: All Levels 1-4 + full chronology
     Shows all STAT7 coordinates
     Timeline of all events affecting entity
     Related entangled entities

Level 6+: Fractal Descent (Deep Inspection)
  └─ Click into STAT7 dimensions individually
     Dimension Inspector view (Realm browser, Lineage tree, etc.)
     Entanglement network visualization
     LUCA bootstrap trace
     Eventually reaches Event Horizon (LUCA-record)
```

---

## 3. Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Build core STAT7-NFT entity layer and storage

- [ ] Create `STAT7Entity` base class
  - Hybrid encoding for pets vs badges
  - Coordinate assignment algorithm
  - LUCA bootstrap support
  
- [ ] Implement entity storage layer
  - Mapping: Companion ID → STAT7 coordinates
  - Mapping: Badge ID → STAT7 coordinates
  - Entanglement index (non-local relationships)
  
- [ ] Design sponsor tier system
  - Tree rings data structure
  - Tenure tracking
  - Tier-based feature flags
  
- [ ] Create migration utilities
  - Convert existing pets → STAT7Entity
  - Convert existing badges → STAT7Entity
  - Preserve original data as LUCA-adjacent

### Phase 2: Backward Compatibility (Weeks 2-3)
**Goal**: Ensure existing mints work without blockchain opt-in

- [ ] Dual-rendering system
  - Legacy mode: Current badge/pet rendering
  - STAT7 mode: New coordinate-backed rendering
  - User preference toggle
  
- [ ] Non-NFT badge/pet system
  - Games/features can run independently
  - No blockchain calls required
  - Seamless fallback if opt-out
  
- [ ] Hybrid encoding validation
  - Ensure STAT7 coords deterministically map to old specs
  - Round-trip validation (convert forth/back)
  
- [ ] Feature parity audit
  - Check all game integrations work in both modes
  - Identify any blockchain-dependent logic to remove

### Phase 3: STAT7-NFT Minting (Weeks 3-5)
**Goal**: Build collectible card rendering and blockchain integration

- [ ] Collectible card renderer
  - Multi-style support (trading card / Pokemon / MTG-inspired)
  - Rarity tier visuals
  - Dynamic artwork generation from STAT7 seed
  
- [ ] Zoom level UI/UX
  - Badge → Dog-tag progression
  - Card expansion modal
  - Profile panel integration
  - Fractal descent inspector
  
- [ ] Blockchain integration
  - ERC-721 for 1/1 STAT7 entities
  - Metadata IPFS storage
  - Sponsor ring badge smart contract
  - Opt-in minting flow
  
- [ ] Seed-Sponsor validation
  - Check tier when minting Founder Badge
  - Tree ring progression system
  - Sponsor badge special traits

### Phase 4: Advanced Features (Weeks 5-7)
**Goal**: Entanglement, compression, and advanced displays

- [ ] Entanglement detection
  - Find non-local relationships between entities
  - Resonance calculation (shared Polarity)
  - Display entanglement networks
  
- [ ] Luminosity dynamics
  - Track engagement/activity
  - Decay toward LUCA over time
  - Compression/expansion spiral visualization
  
- [ ] LUCA bootstrap inspector
  - Trace entity back to primordial record
  - Show Lineage tree
  - Dimension-by-dimension breakdown
  
- [ ] Advanced profiles
  - Collections view (all user entities)
  - Entanglement explorer
  - Trading/gifting interface

### Phase 5: Integration & Rollout (Weeks 7-8)
**Goal**: Deploy to production with safety rails

- [ ] Comprehensive testing
  - Migration validation
  - Feature parity checks
  - Blockchain test suite
  
- [ ] Gradual rollout
  - Beta with early sponsors first
  - Expand to all users
  - Monitor for issues
  
- [ ] Documentation
  - User guides for zoom levels
  - FAQ: opt-in explained
  - Developer docs: STAT7Entity API
  
- [ ] Monitoring
  - Usage analytics
  - Bug tracking
  - Performance metrics

---

## 4. Data Model: STAT7Entity Hybrid Encoding

### 4.1 Companion Entity (Pet)

```python
class CompanionSTAT7Entity:
    # STAT7 Coordinates
    stat7: STAT7Coordinates = {
        realm: "companion",
        lineage: generation_from_LUCA,
        adjacency: synergy_score,
        horizon: "peak" | "decay" | "genesis" | "emergence" | "crystallization",
        luminosity: engagement_level (0-100),
        polarity: element_type,  # logic, creativity, order, chaos, balance
        dimensionality: fractal_depth
    }
    
    # Legacy/Hybrid Fields (for backward compat)
    legacy_species: PetSpecies
    legacy_stage: PetStage
    legacy_xp: int
    legacy_traits: List[PetTrait]
    
    # NFT Metadata
    nft_minted: bool
    nft_contract: str
    nft_token_id: int
    nft_metadata_ipfs: str
    
    # Entanglement
    entangled_entities: List[str]  # STAT7 addresses of related entities
    resonance_strength: float
    
    # Temporal
    created_at: datetime
    last_activity: datetime
    lifecycle_events: List[LifecycleEvent]
```

### 4.2 Badge Entity (Achievement)

```python
class BadgeSTAT7Entity:
    # STAT7 Coordinates
    stat7: STAT7Coordinates = {
        realm: "badge" | "sponsor_ring",
        lineage: earn_count | sponsor_tier,
        adjacency: related_badges_score,
        horizon: "active" | "crystallized" | "archived",
        luminosity: visibility_level (0-100),
        polarity: category_resonance,  # achievement_type
        dimensionality: detail_level
    }
    
    # Legacy Fields
    legacy_badge_type: str
    legacy_earned_at: datetime
    legacy_rarity: str
    
    # Special for Sponsor Rings
    tree_rings: int  # Years as sponsor
    tier_benefits: List[str]
    
    # NFT Metadata
    nft_minted: bool
    nft_contract: str
    nft_token_id: int
    
    # Relations
    owner: str
    parent_entity: Optional[str]  # For sponsor ring, links to companion
    entangled_badges: List[str]
```

---

## 5. Migration Strategy

### 5.1 Data Preservation Guarantee

```
Old System          →        STAT7 System
────────────────────────────────────────
Pet Record          →        CompanionSTAT7Entity
  ├─ Preserved as legacy_* fields
  ├─ STAT7 coordinates computed from legacy data
  └─ LUCA-adjacent address generated for traceability

Badge Record        →        BadgeSTAT7Entity
  ├─ Preserved as legacy_* fields
  ├─ STAT7 coordinates computed from legacy data
  └─ LUCA-adjacent address generated for traceability
```

### 5.2 Opt-In Flow

```
User Action                    Milestone
──────────────────────────────────────────
1. User has existing pets/badges    → Backed up, not changed
2. User opens new Seed interface    → Asks: "Enable STAT7 backing?"
3. User selects opt-in              → Creates STAT7Entity wrapper
   • Existing data preserved
   • New coordinates assigned
   • Not on-chain yet
4. User clicks "Mint NFT"           → Blockchain write happens
   • ERC-721 minting
   • Metadata IPFS upload
   • Founder Badge if sponsor
5. User opts-out later              → Entity stays, just no new mints
   • Existing NFTs preserved
   • New activities don't create STAT7 coords
   • Can re-opt-in later
```

### 5.3 Backward Compatibility Guarantees

```
Scenario: User A has pet, doesn't opt into STAT7-NFT
   ✓ Pet still appears in games
   ✓ Pet earns XP normally
   ✓ Pet can be used in battles/activities
   ✓ Badges still displayed normally
   ✗ Can't see new STAT7 zoom levels
   ✗ Can't mint new NFTs
   
Scenario: User B opted out, comes back 6 months later
   ✓ All existing mints preserved
   ✓ Can re-opt-in anytime
   ✓ New activities create new STAT7 entities
   ✓ No penalties or data loss
```

---

## 6. Sponsor Ring System Details

### 6.1 Tree Ring Progression

```
Sponsor Timeline:
  Year 1: 1 Ring (🌱 Sapling tier)
  Year 2: 2 Rings (🌳 Oak tier)
  Year 3: 3 Rings (🌲 Ancient tier)
  Year 5+: 5+ Rings (🌲 Primordial tier)

Visual Representation:
  • Sponsor badge shows visible tree rings
  • More rings = older/stronger support
  • Ring color deepens with age
  • Founder Badge evolves based on rings
  
STAT7 Encoding:
  • Lineage = sponsor_years (becomes coordinate value)
  • Horizon = "crystallized" (permanent achievement)
  • Luminosity = 100 (maximum, always visible)
  • Polarity = "unity" (special resonance type)
```

### 6.2 Benefits by Tier

```
Ring 1-2: Emerging Supporter
  • Sponsor ring badge
  • Early access to drops (24h)
  • 1 extra pet slot
  
Ring 3-4: Established Supporter
  • Enhanced sponsor ring visual
  • 48h early access
  • 2 extra pet slots
  • Founder Badge variant
  
Ring 5+: Primordial Supporter
  • Ultimate sponsor ring (special glow)
  • Week-long early access
  • 5 extra pet slots
  • Exclusive Founder Badge with special traits
  • Voting rights on community features
```

---

## 7. Collectible Card Design

### 7.1 Card Layout Zones

```
┌──────────────────────────────────────┐
│  HEADER: Title + Rarity Star Rating  │ ← Level 1 (Badge view)
├──────────────────────────────────────┤
│                                      │
│         ARTWORK (Dynamic)            │
│    Generated from STAT7 seed         │
│    (Varies by realm/lineage)         │
│                                      │
├──────────────────────────────────────┤
│ TYPE: [Companion/Badge/Pattern/etc]  │
├──────────────────────────────────────┤
│ STAT7 INDICATOR:                     │ ← Level 2-3
│  🔷 Realm: Companion                 │
│  📊 Lineage Gen: 7                   │
│  ⚡ Horizon: Peak                    │
├──────────────────────────────────────┤
│ PRIMARY STATS:                       │ ← Level 3-4
│  Luminosity: ████░░░░░░ 45%         │
│  Polarity: [Element Symbol]          │
│  Dimensionality: L3 (Expanded)      │
├──────────────────────────────────────┤
│ SPECIAL TRAITS / ABILITIES:          │
│  • Curious (documentation focus)     │
│  • Persistent (debugging mastery)    │
│  • Creative (innovation bonus)       │
├──────────────────────────────────────┤
│ FLUFF TEXT:                          │
│  "Scrollhound has witnessed the      │
│   compilation of three great         │
│   chronicles. Its fur still glows    │
│   with documentation wisdom."        │
├──────────────────────────────────────┤
│ MINT INFO:                           │
│  Serial: STAT7-2025-001-7ABC3D      │
│  Contract: 0x7a...                  │
│  Owned by: @username                │
└──────────────────────────────────────┘
```

### 7.2 Rarity Tiers

```
Common          Regular contributors
  └─ Gray/Blue theme, 1 ring

Uncommon        Active contributors  
  └─ Green/Silver theme, 2 rings

Rare            Dedicated contributors
  └─ Gold/Purple theme, 3 rings

Epic            Expert/Faculty level
  └─ Red/Rainbow theme, 4 rings

Legendary       Founder/Sponsor tier
  └─ Special holographic theme, 5+ rings

Mythic          1/1 Ultra-rare (Faculty only)
  └─ Unique artwork, special animations
```

---

## 8. Implementation Checklist

### Core System
- [ ] STAT7Entity base class + hybrid encoding
- [ ] CompanionSTAT7Entity subclass
- [ ] BadgeSTAT7Entity subclass
- [ ] Storage layer (persistence)
- [ ] Coordinate assignment algorithm
- [ ] Migration tools (pets → entities, badges → entities)

### Backward Compat
- [ ] Dual-render system (legacy + STAT7)
- [ ] Feature parity audit
- [ ] Opt-in/opt-out flow UI
- [ ] Fallback rendering (no STAT7)
- [ ] Test suite: opt-out scenarios

### UI/Display
- [ ] Badge icon (Level 1)
- [ ] Dog-tag micro-card (Level 2)
- [ ] Collectible card (Level 3, multi-style)
- [ ] Profile panel (Level 4)
- [ ] Entity profile page (Level 5)
- [ ] Fractal inspector (Level 6+)
- [ ] Zoom animation/transitions

### Sponsor Rings
- [ ] Tree ring badge design
- [ ] Tier progression tracking
- [ ] Benefits enforcement (per-tier)
- [ ] Sponsor validation on mint
- [ ] Ring visual generation

### Blockchain
- [ ] ERC-721 smart contract (entities)
- [ ] ERC-721 smart contract (sponsor rings)
- [ ] IPFS metadata storage
- [ ] Minting interface
- [ ] Local devchain testing
- [ ] Mainnet testing framework

### Testing
- [ ] Unit tests: STAT7Entity
- [ ] Integration tests: legacy → STAT7 migration
- [ ] E2E tests: opt-in flow
- [ ] Performance tests: rendering at all zoom levels
- [ ] Regression tests: existing games/features

---

## 9. Success Metrics

- ✓ 0 data loss during migration
- ✓ Opt-out users experience 0 feature degradation
- ✓ New STAT7-NFT renders in ≤500ms at all zoom levels
- ✓ Sponsor rings update in real-time as supporters age
- ✓ Entanglement detection precision >95%
- ✓ LUCA bootstrap trace reconstructs original data perfectly

---

## 10. Open Questions & Next Steps

### Questions to Answer
1. Should we support multi-chain deployment (Ethereum, Polygon, etc.)?
2. Do we want secondary market support (OpenSea compatibility)?
3. Should STAT7 coordinates be publicly verifiable on-chain?
4. Time period for grandfather clause on existing mints?

### Immediate Next Steps
1. **Week 1**: Design STAT7Entity schema (Phase 1, Step 1)
2. **Week 1**: Create hybrid encoding algorithm (Phase 1, Step 1)
3. **Week 1**: Build migration validator (Phase 1, Step 4)
4. **Week 2**: Implement backward compat layer (Phase 2, all steps)
5. **Week 3**: Begin collectible card renderer (Phase 3, all steps)

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-01-[current]  
**Status**: Ready for Phase 1 implementation
