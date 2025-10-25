# Bit-Chain Specification

> The formal definition of the smallest addressable unit in The Seed

---

## Bit-Chain: Definition and Anatomy

### What Is a Bit-Chain?
A **bit-chain** is an atomic unit of meaningful information in The Seed that:
1. Cannot be subdivided without losing essential context
2. Contains sufficient information to bootstrap the next iteration of itself
3. Exists in exactly one position in STAT7 coordinate space
4. Can be compressed toward LUCA or expanded into infinite context
5. Can be entangled with other distant bit-chains via resonance

### Why Not Just "Data Node"?
- **Chain** implies: lineage, sequence, connectedness, evolutionary history
- **Bit** implies: minimal unit, information-theoretic reducibility, binary choice at core
- **Bit-Chain** implies: sequences of bits that form meaningful narratives across fractal levels

---

## STAT7 Coordinate System (Formal)

### The Seven Dimensions

#### 1. **Realm** (R)
**Purpose:** Structural domain classification  
**Type:** Categorical/Enum  
**Values:** {data, narrative, system, faculty, event, pattern, void}  
**Question:** What domain does this belong to?

**Examples:**
- `R=data`: A database record, configuration value
- `R=narrative`: A story beat, decision rationale
- `R=system`: An algorithm, architecture pattern
- `R=faculty`: Advice from CID, consultation result
- `R=event`: A state transition, lifecycle moment
- `R=pattern`: A repeated motif, resonance pattern
- `R=void`: Unimplemented space, potential futures

---

#### 2. **Lineage** (L)
**Purpose:** Evolutionary generation and ancestry  
**Type:** Numeric (integer), hierarchical  
**Range:** 1 to ∞ (or bounded to project scope)  
**Question:** How many generations away from LUCA is this?

**Interpretation:**
- `L=1`: Direct descendant of LUCA (primordial, rarely used alone)
- `L=2`: Children of L=1 (foundational patterns)
- `L=3-5`: Mid-generation (most active development)
- `L=6+`: Evolved, compressed, specialized forms

**Fractal Property:** A bit-chain at L=5 contains ALL information needed to bootstrap L=6

---

#### 3. **Adjacency** (A)
**Purpose:** Relational proximity in semantic/functional space  
**Type:** Set of references (UUIDs or hashes)  
**Question:** What other bit-chains are meaningfully near this one?

