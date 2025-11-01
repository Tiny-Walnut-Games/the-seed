# 🔄 Phase 6D: Reproducibility & Export — Development Handoff

**Handoff Date**: 2025-10-31  
**Prepared For**: Next Development Session  
**Status**: Ready for TDD Implementation  
**Scope**: Seed storage, universe JSON export, same-seed replay capability

---

## 📋 Executive Summary

Phase 6D is the **reproducibility wrapper** that enables deterministic universe regeneration. It captures the universe state (including Phase 6A tier assignments) into a portable JSON export, then replays it identically given the same seed.

### Key Deliverables
- ✅ Universe seed captured in REST API response headers
- ✅ Tier structure JSON export (all realms + themes + anchors)
- ✅ Same-seed replay with tier preservation
- ✅ Audit trail for tier assignments
- ✅ Cross-universe tier alignment metadata

### Dependencies (All Complete ✅)
- Phase 5: UniverseBigBang, TorusCycleEngine, STAT7 addressing
- Phase 6A: HierarchicalUniverseAdapter, TierRegistry, TierPersonalityGenerator
- Phase 6B: Phase6BAPIServer, REST endpoints for queries
- Phase 6C: NarrativeRenderer, audit log infrastructure

---

## 🎯 Architecture: What Needs to Be Built

### High-Level Flow

```
User Request:
  POST /api/universe/export?include_seed=true
  ↓
UniverseExporter (NEW)
  ├─ Extract seed from orchestrator
  ├─ Serialize all realms with tier metadata
  ├─ Collect enrichment audit trails
  ├─ Generate cross-universe alignment index
  └─ Return as JSON + seed in response header
  ↓
Response Headers:
  X-Universe-Seed: 42
  X-Universe-Hash: abc123...
  X-Tier-Depth: 2
  ↓
Response Body: { realms, entities, enrichments, tier_assignments, audit_trail }

Same-Seed Replay:
  GET /api/universe/replay?seed=42
  ↓
UniverseReplayer (NEW)
  ├─ Initialize UniverseBigBang with seed 42
  ├─ Run initialization with same spec
  ├─ Apply cached tier assignments
  ├─ Validate identity (hash match)
  └─ Return identical universe
  ↓
[User gets same NPCs, same locations, same enrichments]
```

---

## 📁 Files to Create / Modify

### New Files to Create

1. **`packages/com.twg.the-seed/seed/engine/phase6d_reproducibility.py`** (~200-250 LOC)
   - `UniverseExporter` class (serialize state)
   - `UniverseReplayer` class (replay from seed)
   - `UniverseSnapshot` dataclass (portable export format)
   - `TierAssignmentAudit` dataclass (track tier changes)

2. **`tests/test_phase6d_reproducibility.py`** (~300-400 LOC, TDD-first)
   - TestUniverseExporter (8-10 tests)
   - TestUniverseReplayer (8-10 tests)
   - TestCrossTierAlignment (4-6 tests)
   - TestAuditTrailReconstruction (4-6 tests)

### Files to Modify

3. **`phase6b_rest_api.py`** (add 3-4 new endpoints)
   - `POST /api/universe/export` → calls UniverseExporter
   - `GET /api/universe/replay` → calls UniverseReplayer
   - `GET /api/universe/snapshot/{snapshot_id}` → retrieve saved snapshots
   - `POST /api/universe/validate-seed` → verify determinism

4. **`phase6_orchestrator.py`** (add tracking)
   - Store `initialization_seed` as instance variable
   - Expose `get_universe_seed()` method
   - Cache tier assignments in registry (for replay)
   - Track orchestrator initialization timestamp

---

## 🧪 TDD: Test Cases to Write First

### TestUniverseExporter (8 tests)

```python
# 1. test_export_includes_seed
#    Assert: export["seed"] == original_seed
#    Assert: export["universe_id"] is unique

# 2. test_export_includes_all_realms
#    Assert: len(export["realms"]) == orchestrator.get_realms().count()
#    Assert: All realm IDs present with tier classification

# 3. test_export_includes_tier_metadata
#    Assert: export["tier_assignments"][realm_id].tier in [CELESTIAL, TERRAN, SUBTERRAN]
#    Assert: export["tier_assignments"][realm_id].theme in TierTheme enum

# 4. test_export_includes_enrichment_trails
#    Assert: export["enrichment_audit_trail"] contains timestamped entries
#    Assert: Audit trail is immutable (frozen/read-only)

# 5. test_export_computes_universe_hash
#    Assert: export["universe_hash"] is stable (same universe → same hash)
#    Assert: Hash includes seed, realm count, tier assignments

# 6. test_export_includes_semantic_anchors
#    Assert: export["semantic_anchors"][realm_id] contains all anchors
#    Assert: Sub-realm anchors inherited correctly

# 7. test_export_as_json_serializable
#    Assert: json.dumps(export) succeeds
#    Assert: datetime objects ISO-formatted
#    Assert: Enums serialized as strings

# 8. test_export_excludes_sensitive_data
#    Assert: No connection strings in export
#    Assert: No internal locks or async state
#    Assert: Only immutable, reproducible data
```

