#!/usr/bin/env python3
"""Debug retrieval API search"""
import sys
sys.path.insert(0, '.')

from retrieval_api import RetrievalAPI, RetrievalMode, RetrievalQuery

# Create API instance
api = RetrievalAPI(config={"enable_stat7_hybrid": True})

# Check if context store is empty
print(f"Context store size: {api.get_context_store_size()}")

# Add a test document
api.add_document(
    doc_id="test/doc1",
    content="This is a test document about wisdom and philosophy",
    metadata={"pack": "test", "source": "test_doc"}
)

print(f"After adding 1 doc, context store size: {api.get_context_store_size()}")

# Try semantic search
query = RetrievalQuery(
    query_id="test_q1",
    mode=RetrievalMode.SEMANTIC_SIMILARITY,
    semantic_query="wisdom",
    max_results=10,
    confidence_threshold=0.6
)

print(f"\nQuery: semantic='{query.semantic_query}', confidence_threshold={query.confidence_threshold}")
print(f"Embedding provider: {api.embedding_provider}")
print(f"Semantic anchors: {api.semantic_anchors}")

# Execute query
assembly = api.retrieve_context(query)
print(f"\nResults: {len(assembly.results)}")
for result in assembly.results:
    print(f"  - {result.content_id}: score={result.relevance_score:.3f}")
    print(f"    content: {result.content[:100]}...")

# Debug: Direct context store search
print("\n--- Direct context store inspection ---")
for doc_id, doc_data in api._context_store.items():
    content_lower = doc_data["content"].lower()
    has_wisdom = "wisdom" in content_lower
    print(f"Doc: {doc_id}, has 'wisdom': {has_wisdom}")
    if has_wisdom:
        print(f"  Content: {doc_data['content'][:100]}...")