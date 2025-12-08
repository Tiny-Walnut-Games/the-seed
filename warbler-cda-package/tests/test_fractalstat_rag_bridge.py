# pylint: disable=import-outside-toplevel, protected-access, missing-function-docstring, missing-class-docstring
"""
Comprehensive tests for warbler_cda.fractalstat_rag_bridge module.

Tests the 8D FractalStat-RAG bridge for hybrid scoring and retrieval.
"""

import pytest


class TestRealm:
    """Test Realm dataclass."""

    def test_realm_initialization(self):
        """Realm should initialize with type and label."""
        from warbler_cda.fractalstat_rag_bridge import Realm

        realm = Realm(type="game", label="Test Game")
        assert realm.type == "game"
        assert realm.label == "Test Game"

    def test_realm_equality(self):
        """Realms with same type and label should be equal."""
        from warbler_cda.fractalstat_rag_bridge import Realm

        realm1 = Realm(type="system", label="Test")
        realm2 = Realm(type="system", label="Test")
        assert realm1 == realm2


class TestAlignment:
    """Test Alignment dataclass."""

    def test_alignment_initialization(self):
        """Alignment should initialize with type."""
        from warbler_cda.fractalstat_rag_bridge import Alignment

        alignment = Alignment(type="harmonic")
        assert alignment.type == "harmonic"

    def test_alignment_types(self):
        """Alignment should support all coordination types."""
        from warbler_cda.fractalstat_rag_bridge import Alignment

        types = ["harmonic", "chaotic", "symbiotic", "entropic", "balanced"]
        for align_type in types:
            alignment = Alignment(type=align_type)
            assert alignment.type == align_type