### TestUniverseReplayer (8 tests)

```python
# 1. test_replay_with_same_seed_identical_universe
#    Setup: export1 = await exporter.export(seed=42)
#    Act: universe2 = await replayer.replay_from_seed(42)
#    Assert: Hash matches, realm count matches, tier assignments match

# 2. test_replay_preserves_tier_assignments
#    Assert: Replayed realm tier == exported tier
#    Assert: Replayed theme == exported theme
#    Assert: Sub-realm count matches

# 3. test_replay_preserves_entity_personalities
#    Setup: Export includes NPC personality traits
#    Assert: Replayed NPCs have identical traits
#    Assert: Dialogue seeds match

# 4. test_replay_validates_seed_integrity
#    Act: await replayer.replay_from_seed(42)
#    Assert: Returned universe hash == expected (from export)
#    OR raises ReplayValidationError if mismatch

# 5. test_replay_rejects_nonexistent_seed
#    Act: await replayer.replay_from_seed(999999)
#    Assert: Raises UniverseNotFoundError or returns empty state

# 6. test_replay_runs_initialization_cycle
#    Assert: Replayed universe has enrichment history
#    Assert: Enrichment count == original (audit trail length)

# 7. test_replay_restores_orchestrator_state
#    Assert: orchestrator.initialization_seed == 42
#    Assert: orchestrator.tier_registry contains all tiers

# 8. test_replay_idempotent_multiple_calls
#    Setup: Call replay 3 times with same seed
#    Assert: All 3 universes have identical hashes
```

### TestCrossTierAlignment (5 tests)

```python
# 1. test_alignment_tracks_tier_transitions
#    Setup: Multiple realms with different tiers
#    Assert: Alignment index maps Celestial↔Terran↔Subterran connections
#    Assert: Transition rules preserved (can't jump tiers directly)

# 2. test_alignment_preserves_zoom_chain
#    Setup: Parent realm → sub-realm hierarchy
#    Assert: Exported alignment shows bitchain path
#    Assert: Replayed universe re-materializes same chain

# 3. test_alignment_enables_cross_realm_queries
#    Assert: export["tier_alignment"] supports queries like:
#    - "All realms in tier" (export["by_tier"]["CELESTIAL"])
#    - "All sub-realms of X" (export["by_parent_realm"]["tavern"])
#    - "All realms with anchor Y" (export["by_anchor"]["knowledge"])

# 4. test_alignment_hash_unique_per_seed
#    Setup: Export universes with seed 42, 43, 44
#    Assert: Three different alignment hashes

# 5. test_alignment_survives_tier_depth_expansion
#    Setup: Export with tier_depth=1
#    Modify: Create sub-realms (tier_depth=2)
#    Act: Re-export with same seed
#    Assert: Alignment index still valid (hierarchical)
```

### TestAuditTrailReconstruction (6 tests)

```python
# 1. test_audit_trail_captures_all_tier_assignments
#    Assert: export["audit_trail"] has entry for each realm tier assignment
#    Assert: Each entry timestamped

# 2. test_audit_trail_includes_admin_actions
#    Setup: Bob the Skeptic made governance decisions
#    Assert: export["governance_audit"] captures those decisions
#    Assert: Decisions preserved in replay

# 3. test_audit_trail_captures_enrichment_sequence
#    Assert: Enrichment sequence (dialogue→history→semantic) tracked
#    Assert: Order preserved (no reordering on export/import)

# 4. test_audit_trail_enables_lineage_queries
#    Assert: export["lineage"][npc_id] shows full enrichment path
#    Assert: Can trace NPC back to entity back to realm back to seed

# 5. test_audit_trail_immutable_in_export
#    Setup: Export with read-only flag
#    Act: Try to modify export["audit_trail"]
#    Assert: Raises error or returns copy (not mutable original)

# 6. test_audit_trail_validation_on_replay
#    Setup: Load export with corrupted audit trail
#    Act: await replayer.replay_from_seed(42)
#    Assert: Either refuses (AuditTrailValidationError) or warns
```

