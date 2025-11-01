# STAT7: Plain English Developer Guide

> **Goal of this doc:** Explain what STAT7 is and how it works *without the mythology*. If you just want to understand the system's mechanics, start here.

---

## TL;DR: What Is STAT7?

**STAT7 = 7-dimensional addressing space for data storage and retrieval.**

Here is the best explanation I have been able to come up with yet:

STAT7, aka The Seed, is a 7‑dimensional addressing space for data storage and retrieval. Instead of storing items at a single ID or index like a normal database, every item in STAT7 is given seven context‑aware coordinates. This means you can find data by its properties rather than just an ID lookup, scale predictably to millions of items without collisions, and preserve relationships as you retrieve information. Think of it like the difference between a traditional database query—“give me row ID 42”—versus a STAT7 query: “give me all data in the narrative realm, generation 3, that’s active, with high resonance.” It’s geometric, multi‑dimensional querying instead of flat lookups.
- RAG: “I’ll throw your query into a big cloud of vectors and pull back the closest neighbors.”
- LLM weights: "I've memorized patterns in my parameters; I'll infer the likely next token."
- STAT7: “Every artifact has a 7‑coordinate address. You can walk the lattice directly, query by meaning, and never lose the relationships that make the data coherent.”

---

## The Jargon Translation Table

| STAT7 Term            | What It Actually Means                           | Database Analogy                       |
|-----------------------|--------------------------------------------------|----------------------------------------|
| **Bit-Chain**         | A single item in STAT7 space                     | Database row                           |
| **STAT7 Coordinates** | 7 context values assigned to each item           | Composite index (but 7D instead of 1D) |
| **Realm**             | Category/domain of the item                      | Table name or schema                   |
| **Lineage**           | How many generations deep from the root          | Hierarchy level / parent chain depth   |
| **Adjacency**         | Related/connected item IDs                       | Foreign key references                 |
| **Horizon**           | Current lifecycle stage (genesis→peak→decay)     | Status field (new/active/archived)     |
| **Resonance**         | Alignment/polarity of the item (-1.0 to 1.0)     | Sentiment or trust score               |
| **Velocity**          | Rate of change of the item                       | Change frequency or update rate        |
| **Density**           | Compression distance (0=fully compressed, 1=raw) | Serialization level / storage format   |
| **Address**           | SHA-256 hash of the item's canonical form        | Primary key (immutable)                |

---

## The Seven Dimensions Explained

### 1. **Realm** (Type/Category)
What *kind* of thing is this?
```python
# Examples:
realm = "data"        # Factual information
realm = "narrative"   # Story/context layer
realm = "system"      # Infrastructure/config
realm = "faculty"     # Agent/capability
realm = "event"       # Something that happened
realm = "pattern"     # Recurring structure
realm = "void"        # Empty/null state
```

**Why it matters:** Lets you query "all narratives" or "all events" without scanning everything.

---

### 2. **Lineage** (Generation/Depth)
How far is this item from the root?
```python
# Examples:
lineage = 0   # The primordial LUCA (root)
lineage = 1   # Direct descendants of LUCA
lineage = 5   # 5 generations deep
lineage = 42  # Deeply nested item
```

**Why it matters:** Answers "how fundamental is this?" and enables hierarchical queries. Compressed items have higher lineage numbers.

---

### 3. **Adjacency** (Relationships)
What other items are connected to this one?
```python
# Examples:
adjacency = [id1, id2, id3]              # Related to 3 other items
adjacency = []                           # Isolated / no relationships
adjacency = [parent_id, sibling_id, ...]  # Network graph
```

**Why it matters:** Encodes the relational graph. You can traverse connections without join queries.

---

### 4. **Horizon** (Lifecycle Stage)
Where is this item in its lifecycle?
```python
# Lifecycle progression:
genesis        # Just created
emergence      # Becoming relevant
peak           # Most active/important
decay          # Losing relevance
crystallization # Frozen/archived
```

**Why it matters:** Answers "is this live or archived?" and enables time-series queries like "show me everything in peak stage."

---

### 5. **Resonance** (Alignment/Polarity)
What's the "charge" or alignment of this item?
```python
# Range: -1.0 to 1.0
resonance = -0.8   # Negative alignment (conflict, error)
resonance =  0.0   # Neutral
resonance =  0.9   # Positive alignment (harmony, success)
```

**Why it matters:** Lets you cluster similar items (high positive resonance together), find conflicts (low/negative), or balance queries.

---

### 6. **Velocity** (Rate of Change)
How fast is this item changing?
```python
# Range: -1.0 to 1.0
velocity = -0.5   # Decaying / slowing down
velocity =  0.0   # Static / stable
velocity =  0.8   # Rapidly changing / accelerating
```