class TestFractalStatAddress:
    """Test FractalStatAddress dataclass with 8D coordinates."""

    def test_fractalstat_address_initialization(self):
        """FractalStatAddress should initialize with all 8 dimensions."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="game", label="Test")
        alignment = Alignment(type="harmonic")

        addr = FractalStatAddress(
            realm=realm,
            lineage=5,
            adjacency=75.0,
            horizon="scene",
            luminosity=80.0,
            polarity=0.5,
            dimensionality=4,
            alignment=alignment
        )

        assert addr.realm == realm
        assert addr.lineage == 5
        assert addr.adjacency == 75.0
        assert addr.horizon == "scene"
        assert addr.luminosity == 80.0
        assert addr.polarity == 0.5
        assert addr.dimensionality == 4
        assert addr.alignment == alignment

    def test_fractalstat_address_validation_adjacency(self):
        """FractalStatAddress should validate adjacency range [0, 100]."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")

        with pytest.raises(ValueError, match="adjacency must be"):
            FractalStatAddress(
                realm=realm,
                lineage=0,
                adjacency=150.0,  # Invalid: > 100
                horizon="scene",
                luminosity=50.0,
                polarity=0.0,
                dimensionality=3,
                alignment=alignment
            )

    def test_fractalstat_address_validation_luminosity(self):
        """FractalStatAddress should validate luminosity range [0, 100]."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")

        with pytest.raises(ValueError, match="luminosity must be"):
            FractalStatAddress(
                realm=realm,
                lineage=0,
                adjacency=50.0,
                horizon="scene",
                luminosity=-10.0,  # Invalid: < 0
                polarity=0.0,
                dimensionality=3,
                alignment=alignment
            )

    def test_fractalstat_address_validation_polarity(self):
        """FractalStatAddress should validate polarity range [-1, 1]."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")

        with pytest.raises(ValueError, match="polarity must be"):
            FractalStatAddress(
                realm=realm,
                lineage=0,
                adjacency=50.0,
                horizon="scene",
                luminosity=50.0,
                polarity=2.0,  # Invalid: > 1
                dimensionality=3,
                alignment=alignment
            )

    def test_fractalstat_address_validation_lineage(self):
        """FractalStatAddress should validate lineage >= 0."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")

        with pytest.raises(ValueError, match="lineage must be"):
            FractalStatAddress(
                realm=realm,
                lineage=-5,  # Invalid: < 0
                adjacency=50.0,
                horizon="scene",
                luminosity=50.0,
                polarity=0.0,
                dimensionality=3,
                alignment=alignment
            )

    def test_fractalstat_address_validation_dimensionality(self):
        """FractalStatAddress should validate dimensionality range [1, 8]."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")

        with pytest.raises(ValueError, match="dimensionality must be"):
            FractalStatAddress(
                realm=realm,
                lineage=0,
                adjacency=50.0,
                horizon="scene",
                luminosity=50.0,
                polarity=0.0,
                dimensionality=10,  # Invalid: > 8
                alignment=alignment
            )

    def test_fractalstat_address_to_dict(self):
        """to_dict should export all 8 dimensions."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="game", label="Test")
        alignment = Alignment(type="symbiotic")

        addr = FractalStatAddress(
            realm=realm,
            lineage=3,
            adjacency=60.0,
            horizon="outline",
            luminosity=70.0,
            polarity=-0.3,
            dimensionality=5,
            alignment=alignment
        )

        data = addr.to_dict()

        assert data["realm"]["type"] == "game"
        assert data["realm"]["label"] == "Test"
        assert data["lineage"] == 3
        assert data["adjacency"] == 60.0
        assert data["horizon"] == "outline"
        assert data["luminosity"] == 70.0
        assert data["polarity"] == -0.3
        assert data["dimensionality"] == 5
        assert data["alignment"]["type"] == "symbiotic"


class TestRAGDocument:
    """Test RAGDocument dataclass."""

    def test_rag_document_initialization(self):
        """RAGDocument should initialize with required fields."""
        from warbler_cda.fractalstat_rag_bridge import RAGDocument, FractalStatAddress
        from warbler_cda.fractalstat_rag_bridge import Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        doc = RAGDocument(
            id="doc-1",
            text="Test document",
            embedding=[0.1, 0.2, 0.3],
            fractalstat=fractalstat
        )

        assert doc.id == "doc-1"
        assert doc.text == "Test document"
        assert len(doc.embedding) == 3
        assert doc.fractalstat == fractalstat
        assert doc.metadata == {}

    def test_rag_document_validation_empty_embedding(self):
        """RAGDocument should reject empty embeddings."""
        from warbler_cda.fractalstat_rag_bridge import RAGDocument, FractalStatAddress
        from warbler_cda.fractalstat_rag_bridge import Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        with pytest.raises(ValueError, match="embedding must not be empty"):
            RAGDocument(
                id="doc-1",
                text="Test",
                embedding=[],  # Invalid: empty
                fractalstat=fractalstat
            )


class TestCosineSimilarity:
    """Test cosine_similarity function."""

    def test_cosine_similarity_identical_vectors(self):
        """Cosine similarity of identical vectors should be 1.0."""
        from warbler_cda.fractalstat_rag_bridge import cosine_similarity

        vec = [1.0, 2.0, 3.0]
        sim = cosine_similarity(vec, vec)
        assert abs(sim - 1.0) < 1e-6

    def test_cosine_similarity_orthogonal_vectors(self):
        """Cosine similarity of orthogonal vectors should be 0.0."""
        from warbler_cda.fractalstat_rag_bridge import cosine_similarity

        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        sim = cosine_similarity(vec1, vec2)
        assert abs(sim - 0.0) < 1e-6

    def test_cosine_similarity_opposite_vectors(self):
        """Cosine similarity of opposite vectors should be -1.0."""
        from warbler_cda.fractalstat_rag_bridge import cosine_similarity

        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        sim = cosine_similarity(vec1, vec2)
        assert abs(sim - (-1.0)) < 1e-6

    def test_cosine_similarity_empty_vectors(self):
        """Cosine similarity should handle empty vectors."""
        from warbler_cda.fractalstat_rag_bridge import cosine_similarity

        sim = cosine_similarity([], [])
        assert sim == 0.0

    def test_cosine_similarity_zero_vector(self):
        """Cosine similarity should handle zero vectors."""
        from warbler_cda.fractalstat_rag_bridge import cosine_similarity

        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]
        sim = cosine_similarity(vec1, vec2)
        assert sim == 0.0


class TestFractalStatResonance:
    """Test fractalstat_resonance function with 8D coordinates."""

    def test_fractalstat_resonance_identical_addresses(self):
        """Resonance of identical addresses should be 1.0."""
        from warbler_cda.fractalstat_rag_bridge import fractalstat_resonance
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="game", label="Test")
        alignment = Alignment(type="harmonic")

        addr = FractalStatAddress(
            realm=realm,
            lineage=5,
            adjacency=75.0,
            horizon="scene",
            luminosity=80.0,
            polarity=0.5,
            dimensionality=4,
            alignment=alignment
        )

        resonance = fractalstat_resonance(addr, addr)
        assert 0.9 <= resonance <= 1.0  # Should be very high

    def test_fractalstat_resonance_different_realms(self):
        """Resonance should decrease with different realms."""
        from warbler_cda.fractalstat_rag_bridge import fractalstat_resonance
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm1 = Realm(type="game", label="Test1")
        realm2 = Realm(type="system", label="Test2")
        alignment = Alignment(type="harmonic")

        addr1 = FractalStatAddress(
            realm=realm1,
            lineage=5,
            adjacency=75.0,
            horizon="scene",
            luminosity=80.0,
            polarity=0.5,
            dimensionality=4,
            alignment=alignment
        )

        addr2 = FractalStatAddress(
            realm=realm2,
            lineage=5,
            adjacency=75.0,
            horizon="scene",
            luminosity=80.0,
            polarity=0.5,
            dimensionality=4,
            alignment=alignment
        )

        resonance = fractalstat_resonance(addr1, addr2)
        assert 0.0 <= resonance < 1.0

    def test_fractalstat_resonance_alignment_synergy(self):
        """Resonance should consider alignment synergy."""
        from warbler_cda.fractalstat_rag_bridge import fractalstat_resonance
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="game", label="Test")

        # Harmonic-Harmonic should have high synergy
        addr1 = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=Alignment(type="harmonic")
        )

        addr2 = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=Alignment(type="harmonic")
        )

        resonance_harmonic = fractalstat_resonance(addr1, addr2)

        # Chaotic-Chaotic should have lower synergy
        addr3 = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=Alignment(type="chaotic")
        )

        addr4 = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=Alignment(type="chaotic")
        )

        resonance_chaotic = fractalstat_resonance(addr3, addr4)

        # Harmonic should have higher resonance than chaotic
        assert resonance_harmonic > resonance_chaotic

    def test_fractalstat_resonance_range(self):
        """Resonance should always be in range [0, 1]."""
        from warbler_cda.fractalstat_rag_bridge import fractalstat_resonance
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm1 = Realm(type="game", label="Test1")
        realm2 = Realm(type="system", label="Test2")

        addr1 = FractalStatAddress(
            realm=realm1,
            lineage=0,
            adjacency=0.0,
            horizon="logline",
            luminosity=0.0,
            polarity=-1.0,
            dimensionality=1,
            alignment=Alignment(type="chaotic")
        )

        addr2 = FractalStatAddress(
            realm=realm2,
            lineage=100,
            adjacency=100.0,
            horizon="panel",
            luminosity=100.0,
            polarity=1.0,
            dimensionality=8,
            alignment=Alignment(type="harmonic")
        )

        resonance = fractalstat_resonance(addr1, addr2)
        assert 0.0 <= resonance <= 1.0


class TestHybridScore:
    """Test hybrid_score function."""

    def test_hybrid_score_weights_sum_validation(self):
        """hybrid_score should validate weights sum to 1.0."""
        from warbler_cda.fractalstat_rag_bridge import hybrid_score, RAGDocument
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        doc = RAGDocument(
            id="doc-1",
            text="Test",
            embedding=[0.1, 0.2, 0.3],
            fractalstat=fractalstat
        )

        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            hybrid_score(
                [0.1, 0.2, 0.3],
                doc,
                fractalstat,
                weight_semantic=0.6,
                weight_fractalstat=0.5  # Invalid: sum > 1.0
            )

    def test_hybrid_score_calculation(self):
        """hybrid_score should combine semantic and FractalStat scores."""
        from warbler_cda.fractalstat_rag_bridge import hybrid_score, RAGDocument
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment
        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        doc = RAGDocument(
            id="doc-1",
            text="Test",
            embedding=[1.0, 0.0, 0.0],
            fractalstat=fractalstat
        )

        query_embedding = [1.0, 0.0, 0.0]  # Identical to doc

        score = hybrid_score(
            query_embedding,
            doc,
            fractalstat,
            weight_semantic=0.6,
            weight_fractalstat=0.4
        )

        assert 0.0 <= score <= 1.0
        # Should be high since both semantic and FractalStat match
        assert score > 0.8

    def test_hybrid_score_range(self):
        """hybrid_score should always return value in [0, 1]."""
        from warbler_cda.fractalstat_rag_bridge import hybrid_score, RAGDocument
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        doc = RAGDocument(
            id="doc-1",
            text="Test",
            embedding=[0.1, 0.2, 0.3],
            fractalstat=fractalstat
        )

        score = hybrid_score(
            [0.5, 0.5, 0.5],
            doc,
            fractalstat,
            weight_semantic=0.55,
            weight_fractalstat=0.45
        )

        assert 0.0 <= score <= 1.0


class TestRetrieve:
    """Test retrieve function."""

    def test_retrieve_returns_top_k(self):
        """retrieve should return top-k documents."""
        from warbler_cda.fractalstat_rag_bridge import retrieve, RAGDocument
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        documents = [
            RAGDocument(
                id=f"doc-{i}",
                text=f"Document {i}",
                embedding=[float(i), 0.0, 0.0],
                fractalstat=fractalstat
            )
            for i in range(10)
        ]

        results = retrieve(
            documents,
            [5.0, 0.0, 0.0],
            fractalstat,
            k=3
        )

        assert len(results) == 3
        assert all(isinstance(r, tuple) for r in results)
        assert all(len(r) == 2 for r in results)

    def test_retrieve_sorted_by_score(self):
        """retrieve should return results sorted by score descending."""
        from warbler_cda.fractalstat_rag_bridge import retrieve, RAGDocument
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        documents = [
            RAGDocument(
                id=f"doc-{i}",
                text=f"Document {i}",
                embedding=[float(i), 0.0, 0.0],
                fractalstat=fractalstat
            )
            for i in range(5)
        ]

        results = retrieve(
            documents,
            [2.0, 0.0, 0.0],
            fractalstat,
            k=5
        )

        # Scores should be in descending order
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)


class TestRetrieveSemanticOnly:
    """Test retrieve_semantic_only function."""

    def test_retrieve_semantic_only(self):
        """retrieve_semantic_only should use only semantic similarity."""
        from warbler_cda.fractalstat_rag_bridge import retrieve_semantic_only, RAGDocument
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        documents = [
            RAGDocument(
                id=f"doc-{i}",
                text=f"Document {i}",
                embedding=[float(i), 0.0, 0.0],
                fractalstat=fractalstat
            )
            for i in range(5)
        ]

        results = retrieve_semantic_only(
            documents,
            [2.0, 0.0, 0.0],
            k=3
        )

        assert len(results) == 3
        # Should be sorted by semantic similarity
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)


class TestGenerateRandomFractalStatAddress:
    """Test generate_random_fractalstat_address function."""

    def test_generate_random_address(self):
        """generate_random_fractalstat_address should create valid address."""
        from warbler_cda.fractalstat_rag_bridge import generate_random_fractalstat_address, Realm

        realm = Realm(type="test", label="test")
        addr = generate_random_fractalstat_address(realm)

        assert addr.realm == realm
        assert addr.lineage >= 0
        assert 0.0 <= addr.adjacency <= 100.0
        assert addr.horizon in ["logline", "outline", "scene", "panel"]
        assert 0.0 <= addr.luminosity <= 100.0
        assert -1.0 <= addr.polarity <= 1.0
        assert 1 <= addr.dimensionality <= 8
        assert addr.alignment.type in ["harmonic", "symbiotic", "balanced", "entropic", "chaotic"]

    def test_generate_random_address_with_seed(self):
        """generate_random_fractalstat_address should be deterministic with seed."""
        from warbler_cda.fractalstat_rag_bridge import generate_random_fractalstat_address, Realm

        realm = Realm(type="test", label="test")
        addr1 = generate_random_fractalstat_address(realm, seed_offset=42)
        addr2 = generate_random_fractalstat_address(realm, seed_offset=42)

        # Deterministic parts should match
        assert addr1.horizon == addr2.horizon
        assert addr1.alignment.type == addr2.alignment.type
        assert addr1.lineage == addr2.lineage


class TestFractalStatRAGBridge:
    """Test FractalStatRAGBridge wrapper class."""

    def test_bridge_initialization(self):
        """FractalStatRAGBridge should initialize."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatRAGBridge

        bridge = FractalStatRAGBridge()
        assert bridge is not None

    def test_bridge_fractalstat_resonance(self):
        """Bridge should wrap fractalstat_resonance function."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatRAGBridge, FractalStatAddress
        from warbler_cda.fractalstat_rag_bridge import Realm, Alignment

        bridge = FractalStatRAGBridge()
        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")

        addr = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        resonance = bridge.fractalstat_resonance(addr, addr)
        assert 0.0 <= resonance <= 1.0

    def test_bridge_hybrid_score(self):
        """Bridge should wrap hybrid_score function."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatRAGBridge, RAGDocument
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        bridge = FractalStatRAGBridge()
        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        doc = RAGDocument(
            id="doc-1",
            text="Test",
            embedding=[1.0, 0.0, 0.0],
            fractalstat=fractalstat
        )

        score = bridge.hybrid_score(
            [1.0, 0.0, 0.0],
            doc,
            fractalstat
        )

        assert 0.0 <= score <= 1.0

    def test_bridge_retrieve(self):
        """Bridge should wrap retrieve function."""
        from warbler_cda.fractalstat_rag_bridge import FractalStatRAGBridge, RAGDocument
        from warbler_cda.fractalstat_rag_bridge import FractalStatAddress, Realm, Alignment

        bridge = FractalStatRAGBridge()
        realm = Realm(type="test", label="test")
        alignment = Alignment(type="harmonic")
        fractalstat = FractalStatAddress(
            realm=realm,
            lineage=0,
            adjacency=50.0,
            horizon="scene",
            luminosity=50.0,
            polarity=0.0,
            dimensionality=3,
            alignment=alignment
        )

        documents = [
            RAGDocument(
                id=f"doc-{i}",
                text=f"Document {i}",
                embedding=[float(i), 0.0, 0.0],
                fractalstat=fractalstat
            )
            for i in range(5)
        ]

        results = bridge.retrieve(
            documents,
            [2.0, 0.0, 0.0],
            fractalstat,
            k=3
        )

        assert len(results) == 3


