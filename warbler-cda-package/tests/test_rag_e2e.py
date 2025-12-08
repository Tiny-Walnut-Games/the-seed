"""
End-to-End RAG Integration Test
Validates the complete RAG system: embeddings, retrieval, semantic search, and FractalStat hybrid scoring
"""

import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from warbler_cda.embeddings import EmbeddingProviderFactory
from warbler_cda.retrieval_api import RetrievalAPI, RetrievalMode, RetrievalQuery


class TestEndToEndRAG:
    """End-to-end RAG system validation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup RAG system for testing."""
        self.embedding_provider = EmbeddingProviderFactory.get_default_provider()
        self.api = RetrievalAPI(
            embedding_provider=self.embedding_provider,
            config={
                "enable_fractalstat_hybrid": True,
                "cache_ttl_seconds": 300,
            },
        )
        yield
        self._report_metrics()

    def _report_metrics(self):
        """Report RAG system metrics."""
        metrics = self.api.get_retrieval_metrics()
        print("\n" + "=" * 60)
        print("RAG SYSTEM METRICS")
        print("=" * 60)
        print(f"Embedding Provider: {self.embedding_provider.provider_id}")
        print(f"Embedding Dimension: {self.embedding_provider.get_dimension()}")
        print(f"Documents in Store: {metrics['context_store_size']}")
        print(f"Total Queries: {metrics['retrieval_metrics']['total_queries']}")
        print("=" * 60)

    def test_01_embedding_generation(self):
        """Test 01: Verify embeddings are generated correctly."""
        print("\n[TEST 01] Embedding Generation")

        test_text = "Semantic embeddings enable efficient document retrieval"
        embedding = self.embedding_provider.embed_text(test_text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

        print(f"[PASS] Generated {len(embedding)}-dimensional embedding")
        print(f"   Sample values: {embedding[:5]}")

    def test_02_embedding_similarity(self):
        """Test 02: Verify similarity scoring works."""
        print("\n[TEST 02] Embedding Similarity Scoring")

        text1 = "performance optimization techniques"
        text2 = "optimization for better performance"
        text3 = "completely unrelated weather report"

        emb1 = self.embedding_provider.embed_text(text1)
        emb2 = self.embedding_provider.embed_text(text2)
        emb3 = self.embedding_provider.embed_text(text3)

        sim_12 = self.embedding_provider.calculate_similarity(emb1, emb2)
        sim_13 = self.embedding_provider.calculate_similarity(emb1, emb3)

        print(f"[PASS] Similarity '{text1}' vs '{text2}': {sim_12:.4f}")
        print(f"[PASS] Similarity '{text1}' vs '{text3}': {sim_13:.4f}")

        assert sim_12 > sim_13, "Similar texts should score higher"

    def test_03_document_ingestion(self):
        """Test 03: Verify documents can be ingested and stored."""
        print("\n[TEST 03] Document Ingestion")

        documents = [
            ("doc_1", "Performance optimization requires careful profiling"),
            ("doc_2", "Memory management is critical for scalability"),
            ("doc_3", "Semantic embeddings improve search relevance"),
            ("doc_4", "Caching strategies reduce database load"),
            ("doc_5", "Compression algorithms optimize storage"),
        ]

        for doc_id, content in documents:
            result = self.api.add_document(doc_id, content)
            assert result is True
            print(f"[PASS] Ingested: {doc_id}")

        assert self.api.get_context_store_size() == 5
        print(f"[PASS] Total documents: {self.api.get_context_store_size()}")

    def test_04_semantic_search(self):
        """Test 04: Verify semantic search retrieval works."""
        print("\n[TEST 04] Semantic Search Retrieval")

        documents = [
            ("doc_1", "How to optimize database queries for performance"),
            ("doc_2", "Memory leaks and profiling techniques"),
            ("doc_3", "Network optimization for distributed systems"),
            ("doc_4", "Caching patterns and implementation"),
        ]

        for doc_id, content in documents:
            self.api.add_document(doc_id, content)

        query = RetrievalQuery(
            query_id="test_search_1",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="how to optimize performance",
            max_results=3,
            confidence_threshold=0.3,
        )

        assembly = self.api.retrieve_context(query)

        assert assembly is not None
        assert len(assembly.results) > 0

        print(f"[PASS] Retrieved {len(assembly.results)} relevant documents")
        for i, result in enumerate(assembly.results, 1):
            print(f"   {i}. [{result.relevance_score:.4f}] {result.content[:50]}...")

    def test_05_max_results_respected(self):
        """Test 05: Verify max_results parameter is respected."""
        print("\n[TEST 05] Max Results Parameter")

        for i in range(10):
            self.api.add_document(f"doc_{i}", f"Document content {i}")

        query = RetrievalQuery(
            query_id="test_max_results",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="document",
            max_results=3,
            confidence_threshold=0.0,
        )

        assembly = self.api.retrieve_context(query)

        assert len(assembly.results) <= 3
        print(f"[PASS] Query returned {len(assembly.results)} results (max 3 requested)")

    def test_06_confidence_threshold(self):
        """Test 06: Verify confidence threshold filtering."""
        print("\n[TEST 06] Confidence Threshold Filtering")

        documents = [
            ("doc_1", "Python programming language basics"),
            ("doc_2", "Advanced Python techniques and patterns"),
            ("doc_3", "JavaScript for web development"),
        ]

        for doc_id, content in documents:
            self.api.add_document(doc_id, content)

        query_strict = RetrievalQuery(
            query_id="test_strict",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="python programming",
            max_results=10,
            confidence_threshold=0.8,
        )

        query_loose = RetrievalQuery(
            query_id="test_loose",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="python programming",
            max_results=10,
            confidence_threshold=0.2,
        )

        strict_results = self.api.retrieve_context(query_strict)
        loose_results = self.api.retrieve_context(query_loose)

        print(f"[PASS] Strict threshold (0.8): {len(strict_results.results)} results")
        print(f"[PASS] Loose threshold (0.2): {len(loose_results.results)} results")

        assert len(strict_results.results) <= len(loose_results.results)

    def test_07_fractalstat_hybrid_scoring(self):
        """Test 07: Verify FractalStat hybrid scoring works."""
        print("\n[TEST 07] FractalStat Hybrid Scoring")

        try:
            from warbler_cda.embeddings.sentence_transformer_provider import (
                SentenceTransformerEmbeddingProvider,
            )

            provider = SentenceTransformerEmbeddingProvider()

            hybrid_api = RetrievalAPI(
                embedding_provider=provider, config={"enable_fractalstat_hybrid": True}
            )
        except ImportError:
            pytest.skip("SentenceTransformer not installed for FractalStat testing")

        documents = [
            ("doc_1", "Semantic embeddings with FractalStat coordinates"),
            ("doc_2", "Hybrid scoring combines multiple metrics"),
            ("doc_3", "Multi-dimensional retrieval approach"),
        ]

        for doc_id, content in documents:
            hybrid_api.add_document(doc_id, content)

        query = RetrievalQuery(
            query_id="test_hybrid",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="semantic embeddings and scoring",
            max_results=3,
            fractalstat_hybrid=True,
            weight_semantic=0.6,
            weight_fractalstat=0.4,
        )

        assembly = hybrid_api.retrieve_context(query)

        assert assembly is not None
        if assembly.results:
            for result in assembly.results:
                assert hasattr(result, "semantic_similarity")
                assert hasattr(result, "fractalstat_resonance")
                print(
                    f"[PASS] Result: semantic={result.semantic_similarity:.4f}, FractalStat={result.fractalstat_resonance:.4f}"
                )

    def test_08_temporal_retrieval(self):
        """Test 08: Verify temporal retrieval works."""
        print("\n[TEST 08] Temporal Retrieval")

        current_time = time.time()

        documents = [
            ("recent_doc", "Recently added document"),
            ("old_doc", "Older document"),
        ]

        for doc_id, content in documents:
            self.api.add_document(doc_id, content)

        query = RetrievalQuery(
            query_id="test_temporal",
            mode=RetrievalMode.TEMPORAL_SEQUENCE,
            temporal_range=(current_time - 3600, current_time + 3600),
            max_results=10,
        )

        assembly = self.api.retrieve_context(query)

        assert assembly is not None
        print(f"[PASS] Temporal query retrieved {len(assembly.results)} results")

    def test_09_retrieval_metrics(self):
        """Test 09: Verify retrieval metrics are tracked."""
        print("\n[TEST 09] Retrieval Metrics Tracking")

        for i in range(3):
            self.api.add_document(f"doc_{i}", f"Content {i}")

        for i in range(2):
            query = RetrievalQuery(
                query_id=f"metric_query_{i}",
                mode=RetrievalMode.SEMANTIC_SIMILARITY,
                semantic_query="content",
                max_results=5,
            )
            self.api.retrieve_context(query)

        metrics = self.api.get_retrieval_metrics()

        assert metrics["context_store_size"] == 3
        assert metrics["retrieval_metrics"]["total_queries"] >= 2

        print(f"[PASS] Metrics tracked: {metrics['retrieval_metrics']['total_queries']} queries")

    def test_10_full_rag_pipeline(self):
        """Test 10: Complete RAG pipeline end-to-end."""
        print("\n[TEST 10] Full RAG Pipeline")

        knowledge_base = [
            "Python is a popular programming language",
            "Machine learning models learn from data",
            "Embeddings represent text as vectors",
            "Semantic search finds relevant documents",
            "RAG systems combine retrieval and generation",
        ]

        print("Step 1: Ingesting knowledge base...")
        for i, content in enumerate(knowledge_base):
            self.api.add_document(f"kb_{i}", content)
        print(f"[PASS] Ingested {len(knowledge_base)} documents")

        print("Step 2: Creating query...")
        query = RetrievalQuery(
            query_id="rag_pipeline_query",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query="How do embeddings work in machine learning?",
            max_results=3,
            confidence_threshold=0.3,
        )
        print(f"[PASS] Query created: '{query.semantic_query}'")

        print("Step 3: Retrieving context...")
        assembly = self.api.retrieve_context(query)
        print(f"[PASS] Retrieved {len(assembly.results)} relevant results")

        print("Step 4: Analyzing results...")
        for i, result in enumerate(assembly.results, 1):
            print(f"   {i}. Score: {result.relevance_score:.4f}")
            print(f"      Content: {result.content[:60]}...")

        assert len(assembly.results) > 0
        print("[PASS] RAG pipeline executed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