---

## 💾 Data Structures to Implement

### UniverseSnapshot (Portable Export Format)

```python
@dataclass
class UniverseSnapshot:
    """Complete, portable universe export for reproducibility."""
    
    # Core Identification
    seed: int                           # Original initialization seed
    universe_id: str                    # Unique identifier (seed + timestamp hash)
    universe_hash: str                  # Deterministic hash of entire state
    exported_at: str                    # ISO timestamp
    
    # Tier Structure
    tier_assignments: Dict[str, TierAssignmentRecord]  # realm_id → tier metadata
    tier_depth: int                     # Max sub-realm depth (0, 1, 2...)
    tier_themes: Dict[str, str]         # realm_id → TierTheme (serialized as string)
    
    # Realm & Entity Data
    realms: List[RealmExport]           # All realms with IDs, anchors, metadata
    entities: List[EntityExport]        # All entities (NPCs) with personality
    enrichments: List[EnrichmentExport] # All enrichment records (dialogue, history, semantic)
    
    # Cross-Tier Alignment Index
    tier_alignment: Dict[str, Any]      # Celestial↔Terran↔Subterran mappings
    parent_child_index: Dict[str, List[str]]  # realm_id → [sub_realm_ids]
    semantic_anchor_index: Dict[str, List[str]]  # anchor → [realm_ids]
    
    # Audit & Lineage
    audit_trail: List[AuditTrailEntry]  # Complete tier assignment history
    governance_audit: List[Dict]        # Bob the Skeptic decisions
    enrichment_lineage: Dict[str, List[str]]  # npc_id → [enrichment_ids in order]
    
    # Metadata for Validation
    orchestrator_config: Dict           # OrchestratorConfig settings (for replay)
    universe_specifications: Dict       # Realms, entity counts, enrichment config
    
    @property
    def is_deterministic(self) -> bool:
        """True if this snapshot can be replayed identically."""
        return self.seed is not None and self.universe_hash is not None

@dataclass
class TierAssignmentRecord:
    """Single tier assignment for a realm."""
    realm_id: str
    tier_classification: str            # "CELESTIAL" | "TERRAN" | "SUBTERRAN" (as string)
    tier_theme: str                     # "HEAVEN", "CITY_STATE", "HELL", etc.
    semantic_anchors: List[str]         # ["peaceful", "urban", ...]
    tier_depth: int                     # 0 (root), 1 (sub-realm), 2+ (nested)
    parent_realm_id: Optional[str]      # None for root realms
    assigned_at: str                    # ISO timestamp
    assigned_by: str                    # "orchestrator" | "admin_id" if manual

@dataclass
class EnrichmentExport:
    """Single enrichment record for export."""
    enrichment_id: str
    entity_id: str
    enrichment_type: str                # "dialogue" | "history" | "semantic_context"
    content: Dict                       # Full enrichment data (no references)
    created_at: str                     # ISO timestamp
    audit_depth: int                    # Nesting depth in audit trail
```

### Export/Replay Methods

```python
class UniverseExporter:
    """Serialize universe to portable JSON snapshot."""
    
    async def export(
        self,
        orchestrator: UniverseDemoOrchestrator,
        include_enrichments: bool = True,
        include_audit_trail: bool = True,
        include_governance: bool = True,
    ) -> UniverseSnapshot:
        """Export complete universe state."""
        # Implementation: gather all components, serialize, validate JSON
        pass
    
    async def export_to_file(
        self,
        orchestrator: UniverseDemoOrchestrator,
        filepath: str,
    ) -> UniverseSnapshot:
        """Export and save to JSON file."""
        pass
    
    def compute_universe_hash(self, snapshot: UniverseSnapshot) -> str:
        """Deterministic hash of snapshot for reproducibility validation."""
        # Hash should be identical for same seed + config
        pass

class UniverseReplayer:
    """Recreate universe from seed using cached snapshot."""
    
    async def replay_from_seed(
        self,
        seed: int,
        config: OrchestratorConfig,
        validate_hash: Optional[str] = None,  # Expected hash (raises if mismatch)
    ) -> UniverseDemoOrchestrator:
        """Recreate orchestrator with identical seed."""
        # Implementation: init orchestra with seed, run launch_demo(), restore cache
        pass
    
    async def load_from_file(self, filepath: str) -> UniverseSnapshot:
        """Load snapshot from JSON file."""
        pass
    
    async def validate_seed_integrity(
        self,
        original_snapshot: UniverseSnapshot,
        replayed_orchestrator: UniverseDemoOrchestrator,
    ) -> bool:
        """Verify replayed universe is identical to original."""
        # Implementation: compare hashes, counts, tier assignments
        pass
```

