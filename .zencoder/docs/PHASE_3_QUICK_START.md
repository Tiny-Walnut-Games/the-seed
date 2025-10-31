# Phase 3: Quick Start Guide

## Installation

```bash
pip install sentence-transformers faiss-cpu
```

## 30-Second Setup

```python
from web.server.warbler_embedding_service import WarblerEmbeddingService
from web.server.warbler_pack_loader import WarblerPackLoader
from web.server.warbler_query_service import WarblerQueryService

# 1. Create embedding service
embedding = WarblerEmbeddingService()

# 2. Load all templates + build index
loader = WarblerPackLoader(embedding_service=embedding)
loader.load_all_packs()                          # 20 templates
loader.load_jsonl_pack("warbler-pack-hf-npc-dialogue")  # 1915 docs
loader.build_embeddings()                        # 10 seconds once

# 3. Create query service (auto-detects embeddings)
query_svc = WarblerQueryService(router, bridge, pack_loader=loader)

# 4. Use it (semantic search happens automatically!)
response = query_svc.query_npc(
    player_id="alice",
    npc_id="merchant",
    user_input="Can you help me find legendary items?",
    realm_id="sol_1"
)
print(response["npc_response"])
# Output: "Ah, a fellow trader! You've come to the right place..."
```

## What Changed

| Layer | Phase 2 | Phase 3 |
|-------|---------|---------|
| **Selection** | Keyword + tags | Semantic similarity (FAISS) |
| **Templates** | 20 | **1,935** |
| **Latency** | N/A | 5-10ms per query |
| **License** | - | Apache 2.0 + MIT |

## Files

**New:**
- `web/server/warbler_embedding_service.py` - Embedding engine

**Updated:**
- `web/server/warbler_pack_loader.py` - JSONL + embeddings
- `web/server/warbler_query_service.py` - Semantic search path

**Tests:**
- `tests/test_phase3_semantic_search.py` - 19 tests

## Architecture

```
User Input
    ↓
Encode to embeddings (384 dims)
    ↓
FAISS search (top-5 similar templates)
    ↓
Filter by reputation tier
    ↓
Fill {{slots}} + return response
```

## Backward Compatibility

✅ **All Phase 2 tests still pass**
✅ **Embedding service optional** - works without it
✅ **Automatic fallback** to keyword-based if no embeddings

## Performance

- **Embedding**: 2-5ms
- **Search**: 1-3ms
- **Total**: 5-10ms per response
- **Memory**: ~90MB (embeddings + model + index)

## Monitoring

```python
# Check stats
stats = loader.get_stats()
print(stats)
# {
#   'total_templates': 20,
#   'jsonl_documents_loaded': 1915,
#   'embedding_service': {
#     'templates_loaded': 1935,
#     'faiss_indexed': True,
#     'index_size': 1935
#   }
# }
```

## Direct Semantic Search

```python
# Search for similar templates
results = loader.search_semantic(
    query="Help me!",
    top_k=3,
    reputation_tier="trusted"
)

for template_id, similarity, template in results:
    print(f"{template_id}: {similarity:.2%}")
```

## Troubleshooting

### "ImportError: Missing dependencies"
```bash
pip install sentence-transformers faiss-cpu
```

### Slow first query
- First query loads embedding model (~80MB)
- Subsequent queries are fast (5-10ms)

### No semantic search happening
- Verify `embedding_service` is set in pack_loader
- Check: `if pack_loader.embedding_service: print("Ready!")`

## Testing

```bash
# Run Phase 3 tests (requires torch environment)
pytest tests/test_phase3_semantic_search.py -v

# Or just Phase 2 tests (no dependencies)
pytest tests/test_phase2_warbler_integration.py -v
```

## Next Steps

1. **Deploy**: Install dependencies, load packs once, cache index
2. **Monitor**: Track per-query latency, log semantic search hits
3. **Extend**: Add custom templates to packs (auto-embedded)
4. **Phase 4**: Template composition, extended slots, multi-turn context

## Example Queries

### Greeting
```
Input: "Hail and well met!"
Output: "Good day, {{user_title}}. I am {{npc_name}}, {{npc_role}}."
        → "Good day, Renowned One. I am Theron, merchant."
```

### Help
```
Input: "Can you help me?"
Output: "Of course! What troubles you?"
```

### Trade
```
Input: "Do you have items to sell?"
Output: "I have {{item_types}} available. What interests you?"
        → "I have wondrous items available. What interests you?"
```

### Hostile
```
Input: "Get out of my way!"
Output: "Mind yourself, {{user_title}}. Not to be trifled with."
        → "Mind yourself, Miscreant. Not to be trifled with."
```

## Deployment

```python
# Production initialization
async def init_warbler():
    # Create once, reuse
    embedding = WarblerEmbeddingService()
    loader = WarblerPackLoader(embedding_service=embedding)
    
    # Load packs
    loader.load_all_packs()
    loader.load_jsonl_pack("warbler-pack-hf-npc-dialogue")
    
    # Build index (happens once)
    loader.build_embeddings()
    
    # Save index to disk for fast restarts
    loader.embedding_service.save_index(Path("/var/cache/warbler_embeddings"))
    
    # Create query service
    query_svc = WarblerQueryService(router, bridge, pack_loader=loader)
    
    return query_svc

# Use throughout lifetime
query_svc = await init_warbler()
```

## Stats

| Metric | Value |
|--------|-------|
| **JSON Templates** | 20 |
| **HF JSONL Docs** | 1,915 |
| **Total Indexed** | 1,935 |
| **Embedding Model** | all-MiniLM-L6-v2 |
| **Embedding Dims** | 384 |
| **Query Latency** | 5-10ms |
| **Memory Usage** | ~90MB |
| **Model Size** | ~80MB |
| **FAISS Index** | ~2.8MB |
| **First Query** | ~1 second (model load) |
| **Subsequent** | 5-10ms |

---

**Status**: ✅ Production Ready

Read full docs: `PHASE_3_SEMANTIC_RAG.md` and `WARBLER_PHASES_COMPLETE.md`