"""
Phase 3: Semantic Similarity Search with Embeddings

Tests semantic search capabilities using FAISS and Sentence-Transformers
to retrieve contextually appropriate NPC dialogue from 1900+ templates.

Validates:
- Embedding service initialization
- FAISS index construction
- Semantic similarity search accuracy
- Integration with 1915 HF NPC dialogue documents
- Performance benchmarks
"""

import pytest
import numpy as np
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def embedding_service():
    """Initialize embedding service (expensive operation, session-scoped)"""
    try:
        from web.server.warbler_embedding_service import WarblerEmbeddingService
        service = WarblerEmbeddingService()
        logger.info(f"✓ Initialized {service.MODEL_NAME} embeddings")
        return service
    except ImportError:
        pytest.skip("sentence-transformers not available")


@pytest.fixture(scope="session")
def pack_loader_with_embeddings(embedding_service):
    """Load all packs and build embeddings (session-scoped for performance)"""
    from web.server.warbler_pack_loader import WarblerPackLoader
    
    loader = WarblerPackLoader(embedding_service=embedding_service)
    
    # Load JSON templates
    loader.load_all_packs()
    logger.info(f"✓ Loaded {len(loader.templates)} templates from JSON packs")
    
    # Load JSONL documents (1915 HF NPC dialogues)
    hf_count = loader.load_jsonl_pack("warbler-pack-hf-npc-dialogue")
    logger.info(f"✓ Loaded {hf_count} JSONL documents from HF pack")
    
    # Build embeddings
    loader.build_embeddings()
    
    return loader


class TestEmbeddingServiceBasics:
    """Test embedding service core functionality"""
    
    def test_embedding_service_initialization(self, embedding_service):
        """Verify embedding service initializes correctly"""
        assert embedding_service is not None
        assert embedding_service.MODEL_NAME == "all-MiniLM-L6-v2"
        assert embedding_service.EMBEDDING_DIM == 384
        
        stats = embedding_service.get_stats()
        assert stats["embedding_model"] == "all-MiniLM-L6-v2"
        assert stats["embedding_dim"] == 384
    
    def test_embed_single_text(self, embedding_service):
        """Test embedding a single text"""
        texts = ["Hello, how can I help you?"]
        embeddings = embedding_service.embed_texts(texts)
        
        assert embeddings.shape == (1, 384)
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.dtype == np.float32
    
    def test_embed_batch_texts(self, embedding_service):
        """Test embedding a batch of texts"""
        texts = [
            "Hello, traveler!",
            "I have wondrous items for sale.",
            "Beware the bandits on the road.",
            "The king seeks brave adventurers.",
            "I know nothing of such matters."
        ]
        embeddings = embedding_service.embed_texts(texts)
        
        assert embeddings.shape == (5, 384)
        assert isinstance(embeddings, np.ndarray)
    
    def test_add_single_template(self, embedding_service):
        """Test adding a single template with embedding"""
        template = embedding_service.add_template(
            template_id="test_greeting",
            content="Hail and well met, friend!",
            metadata={"pack": "test", "type": "greeting"},
            tags=["greeting", "friendly"]
        )
        
        assert template.template_id == "test_greeting"
        assert template.embedding.shape == (384,)
        assert "greeting" in template.tags
        assert embedding_service.get_template("test_greeting") is not None


