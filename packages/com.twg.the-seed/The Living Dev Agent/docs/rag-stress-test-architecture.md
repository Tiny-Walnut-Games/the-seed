# RAG Stress Test Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   RAG STRESS TEST SUITE                     │
│                (test_rag_stress_suite.py)                   │
└────────────┬────────────────────────────────────────────────┘
             │
        ┌────┴──────┬──────────┬──────────┬──────────┬─────────┐
        │            │          │          │          │         │
    [1] │        [2] │      [3] │      [4] │      [5] │     [6] │ [7]
    EMB │      ANCHOR│ RETRIEVAL│  CACHE  │CONCURRENT│ MEMORY  │SOAK
    SCALE          CREATION    PERF      HIT RATE  SAFETY    PRESSURE
        │            │          │          │          │         │
        └────┬───────┴──────────┴──────────┴──────────┴─────────┘
             │
    ┌────────▼──────────────────────────────────────────┐
    │       WARBLER PACK TEST DATA (24 templates)       │
    ├──────────────────────────────────────────────────┤
    │ • Core Pack (8): greetings, farewells, help     │
    │ • Wisdom Scrolls (8): wisdom, debugging, docs   │
    │ • Faction Politics (8): diplomacy, intrigue     │
    ├──────────────────────────────────────────────────┤
    │ → Synthetic Documents: 100 / 1,000 / 10,000     │
    │ → Variations: unique IDs, timestamps, metadata  │
    │ → Total corpus: 24K+ test scenarios             │
    └────────▼──────────────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────────────────────────┐
    │              RAG SYSTEM UNDER TEST (seed/engine/)             │
    ├────────┬────────┬──────────────┬──────────────────────────────┤
    │ Emb.   │ Anchors│ Retrieval    │ Cache                        │
    │Provider│ Graph  │ API          │ Layer                        │
    ├────────┼────────┼──────────────┼──────────────────────────────┤
    │LocalEMB│SemanticA│RetrievalAPI│Query Cache                    │
    │        │nchorGrph│w/similarity │(TTL: 300s)                   │
    │        │         │search       │                              │
    │        │         │+ temporal   │                              │
    │        │         │+ caching    │                              │
    └────────┴────────┴──────────────┴──────────────────────────────┘
```

## Test Flow

### Test 1: Embedding Scale
```
generate_synthetic_documents(WARBLER_ALL_CONTENT, batch_size)
  ↓
embedding_provider.embed_batch(texts)  [MEASURE]
  ↓
[VERIFY]
  • Length matches input count
  • All are float vectors
  • Repeated calls produce identical results
  ↓
ASSERT: throughput > 500 items/sec
```

### Test 2: Anchor Creation
```
generate_synthetic_documents(WARBLER_ALL_CONTENT, batch_size)
  ↓
for doc in documents:
  anchor_graph.create_or_update_anchor(...)  [MEASURE LATENCY]
    ↓
    [COLLECT] min, max, mean, p95, p99 latencies
  ↓
[VERIFY]
  • All anchor_ids are unique
  • Provenance is tracked
  • Similar content consolidates
  ↓
ASSERT: throughput > 500 anchors/sec
```

### Test 3: Retrieval
```
index 100/1000/10000 documents
  ↓
for each query in ["wisdom", "debugging", "politics", ...]:
  retrieval_api.retrieve_context(query)  [MEASURE]
    ↓
    [COLLECT] result count, latency
  ↓
[VERIFY]
  • Results returned
  • Scores in descending order (monotonic)
  • Relevance makes semantic sense
  ↓
ASSERT: p95 latency < 25ms
```

### Test 4: Cache
```
Create RetrievalAPI with cache (TTL=300s)
  ↓
Query 1: retrieval_api.retrieve_context(Q)  [CACHE MISS]
  ↓
Query 2-10: retrieval_api.retrieve_context(Q)  [MEASURE]
  ↓
[VERIFY]
  • First query: ~50ms (uncached)
  • Queries 2-10: ~2-5ms (cached, 10x faster)
  • Cache hit rate: 90% (9/10)
  ↓
ASSERT: hit_rate > 80% AND speedup > 10x
```

### Test 5: Concurrency
```
ThreadPoolExecutor(max_workers=1|4|8)
  ↓
submit 20 concurrent queries
  ↓
[COLLECT] results in order
  ↓
[VERIFY]
  • No exceptions
  • All queries completed
  • Results consistent
  • Throughput scaled (n threads ≈ n× faster)
  ↓
ASSERT: no errors AND consistency 100%
```

### Test 6: Memory Pressure
```
Query baseline: retrieval_api.retrieve_context(Q) → quality_score
  ↓
for cycle in 1..5:
  force_memory_pressure_kb(128MB)  [GC PRESSURE]
    ↓
    Query again: retrieve_context(Q) → quality_score_i
    ↓
[VERIFY]
  • All quality scores within ±0.01 of baseline
  • No errors thrown
  • Results still sensible
  ↓
ASSERT: max_variance < 0.01 AND errors == 0
```

### Test 7: Soak Test
```
index 1000 documents
  ↓
start_time = now()
  ↓
while time_elapsed < 300 seconds:
  pick random query
  retrieve_context(query)  [MEASURE + COUNT]
  collect_metrics()
  ↓
[VERIFY]
  • Zero errors in 5 minutes
  • Latency doesn't increase over time
  • ~200-250 queries completed
  • Memory stable (no leak pattern)
  ↓
