# RAG Stress Test Suite

**Comprehensive validation of the RAG (Retrieval-Augmented Generation) system under realistic load conditions.**

## Overview

The RAG Stress Test Suite proves your RAG system is production-ready by stressing it across 7 critical dimensions:

| Dimension           | Focus                    | Tests                 | Data Scale           |
|---------------------|--------------------------|-----------------------|----------------------|
| **Embedding Scale** | Throughput & determinism | batch 100, 1K, 10K    | Warbler packs        |
| **Anchor Creation** | Index performance        | scale + deduplication | 100-10K items        |
| **Retrieval**       | Query latency & ranking  | semantic search       | 100-1K corpus        |
| **Caching**         | Hit rates & performance  | repeated queries      | 5-10 cycles          |
| **Concurrency**     | Thread safety            | 1, 4, 8 threads       | 20 parallel queries  |
| **Memory Pressure** | GC stability             | 5 cycles × 128MB      | Quality preservation |
| **Soak**            | Sustained operation      | 5 minutes continuous  | ~200 QPS             |

## Test Data: Warbler Packs

The suite uses realistic content from three Warbler conversation packs:

### Core Pack (8 templates)
- Greetings, farewells, help requests, commerce
- Example: *"Greeting formal: Professional greeting for officials and merchants"*

### Wisdom Scrolls Pack (8 templates)
- Development wisdom, debugging proverbs, documentation philosophy
- Example: *"Refactoring is not admitting failure; it's evolution of understanding"*

### Faction Politics Pack (8 templates)
- Political intrigue, diplomacy, betrayal, alliance
- Example: *"Diplomatic overtures for formal political cooperation between powers"*

**Total:** 24 distinct content templates, combined into 100/1K/10K synthetic documents with variations.

## Running the Tests

### Quick Mode (30 seconds)
```bash
python scripts/run_rag_stress_test.py --quick

# Or via pytest
pytest tests/stress/test_rag_stress_suite.py --quick -v -s
```

**Tests:**
1. Embedding generation at 100 items
2. Anchor creation at 500 items
3. Retrieval performance at 500 items

### Full Mode (5-10 minutes)
```bash
python scripts/run_rag_stress_test.py --full

# Or default (full is default)
python scripts/run_rag_stress_test.py
```

**Tests:**
1. Embedding similarity consistency
2. Anchor deduplication accuracy
3. Retrieval ranking quality
4. Cache hit rate on repeated queries
5. Soak test (sustained 5-minute load)

### Specific Tests via pytest
```bash
# Run single test
pytest tests/stress/test_rag_stress_suite.py::TestRAGStress::test_embedding_generation_scale -v

# Run with output
pytest tests/stress/test_rag_stress_suite.py -v -s

# Run specific scale
pytest tests/stress/test_rag_stress_suite.py::TestRAGStress::test_retrieval_latency_scale -v -k "10000"

# Parametrized test: all batch sizes
pytest tests/stress/test_rag_stress_suite.py::TestRAGStress::test_embedding_generation_scale -v
```

## Test Details

### 1. Embedding Scale Tests

**Purpose:** Verify embeddings generate consistently at all scales without performance degradation.

**What's tested:**
- ✅ Batch embedding latency (ms per item)
- ✅ Throughput (items/sec)
- ✅ Determinism (repeated embeddings match exactly)
- ✅ All dimensions present (128-dim for LocalEmbeddingProvider)

**Expected output:**
```
[TEST] Embedding Generation at Scale: 1000 items
✅ Generated 1000 embeddings in 0.45s (0.45ms per item)
   Total throughput: 2222 items/sec
✅ Determinism verified: repeated embeddings match exactly
```

**Healthy metrics:**
- Per-item latency: < 2ms
- Throughput: > 500 items/sec
- Determinism: 100% match

### 2. Anchor Creation Tests

**Purpose:** Prove semantic anchors create efficiently with full provenance tracking.

**What's tested:**
- ✅ Creation latency distribution
- ✅ Throughput across scales
- ✅ Uniqueness of anchor IDs
- ✅ Deduplication of similar content

**Expected output:**
```
[TEST] Anchor Creation at Scale: 1000 items
✅ Created 1000 anchors
   Latency: min=0.25ms, mean=0.80ms, p95=1.50ms, max=3.20ms
   Throughput: 1250 anchors/sec
✅ Anchor uniqueness verified
```