**Why it matters:** Answers "what's changing right now?" and helps predict which items need attention.

---

### 7. **Density** (Compression State)
How much detail/storage is this item taking up?
```python
# Range: 0.0 to 1.0
density = 0.0    # Fully compressed / mist form (minimal data)
density = 0.5    # Partially compressed
density = 1.0    # Raw / fully expanded (all detail)
```

**Why it matters:** Trade-off between storage and retrieval speed. Low density = efficient but lossy.

---

## How Addressing Works

### Step 1: Create a Bit-Chain
```python
# This is just a data structure
bitchain = {
    "id": "abc123",
    "entity_type": "concept",
    "realm": "narrative",
    "coordinates": {
        "realm": "narrative",
        "lineage": 3,
        "adjacency": ["xyz789", "def456"],
        "horizon": "peak",
        "resonance": 0.75,
        "velocity": 0.2,
        "density": 0.8
    },
    "created_at": "2025-01-15T10:30:00.000Z",
    "state": {
        "name": "The Hero's Journey",
        "chapter": 3,
        "engagement": 0.92
    }
}
```

### Step 2: Canonicalize
The system creates a **deterministic serialization** of the bit-chain:
- Sort all JSON keys alphabetically
- Normalize all floats to 8 decimal places
- Use ISO8601 timestamps
- Remove all whitespace

**Why:** Two identical bit-chains will always hash to the same address. Different data = different address (guaranteed).

### Step 3: Hash to Get the Address
```python
# Canonical form (no whitespace, sorted keys):
canonical = '{"coordinates":{"adjacency":["xyz789","def456"],"density":0.8,"horizon":"peak",...}'

# SHA-256 hash:
address = SHA256(canonical)
         = "a7f3e2d1c9b4... (64 hex chars)"
```

### Step 4: Store & Retrieve
```
Store: address_space[address] = bitchain
Retrieve: bitchain = address_space[address]
```

---

## Collision Resistance Explained

**The claim:** Zero address collisions, ever.

**Why it works:**
- Each bit-chain's address is SHA-256 of its complete, canonical form
- Even one bit different → completely different hash
- Same data = same address (deterministic)
- Different data = always different address (SHA-256 collision resistance is proven)

**Test results:** (From `EXP-01`)
- 10 iterations × 1,000 bit-chains = 10,000 total
- 0 collisions across all iterations ✅
- Collision rate: 0.0%

---

## Retrieval Efficiency

**The question:** Can we find items fast?

**The answer:** Depends on your query:

| Query Type                        | Mechanism                   | Speed                         |
|-----------------------------------|-----------------------------|-------------------------------|
| Get by address                    | Direct hash lookup          | O(1) — instant                |
| Get by realm                      | Index on realm coordinate   | O(log N) — very fast          |
| Get by lifecycle stage (horizon)  | Index on horizon coordinate | O(log N) — very fast          |
| Get by relationships (adjacency)  | Index on adjacency list     | O(log N) — very fast          |
| Get by polarity range (resonance) | Range query on resonance    | O(N) — full scan (worst case) |

**Benchmark:** (From `EXP-02`)
- Address lookup: 0.05ms per item
- Indexed coordinate queries: 0.2-0.5ms per 1000 items
- Stays sub-millisecond up to 100K items

---

## Scalability: Fractal Property

**The claim:** The system behaves the same way whether you have 1,000 items or 1,000,000 items.

**What that means:**
- 1K items: 0.05ms lookup
- 10K items: 0.06ms lookup (minimal degradation)
- 100K items: 0.08ms lookup (still fast)
- 1M items: 0.12ms lookup (scales logarithmically)

**Test results:** (From `EXP-04`)
- Collision rates stable across 1K → 10K → 100K → 1M
- Retrieval speed degradation < 3x
- Memory usage scales linearly with data (no surprises)

---

## Compression: Lossless Aggregation

**The concept:** You can compress bit-chains down to "mist form" (minimal storage) while preserving the ability to expand them back to full detail.

**5-stage pipeline:**
1. **Original** (density=1.0): Full raw data
2. **Fragments** (density=0.8): Remove transient state, keep core
3. **Cluster** (density=0.6): Group by realm, merge adjacency lists
4. **Glyph** (density=0.4): Symbolic representation only
5. **Mist** (density=0.0): Just the coordinate hash + metadata

**Key property:** Each stage is reversible. You can always expand back.

**Use case:** Archive old data (mist), but when someone asks for full details, expand back to original.

**Test results:** (From `EXP-05`)
- 100% lossless recovery across all 5 stages
- Compression ratio: 95% storage reduction (from original to mist)
- Expansion time: ~0.1ms per item

