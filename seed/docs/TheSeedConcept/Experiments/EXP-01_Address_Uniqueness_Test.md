## EXP-01: Address Uniqueness Test

### Hypothesis
Every bit-chain in STAT7 coordinate space gets a unique address with zero collisions.

### Method
1. **Generate synthetic data:** 1000 random bit-chains with random STAT7 coordinates
2. **Compute address hashes:** Use SHA256(realm + lineage + adjacency + horizon + luminosity + polarity + dimensionality)
3. **Check for collisions:** Count unique hashes vs. total bit-chains
4. **Statistical check:** Run 10 iterations with different random seeds

### Test Data
```python
# Pseudocode
for iteration in range(10):
    bit_chains = generate_random_bitchains(count=1000)
    addresses = set()
    collisions = 0
    
    for bc in bit_chains:
        addr = compute_address(bc)
        if addr in addresses:
            collisions += 1
        addresses.add(addr)
    
    success_rate = (1000 - collisions) / 1000
    assert success_rate == 1.0, f"Collision rate: {collisions}/1000"
```

### Expected Result
✓ 100% unique addresses across all 10 iterations
✓ No hash collisions
✓ Address computation is deterministic (same input = same hash every time)

### Failure Handling
If collisions occur:
- Investigate which STAT7 dimensions are colliding
- Possibly add an 8th dimension for disambiguation
- Or increase hash space beyond SHA256