**Healthy metrics:**
- Mean latency: < 2ms per anchor
- Throughput: > 500 anchors/sec
- Deduplication: Similar texts consolidate

### 3. Retrieval Performance Tests

**Purpose:** Validate query latency and ranking quality at scale.

**What's tested:**
- ✅ Query latency percentiles
- ✅ Result ranking order
- ✅ Score monotonicity (highest first)
- ✅ Relevance meaningfulness

**Expected output:**
```
[TEST] Retrieval Latency at Scale: 1000 items
✅ Indexed 1000 documents
   Query: 'development wisdom and understanding' → 5 results in 12.45ms
   Query: 'debugging and troubleshooting' → 5 results in 11.80ms
✅ Query latencies: mean=12.10ms, p95=15.20ms, max=18.50ms
```

**Healthy metrics:**
- Query latency: < 20ms median
- P95 latency: < 25ms
- Ranking: monotonically decreasing scores

### 4. Cache Performance Tests

**Purpose:** Prove caching significantly improves repeated query performance.

**What's tested:**
- ✅ Cache hit rate on identical queries
- ✅ Latency improvement (first vs repeated)
- ✅ Cache persistence across operations

**Expected output:**
```
[TEST] Cache Hit Rate on Repeated Queries
✅ Performed 10 repeated queries
   Cache hits: 9, misses: 1, hit rate: 90.0%
   Latency: first=45.20ms, subsequent=2.15ms
```

**Healthy metrics:**
- Hit rate: > 80% after first query
- Speedup: > 10x for cached queries
- TTL behavior: consistent across cycles

### 5. Concurrency Tests

**Purpose:** Verify thread-safe concurrent query execution.

**What's tested:**
- ✅ Multiple threads querying simultaneously
- ✅ No race conditions
- ✅ Result consistency
- ✅ Throughput improvement

**Expected output:**
```
[TEST] Concurrent Retrieval (4 threads)
✅ Executed 20 concurrent queries in 1.25s
   Average throughput: 16.0 queries/sec
   Result consistency: all queries returned 5 results
```

**Healthy metrics:**
- No exceptions or race conditions
- Throughput scales with thread count
- Result consistency maintained

### 6. Memory Pressure Tests

**Purpose:** Ensure system stability under GC/memory pressure.

**What's tested:**
- ✅ Retrieval quality preservation
- ✅ No memory leaks
- ✅ GC doesn't corrupt state
- ✅ Consistent results after GC

**Expected output:**
```
[TEST] GC Pressure Stability
   Cycle 1: quality=0.7850
   Cycle 2: quality=0.7855
   Cycle 3: quality=0.7851
   Cycle 4: quality=0.7849
   Cycle 5: quality=0.7852
✅ Quality remained stable: baseline=0.7850, mean=0.7851
```

**Healthy metrics:**
- Quality variance: < 0.01
- No errors after GC
- Consistent performance

### 7. Soak Test

**Purpose:** Prove system remains stable under sustained load.

**What's tested:**
- ✅ 5-minute continuous operation
- ✅ No degradation over time
- ✅ No memory leaks (sustained ~200 QPS)
- ✅ Zero errors

**Expected output:**
```
[TEST] Soak Test (5 minutes)
✅ Indexed 1000 documents
   0.0min: 0 queries, 0 errors
   0.8min: 50 queries, 0 errors
   1.7min: 100 queries, 0 errors
   2.5min: 150 queries, 0 errors
   3.3min: 200 queries, 0 errors
   4.2min: 250 queries, 0 errors
✅ Soak test complete: 258 queries in 300s
   Throughput: 0.9 queries/sec
   Latency: mean=12.45ms, p95=18.20ms
   Errors: 0
✅ Stability verified: no errors during sustained load
```

**Healthy metrics:**
- Total queries: > 100 in 5 minutes
- Errors: 0
- Latency: stable (no increase over time)
- Memory: stable (no leak pattern)

## Interpreting Results

### Success Criteria

All tests pass when:

| Metric                     | Threshold               | Status |
|----------------------------|-------------------------|--------|
| Embedding throughput       | > 500 items/sec         | ✅      |
| Anchor creation throughput | > 500 anchors/sec       | ✅      |
| Query latency (p95)        | < 25ms                  | ✅      |
| Cache hit rate             | > 80%                   | ✅      |
| Concurrent queries         | no errors               | ✅      |
| Memory stability           | < 0.01 quality variance | ✅      |
| Soak errors                | 0                       | ✅      |