class TestSemanticSearch:
    """Test semantic similarity search functionality"""
    
    def test_semantic_search_basics(self, embedding_service):
        """Test basic semantic search on small dataset"""
        # Add test templates
        templates = [
            {"template_id": "greeting_1", "content": "Hello there, friend!", "metadata": {}, "tags": ["greeting"]},
            {"template_id": "trade_1", "content": "I have fine merchandise for sale.", "metadata": {}, "tags": ["trade"]},
            {"template_id": "warning_1", "content": "Beware the dark forests!", "metadata": {}, "tags": ["warning"]},
        ]
        
        embedding_service.add_templates_batch(templates)
        
        # Search for greeting
        results = embedding_service.search_semantic("Hello", top_k=2)
        assert len(results) <= 2
        assert results[0][0] == "greeting_1"  # Best match should be greeting
    
    def test_semantic_search_filters_by_reputation(self, embedding_service):
        """Test semantic search with reputation tier filtering"""
        templates = [
            {
                "template_id": "formal_greeting",
                "content": "Greetings, your excellence!",
                "metadata": {},
                "tags": ["greeting"],
                "reputation_tier": "revered"
            },
            {
                "template_id": "casual_greeting",
                "content": "Hey there, buddy!",
                "metadata": {},
                "tags": ["greeting"],
                "reputation_tier": "trusted"
            },
        ]
        
        embedding_service.add_templates_batch(templates)
        
        # Search with reputation filter
        results = embedding_service.search_semantic(
            "Hello friend",
            top_k=1,
            reputation_tier="revered"
        )
        
        if results:
            assert results[0][2].reputation_tier == "revered"
    
    def test_similarity_scores_normalized(self, embedding_service):
        """Verify similarity scores are in [0, 1] range"""
        templates = [
            {"template_id": "t1", "content": "Hello world", "metadata": {}},
            {"template_id": "t2", "content": "Goodbye world", "metadata": {}},
        ]
        
        embedding_service.add_templates_batch(templates)
        
        results = embedding_service.search_semantic("Hello", top_k=2)
        
        for _, score, _ in results:
            assert 0.0 <= score <= 1.0, f"Score {score} outside [0, 1]"


class TestPackLoaderWithEmbeddings:
    """Test WarblerPackLoader integration with embeddings"""
    
    def test_pack_loader_loads_json_templates(self, pack_loader_with_embeddings):
        """Verify JSON templates loaded"""
        stats = pack_loader_with_embeddings.get_stats()
        
        assert stats["total_templates"] > 0
        logger.info(f"Total templates: {stats['total_templates']}")
    
    def test_pack_loader_loads_jsonl_documents(self, pack_loader_with_embeddings):
        """Verify JSONL documents loaded from HF pack"""
        stats = pack_loader_with_embeddings.get_stats()
        
        assert stats["jsonl_documents_loaded"] == 1915
        logger.info(f"JSONL documents loaded: {stats['jsonl_documents_loaded']}")
    
    def test_pack_loader_builds_embeddings(self, pack_loader_with_embeddings):
        """Verify embeddings built for all templates + documents"""
        stats = pack_loader_with_embeddings.get_stats()
        embedding_stats = stats.get("embedding_service", {})
        
        total_embedded = stats["total_templates"] + stats["jsonl_documents_loaded"]
        assert embedding_stats.get("templates_loaded") == total_embedded
        logger.info(f"Embeddings built: {embedding_stats['templates_loaded']}")
    
    def test_semantic_search_on_pack_loader(self, pack_loader_with_embeddings):
        """Test semantic search through pack loader"""
        results = pack_loader_with_embeddings.search_semantic(
            query="Hello, can you help me?",
            top_k=5
        )
        
        assert len(results) > 0
        assert len(results) <= 5
        
        # Verify result structure
        for template_id, similarity, template in results:
            assert isinstance(template_id, str)
            assert 0.0 <= similarity <= 1.0
            assert template is not None
            logger.info(f"  - {template_id}: {similarity:.3f}")