**Properties:**
- Not spatial distance (doesn't care about physical/computational location)
- Is semantic resonance (functional, conceptual, narrative similarity)
- Can be computed via:
  - Shared Realm
  - Shared Lineage
  - Explicit cross-references in content
  - Harmonic similarity (if implemented)

**Example:**
```
Bit-Chain A (code decision): R=system, L=4, A={uuid-B, uuid-C}
Bit-Chain B (related test):   R=system, L=4, A={uuid-A, uuid-C}
Bit-Chain C (architecture):   R=system, L=3, A={uuid-A, uuid-B}

→ A-B-C form a cluster; distance from each other ≈ 1 or 2 hops
```

---

#### 4. **Horizon** (H)
**Purpose:** Temporal scope and lifecycle stage  
**Type:** Categorical + numeric  
**Values:** {genesis, emergence, peak, decay, crystallization, void}  
**Timeline:** Past < Present < Future  
**Question:** Where in its lifecycle is this bit-chain?

**Stages:**
- `H=genesis`: New, just created, not yet integrated
- `H=emergence`: Growing, being used, expanding context
- `H=peak`: Active, frequently accessed, full detail retained
- `H=decay`: Cooling, usage declining, compression beginning
- `H=crystallization`: Cold, compressed, only essence remains
- `H=void`: Pre-existing potential, not yet manifested

**Interaction with Luminosity:**
- `H=peak` typically has high Luminosity
- `H=crystallization` typically has low Luminosity
- (But not always—active exploration can re-heat crystallized data)

---

#### 5. **Luminosity** (Lum)
**Purpose:** Activity level and compression distance from LUCA  
**Type:** Float [0.0 to 1.0] or energy metric [0 to ∞]  
**Question:** How "hot" is this data right now?

**Interpretation:**
- `Lum=0.0` → Ice cold, maximally compressed, at LUCA threshold
- `Lum=0.3` → Cool, crystallized, compressed form
- `Lum=0.7` → Warm, actively used, moderate detail
- `Lum=1.0` → Burning hot, full context expanded, actively modified

**Decay Mechanics:**
- Luminosity naturally decays over time (Evaporation Engine)
- Can be re-heated by access, discussion, or explicit "reminder"
- Serves as the **distance metric from LUCA**

**Key Insight:** Luminosity IS your compression axis. Lower Lum = closer to LUCA.

---

#### 6. **Polarity** (P)
**Purpose:** Charge, alignment, resonance pattern  
**Type:** Signed value or vector  
**Range:** -1.0 to +1.0 (or {+, -, 0, ?})  
**Question:** What's this bit-chain's charge relative to the system?

**Possible Interpretations:**
1. **Alignment:** `+` = supports main narrative, `-` = questions/contrasts it, `0` = neutral
2. **Affect:** `+` = positive emotion/growth, `-` = shadow/struggle, `0` = analytical
3. **Certainty:** `+` = high confidence, `-` = experimental/uncertain, `0` = neutral
4. **Direction:** `+` = moves toward LUCA, `-` = moves away, `0` = orthogonal

**Entanglement via Polarity:**
```
Bit-Chain A: P=+0.8 (strongly supportive)
Bit-Chain B: P=-0.7 (strongly contrasting)

Resonance type: Harmonic opposition
Entanglement strength: VERY HIGH (complementary charges attract)

→ These might be better understood AS A PAIR
```

---

#### 7. **Dimensionality** (D)
**Purpose:** Complexity and recursive depth of this bit-chain  
**Type:** Integer [0 to N] or categorical  
**Values:** {point, line, plane, volume, tesseract, ...}  
**Question:** How many fractal layers does this bit-chain contain?

**Interpretation:**
- `D=0` (Point): Atomic, cannot be decomposed, no internal structure
- `D=1` (Line): Sequential; contains a chain of decisions
- `D=2` (Plane): Relational; contains 2D map of concepts
- `D=3` (Volume): Full system; contains a 3D ecosystem
- `D=4+` (Tesseract+): Recursive; contains nested sub-fractals

**Consequence:**
- High-D bit-chains are expensive to retrieve (more context needed)
- Low-D bit-chains are cheap but less information-dense
- Expansion/compression may change D (unfold increases it, compress decreases it)

---

## Complete Bit-Chain Record Structure

```
BitChain {
  id: UUID                                    # Globally unique identifier
  
  # STAT7 Coordinates
  realm: Enum(data|narrative|system|faculty|event|pattern|void)
  lineage: Integer >= 1                       # Generation from LUCA
  adjacency: Set<UUID>                        # Related bit-chains
  horizon: Enum(genesis|emergence|peak|decay|crystallization|void)
  luminosity: Float [0.0, 1.0]                # Activity/temperature
  polarity: Float [-1.0, 1.0]                 # Charge/alignment
  dimensionality: Integer [0, N]              # Fractal depth
  
  # Content
  content: String                             # The actual information (variable length)
  content_hash: SHA256                        # For content-addressed retrieval
  
  # Context and Navigation
  created_at: Timestamp                       # When was this bit-chain born?
  last_accessed: Timestamp                    # When was it last read?
  last_modified: Timestamp                    # When was it last changed?
  access_count: Integer                       # How many times retrieved?
  
  # Lifecycle Management
  compression_level: {raw|mist|crystallized}  # Current storage state
  parent_lineage: UUID                        # Immediate ancestor (for bootstrapping)
  children: Set<UUID>                         # Immediate descendants
  
  # Semantic Metadata
  tags: Set<String>                           # Human-readable labels
  harmonic_signature: Vector(float)           # For resonance computation
  narrative_role: String                      # In what story does this matter?
  
  # Entanglement
  entangled_with: Map<UUID, Float>            # UUID → resonance strength (0.0 to 1.0)
  
  # Validation
  provenance: String                          # How was this created? (human/AI/system)
  integrity_hash: SHA256                      # For corruption detection
}
```

---

## STAT7 Coordinate Computation

### Algorithm: Assign STAT7 to Incoming Bit-Chain

```
Input: new_bit_chain (content, basic metadata)
Output: STAT7 coordinates

1. REALM DETECTION
   - Parse content for keywords/patterns
   - Match to {data, narrative, system, faculty, event, pattern}
   - If ambiguous, set R = "pattern" (meta-information)

2. LINEAGE ASSIGNMENT
   - Does this descend from existing bit-chain? YES → L = parent.L + 1
   - Is this primordial/foundational? → L = 1
   - Is this a re-expression of known concept? → L = parent.L (same generation)

3. ADJACENCY COMPUTATION
   - Semantic similarity search against existing bit-chains
   - Accept top-k matches (k = 3-5)
   - Verify shared Realm or Lineage (strong signal)

4. HORIZON ASSIGNMENT
   - If created in last 24h → H = genesis
   - If accessed in last 7d → H = emergence or peak
   - If not accessed in 30d+ → H = decay
   - If Luminosity < 0.1 → H = crystallization

5. LUMINOSITY CALCULATION
   - L = access_count / max_possible_count (normalize to [0,1])
   - OR: L = exp(-(days_since_access / half_life))
   - Start new bit-chains at L = 0.7 (warm, active)

6. POLARITY DETECTION
   - Sentiment analysis on content → positive/negative
   - Query against "main narrative" or "system axioms" → aligned/opposed
   - Default: P = 0.0 (neutral) if uncertain

7. DIMENSIONALITY INFERENCE
   - Count immediate children → if < 2, D = 0
   - Count Adjacency set size → if < 3, D = 1
   - Recursive depth analysis → how many levels to drill down?
   - D = max(1, floor(log(content_size / 100)))  # Rough heuristic
```

---

## Bit-Chain Lifecycle

```
Genesis (L created)
    ↓
Emergence (used, context grows, Lum rises)
    ↓
Peak (hot, frequently accessed, full detail)
    ↓
CHOICE POINT:
    ├→ Decay (if not accessed)
    │   ↓
    │ Crystallization (compressed, cold)
    │   ↓
    │ Storage (LUCA-adjacent, essence only)
    │
    └→ Re-ignition (if accessed again)
        ↓
        Peak (Lum reheats, context expands)
        ↓
        (cycle repeats)

Deletion: Bit-chain can be "retired" but not destroyed (kept as crystallized essence)
```

---

## Entanglement Detection

### Algorithm: Find Entangled Pairs

```
For each bit-chain B:
  For each other bit-chain C where C != B:
    
    # Compute resonance factors
    realm_match = (B.realm == C.realm) ? 1.0 : 0.3
    lineage_delta = 1.0 / (1.0 + abs(B.lineage - C.lineage))
    polarity_resonance = 1.0 - abs(B.polarity - C.polarity) / 2.0
    
    # Harmonic similarity (if implemented)
    harmonic_sim = cosine_similarity(B.harmonic_signature, C.harmonic_signature)
    
    # Combined entanglement strength
    entanglement = (realm_match * 0.3 
                   + lineage_delta * 0.2 
                   + polarity_resonance * 0.25
                   + harmonic_sim * 0.25)
    
    # Threshold for significance
    if entanglement > 0.6:
      B.entangled_with[C.id] = entanglement
      C.entangled_with[B.id] = entanglement
```

---

## Open Questions for Bit-Chain Spec

1. **Granularity:** Is a bit-chain a character, a word, a line, a paragraph, a document?
2. **Mutability:** Can STAT7 coordinates change, or are they fixed at creation?
3. **Versioning:** If content changes, is it a new bit-chain or an update?
4. **Compression Format:** How is content stored at different Luminosity levels?
5. **Network Structure:** Is Adjacency a graph, a matrix, or something else?
6. **Querying:** How do you query "find me all bit-chains where R=system AND Lum > 0.5"?
7. **Entanglement Limit:** Can one bit-chain be entangled with thousands of others?

---

**Status:** Specification drafted, awaiting implementation validation
**Next:** `04-VALIDATION-EXPERIMENTS.md` - How to test this actually works