---

## 🔌 REST API Endpoints to Add (phase6b_rest_api.py)

### 1. Export Universe

```python
@router.post("/api/universe/export")
async def export_universe(
    include_enrichments: bool = Query(True),
    include_audit_trail: bool = Query(True),
    include_governance: bool = Query(True),
) -> Dict:
    """
    Export complete universe snapshot for reproducibility.
    
    Response headers:
    - X-Universe-Seed: Original seed used to initialize
    - X-Universe-Hash: Deterministic universe hash
    - X-Tier-Depth: Maximum sub-realm tier depth
    
    Response body: UniverseSnapshot (JSON-serializable dict)
    """
    exporter = UniverseExporter()
    snapshot = await exporter.export(
        orchestrator,
        include_enrichments=include_enrichments,
        include_audit_trail=include_audit_trail,
        include_governance=include_governance,
    )
    
    return JSONResponse(
        content=snapshot_to_dict(snapshot),
        headers={
            "X-Universe-Seed": str(snapshot.seed),
            "X-Universe-Hash": snapshot.universe_hash,
            "X-Tier-Depth": str(snapshot.tier_depth),
            "X-Export-Timestamp": snapshot.exported_at,
        }
    )
```

### 2. Replay with Same Seed

```python
@router.get("/api/universe/replay")
async def replay_universe(
    seed: int = Query(...),
    validate_hash: Optional[str] = Query(None),
) -> Dict:
    """
    Recreate universe with identical seed.
    
    If validate_hash provided, ensures replayed universe matches original.
    
    Returns: Metadata about replayed universe
    """
    replayer = UniverseReplayer()
    replayed_orchestrator = await replayer.replay_from_seed(
        seed,
        config=orchestrator.config,
        validate_hash=validate_hash,
    )
    
    return {
        "seed": seed,
        "universe_id": replayed_orchestrator.universe_id,
        "universe_hash": replayed_orchestrator.universe_hash,
        "realm_count": len(await replayed_orchestrator.get_realms()),
        "entity_count": len(await replayed_orchestrator.bridge.phase2_adapter.get_all_npcs()),
        "status": "replayed_successfully",
    }
```

### 3. Snapshot Management

```python
@router.post("/api/universe/snapshots")
async def save_snapshot(name: str = Query(...)) -> Dict:
    """Save current universe as named snapshot."""
    # Store snapshot with name, return snapshot_id
    pass

@router.get("/api/universe/snapshots/{snapshot_id}")
async def load_snapshot(snapshot_id: str) -> Dict:
    """Load previously saved snapshot."""
    pass

@router.get("/api/universe/snapshots")
async def list_snapshots() -> List[Dict]:
    """List all saved snapshots with metadata."""
    pass
```

### 4. Seed Validation

```python
@router.post("/api/universe/validate-seed")
async def validate_seed(seed: int, expected_hash: str) -> Dict:
    """
    Validate that seed produces expected universe hash.
    
    Use case: Verify reproducibility before replay.
    """
    replayer = UniverseReplayer()
    replayed = await replayer.replay_from_seed(seed, orchestrator.config)
    
    is_valid = replayed.universe_hash == expected_hash
    
    return {
        "seed": seed,
        "expected_hash": expected_hash,
        "actual_hash": replayed.universe_hash,
        "is_valid": is_valid,
        "status": "valid" if is_valid else "mismatch",
    }
```

---

## 🔧 Integration Points

### With Phase 6A (Orchestrator)