class TestSemanticSearchQuality:
    """Test semantic search accuracy and quality"""
    
    def test_greeting_search(self, pack_loader_with_embeddings):
        """Test search for greeting-like queries"""
        queries = [
            "Hello there!",
            "Greetings, friend!",
            "How do you do?",
            "Salutations!",
        ]
        
        for query in queries:
            results = pack_loader_with_embeddings.search_semantic(query, top_k=3)
            assert len(results) > 0, f"No results for '{query}'"
            logger.info(f"Query '{query}' -> {results[0][0]}: {results[0][1]:.3f}")
    
    def test_trade_search(self, pack_loader_with_embeddings):
        """Test search for trade/commerce-like queries"""
        queries = [
            "Do you have any items for sale?",
            "What merchandise do you offer?",
            "I'm interested in buying something.",
            "What's your inventory?",
        ]
        
        for query in queries:
            results = pack_loader_with_embeddings.search_semantic(query, top_k=3)
            assert len(results) > 0, f"No results for '{query}'"
            logger.info(f"Query '{query}' -> {results[0][0]}: {results[0][1]:.3f}")
    
    def test_help_search(self, pack_loader_with_embeddings):
        """Test search for help/assistance queries"""
        queries = [
            "Can you help me?",
            "I need assistance.",
            "Could you lend a hand?",
            "I'm in trouble, help!",
        ]
        
        for query in queries:
            results = pack_loader_with_embeddings.search_semantic(query, top_k=3)
            assert len(results) > 0, f"No results for '{query}'"
            logger.info(f"Query '{query}' -> {results[0][0]}: {results[0][1]:.3f}")
    
    def test_hostile_search(self, pack_loader_with_embeddings):
        """Test search for hostile/aggressive queries"""
        queries = [
            "Get out of my way!",
            "I'll take what I want!",
            "Don't mess with me!",
        ]
        
        for query in queries:
            results = pack_loader_with_embeddings.search_semantic(query, top_k=3)
            # May or may not have hostile templates, but should return something
            logger.info(f"Query '{query}' -> {results[0][0] if results else 'no match'}")


class TestPerformance:
    """Performance and scale tests"""
    
    def test_semantic_search_latency(self, pack_loader_with_embeddings):
        """Measure semantic search latency"""
        import time
        
        query = "Hello, can you help me find something?"
        
        # Warmup
        pack_loader_with_embeddings.search_semantic(query, top_k=5)
        
        # Measure
        times = []
        for _ in range(10):
            start = time.time()
            pack_loader_with_embeddings.search_semantic(query, top_k=5)
            times.append((time.time() - start) * 1000)
        
        avg_ms = np.mean(times)
        max_ms = np.max(times)
        
        logger.info(f"Semantic search latency: avg={avg_ms:.2f}ms, max={max_ms:.2f}ms")
        assert avg_ms < 100, f"Search too slow: {avg_ms}ms"  # Should be <100ms
    
    def test_embedding_service_stats(self, pack_loader_with_embeddings):
        """Log embedding service statistics"""
        stats = pack_loader_with_embeddings.get_stats()
        
        logger.info("=== Phase 3 Statistics ===")
        logger.info(f"JSON templates: {stats['total_templates']}")
        logger.info(f"HF JSONL documents: {stats['jsonl_documents_loaded']}")
        logger.info(f"Total embeddings: {stats['total_templates'] + stats['jsonl_documents_loaded']}")
        logger.info(f"Embedding model: {stats['embedding_service']['embedding_model']}")
        logger.info(f"Embedding dim: {stats['embedding_service']['embedding_dim']}")
        logger.info(f"FAISS index size: {stats['embedding_service']['index_size']}")


class TestPhase3Integration:
    """Integration tests for Phase 3 complete workflow"""
    
    def test_semantic_search_with_query_service(self, pack_loader_with_embeddings):
        """Test semantic search integrated with WarblerQueryService"""
        # Verify pack loader has embedding service
        assert pack_loader_with_embeddings.embedding_service is not None
        
        # Verify can search
        results = pack_loader_with_embeddings.search_semantic("Hello friend", top_k=3)
        assert len(results) > 0
        
        logger.info("✓ Semantic search ready for WarblerQueryService integration")
    
    def test_hf_dataset_coverage(self, pack_loader_with_embeddings):
        """Verify HF dataset provides diverse dialogue"""
        # Sample diverse queries
        queries = [
            "Tell me about your background",
            "What brings you to this place?",
            "Do you have any wisdom to share?",
            "I'm looking for adventure",
            "What do you fear?",
        ]
        
        results_per_query = {}
        for query in queries:
            results = pack_loader_with_embeddings.search_semantic(query, top_k=3)
            results_per_query[query] = len(results)
        
        logger.info("=== Query Diversity Test ===")
        for query, count in results_per_query.items():
            logger.info(f"  '{query}' -> {count} results")
        
        # All queries should get results
        assert all(count > 0 for count in results_per_query.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])