### Warning Signs

⚠️ **Performance Degradation**
- Latency increases linearly with scale
- Throughput drops at 10K items
- → Check: cache efficiency, embedding provider, index structure

⚠️ **Cache Issues**
- Hit rate < 50%
- No speedup for repeated queries
- → Check: query normalization, cache configuration, TTL settings

⚠️ **Concurrency Errors**
- Race conditions in threaded test
- Inconsistent results
- → Check: thread-safe data structures, locking mechanisms

⚠️ **Memory Instability**
- Quality scores drift under GC pressure
- Errors increase over time
- → Check: memory management, object pooling, GC tuning

⚠️ **Soak Failures**
- Errors during sustained load
- Latency increase over time
- → Check: resource leaks, unbounded queues, timeout issues

## Performance Baseline

Typical results from LocalEmbeddingProvider on modern hardware:

```
Embedding Scale (1000 items):
  - Latency: 0.4-0.8ms per item
  - Throughput: 1200-2500 items/sec
  - Determinism: 100% match

Anchor Creation (1000 items):
  - Latency: 0.3-1.5ms per anchor
  - Throughput: 600-1500 anchors/sec
  - Deduplication: ~15-20% consolidation

Retrieval (1000-item corpus):
  - Query latency: 10-20ms
  - P95 latency: 15-25ms
  - Ranking: monotonic 100% of time

Cache Performance:
  - Hit rate: 90-95% after first query
  - Speedup: 10-20x for cached queries
  - TTL: 300 seconds default

Concurrency (8 threads):
  - Throughput: 15-30 queries/sec
  - No errors
  - Result consistency: 100%

Soak (5 minutes, ~200 QPS):
  - Total queries: 200-300
  - Error rate: 0%
  - Latency stability: ±5% variance
```

## Integration with CI/CD

### GitHub Actions
```yaml
- name: RAG Stress Test
  run: python scripts/run_rag_stress_test.py --quick
```

### Local Pre-commit
```bash
#!/bin/bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q "seed/engine/"; then
    echo "Running RAG stress test..."
    python scripts/run_rag_stress_test.py --quick || exit 1
fi
```

## Troubleshooting

### Import Errors
```
❌ Import failed: No module named 'seed.engine.embeddings'
```
**Solution:** Ensure RAG components are built:
```bash
cd seed/engine
python -m pytest tests/  # Build components
```

### Memory Issues
```
RuntimeError: Cannot allocate 256MB for pressure test
```
**Solution:** Reduce pressure in test config:
```python
force_memory_pressure_kb(64_000)  # 64MB instead of 256MB
```

### Timeout on Soak Test
```
Test timeout after 600 seconds
```
**Solution:** Reduce soak duration or extend timeout:
```python
SOAK_DURATION_SECONDS = 60 * 2  # 2 minutes instead of 5
```

## Next Steps

### After Tests Pass ✅
1. **Record baseline** - Save current metrics as reference
2. **Integrate to CI** - Add to GitHub Actions workflow
3. **Monitor regression** - Track metrics over time
4. **Document findings** - Update VALIDATION-RESULTS.md

### Performance Optimization
If metrics are below threshold:
1. Profile embeddings: `test_embedding_generation_scale`
2. Profile retrieval: `test_retrieval_latency_scale`
3. Analyze cache: `test_cache_hit_rate_repeated_queries`
4. Stress concurrency: `test_concurrent_retrieval_safety`

### Extended Testing
For production readiness:
1. Run full soak for 1 hour
2. Test with 100K items
3. Add network latency simulation
4. Test with external embedding service

## References

- **EXP-08:** See `tests/test_exp08_rag_integration.py` for end-to-end validation
- **STAT7 Tests:** See `tests/stress/test_stat7_reproducibility.py` for similar pattern
- **RAG System:** See `seed/engine/` for implementation details
- **Warbler Packs:** See `packs/` for content sources

## Related Documentation

- [RAG System Integration Guide](rag-integration-guide.md)
- [Validation Experiments](04-VALIDATION-EXPERIMENTS.md)
- [Performance Benchmarks](performance-benchmarks.md)

---

**Status:** Production stress test suite  
**Last Updated:** 2025-01-DD  
**Maintained by:** The Seed Project Team  
**License:** MIT