class TestCompareRetrievalResults:
    """Test compare_retrieval_results analysis function."""

    def test_compare_retrieval_results(self):
        """compare_retrieval_results should analyze differences."""
        from warbler_cda.fractalstat_rag_bridge import compare_retrieval_results

        semantic_results = [
            ("doc-1", 0.9),
            ("doc-2", 0.8),
            ("doc-3", 0.7)
        ]

        hybrid_results = [
            ("doc-1", 0.95),
            ("doc-3", 0.85),
            ("doc-2", 0.75)
        ]

        comparison = compare_retrieval_results(semantic_results, hybrid_results, k=3)

        assert "overlap_count" in comparison
        assert "overlap_pct" in comparison
        assert "semantic_avg_score" in comparison
        assert "hybrid_avg_score" in comparison
        assert "score_improvement" in comparison
        assert "avg_reranking_distance" in comparison
        assert "intelligence_signal" in comparison

    def test_compare_retrieval_results_perfect_overlap(self):
        """compare_retrieval_results should detect perfect overlap."""
        from warbler_cda.fractalstat_rag_bridge import compare_retrieval_results

        results = [("doc-1", 0.9), ("doc-2", 0.8), ("doc-3", 0.7)]

        comparison = compare_retrieval_results(results, results, k=3)

        assert comparison["overlap_count"] == 3
        assert comparison["overlap_pct"] == 100.0
