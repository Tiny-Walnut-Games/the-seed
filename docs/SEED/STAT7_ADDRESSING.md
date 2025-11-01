# STAT7 Addressing System: Complete Specification

Status: Production Implementation  
Phase: Phase 1 Doctrine (Locked)  

---

## Overview: What Is STAT7?

STAT7 (Space-Time Addressing Technology, 7 dimensions) is a multidimensional addressing space for data storage, retrieval, and narrative coordination across The Seed multiverse.

Key capabilities:
- Unique, collision-free addressing at scale (10,000+ entities)
- Geometric, multidimensional querying by properties
- Preservation of semantic relationships during retrieval
- Deterministic coordinate assignment through hybrid encoding
- Fractal scalability across domains and systems

---

## The 7 Dimensions of STAT7

### 1. Realm - Domain Classification
Which system/domain does this entity belong to?
Values: COMPANION, BADGE, SPONSOR_RING, ACHIEVEMENT, PATTERN, FACULTY, VOID

### 2. Lineage - Generation/Tier Progression
Ancestral or generational position (Integer >= 0)
- 0 = Genesis/original
- 1+ = Generations derived from genesis

### 3. Adjacency - Semantic Proximity Score
How functionally/semantically close is this entity? (Float 0.0 - 1.0)
- 0.0 = Isolated
- 1.0 = Core hub, densely connected

### 4. Horizon - Lifecycle Stage
Current lifecycle state of the entity
Values: GENESIS, EMERGENCE, PEAK, DECAY, CRYSTALLIZATION, ARCHIVED

### 5. Luminosity - Activity Level
How hot or actively used? (Integer 0-100)
- 0 = Dormant
- 100 = Peak activity

### 6. Polarity - Resonance/Affinity Type
Qualitative nature or resonance pattern
Values: LOGIC, CREATIVITY, ORDER, CHAOS, BALANCE, ACHIEVEMENT, CONTRIBUTION, COMMUNITY

### 7. Dimensionality - Fractal Depth Level
Detail/complexity level (Integer 1+)
- 1 = Point (atomic)
- 3 = Plane (2D surface)
- 5+ = Hyperdimensional

---

## Implementation References

Core: packages/com.twg.the-seed/seed/engine/stat7_entity.py
Specialized: stat7_companion.py, stat7_badge.py, stat7_rag_bridge.py

Validation: tests/test_stat7.py, stat7_experiments.py

---

Truth Status: Production-ready, validated through EXP-01 through EXP-10
