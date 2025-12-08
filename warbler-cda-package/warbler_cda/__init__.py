"""
Warbler CDA - Cognitive Development Architecture RAG System.

A production-ready RAG (Retrieval-Augmented Generation) system with FractalStat
8-dimensional addressing for intelligent document retrieval.

Features:
- Semantic anchor-based memory with provenance tracking
- FractalStat 8-dimensional addressing for hybrid scoring
- Hierarchical summarization with micro/macro distillation
- Conflict detection and resolution
- Memory pooling for performance optimization
- Production API with FastAPI
"""

__version__ = "0.1.0"
__author__ = "Tiny Walnut Games"
__license__ = "MIT"

# Core components
from .retrieval_api import (
    RetrievalAPI,
    RetrievalQuery,
    RetrievalMode,
    RetrievalResult,
    ContextAssembly,
)
from .semantic_anchors import SemanticAnchorGraph
from warbler_cda.anchor_data_classes import SemanticAnchor, AnchorProvenance
from warbler_cda.anchor_memory_pool import AnchorMemoryPool, get_global_anchor_pool
from .summarization_ladder import SummarizationLadder, MicroSummary, MacroDistillation
from .conflict_detector import ConflictDetector, ConflictType, ConflictEvidence
from .castle_graph import CastleGraph
from .melt_layer import MeltLayer, MagmaStore
from .evaporation import EvaporationEngine, CloudStore

# FractalStat System (8D upgrade from 7D FractalStat)
from .fractalstat_rag_bridge import (
    FractalStatRAGBridge,
    FractalStatAddress,
    Alignment,
    Realm,
    RAGDocument,
    fractalstat_resonance,
    compare_retrieval_results,
    cosine_similarity,
    generate_random_fractalstat_address,
    generate_synthetic_rag_documents,
    hybrid_score,
    retrieve,
    retrieve_semantic_only,
)
from .fractalstat_entity import (
    Alignment as EntityAlignment,
    DataClass,
    Capability,
    FractalStatCoordinates,
    FractalStatEntity,
    Horizon,
    Polarity,
    Realm as EntityRealm,
    compute_adjacency_score,
    hash_for_coordinates,
)
from .fractalstat_experiments import (
    run_all_experiments,
)

# Backward compatibility aliases (upgrade from 7D FractalStat)
# These are already imported above, no aliases needed

# Embeddings (optional - may not be available without ML dependencies)
try:
    from warbler_cda.embeddings import (
        EmbeddingProvider,
        EmbeddingProviderFactory,
        LocalEmbeddingProvider,
        OpenAIEmbeddingProvider,
        SentenceTransformerEmbeddingProvider,
    )
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    # ML dependencies (torch, transformers) not available
    EmbeddingProvider = None
    EmbeddingProviderFactory = None
    LocalEmbeddingProvider = None
    OpenAIEmbeddingProvider = None
    SentenceTransformerEmbeddingProvider = None
    EMBEDDINGS_AVAILABLE = False
    import warnings
    warnings.warn(
        "Embedding providers not available (torch/transformers not installed). "
        "Install with: pip install torch sentence-transformers",
        ImportWarning
    )

__all__ = [
    # Core RAG
    "RetrievalAPI",
    "RetrievalQuery",
    "RetrievalMode",
    "RetrievalResult",
    "ContextAssembly",
    "SemanticAnchorGraph",
    "SemanticAnchor",
    "AnchorProvenance",
    "AnchorMemoryPool",
    "get_global_anchor_pool",
    "SummarizationLadder",
    "MicroSummary",
    "MacroDistillation",
    "ConflictDetector",
    "ConflictType",
    "ConflictEvidence",
    "CastleGraph",
    "MeltLayer",
    "MagmaStore",
    "EvaporationEngine",
    "CloudStore",
    # FractalStat (8D upgrade)
    "FractalStatRAGBridge",
    "FractalStatAddress",
    "Alignment",
    "Realm",
    "RAGDocument",
    "fractalstat_resonance",
    "compare_retrieval_results",
    "cosine_similarity",
    "generate_random_fractalstat_address",
    "generate_synthetic_rag_documents",
    "hybrid_score",
    "retrieve",
    "retrieve_semantic_only",
    "FractalStatCoordinates",
    "FractalStatEntity",
    "EntityRealm",
    "Horizon",
    "Polarity",
    "EntityAlignment",
    "DataClass",
    "Capability",
    "compute_adjacency_score",
    "hash_for_coordinates",
    "run_all_experiments",
    # Legacy aliases (7D FractalStat compatibility)
    "FractalStatRAGBridge",
    "FractalStatAddress",
    "fractalstat_resonance",
    "FractalStatEntity",
    "FractalStatCoordinates",
    # Embeddings
    "EmbeddingProvider",
    "EmbeddingProviderFactory",
    "LocalEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "SentenceTransformerEmbeddingProvider",
]
