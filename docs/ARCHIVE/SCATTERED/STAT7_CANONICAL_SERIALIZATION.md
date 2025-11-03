# STAT7 Canonical Serialization Specification

**Version:** 1.0.0  
**Status:** Phase 1 Doctrine (Locked)  
**Purpose:** Ensure deterministic, reproducible computation of canonical hashes across all systems and languages.

---

## Overview

Canonical serialization is the process of converting an entity's state into a byte-perfect, deterministic representation that produces the same hash regardless of language, platform, or time. This enables:

- **Replay validation**: Recompute final state hash from bit-chain events and verify against stored canonical_hash
- **Cross-system consensus**: Multiple implementations produce identical hashes
- **Audit chain integrity**: Prove that no mutations occurred post-genesis
- **Chain integrity validation**: Verify rolling chain hash across event sequence

---

## Float Normalization (CRITICAL)

### Rule: Round-Half-Even to 8 Decimal Places

All floating-point values (`resonance`, `velocity`, `density`, `resonance_strength`) must be normalized before serialization.

### Algorithm

```
normalize(value):
  1. If value is NaN or Inf, REJECT (schema violation)
  2. Round to 8 decimal places using round-half-even (banker's rounding)
  3. Strip trailing zeros BUT keep at least one decimal place
  4. Serialize as plain decimal (no scientific notation, no e-notation)
```

### Examples

| Input  | After Round | After Strip | Serialized |
|--------|-------------|-------------|------------|
| 1.0    | 1.00000000  | 1.0        | 1.0        |
| 0.0    | 0.00000000  | 0.0        | 0.0        |
| 0.5    | 0.50000000  | 0.5        | 0.5        |
| 1.123456789 | 1.12345679  | 1.12345679 | 1.12345679 |
| 0.1 + 0.2 | 0.30000000  | 0.3        | 0.3        |
| 999.999999999 | 1000.00000000 | 1000.0 | 1000.0 |

### Language-Specific Guidance

- **Python**: Use `decimal.Decimal` with `ROUND_HALF_EVEN`
- **JavaScript**: Use `Math.round(value * 1e8) / 1e8`; then format via custom function
- **C#/.NET**: Use `decimal` type with `MidpointRounding.ToEven`
- **Rust**: Use `ordered-float` crate or manual rounding; verify with tests

---

## JSON Key Ordering

### Rule: Case-Sensitive ASCII Alphabetical Order

All JSON keys must be sorted case-sensitively in ASCII order before serialization. This applies to:
- Top-level keys in objects
- Nested object keys at any depth
- Array elements that are themselves objects (if semantically ordered)

### Example

```json
{
  "adjacency_hash": "...",
  "canonical_hash": "...",
  "chain_integrity_hash": "...",
  "coordinates": { ... },
  "entanglement_links": [ ... ],
  "state": { ... }
}
```

**NOT VALID:**
```json
{
  "state": { ... },
  "canonical_hash": "...",
  "coordinates": { ... }
}
```

---

## Timestamp Normalization

### Rule: ISO8601 UTC with Millisecond Precision

All timestamps must be in ISO8601 format with UTC timezone and millisecond precision.

```
Format: YYYY-MM-DDTHH:MM:SS.mmmZ
```

### Examples

```
Valid:   2025-01-01T00:00:00.000Z
Valid:   2025-10-18T15:23:45.123Z
Invalid: 2025-01-01T00:00:00Z (missing milliseconds)
Invalid: 2025-01-01T00:00:00.123+00:00 (non-UTC offset)
Invalid: 2025-01-01 00:00:00.123 (not ISO8601)
```

---

## Array Ordering

### Rule: Deterministic Ordering per Semantic Context

- **`adjacency` array**: Sort lexicographically (string comparison)
- **`bit_chain_events` array**: Maintain insertion order (temporal immutability)
- **`entanglement_links` array**: Sort by `target_identity_core_id` lexicographically

### Example