```python
# In phase6_orchestrator.py, UniverseDemoOrchestrator class:

class UniverseDemoOrchestrator:
    """..."""
    
    def __init__(self, config: OrchestratorConfig):
        self.initialization_seed: Optional[int] = None
        self.universe_hash: Optional[str] = None
        self.tier_registry_cache: Dict = {}
        # ... existing fields
    
    async def launch_demo(self, seed: Optional[int] = None):
        """Launch demo with optional seed."""
        if seed is not None:
            self.initialization_seed = seed
        else:
            self.initialization_seed = random.randint(0, 2**32 - 1)
        
        # Existing initialization...
        await self.universe.initialize_multiverse(...)
        # ... bridge setup, NPC registration, etc.
        
        # NEW: Cache tier registry for reproducibility
        self.tier_registry_cache = await self.tier_registry.export_structure()
        
        # NEW: Compute universe hash
        self.universe_hash = compute_universe_hash(
            seed=self.initialization_seed,
            realms=await self.get_realms(),
            entities=await self.get_entities(),
        )
    
    def get_universe_seed(self) -> Optional[int]:
        """Expose seed for export/replay."""
        return self.initialization_seed
    
    def get_universe_hash(self) -> Optional[str]:
        """Expose hash for validation."""
        return self.universe_hash
```

### With Phase 6C (Audit Governance)

```python
# Export includes governance audit trail:

snapshot.governance_audit = [
    {
        "decision_id": "gov_001",
        "decision_type": "tier_assignment_challenge",
        "admin_id": "bob_skeptic",
        "entity_id": realm_id,
        "timestamp": "...",
        "passed": True/False,
        "violations": [...],
    },
    # ... all governance decisions
]
```

---

## 📚 Design Decisions (Why This Approach)

### 1. **JSON Export Format (Not Binary)**
- **Why**: Human-readable for debugging, languge-agnostic for integration
- **Trade-off**: Slightly larger file size vs. portability
- **Validation**: All objects ISO-formatted, enum strings, no circular refs

### 2. **Deterministic Hash Includes Seed + Config**
- **Why**: Same seed with different config shouldn't replicate
- **How**: hash(seed + realm_count + tier_assignments + entity_count)
- **Result**: Can detect config mismatches before replay

### 3. **Separate Audit Trail for Governance**
- **Why**: Bob the Skeptic decisions are orthogonal to universe state
- **How**: governance_audit is list of validation records
- **Result**: Can audit replay without changing gameplay

### 4. **Caching Tier Assignments (Not Re-Computing)**
- **Why**: Tier assignments are deterministic but expensive (registry lookups)
- **How**: UniverseExporter caches tier_assignments at export time
- **Result**: Replay is fast (no re-classification needed)

---

## 🚀 Implementation Sequence (TDD)

### Step 1: Write All Tests (No Implementation)
- Create `tests/test_phase6d_reproducibility.py`
- Write all 30+ test cases (red)
- Commit: `git add tests/test_phase6d_reproducibility.py && git commit -m "Phase 6D: TDD - Test cases drafted (all failing)"`

### Step 2: Create Data Structures
- Create `phase6d_reproducibility.py`
- Implement dataclasses: `UniverseSnapshot`, `TierAssignmentRecord`, `EnrichmentExport`
- Implement: `UniverseExporter` class (empty methods)
- Implement: `UniverseReplayer` class (empty methods)
- Tests still fail (red)

### Step 3: Implement Exporter
- `UniverseExporter.export()` method → gather all data
- `UniverseExporter.compute_universe_hash()` → deterministic hash
- `UniverseExporter.export_to_file()` → JSON serialization
- Run tests: TestUniverseExporter should go green ✅
- Run tests: TestAuditTrailReconstruction should go green ✅

### Step 4: Implement Replayer
- `UniverseReplayer.replay_from_seed()` → create identical universe
- `UniverseReplayer.validate_seed_integrity()` → compare hashes
- `UniverseReplayer.load_from_file()` → JSON deserialization
- Run tests: TestUniverseReplayer should go green ✅
- Run tests: TestCrossTierAlignment should go green ✅

### Step 5: Add REST API Endpoints
- Add to `phase6b_rest_api.py`: `/api/universe/export`
- Add to `phase6b_rest_api.py`: `/api/universe/replay`
- Add to `phase6b_rest_api.py`: `/api/universe/snapshots`
- Add to `phase6b_rest_api.py`: `/api/universe/validate-seed`
- Run integration tests

### Step 6: Update Orchestrator
- Modify `phase6_orchestrator.py`: Store seed, compute hash
- Expose methods: `get_universe_seed()`, `get_universe_hash()`
- Update tests that depend on orchestrator

### Step 7: Validation & Documentation
- Run full test suite: `pytest tests/test_phase6d_reproducibility.py -v`
- Generate coverage report
- Create user-facing documentation (how to export/replay)

---

## 📊 Success Criteria

