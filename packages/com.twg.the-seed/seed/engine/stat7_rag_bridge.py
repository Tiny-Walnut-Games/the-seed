"""
STAT7-RAG Bridge: Realm-Agnostic Hybrid Scoring for Document Retrieval

Bridges RAG documents with STAT7 addressing coordinates for intelligent,
multi-dimensional hybrid scoring that combines semantic similarity with
STAT7 entanglement resonance.

Supports any realm type (game, system, faculty, pattern, data, business, concept, etc.)
and scales deterministically to 10K+ documents.

Author: The Seed Phase 1 Integration
Status: Production-ready validation bridge
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional
import math
import random


# ============================================================================
# Data Structures: Realm-Agnostic STAT7 Addressing
# ============================================================================

@dataclass
class Realm:
    """Flexible realm definition for any relationship domain."""
    type: str   # e.g. "game", "system", "faculty", "pattern", "data", "narrative", "business", "concept"
    label: str  # human-readable name


@dataclass
class STAT7Address:
    """
    STAT7 coordinate system: 7 dimensions for unique, multidimensional addressing.
    
    - realm: Domain/context (flexible type + label)
    - lineage: Version/generation (int >= 0)
    - adjacency: Graph connectivity score (0.0-1.0)
    - horizon: Zoom level / lifecycle stage (logline, outline, scene, panel, etc.)
    - luminosity: Clarity/coherence/activity (0.0-1.0)
    - polarity: Tension/contrast/resonance (0.0-1.0)
    - dimensionality: Complexity/thread count (1-7 or bucketed)
    """
    realm: Realm
    lineage: int
    adjacency: float
    horizon: str
    luminosity: float
    polarity: float
    dimensionality: int

    def __post_init__(self):
        """Validate STAT7 constraints."""
        assert 0.0 <= self.adjacency <= 1.0, f"adjacency must be [0,1], got {self.adjacency}"
        assert 0.0 <= self.luminosity <= 1.0, f"luminosity must be [0,1], got {self.luminosity}"
        assert 0.0 <= self.polarity <= 1.0, f"polarity must be [0,1], got {self.polarity}"
        assert self.lineage >= 0, f"lineage must be >= 0, got {self.lineage}"
        assert 1 <= self.dimensionality <= 7, f"dimensionality must be [1,7], got {self.dimensionality}"

    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary for serialization."""
        return {
            "realm": {"type": self.realm.type, "label": self.realm.label},
            "lineage": self.lineage,
            "adjacency": self.adjacency,
            "horizon": self.horizon,
            "luminosity": self.luminosity,
            "polarity": self.polarity,
            "dimensionality": self.dimensionality,
        }


@dataclass
class RAGDocument:
    """RAG document enhanced with STAT7 addressing."""
    id: str
    text: str
    embedding: List[float]
    stat7: STAT7Address
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate document structure."""
        assert len(self.embedding) > 0, f"embedding must not be empty for {self.id}"


# ============================================================================
# Scoring Functions: Semantic + STAT7 Hybrid
# ============================================================================

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    Range: [-1, 1], typically [0, 1] for normalized embeddings.
    """
    if not a or not b:
        return 0.0
    
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    
    denom = norm_a * norm_b + 1e-12  # Avoid division by zero
    return dot / denom