```json
{
  "adjacency": [
    "concept-001",
    "concept-002",
    "concept-003"
  ],
  "entanglement_links": [
    {
      "target_identity_core_id": "agent-001",
      ...
    },
    {
      "target_identity_core_id": "artifact-002",
      ...
    }
  ]
}
```

---

## Canonical Hash Computation

### For `identity_core`

```
canonical_hash = SHA-256(
  minified_json(
    sort_keys(identity_core)
  )
)
```

**Include fields:**
- `id`
- `entity_type`
- `created_at`
- `semantic_hash`

**Exclude fields:**
- `canonical_hash` (self-referential)
- `stat7_address_root` (derived)

**Example computation:**
```json
{
  "created_at": "2025-01-01T00:00:00.000Z",
  "entity_type": "fragment",
  "id": "LUCA-0000",
  "semantic_hash": "sha256-9f86d081884c7d6d9ffd60a2717b5efb9a8f2f5c8d0e9c0a9a9b8c8d8e8e8e"
}
```

Minified: `{"created_at":"2025-01-01T00:00:00.000Z","entity_type":"fragment","id":"LUCA-0000","semantic_hash":"sha256-9f86d081884c7d6d9ffd60a2717b5efb9a8f2f5c8d0e9c0a9a9b8c8d8e8e8e"}`

Hash: `sha256-9f86d081884c7d6d9ffd60a2717b5efb9a8f2f5c8d0e9c0a9a9b8c8d8e8e8e`

### For `manifestations[i]`

```
canonical_hash = SHA-256(
  minified_json(
    sort_keys(manifestation_without_chain_fields)
  )
)
```

**Include fields:**
- `reality_branch`
- `timestamp`
- `luminosity_level`
- `coordinates` (with floats normalized)
- `state`
- `entanglement_links` (sorted)

**Exclude fields:**
- `canonical_hash` (self-referential)
- `stat7_address` (derived)
- `adjacency_hash` (derived)
- `chain_integrity_hash` (depends on events)
- `fold_map_id` (metadata, not state)
- `bit_chain_events` (audit trail, not canonical state)

---

## Adjacency Hash Computation

```
adjacency_hash = SHA-256(
  minified_json(
    sort_array(adjacency)
  )
)
```

**Example:**
```json
["concept-001", "concept-002", "concept-003"]
```

Minified: `["concept-001","concept-002","concept-003"]`

Hash: `sha256-da39a3ee5e6b4b0d3255bfef95601890afd80709`

---

## STAT7 Address Computation

```
stat7_address = "stat7://{realm}/{lineage}/{adjacency_hash}/{horizon}?r={resonance}&v={velocity}&d={density}"
```

**Rules:**
- `realm`, `lineage`, `horizon`: Use raw string values
- `adjacency_hash`: Computed per above
- `resonance`, `velocity`, `density`: Use normalized float strings (8dp)
- `?` separates path from query parameters
- Parameters in order: `r`, `v`, `d` (alphabetical)

**Example:**
```
stat7://void/0/da39a3ee5e6b4b0d3255bfef95601890afd80709/genesis?r=1.00000000&v=0.00000000&d=0.00000000
```

---

## Chain Integrity Hash Computation

Chain integrity hash is a **rolling hash** that chains events together, enabling replay validation.

```
chain_integrity_hash[0] = SHA-256(minified_json(sort_keys(bit_chain_events[0])))

For n > 0:
chain_integrity_hash[n] = SHA-256(
  chain_integrity_hash[n-1] || bit_chain_events[n]_canonical
)
```

**Rules:**
- Each event contributes to the chain
- Order is immutable (events are append-only)
- Retroactive edits are detectable (chain hash changes)
- Final chain hash validates all prior events

**Example pseudocode:**
```python
def compute_chain_integrity(events):
    chain_hash = ""
    for event in events:
        canonical = minified_json(sort_keys(event))
        if chain_hash == "":
            chain_hash = sha256(canonical)
        else:
            chain_hash = sha256(chain_hash + canonical)
    return chain_hash
```

---

## Event Canonical Form

Each bit-chain event must be serialized canonically:

```json
{
  "actor": "agent-xyz (or null)",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "mutation_type": "emergence",
  "new_state_hash": "sha256-b0a3f2c9d1e5a8f3b7c2d9e8f1a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1",
  "previous_state_hash": null,
  "timestamp": "2025-01-01T00:00:00.000Z"
}
```

---

## Replay Validation Algorithm

**Purpose**: Verify that no mutations occurred post-genesis.

```python
def validate_manifestation_replay(manifestation):
    """
    Recompute canonical_hash from bit-chain events and compare.
    """
    # 1. Extract all events
    events = manifestation.bit_chain_events
    
    # 2. Compute initial state from genesis event
    state = json.loads(events[0].new_state_hash)  # Assume hashes reference state
    
    # 3. Replay mutations
    for i, event in enumerate(events[1:], 1):
        # Verify previous_state_hash matches current state
        assert hash(state) == event.previous_state_hash
        
        # Apply mutation (conceptual; depends on mutation_type)
        state = apply_mutation(state, event)
        
        # Verify new_state_hash matches
        assert hash(state) == event.new_state_hash
    
    # 4. Verify final canonical_hash
    assert manifestation.canonical_hash == hash(state)
    
    return True  # Replay successful, no post-genesis edits detected
```

---

## Serialization Pseudocode

```python
def canonical_serialize(obj):
    """
    Convert object to canonical JSON string.
    """
    # 1. Recursively normalize floats
    obj = normalize_floats(obj)
    
    # 2. Recursively sort keys
    obj = sort_keys_recursive(obj)
    
    # 3. Minify (no extraneous whitespace)
    json_string = json.dumps(obj, separators=(',', ':'), sort_keys=True)
    
    return json_string

def normalize_floats(obj):
    """Recursively normalize all float values to 8dp."""
    if isinstance(obj, dict):
        return {k: normalize_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_floats(v) for v in obj]
    elif isinstance(obj, float):
        # Round to 8 decimal places, strip trailing zeros but keep 1 decimal place
        rounded = round(obj, 8)
        return float(f"{rounded:.8f}".rstrip('0').rstrip('.') or '0')
    else:
        return obj

def sort_keys_recursive(obj):
    """Recursively sort all dict keys."""
    if isinstance(obj, dict):
        return {k: sort_keys_recursive(obj[k]) for k in sorted(obj.keys())}
    elif isinstance(obj, list):
        return [sort_keys_recursive(v) for v in obj]
    else:
        return obj
```

---

## Validation Checklist

Before computing any hash, verify:

- [ ] All floats are finite (not NaN, not Inf)
- [ ] All timestamps are ISO8601 UTC with milliseconds
- [ ] All arrays are sorted per semantic context
- [ ] All JSON keys are in ASCII alphabetical order
- [ ] No extraneous whitespace in JSON
- [ ] UUIDs (event_id) are valid UUIDv4

---

## Testing

### Required Test Cases

1. **Float normalization**: Verify round-half-even behavior
2. **Key ordering**: Confirm ASCII sort matches canonical
3. **Timestamp parsing**: Ensure all systems parse ISO8601 identically
4. **Chain replay**: Recompute chain hash and match stored value
5. **Hash reproducibility**: Compute same hash 100x in loop

### CI Integration

All STAT7 entities must pass canonical serialization validation before being persisted.

---

## FAQ

**Q: Why 8 decimal places?**  
A: Sufficient for sub-micron precision in spatial coordinates while avoiding IEEE754 double-precision drift.

**Q: Can I use hex-encoded SHA-256?**  
A: Yes; specify format in your implementation contract.

**Q: What if two systems compute different hashes?**  
A: Follow the Serialization Pseudocode step-by-step; most conflicts arise from float formatting or key ordering.

**Q: Is minified JSON required?**  
A: Yes, for hashing. Human-readable versions are non-canonical and should not be hashed.

---

**Last Updated:** 2025-01-01  
**Locked by:** Phase 1 Doctrine (do not modify without cross-Faculty consensus)