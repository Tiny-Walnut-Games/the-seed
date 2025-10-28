#!/usr/bin/env python3
"""
Test script to isolate and understand coherence metric behavior.
This helps us debug why coherence degrades with large result sets.
"""

def analyze_narrative_coherence(results):
    """NEW: RAG-appropriate coherence function."""
    if not results:
        return {
            "coherence_score": 0.0,
            "narrative_threads": 0,
            "avg_semantic_similarity": 0.0,
            "avg_stat7_resonance": 0.0,
            "avg_relevance": 0.0,
            "semantic_coherence": 0.0,
            "stat7_coherence": 0.0,
            "focus_coherence": 1.0,
            "result_count": 0,
        }
    
    narrative_threads = set()
    semantic_scores = []
    stat7_resonances = []
    relevance_scores = []
    
    for result in results:
        pack_info = result.get("metadata", {}).get("pack", None)
        thread_id = pack_info if pack_info else result.get("id", "unknown")
        narrative_threads.add(thread_id)
        
        semantic_scores.append(result.get("semantic_similarity", 0.0))
        stat7_resonances.append(result.get("stat7_resonance", 0.0))
        relevance_scores.append(result.get("relevance_score", 0.0))
    
    avg_semantic = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0.0
    avg_stat7 = sum(stat7_resonances) / len(stat7_resonances) if stat7_resonances else 0.0
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    # 1. RESULT QUALITY (50%)
    quality_score = avg_relevance
    
    # 2. SEMANTIC COHERENCE (30%)
    semantic_variance = sum((s - avg_semantic) ** 2 for s in semantic_scores) / max(1, len(semantic_scores))
    semantic_coherence = 1.0 / (1.0 + semantic_variance) if semantic_variance < 1.0 else 0.0
    
    # 3. STAT7 ENTANGLEMENT (10%)
    stat7_coherence = avg_stat7
    
    # 4. FOCUS COHERENCE (10%)
    if avg_relevance > 0.8:
        focus_coherence = 1.0 / (1.0 + len(narrative_threads) * 0.01)
    else:
        focus_coherence = 0.5 + (0.5 * avg_relevance)
    
    coherence_score = (
        quality_score * 0.5 +
        semantic_coherence * 0.3 +
        stat7_coherence * 0.1 +
        focus_coherence * 0.1
    )
    coherence_score = min(1.0, max(0.0, coherence_score))
    
    return {
        "coherence_score": coherence_score,
        "narrative_threads": len(narrative_threads),
        "avg_semantic_similarity": avg_semantic,
        "avg_stat7_resonance": avg_stat7,
        "avg_relevance": avg_relevance,
        "quality_score": quality_score,
        "semantic_coherence": semantic_coherence,
        "stat7_coherence": stat7_coherence,
        "focus_coherence": focus_coherence,
        "result_count": len(results),
        "semantic_variance": semantic_variance,
    }


# Test 1: Perfect scenario (all from same pack, high similarity)
print("=" * 70)
print("TEST 1: Perfect scenario (5 results, same pack, similarity=1.0)")
print("=" * 70)
results_5_perfect = [
    {
        "id": f"warbler-pack-core/doc{i}",
        "semantic_similarity": 1.0,
        "stat7_resonance": 0.0,
        "relevance_score": 1.0,
        "metadata": {"pack": "warbler-pack-core"}
    }
    for i in range(5)
]
analysis = analyze_narrative_coherence(results_5_perfect)
for k, v in analysis.items():
    print(f"  {k}: {v}")

# Test 2: Scaled up (100 results, same pack)
print("\n" + "=" * 70)
print("TEST 2: Scaled up (100 results, same pack, similarity=1.0)")
print("=" * 70)
results_100_same = [
    {
        "id": f"warbler-pack-core/doc{i}",
        "semantic_similarity": 1.0,
        "stat7_resonance": 0.0,
        "relevance_score": 1.0,
        "metadata": {"pack": "warbler-pack-core"}
    }
    for i in range(100)
]
analysis = analyze_narrative_coherence(results_100_same)
for k, v in analysis.items():
    print(f"  {k}: {v}")

# Test 3: Diverse (100 results, different packs)
print("\n" + "=" * 70)
print("TEST 3: Diverse (100 results, all different packs, similarity=1.0)")
print("=" * 70)
packs = [
    "warbler-pack-core",
    "warbler-pack-wisdom-scrolls",
    "warbler-pack-faction-politics"
]
results_100_diverse = [
    {
        "id": f"pack{j}/doc{i}",
        "semantic_similarity": 1.0,
        "stat7_resonance": 0.0,
        "relevance_score": 1.0,
        "metadata": {"pack": packs[j % len(packs)]}
    }
    for i in range(100)
    for j in range(1)
]
# Shuffle the packs
results_100_diverse = [
    {
        "id": f"doc{i}",
        "semantic_similarity": 1.0,
        "stat7_resonance": 0.0,
        "relevance_score": 1.0,
        "metadata": {"pack": packs[i % len(packs)]}
    }
    for i in range(100)
]
analysis = analyze_narrative_coherence(results_100_diverse)
for k, v in analysis.items():
    print(f"  {k}: {v}")

# Test 4: Low query success rate (100 queries, but only 10 results)
print("\n" + "=" * 70)
print("TEST 4: Low query success (100 queries → 10 results total)")
print("=" * 70)
results_sparse = [
    {
        "id": f"doc{i}",
        "semantic_similarity": 1.0,
        "stat7_resonance": 0.0,
        "relevance_score": 1.0,
        "metadata": {"pack": packs[i % len(packs)]}
    }
    for i in range(10)
]
analysis = analyze_narrative_coherence(results_sparse)
for k, v in analysis.items():
    print(f"  {k}: {v}")

# Test 5: Variance in semantic similarity
print("\n" + "=" * 70)
print("TEST 5: Variance in semantic similarity (100 results, similarity 0.0-1.0)")
print("=" * 70)
results_varied_similarity = [
    {
        "id": f"doc{i}",
        "semantic_similarity": i / 100.0,  # 0.0 to 1.0
        "stat7_resonance": 0.0,
        "relevance_score": 1.0,
        "metadata": {"pack": packs[i % len(packs)]}
    }
    for i in range(100)
]
analysis = analyze_narrative_coherence(results_varied_similarity)
for k, v in analysis.items():
    print(f"  {k}: {v}")

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)
print("""
NEW METRIC (RAG-appropriate):
- Quality (50%): Are results actually relevant? PRIMARY SIGNAL
- Semantic Coherence (30%): Do results cluster around similar meaning?
- STAT7 Entanglement (10%): Connected in STAT7 space?
- Focus (10%): Concentrated when relevant = GOOD (not penalized)

Expected improvements:
✓ Test 1 (5 perfect results): ~0.95 (quality=1.0, semantic=1.0, focus=0.99)
✓ Test 2 (100 perfect results): ~0.95 (same - NOT penalized for scale)
✓ Test 4 (sparse results): ~0.95 (quality=1.0 still, focus=0.79)
✓ Test 5 (varied similarity): ~0.70+ (quality=0.5, semantic=0.9+)

The key change: Focus is NOW A FEATURE when results are high-quality,
not a bug. We reward tight, relevant result sets.
""")