def stat7_resonance(query_stat7: STAT7Address, doc_stat7: STAT7Address) -> float:
    """
    Compute STAT7 resonance between query and document addresses.
    
    This is the "entanglement score" — how well-aligned are the 7 dimensions?
    
    Scoring strategy:
    - Realm match (type > label): 1.0 if type matches, 0.85 if not; +0.1 if label matches
    - Horizon alignment: 1.0 if same, 0.9 if adjacent, 0.7 if different
    - Lineage proximity: decay by generation distance (±1 best)
    - Signal alignment: how close are luminosity/polarity? (0.0-1.0)
    - Adjacency/Dimensionality: connectivity and complexity bonuses
    
    Returns: [0.0, 1.0] resonance score
    """
    # Realm match (type is primary, label is secondary boost)
    realm_score = 1.0 if query_stat7.realm.type == doc_stat7.realm.type else 0.85
    if query_stat7.realm.label == doc_stat7.realm.label:
        realm_score += 0.1
    realm_score = min(realm_score, 1.0)  # Cap at 1.0
    
    # Horizon alignment: scale by distance
    horizon_levels = {"logline": 1, "outline": 2, "scene": 3, "panel": 4}
    h_query = horizon_levels.get(query_stat7.horizon, 3)
    h_doc = horizon_levels.get(doc_stat7.horizon, 3)
    h_distance = abs(h_query - h_doc)
    
    if h_distance == 0:
        horizon_score = 1.0
    elif h_distance == 1:
        horizon_score = 0.9
    else:
        horizon_score = 0.7
    
    # Lineage proximity: prefer ±0-1 generation distance
    lineage_distance = abs(query_stat7.lineage - doc_stat7.lineage)
    lineage_score = max(0.7, 1.0 - 0.05 * lineage_distance)
    
    # Signal alignment: luminosity + polarity
    luminosity_diff = abs(query_stat7.luminosity - doc_stat7.luminosity)
    polarity_diff = abs(query_stat7.polarity - doc_stat7.polarity)
    signal_score = 1.0 - 0.5 * (luminosity_diff + polarity_diff)
    signal_score = max(0.0, signal_score)
    
    # Adjacency/Dimensionality bonus: connectivity + complexity
    adj_bonus = doc_stat7.adjacency  # Prefer well-connected docs
    dim_bonus = min(1.0, doc_stat7.dimensionality / 7.0)  # Normalize to [0,1]
    adj_dim_score = 0.5 * adj_bonus + 0.5 * dim_bonus
    
    # Combine all scores (multiplicative for strict alignment, additive bonus for complexity)
    resonance = realm_score * horizon_score * lineage_score * signal_score
    resonance *= (0.8 + 0.2 * adj_dim_score)  # 20% bonus from connectivity/complexity
    
    return max(0.0, min(resonance, 1.0))  # Clamp to [0,1]


def hybrid_score(
    query_embedding: List[float],
    doc: RAGDocument,
    query_stat7: STAT7Address,
    weight_semantic: float = 0.6,
    weight_stat7: float = 0.4,
) -> float:
    """
    Hybrid scoring: combine semantic similarity with STAT7 resonance.
    
    Args:
        query_embedding: Query embedding vector
        doc: RAG document with embedding and STAT7 address
        query_stat7: Query STAT7 address
        weight_semantic: Weight for semantic similarity (default 0.6)
        weight_stat7: Weight for STAT7 resonance (default 0.4)
    
    Returns: [0.0, 1.0] hybrid score
    """
    assert weight_semantic + weight_stat7 == 1.0, "Weights must sum to 1.0"
    
    semantic_sim = cosine_similarity(query_embedding, doc.embedding)
    stat7_res = stat7_resonance(query_stat7, doc.stat7)
    
    hybrid = (weight_semantic * semantic_sim) + (weight_stat7 * stat7_res)
    return max(0.0, min(hybrid, 1.0))  # Clamp to [0,1]


# ============================================================================
# Retrieval: Hybrid RAG Search
# ============================================================================

def retrieve(
    documents: List[RAGDocument],
    query_embedding: List[float],
    query_stat7: STAT7Address,
    k: int = 10,
    weight_semantic: float = 0.6,
    weight_stat7: float = 0.4,
) -> List[Tuple[str, float]]:
    """
    Retrieve top-k documents using hybrid (semantic + STAT7) scoring.
    
    Args:
        documents: List of RAG documents to search
        query_embedding: Query embedding vector
        query_stat7: Query STAT7 address
        k: Number of results to return
        weight_semantic: Weight for semantic similarity
        weight_stat7: Weight for STAT7 resonance
    
    Returns: List of (doc_id, hybrid_score) tuples, sorted by score (descending)
    """
    scores = []
    for doc in documents:
        score = hybrid_score(query_embedding, doc, query_stat7, weight_semantic, weight_stat7)
        scores.append((doc.id, score))
    
    # Sort by score descending, return top-k
    return sorted(scores, key=lambda x: x[1], reverse=True)[:k]