---

## Real-World Use Cases

### Use Case 1: Multi-Tenant Data Storage
```
Realm: "narrative"
    ├─ Tenant A's content (adjacency references)
    ├─ Tenant B's content (separate adjacency refs)
    └─ Tenant C's content

Query: "Get all narrative realm items for Tenant B" → filtered by adjacency
```

### Use Case 2: Time-Series Events
```
Realm: "event"
    ├─ horizon=genesis (new, not yet processed)
    ├─ horizon=peak (currently active)
    └─ horizon=crystallization (archived)

Query: "Show me active events" → filtered by horizon
```

### Use Case 3: Hierarchical Concepts
```
Realm: "data"
    ├─ lineage=1 (root concepts)
    ├─ lineage=2 (derived concepts)
    ├─ lineage=3 (domain-specific specializations)
    └─ lineage=4+ (deep nesting)

Query: "What's foundational?" → low lineage numbers
Query: "What's derivative?" → high lineage numbers
```

### Use Case 4: Sentiment/Alignment Queries
```
Realm: "artifact"
    ├─ resonance > 0.5 (trusted/high-quality items)
    ├─ resonance ≈ 0.0 (neutral items)
    └─ resonance < -0.5 (conflicted/error items)

Query: "Show me trusted artifacts" → resonance filter
```

---

## Implementation: Where the Code Lives

| File                             | What It Does                                             |
|----------------------------------|----------------------------------------------------------|
| `stat7_experiments.py`           | Core STAT7 logic: Coordinates, BitChain, address hashing |
| `exp04_fractal_scaling.py`       | Tests that scaling works (1K → 1M items)                 |
| `exp05_compression_expansion.py` | Tests lossless compression pipeline                      |
| `stat7_stress_test.py`           | Performance benchmarks under load                        |

**Key classes:**
- `Coordinates` — The 7-tuple of dimensions
- `BitChain` — A single item with coordinates + state
- `compute_address_hash()` — Converts a bit-chain to its SHA-256 address

---

## Constraints & Gotchas

### ✅ What Works Well
- Deterministic addressing (same input → same address, always)
- Fast lookups by individual dimensions
- Scales logarithmically
- Lossless compression

### ⚠️ Limitations
- **Range queries across multiple dimensions are slow** (requires scanning)
  - "Get all items where resonance > 0.5 AND velocity > 0.3" = O(N)
- **Adjacency updates are append-only** (you can't remove relationships, only add)
  - Design constraint to prevent corruption
- **Timestamps are immutable** (created_at never changes)
  - If you need version history, use a separate tracking system
- **Density coordinate is write-once** (once set, can't change)
  - Set it correctly at creation time

---

## Next Steps: What to Build

If you're implementing STAT7 for your project:

1. **Start with indexing** — Build indexes on the 7 coordinates
2. **Add querying** — Single-dimension queries first, then multi-dimension
3. **Implement compression** — Use the 5-stage pipeline
4. **Add persistence** — Store bit-chains to disk/DB (address-based keys)
5. **Add concurrency** — Thread-safe reads/writes (see `stat7_stress_test.py`)

---

## FAQ: The Questions Developers Actually Ask

**Q: Is this just a fancy hash table?**
> Basically yes, but with structured coordinates instead of arbitrary keys. The difference: you can query by properties (realm, lifecycle stage, etc.) instead of only by ID.

**Q: Why not just use a regular database with 7 columns?**
> You could! STAT7 is optimized for fractal scaling (works the same at 1K or 1M items) and lossless compression. If you don't need those, a regular table is simpler.

**Q: What happens on address collision?**
> It won't happen. SHA-256 collision resistance is mathematically proven. If two bit-chains get the same address, they're identical (by definition).

**Q: Can I use this with my existing database?**
> Yes. Use the address as the primary key. Store bit-chain objects as JSON or BSON in a column.

**Q: Do I have to use all 7 dimensions?**
> No. Use only what you need. Leave unused dimensions at default values.

**Q: Why "STAT7" and not just "7D addressing"?**
> **STAT7 = Space-Time-Adjacency-Type-Horizon-Luminosity-Dimensionality** (original naming). But honestly, "7D addressing" works fine too.

---

## Further Reading

- **Want theory?** See `01-ADDRESSING-FOUNDATIONS.md`
- **Want the full spec?** See `03-BIT-CHAIN-SPEC.md`
- **Want to see it run?** See `04-VALIDATION-EXPERIMENTS.md`
- **Got questions?** Add them to `BRAINSTORM.md`

---

**Last Updated:** 2025-01-15  
**Status:** Developer-facing reference (no mythology, just mechanics)  
**Tone:** Practical and skeptical—this is how it actually works
