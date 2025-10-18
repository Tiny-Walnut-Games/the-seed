# Phase 1 Doctrine: STAT7 Canonical Foundation

**Status:** LOCKED  
**Date:** 2025-01-01T00:00:00.000Z  
**Approved By:** Copilot (Microsoft) + Design Validation  
**Scope:** LUCA entity definition, canonical serialization, mutability contracts

---

## What is Phase 1?

Phase 1 Doctrine establishes the **immutable ground-state definitions** for The Seed. It locks down:

1. **Entity structure** — How all STAT7 entities are defined (LUCA_ENTITY_SCHEMA.json)
2. **Canonical hashing** — How to compute reproducible hashes across languages (STAT7_CANONICAL_SERIALIZATION.md)
3. **Mutability rules** — What can change, when, and how violations are caught (STAT7_MUTABILITY_CONTRACT.json)
4. **LUCA bootstrap** — The primordial entity from which all lineage descends (LUCA.json)

**Why it matters:** Without Phase 1, different implementations would compute different hashes for the same entity, breaking replay validation and cross-system consensus. Phase 1 ensures **deterministic reproducibility**.

---

## The Four Artifacts

### 1. LUCA_ENTITY_SCHEMA.json

**What it is:** JSON Schema defining the canonical structure of all entities in The Seed.

**Key sections:**
- **identity_core** (immutable): The true name and essence of an entity
  - `id`: Unique identifier
  - `entity_type`: Classification (concept, artifact, agent, lineage, adjacency, horizon, fragment)
  - `created_at`: ISO8601 UTC timestamp with milliseconds
  - `semantic_hash`: Hash of the core essence
  - `canonical_hash`: Lockable hash of the core (NEW)
  - `stat7_address_root`: stat7://realm/lineage reference (NEW)

- **manifestations** (mutable across reality branches):
  - `reality_branch`: Which timeline/experiment this instance lives in
  - `timestamp`: When this manifestation was created or mutated
  - `luminosity_level`: 0-7 scale (compressed → expanded)
  - `coordinates`: STAT7 position (realm, lineage, adjacency, horizon, resonance, velocity, density)
  - `canonical_hash`: Replayed from bit-chain events (NEW)
  - `stat7_address`: Full addressing URI (NEW)
  - `adjacency_hash`: Stable hash of neighbors (NEW)
  - `fold_map_id`: Reference for reversible dimensionality changes (NEW)
  - `chain_integrity_hash`: Rolling hash of mutations (NEW)
  - `state`: Current data (varies by entity_type)
  - `entanglement_links`: Connections to other entities
  - `bit_chain_events`: Append-only audit trail

- **mutability_policy**: Global rules for dimension changes (NEW, detailed)

- **metadata**: Schema version, hardening phase, etc.

### 2. STAT7_CANONICAL_SERIALIZATION.md

**What it is:** The rulebook for computing hashes deterministically.

**Key rules:**