def retrieve_semantic_only(
    documents: List[RAGDocument],
    query_embedding: List[float],
    k: int = 10,
) -> List[Tuple[str, float]]:
    """
    Retrieve top-k documents using semantic similarity only (baseline).
    
    Args:
        documents: List of RAG documents to search
        query_embedding: Query embedding vector
        k: Number of results to return
    
    Returns: List of (doc_id, semantic_score) tuples, sorted by score (descending)
    """
    scores = []
    for doc in documents:
        score = cosine_similarity(query_embedding, doc.embedding)
        scores.append((doc.id, score))
    
    return sorted(scores, key=lambda x: x[1], reverse=True)[:k]


# ============================================================================
# Utilities: Document Generation & STAT7 Randomization
# ============================================================================

def generate_random_stat7_address(
    realm: Realm,
    lineage_range: Tuple[int, int] = (0, 10),
    horizon_choices: Optional[List[str]] = None,
    seed_offset: int = 0,
) -> STAT7Address:
    """
    Generate a random STAT7 address with optional seeding.
    
    Args:
        realm: Realm for this address
        lineage_range: Min/max for lineage generation
        horizon_choices: List of horizon options (default: common levels)
        seed_offset: For reproducibility, offset from global random state
    
    Returns: Randomized STAT7Address
    """
    if horizon_choices is None:
        horizon_choices = ["logline", "outline", "scene", "panel"]
    
    return STAT7Address(
        realm=realm,
        lineage=random.randint(lineage_range[0], lineage_range[1]),
        adjacency=round(random.random(), 2),
        horizon=random.choice(horizon_choices),
        luminosity=round(random.random(), 2),
        polarity=round(random.random(), 2),
        dimensionality=random.randint(1, 7),
    )


def generate_synthetic_rag_documents(
    base_texts: List[str],
    realm: Realm,
    scale: int,
    embedding_fn: callable,
    randomize_stat7: bool = False,
    seed: Optional[int] = None,
) -> List[RAGDocument]:
    """
    Generate synthetic RAG documents with STAT7 addresses.
    
    Args:
        base_texts: List of base text templates (will be varied)
        realm: Realm for all generated documents
        scale: Number of documents to generate
        embedding_fn: Function to embed text (e.g., embedding_provider.embed_text)
        randomize_stat7: If True, randomize all 7 STAT7 dimensions per doc
        seed: Random seed for reproducibility
    
    Returns: List of RAGDocument with embeddings and STAT7 addresses
    """
    if seed is not None:
        random.seed(seed)
    
    documents = []
    for i in range(scale):
        # Vary text template
        base_idx = i % len(base_texts)
        base_text = base_texts[base_idx]
        text = f"[Context {i}] {base_text} (instance {i})"
        
        # Embed text
        embedding = embedding_fn(text)
        
        # Assign STAT7 address
        if randomize_stat7:
            stat7 = generate_random_stat7_address(realm, seed_offset=i)
        else:
            # Deterministic: map index to STAT7 dimensions
            stat7 = STAT7Address(
                realm=realm,
                lineage=i % 10,
                adjacency=round((i % 100) / 100.0, 2),
                horizon=["logline", "outline", "scene", "panel"][i % 4],
                luminosity=round((i % 10) / 10.0, 2),
                polarity=round(((i + 5) % 10) / 10.0, 2),
                dimensionality=1 + (i % 7),
            )
        
        doc = RAGDocument(
            id=f"doc-{i:06d}",
            text=text,
            embedding=embedding,
            stat7=stat7,
            metadata={
                "source": f"pack-{base_idx % 3}",
                "category": ["core", "wisdom", "politics"][base_idx % 3],
                "generated_index": i,
            },
        )
        documents.append(doc)
    
    return documents


# ============================================================================
# Analysis: Comparison & Diagnostics
# ============================================================================