### Automated Tests (All Green ✅)
```
test_phase6d_reproducibility.py
├─ TestUniverseExporter: 8/8 PASS
├─ TestUniverseReplayer: 8/8 PASS
├─ TestCrossTierAlignment: 5/5 PASS
└─ TestAuditTrailReconstruction: 6/6 PASS
────────────────────────────────────
TOTAL: 27+ PASS (100% coverage)
```

### Manual Validation
1. **Determinism**: Export seed X, replay seed X, hash matches ✅
2. **Different Seeds Differ**: Export seed X, replay seed Y, hash differs ✅
3. **Tier Preservation**: Replayed universe has identical tier structure ✅
4. **Enrichment Lineage**: All NPC enrichments preserved ✅
5. **File Size Reasonable**: Export ~1MB for typical universe ✅
6. **JSON Valid**: Can load export in any JSON parser ✅
7. **Circular Reference Free**: No infinite loops in serialization ✅

---

## ⚠️ Known Challenges & Mitigations

### Challenge 1: Random State (UniverseBigBang Uses Random)
- **Problem**: Even with same seed, random number generator state might diverge
- **Mitigation**: UniverseBigBang already seeds its own RNG; capture that seed
- **Validation**: Add test that compares entity IDs, coordinates (not just counts)

### Challenge 2: Async Ordering (Phase 5 Uses Concurrent Tasks)
- **Problem**: Concurrent tasks might execute in different order on replay
- **Mitigation**: TorusCycleEngine should be deterministic for same seed; if not, refactor
- **Validation**: Test enrichment audit trail order matches exactly

### Challenge 3: Tier Assignment Mutations (If Admins Manually Override Tiers)
- **Problem**: If tier_registry is mutable during replay, state could diverge
- **Mitigation**: Export tier_assignments as snapshot; restore exactly on replay
- **Validation**: Bob the Skeptic audit trail should show no override on replay-from-seed

### Challenge 4: File Size Growth (Large Universes = Large Exports)
- **Problem**: Exporting 1000 NPCs might create multi-MB JSON
- **Mitigation**: Implement compression option (gzip), streaming export
- **Timeline**: Phase 6D v1 supports full export; v2 adds compression

---

## 📞 Handoff Checklist

Before starting Phase 6D in next session:

- [ ] Review this document (5 min)
- [ ] Check all Phase 6A-6C tests still pass (`pytest tests/test_phase6*.py`)
- [ ] Review Phase 5 random seed handling (in `UniverseBigBang.__init__`)
- [ ] Verify Phase 6A tier_registry is queryable and exportable
- [ ] Decide: JSON only, or JSON + binary compression?
- [ ] Decide: Store snapshots in memory (fast), file (persistent), or both?
- [ ] Review `OrchestratorConfig` to understand all initialization parameters
- [ ] Set up IDE debug configuration for replay testing

---

## 🎓 Quick Reference: Key Files & Methods to Know

| File | Key Class/Method | Purpose |
|------|------------------|---------|
| `phase6_orchestrator.py` | `UniverseDemoOrchestrator.launch_demo()` | Initialize universe with seed |
| `phase6a_hierarchical_realms.py` | `HierarchicalUniverseAdapter.export_tier_structure()` | Export tier assignments |
| `phase6_orchestrator.py` | `OrchestratorConfig` | Initialization parameters |
| `phase6b_rest_api.py` | `Phase6BAPIServer` | REST API server (add endpoints here) |
| `phase6c_narrative_audit.py` | `AuditLogEntry` | Governance audit record schema |

---

## 🔗 Next Steps After Phase 6D

### Phase 7 (Hypothetical Future)
- **Distributed Universe Sync**: Multiple servers share same universe
- **Seed-Based Tournament Brackets**: Generate tournament universes with linked seeds
- **AI-Guided World Exploration**: AI learns optimal dialogue strategies per seed

### Documented Limitation (Future Enhancement)
- Cross-version reproducibility: Seed X on codebase v1 ≠ v2 (schema evolution)
- Solution: Version-aware snapshot format with migration logic

---

## ✨ The Scroll is Prepared

**All context preserved, all design decisions documented, all test cases ready.**

*The path to reproducibility is clear. May the next session find swift success.*

---

**Prepared by**: Companion Scribe  
**Inscribed on**: 2025-10-31  
**Status**: Ready for TDD Implementation  
**Estimated Effort**: 6-8 hours (comfortable), 4-5 hours (aggressive)