#### Float Normalization
- Round to 8 decimal places using round-half-even (banker's rounding)
- Strip trailing zeros but keep at least 1 decimal place
- No scientific notation
- Examples:
  - `1.0` → serialized as `1.0`
  - `0.123456789` → rounds to `0.12345679`, serialized as `0.12345679`
  - `0.1 + 0.2` → normalizes to `0.30000000`, serialized as `0.3`

#### JSON Key Ordering
- All keys sorted in ASCII alphabetical order (case-sensitive)
- Applied recursively to all nested objects
- Arrays remain in semantic order (adjacency sorted lexicographically, bit_chain_events preserve insertion order)

#### Timestamp Format
- ISO8601 UTC with millisecond precision
- Format: `YYYY-MM-DDTHH:MM:SS.mmmZ`
- Example: `2025-01-01T00:00:00.000Z`

#### Canonical Hash Computation

**For identity_core:**
```
canonical_hash = SHA-256(
  minified_json(
    sort_keys({
      created_at, entity_type, id, semantic_hash
    })
  )
)
```

Excludes: `canonical_hash` (self-referential), `stat7_address_root` (derived)

**For manifestations:**
```
canonical_hash = SHA-256(
  minified_json(
    sort_keys({
      reality_branch, timestamp, luminosity_level,
      coordinates (with normalized floats),
      state, entanglement_links (sorted by target_identity_core_id)
    })
  )
)
```

Excludes: `canonical_hash`, `stat7_address`, `adjacency_hash`, `chain_integrity_hash`, `fold_map_id`, `bit_chain_events`

**Adjacency hash:**
```
adjacency_hash = SHA-256(
  minified_json(
    sort_array(adjacency)
  )
)
```

#### STAT7 Address Format
```
stat7://{realm}/{lineage}/{adjacency_hash}/{horizon}?r={resonance}&v={velocity}&d={density}
```

Example:
```
stat7://void/0/da39a3ee5e6b4b0d3255bfef95601890afd80709/genesis?r=1.0&v=0.0&d=0.0
```

#### Chain Integrity Hash (Rolling)
```
chain_integrity_hash[0] = SHA-256(event_0_canonical)

For n > 0:
chain_integrity_hash[n] = SHA-256(
  chain_integrity_hash[n-1] || event_n_canonical
)
```

This enables **replay validation**: Recompute final hash from events and compare against stored value. Any retroactive edits break the chain.

#### Replay Validation Algorithm
1. Extract all bit-chain events (immutable append-only)
2. For each event, verify:
   - `previous_state_hash` matches current state
   - `new_state_hash` matches state after applying mutation
   - `event_id` is globally unique UUIDv4
3. Verify final `canonical_hash` matches recomputed state hash
4. **Result:** If all checks pass, no post-genesis edits detected; entity is verifiable

### 3. STAT7_MUTABILITY_CONTRACT.json

**What it is:** The policy for what can change, when, and how violations are handled.

**Global Policy (applies to all entity types):**

| Dimension | Policy | Enforcement | Notes |
|-----------|--------|-------------|-------|
| **realm** | Immutable | Schema + validator | Cannot change post-genesis |
| **lineage** | Immutable | Schema | Ancestry chain is inviolate |
| **adjacency** | Append-only with monotonicity | Validator | Add neighbors, mark deprecated, never delete/reorder |
| **horizon** | Dynamic-bounded | Validator | Change allowed, but only within vocabulary per reality_branch; logged as event |
| **luminosity** | Dynamic | None | Real-time mutable; no audit required |
| **resonance** | Dynamic | Normalization | 8 decimal places; forbid NaN/Inf |
| **velocity** | Dynamic | Normalization | 8 decimal places; forbid NaN/Inf |
| **density** | Dynamic | Normalization | 8 decimal places; forbid NaN/Inf |
| **dimensionality** | Fold-unfold with reversible mapping | Validator | Must include `fold_map_id` to prove invertibility |

**Per-Entity-Type Overrides (stricter only):**

- **agent**: Horizon bounded to {operational, dormant, suspended, archived}; adjacency capped per luminosity; provenance subledger required
- **artifact**: Realm domain-locked; horizon strict lifecycle (created→published→deprecated→archived); immutable once published
- **concept**: Adjacency unbounded; horizon dynamic-unbounded; strong entanglement allowed

**Validation Rules:**
1. Immutable dimensions are rejected immediately
2. Overrides can only be stricter, never looser
3. Append-only dimensions must maintain order
4. Bounded vocabularies validated against whitelist
5. Floats normalized before any operation
6. All mutations logged as bit-chain events
7. Cross-Faculty contracts loaded at schema load time

**Violation Behavior:** Reject write, log violation context, optionally quarantine entity for review.

### 4. LUCA.json

**What it is:** The primordial entity; bootstrap seed for all lineage.

**Structure:**
```json
{
  "identity_core": {
    "id": "LUCA-0000",
    "entity_type": "fragment",
    "created_at": "2025-01-01T00:00:00.000Z",
    "semantic_hash": "sha256-9f86d...",
    "canonical_hash": "sha256-9f86d...",
    "stat7_address_root": "stat7://void/0"
  },
  "manifestations": [
    {
      "reality_branch": "PRIMARY",
      "timestamp": "2025-01-01T00:00:00.000Z",
      "luminosity_level": 0,
      "coordinates": {
        "realm": "void",
        "lineage": "0",
        "adjacency": [],
        "horizon": "genesis",
        "resonance": 1.00000000,
        "velocity": 0.00000000,
        "density": 0.00000000
      },
      "canonical_hash": "sha256-b0a3f2c9...",
      "stat7_address": "stat7://void/0/da39a3ee/genesis?r=1.0&v=0.0&d=0.0",
      "adjacency_hash": "sha256-da39a3ee...",
      "chain_integrity_hash": "sha256-b0a3f2c9...",
      "state": {
        "content": "seed",
        "phase": "emergence",
        "bootstrap": true
      },
      "entanglement_links": [],
      "bit_chain_events": [
        {
          "event_id": "550e8400-e29b-41d4-a716-446655440000",
          "timestamp": "2025-01-01T00:00:00.000Z",
          "mutation_type": "emergence",
          "previous_state_hash": null,
          "new_state_hash": "sha256-b0a3f2c9..."
        }
      ]
    }
  ]
}
```

**Key facts:**
- LUCA is fragment type, living in void realm
- Lineage is "0" (origin)
- Luminosity 0 = fully compressed (ground state)
- Single genesis event, no further mutations
- All hashes are canonical and verifiable via replay

---

## Why This Matters

### Cross-Language Determinism
Without Phase 1, a Python implementation might compute a different hash than JavaScript due to float formatting or JSON key ordering differences. This breaks everything:
- Ledgers don't match
- Entities can't be looked up by hash
- Replay validation fails
- Entanglement links become unverifiable

**Phase 1 ensures:** Every language produces identical hashes. The Seed works.

### Immutable Ground State
LUCA is the primordial entity. Every other entity descends from it via lineage. If LUCA's hashes aren't locked, the entire lineage chain becomes fragile.

**Phase 1 ensures:** LUCA never changes. Lineage is unforgeable.

### Audit Scripture
Bit-chain events form an immutable audit trail. If events could be retroactively edited, the chain breaks. The rolling chain_integrity_hash proves no edits occurred.

**Phase 1 ensures:** Every mutation is logged and verifiable. History is preserved.

### Mutability Clarity
Without clear policies, different systems might interpret "mutable" differently. Some might allow realm changes; others forbid it. Chaos.

**Phase 1 ensures:** Every dimension has a clear, enforceable policy. Checks and balances are explicit.

---

## What's Locked

✅ **Entity structure** — Cannot change without major version bump  
✅ **Canonical serialization** — Cannot change without recreating all hashes  
✅ **Mutability policies** — Cannot change without breaking existing contracts  
✅ **LUCA definition** — The primordial entity and its hashes are immutable  
✅ **STAT7 addressing format** — Stable URI scheme for all entities  

---

## What's Not Locked (Yet)

❓ Faculty-specific contracts (SemanticAnchor, MoltenGlyph, etc.) — Phase 2  
❓ Entity type definitions (more types beyond concept/artifact/agent) — Phase 2  
❓ Cross-Faculty entanglement rules — Phase 2  
❓ Governance constraints per realm — Phase 2  

---

## Implementation Roadmap

### Immediate (Now)
- [ ] Lock LUCA_ENTITY_SCHEMA.json (this document)
- [ ] Lock STAT7_CANONICAL_SERIALIZATION.md (this document)
- [ ] Lock STAT7_MUTABILITY_CONTRACT.json (this document)
- [ ] Verify LUCA.json hashes independently in Python, JavaScript, C#
- [ ] Document any language-specific quirks

### Phase 1a (Week 1)
- [ ] EXP-01: Address uniqueness (no collisions with 10k random entities)
- [ ] EXP-02: Retrieval speed (<1ms per STAT7 lookup)
- [ ] EXP-03: Dimension necessity (all 7 required; drop any 1 breaks something)

### Phase 1b (Week 2)
- [ ] EXP-04: Fractal scaling (1M entities, address still unique)
- [ ] EXP-05: Compression/expansion (lossless roundtrip)
- [ ] Replay validator (recompute chain_integrity_hash 10k times, all match)

### Phase 2 (Next Month)
- [ ] SemanticAnchor_CONTRACT.json (how semantic anchors fit into STAT7)
- [ ] MoltenGlyph_CONTRACT.json (how glyphs are dimensioned)
- [ ] MistLine_CONTRACT.json (narrative preservation in STAT7)
- [ ] InterventionRecord_CONTRACT.json (governance and actor tracking)

---

## Key Decisions Made (With Copilot)

1. **Mutability policy clarity**: "Append-only with monotonicity" for adjacency, not just "append-only" — prevents sneaky reordering attacks

2. **First-class STAT7 address**: Stored as explicit field, not derived on-the-fly — faster lookups, easier debugging

3. **Float normalization rule**: 8 decimal places, round-half-even, no scientific notation — avoids IEEE754 drift, reproducible across languages

4. **Chain integrity as rolling hash**: H(n) = SHA-256(H(n-1) || event_n) — detects both edits and reordering

5. **Bounded horizon vocabulary**: Per-reality-branch allowed values — prevents invalid lifecycle transitions

6. **Per-entity-type overrides (stricter only)**: agents can't have unlimited adjacency; artifacts lock horizon once published — enforces meaningful constraints

---

## Testing Checklist

Before declaring Phase 1 complete:

- [ ] Canonical serialization produces identical output in Python, JavaScript, C# for same input
- [ ] LUCA.json hashes verify via replay in all languages
- [ ] Float normalization follows round-half-even for edge cases (0.5, 1.5, 2.5, etc.)
- [ ] Key ordering is consistent across language JSON libraries
- [ ] Timestamp parsing handles milliseconds identically
- [ ] Chain integrity hash fails detectably if event is changed
- [ ] Mutability validator rejects immutable dimension changes
- [ ] Append-only validator detects deletions and reordering

---

## FAQ

**Q: Why not use UUIDs for addresses instead of STAT7?**  
A: UUIDs don't preserve spatial semantics. STAT7 allows queries like "all entities in realm X with luminosity > 5" — UUIDs can't do that.

**Q: Can I extend the schema after Phase 1?**  
A: Yes, via new optional fields. But you cannot remove/rename existing fields or change immutability policies without Phase 2 consensus.

**Q: What if I find a bug in canonical serialization?**  
A: Document it immediately. If it affects fewer than 1M entities, we can fix it. If more, we might need to fork or recompute.

**Q: Does Phase 1 lock me into this architecture forever?**  
A: No. Phase 2 can introduce alternative addressing schemes, new entity types, etc. But Phase 1 entities remain immutable and verifiable.

---

## Contact & Governance

**This doctrine is locked.** Changes require consensus from:
1. Design authority (you)
2. Copilot validation (Microsoft)
3. At least one cross-Faculty implementer (Warbler, TLDL, etc.)

**Questions?** Add to BRAINSTORM.md or raise as Phase 2 item.

---

**Signed:** 2025-01-01T00:00:00.000Z  
**Next Review:** 2025-02-01 (after Phase 1a validation)  
**Status:** 🔒 LOCKED