ASSERT: errors == 0 AND latency_stable AND memory_stable
```

## Metrics Collection

### Per-Test Metrics

| Test | Metrics | Format |
|------|---------|--------|
| Embedding | Throughput (items/sec), latency/item (ms), determinism % | Scalar |
| Anchor | Throughput (anchors/sec), latency percentiles, uniqueness % | Distribution |
| Retrieval | Latency percentiles, ranking correctness %, relevance scores | Distribution |
| Cache | Hit rate %, speedup factor, first vs repeat latency | Scalar |
| Concurrent | Queries completed, error rate %, latency by thread count | Scalar |
| Memory | Quality variance, error count, GC cycle count | Scalar |
| Soak | Total queries, error rate %, latency over time trend | Time series |

### Latency Metrics Computed
```python
latencies_ms = [measured times]
metrics = LatencyMetrics(
    min_ms = min(latencies_ms),
    max_ms = max(latencies_ms),
    mean_ms = statistics.mean(latencies_ms),
    median_ms = statistics.median(latencies_ms),
    p95_ms = sorted_latencies[int(n * 0.95)],
    p99_ms = sorted_latencies[int(n * 0.99)],
)
```

## Data Generation

### Synthetic Document Creation
```python
def generate_synthetic_documents(base_content, scale):
    """Create 'scale' documents from 'base_content' templates"""
    docs = []
    for i in range(scale):
        base_idx = i % len(base_content)
        variation = f"[Context {i}] {base_content[base_idx]} (instance {i})"
        
        doc = {
            "doc_id": f"doc-{i:06d}",
            "content": variation,
            "source": f"pack-{base_idx % 3}",
            "category": ["core", "wisdom", "politics"][base_idx % 3],
            "timestamp": time.time() - (scale - i) * 0.1,
        }
        docs.append(doc)
    return docs
```

### Content Distribution
```
100 documents:
├── 33 from Core pack (rotated through 8 templates)
├── 33 from Wisdom Scrolls pack
└── 34 from Faction Politics pack

1,000 documents:
├── 333 from Core pack (~41 per template)
├── 333 from Wisdom Scrolls pack
└── 334 from Faction Politics pack

10,000 documents:
├── 3,333 from Core pack (~416 per template)
├── 3,333 from Wisdom Scrolls pack
└── 3,334 from Faction Politics pack
```

## Test Execution Modes

### Quick Mode (CLI)
```bash
python scripts/run_rag_stress_test.py --quick
```
- Duration: ~30 seconds
- Tests: 3 (embedding scale, anchor creation, retrieval)
- Scale: 100-500 items
- Use: Fast feedback loop, pre-commit verification

### Full Mode (CLI)
```bash
python scripts/run_rag_stress_test.py --full
```
- Duration: ~5-10 minutes
- Tests: 7 (all dimensions)
- Scale: 100-1000 items, 5-minute soak
- Use: Pre-release validation, nightly CI

### Pytest Mode (Selective)
```bash
pytest tests/stress/test_rag_stress_suite.py -v -s -k "embedding"
```
- Duration: Per-test configurable
- Tests: Selectable by name, parameter
- Scale: Parametrized (100, 1K, 10K)
- Use: Development, debugging, benchmarking

## Exit Codes & Signals

| Code | Meaning | Typical Cause |
|------|---------|--------------|
| `0` | All tests passed | System healthy ✅ |
| `1` | Test failed | See assertion error |
| `TIMEOUT` | Test exceeded limit | Performance degradation |
| `SKIP` | Test skipped | RAG components unavailable |

## Performance Expectations

### Hardware Profile
Tested on typical development machine:
- CPU: 4-8 cores
- RAM: 8-16GB
- Storage: SSD

### Expected Latencies

| Operation | Count | Expected | Status |
|-----------|-------|----------|--------|
| Embed item | 1 | 0.5-2ms | ✅ Fast |
| Embed batch | 1,000 | 0.4-0.8ms/item | ✅ Linear |
| Create anchor | 1 | 0.5-2ms | ✅ Fast |
| Query search | 1 | 10-20ms | ✅ Good |
| Query (cached) | 1 | 1-5ms | ✅ Very fast |
| GC cycle | - | Transparent | ✅ No impact |
| Concurrent (8T) | 20 | 1-2s total | ✅ Parallel |

## Error Handling

Tests verify error conditions:

### Expected Errors (Handled)
- ✅ Import missing → pytest.skip()
- ✅ Embedding errors → Re-raised with context
- ✅ Query errors → Collected and reported

### Unexpected Errors (Failures)
- ❌ Race condition → Test fails
- ❌ Memory leak → Quality degrades
- ❌ Soak timeout → Test fails
- ❌ Cache inconsistency → Results mismatch

## Integration Points

### With EXP-08
```
EXP-08 (test_exp08_rag_integration.py)
  - End-to-end validation
  - Basic functionality proof
  - 8 individual tests

RAG Stress Suite
  - Performance validation
  - Scale testing
  - 7 stress dimensions
```

### With STAT7 Tests
```
STAT7 Reproducibility (test_stat7_reproducibility.py)
  - Determinism under stress
  - Reproducibility proof
  - 7 scenarios

RAG Stress Suite
  - Similar pattern
  - Different subject (RAG vs STAT7)
  - Reusable test architecture
```

### With CI/CD
```
GitHub Actions
  ↓
pytest test_rag_stress_suite.py --quick  (5 min)
  ↓
if passes:
  → Merge allowed ✅
else:
  → Failure reported ❌
```

---

**Architecture Version:** 1.0  
**Last Updated:** 2025-01-DD  
**Test Framework:** pytest + custom harness  
**Data Source:** Warbler packs (24 templates)