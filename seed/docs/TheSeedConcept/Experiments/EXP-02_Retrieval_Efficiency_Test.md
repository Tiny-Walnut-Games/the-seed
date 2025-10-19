## EXP-02: Retrieval Efficiency Test

### Hypothesis
Retrieving a bit-chain by STAT7 address is fast (< 1ms) even at large scales.

### Method
1. **Build index:** Create 10,000 bit-chains with indexed STAT7 coordinates
2. **Random retrieval:** Query random addresses 1000 times
3. **Measure latency:** Track mean, median, p95, p99 retrieval times
4. **Benchmark:** Compare against linear search baseline

### Test Conditions
```
Scale levels:
- 1K bit-chains → target < 0.1ms per query
- 10K bit-chains → target < 0.5ms per query
- 100K bit-chains → target < 2ms per query
```

### Expected Result
✓ Retrieval times scale logarithmically or better
✓ No linear degradation as dataset grows
✓ Index-based retrieval beats linear search by 10x+

### Failure Handling
If retrieval is too slow:
- Use B-tree or R-tree spatial indexing
- Shard by Realm to reduce search space
- Implement hierarchical index (Lineage-based bucketing)
