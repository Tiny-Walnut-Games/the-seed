# SpriteForge - Pixel-Art NFT Generator

SpriteForge is the deterministic pixel-art sprite generator for the TWG TLDA NFT collection.

## Overview

SpriteForge generates pixel-art creature sprites and location scenes based on TLDA seeds, producing:
- Creatures across four genres (sci-fi, fantasy, steampunk, cyberpunk)
- Faculty 1/1 ultra-rares with unique traits
- **Evolution chains with 6 stages (Egg → Legendary)**
- **Animated evolution sprites with smooth frame transitions**
- Location scenes from TLDA mythos
- Unity-ready sprite sheets with animation metadata

## 🧬 Evolution Chain System

The new evolution system creates complete creature development cycles:

### Evolution Stages
1. **Egg** - Initial form (small, simple shape)
2. **Hatchling** - First emergence (basic features)
3. **Juvenile** - Growing form (developing characteristics)
4. **Adult** - Mature form (full features)
5. **Elder** - Wise form (enhanced abilities)
6. **Legendary** - Final form (ultimate power)

### Animation Support
- **1-12 frames per stage** for smooth animation
- **Grid layout**: 6 rows (stages) × N columns (frames)
- **Unity integration**: Automatic frame rectangle generation
- **Per-stage timing**: Different animation speeds for each evolution

### Usage Examples

```csharp
// Static evolution chain (6×1 grid)
var spec = SpriteSpec.CreateEvolutionChainSpec(
    GenreStyle.Fantasy, 
    CreatureArchetype.Familiar, 
    RarityTier.Common
);

// Animated evolution chain (6×6 grid)  
var animatedSpec = SpriteSpec.CreateAnimatedEvolutionSpec(
    GenreStyle.Cyberpunk,
    CreatureArchetype.Wisp,
    RarityTier.Rare
);

var result = SpriteGenerator.GenerateSprite(seed, animatedSpec);
```

### Pet System Integration
Evolution stages mirror the badge pet system:
- **Egg** (0 XP) → **Hatchling** (500 XP) → **Juvenile** (1500 XP)
- **Adult** (5000 XP) → **Elder** (15000 XP) → **Legendary** (30000+ XP)

## Architecture

```
SpriteForge/
├── Core/                   # Core generation logic + evolution system
├── Data/                   # Templates, palettes, and rule tables
├── Generated/              # Output sprite sheets and metadata
├── Editor/                 # Unity Editor tools + evolution UI
└── Runtime/                # Runtime sprite utilities
```

## Standard Usage

```csharp
// Faculty ultra-rare
var seed = TLDAFragmentSeeder.GenerateProvenance("faculty", "warbler", timestamp);
var spec = SpriteSpec.CreateFacultySpec(FacultyRole.Warbler, "FAC-WARBLER-001");
var result = SpriteGenerator.GenerateSprite(seed, spec);

// Genre creature
var genreSpec = SpriteSpec.CreateGenreSpec(
    GenreStyle.Fantasy, 
    CreatureArchetype.Familiar, 
    RarityTier.Common
);
```

## 🎮 Unity Editor Integration

Access via **Tools → TWG → TLDA → SpriteForge Editor**

### Evolution Chain Workflow
1. **Toggle Evolution Chain** - Enable evolution generation
2. **Set Frames Per Stage** - Configure animation (1-12 frames)
3. **Choose Quick Presets**:
   - "Evolution Chain" - Basic 6×6 static evolution
   - "Animated Evolution" - Smooth 6×6 animated evolution
4. **Generate & Preview** - See real-time results
5. **Export** - Save sprite sheets with Unity .meta files

### Layout Visualization
```
Evolution Grid (6×6 example):
┌─────┬─────┬─────┬─────┬─────┬─────┐
│ Egg │Frame│Frame│Frame│Frame│Frame│ ← Row 0
├─────┼─────┼─────┼─────┼─────┼─────┤
│Htch │Frame│Frame│Frame│Frame│Frame│ ← Row 1
├─────┼─────┼─────┼─────┼─────┼─────┤
│Juv  │Frame│Frame│Frame│Frame│Frame│ ← Row 2
├─────┼─────┼─────┼─────┼─────┼─────┤
│Adult│Frame│Frame│Frame│Frame│Frame│ ← Row 3
├─────┼─────┼─────┼─────┼─────┼─────┤
│Elder│Frame│Frame│Frame│Frame│Frame│ ← Row 4
├─────┼─────┼─────┼─────┼─────┼─────┤
│Leg  │Frame│Frame│Frame│Frame│Frame│ ← Row 5
└─────┴─────┴─────┴─────┴─────┴─────┘
Sheet Size: 144×144 pixels (6×24px frames)
```

## Integration

- **TLDA Bridge**: Triggered by validated rituals
- **Pet System**: Compatible with badge pet evolution stages
- **Unity ECS**: Spawns creatures and scenes from minted tokens
- **NFT Metadata**: Generates trait tables and rarity assignments
- **Local Chain**: Tests minting and validation flows

## 🎨 Visual Features

### Evolution-Specific Enhancements
- **Size scaling**: Each stage grows progressively larger
- **Color intensity**: Higher stages have enhanced saturation
- **Special effects**:
  - Egg: Shell patterns with crack animation
  - Elder: Wisdom aura with gentle glow
  - Legendary: Divine radiance with light bursts
- **Stage-specific details**: Accessories, armor, magical effects

### Archetype Evolution Patterns
- **Familiar**: Collar → Flowing mane → Radiant aura
- **Wisp**: 2 trails → 8 trails → Pulsing energy core
- **Golem**: Simple block → Armor plates → Divine crown
- **Sentinel**: Basic form → Weapons → Divine guardian

## Testing

Run the evolution system test suite:
```bash
python3 scripts/test_evolution_system.py
```

Tests validate:
- Evolution stage definitions
- Animation frame generation
- Pet system compatibility
- Unity integration points
- Sprite layout correctness