def compare_retrieval_results(
    semantic_results: List[Tuple[str, float]],
    hybrid_results: List[Tuple[str, float]],
    k: int = 10,
) -> Dict[str, Any]:
    """
    Compare semantic-only vs hybrid retrieval results.
    
    Returns metrics:
    - overlap: How many of top-k are shared?
    - semantic_avg_score: Average semantic score in top-k
    - hybrid_avg_score: Average hybrid score in top-k
    - reranking_distance: How much did hybrid rerank results?
    """
    semantic_ids = {doc_id for doc_id, _ in semantic_results[:k]}
    hybrid_ids = {doc_id for doc_id, _ in hybrid_results[:k]}
    
    overlap = len(semantic_ids & hybrid_ids)
    overlap_pct = (overlap / k * 100) if k > 0 else 0.0
    
    semantic_avg = sum(score for _, score in semantic_results[:k]) / k if k > 0 else 0.0
    hybrid_avg = sum(score for _, score in hybrid_results[:k]) / k if k > 0 else 0.0
    
    # Measure ranking distance: how far did top-k items move?
    semantic_rank = {doc_id: idx for idx, (doc_id, _) in enumerate(semantic_results[:k])}
    reranking_distances = []
    for idx, (doc_id, _) in enumerate(hybrid_results[:k]):
        if doc_id in semantic_rank:
            distance = abs(idx - semantic_rank[doc_id])
            reranking_distances.append(distance)
    
    avg_reranking_distance = (
        sum(reranking_distances) / len(reranking_distances) if reranking_distances else 0.0
    )
    
    return {
        "overlap_count": overlap,
        "overlap_pct": overlap_pct,
        "semantic_avg_score": round(semantic_avg, 4),
        "hybrid_avg_score": round(hybrid_avg, 4),
        "score_improvement": round(hybrid_avg - semantic_avg, 4),
        "avg_reranking_distance": round(avg_reranking_distance, 2),
    }


# ============================================================================
# STAT7RAGBridge: Wrapper for RetrievalAPI Integration
# ============================================================================

class STAT7RAGBridge:
    """
    Bridge class that provides STAT7 functionality for RetrievalAPI integration.
    
    Wraps the module-level STAT7 functions (stat7_resonance, hybrid_score, retrieve)
    to provide a consistent interface for the RetrievalAPI's hybrid scoring system.
    
    This allows RetrievalAPI to work with STAT7 coordinates seamlessly through
    dependency injection.
    """
    
    def stat7_resonance(self, query_stat7: STAT7Address, doc_stat7: STAT7Address) -> float:
        """
        Compute STAT7 resonance between query and document addresses.
        
        Args:
            query_stat7: Query STAT7 address
            doc_stat7: Document STAT7 address
        
        Returns: [0.0, 1.0] resonance score
        """
        return stat7_resonance(query_stat7, doc_stat7)
    
    def hybrid_score(
        self,
        query_embedding: List[float],
        doc: RAGDocument,
        query_stat7: STAT7Address,
        weight_semantic: float = 0.6,
        weight_stat7: float = 0.4,
    ) -> float:
        """
        Compute hybrid score combining semantic similarity with STAT7 resonance.
        
        Args:
            query_embedding: Query embedding vector
            doc: RAG document with embedding and STAT7 address
            query_stat7: Query STAT7 address
            weight_semantic: Weight for semantic similarity (default 0.6)
            weight_stat7: Weight for STAT7 resonance (default 0.4)
        
        Returns: [0.0, 1.0] hybrid score
        """
        return hybrid_score(query_embedding, doc, query_stat7, weight_semantic, weight_stat7)
    
    def retrieve(
        self,
        documents: List[RAGDocument],
        query_embedding: List[float],
        query_stat7: STAT7Address,
        k: int = 10,
        weight_semantic: float = 0.6,
        weight_stat7: float = 0.4,
    ) -> List[Tuple[str, float]]:
        """
        Retrieve top-k documents using hybrid (semantic + STAT7) scoring.
        
        Args:
            documents: List of RAG documents to search
            query_embedding: Query embedding vector
            query_stat7: Query STAT7 address
            k: Number of results to return
            weight_semantic: Weight for semantic similarity
            weight_stat7: Weight for STAT7 resonance
        
        Returns: List of (doc_id, hybrid_score) tuples, sorted by score (descending)
        """
        return retrieve(documents, query_embedding, query_stat7, k, weight_semantic, weight_stat7)