"""
Retrieval API - Anchor-Grounded Recall Context System

Provides anchor-grounded context retrieval and recall capabilities
for the Cognitive Geo-Thermal Lore Engine v0.3.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import time
import hashlib
from dataclasses import dataclass
from enum import Enum


class RetrievalMode(Enum):
    """Types of retrieval operations."""

    SEMANTIC_SIMILARITY = "semantic_similarity"  # Find semantically similar content
    TEMPORAL_SEQUENCE = "temporal_sequence"  # Retrieve by time sequence
    ANCHOR_NEIGHBORHOOD = "anchor_neighborhood"  # Content around specific anchors
    PROVENANCE_CHAIN = "provenance_chain"  # Follow provenance relationships
    CONFLICT_AWARE = "conflict_aware"  # Exclude conflicting content
    COMPOSITE = "composite"  # Multi-modal retrieval


@dataclass
class RetrievalQuery:
    """Structured query for context retrieval."""

    query_id: str
    mode: RetrievalMode
    anchor_ids: Optional[List[str]] = None
    semantic_query: Optional[str] = None
    temporal_range: Optional[Tuple[float, float]] = None  # (start_time, end_time)
    max_results: int = 10
    confidence_threshold: float = 0.6
    exclude_conflicts: bool = True
    include_provenance: bool = True
    query_timestamp: float = None
    fractalstat_hybrid: bool = True  # Enable FractalStat hybrid scoring
    fractalstat_address: Optional[Dict[str, Any]] = None  # FractalStat coordinates for hybrid scoring
    weight_semantic: float = 0.6  # Weight for semantic similarity in hybrid mode
    weight_fractalstat: float = 0.4  # Weight for FractalStat resonance in hybrid mode

    def __post_init__(self):
        if self.query_timestamp is None:
            self.query_timestamp = time.time()
        if self.fractalstat_hybrid and not self.fractalstat_address:
            # Default 8D FractalStat address if not specified
            self.fractalstat_address = {
                "realm": {"type": "default", "label": "retrieval_query"},
                "lineage": 0,
                "adjacency": 0.5,
                "horizon": "scene",
                "luminosity": 70.0,  # Updated scale 0-100
                "polarity": 0.0,      # Updated scale -1 to 1
                "dimensionality": 3,
                "alignment": {"type": "true_neutral"},  # 8th dimension added
            }


@dataclass
class RetrievalResult:
    """Result from a retrieval operation."""

    result_id: str
    content_type: str  # "anchor", "micro_summary", "macro_distillation", "molten_glyph"
    content_id: str
    content: str
    relevance_score: float
    temporal_distance: float  # How far from query time
    anchor_connections: List[str]  # Connected anchor IDs
    provenance_depth: int
    conflict_flags: List[str]  # Any conflicts detected
    metadata: Dict[str, Any]
    fractalstat_resonance: float = 0.0  # FractalStat hybrid scoring component (if enabled)
    semantic_similarity: float = 0.0  # Semantic scoring component (if hybrid)


@dataclass
class ContextAssembly:
    """Assembled context from multiple retrieval results."""

    assembly_id: str
    query: RetrievalQuery
    results: List[RetrievalResult]
    total_relevance: float
    temporal_span_hours: float
    anchor_coverage: List[str]
    assembly_quality: float  # Overall quality score
    conflict_summary: Dict[str, int]
    retrieval_timestamp: float


class RetrievalAPI:
    """
    Anchor-grounded context retrieval system with optional FractalStat hybrid scoring.

    Provides intelligent context assembly by combining semantic anchors,
    micro-summaries, macro distillations, and memory fragments with
    conflict awareness and provenance tracking.

    Supports FractalStat hybrid scoring for multi-dimensional retrieval when enabled.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        semantic_anchors=None,
        summarization_ladder=None,
        conflict_detector=None,
        embedding_provider=None,
        fractalstat_bridge=None,
    ):
        """Initialize the retrieval API."""
        self.config = config or {}

        # Component dependencies
        self.semantic_anchors = semantic_anchors
        self.summarization_ladder = summarization_ladder
        self.conflict_detector = conflict_detector
        self.embedding_provider = embedding_provider
        self.fractalstat_bridge = fractalstat_bridge  # Optional FractalStat RAG bridge for hybrid scoring

        # Configuration parameters
        self.default_max_results = self.config.get("default_max_results", 10)
        self.relevance_threshold = self.config.get("relevance_threshold", 0.5)
        self.temporal_decay_hours = self.config.get("temporal_decay_hours", 24)
        self.quality_threshold = self.config.get("quality_threshold", 0.6)

        # FractalStat hybrid scoring configuration
        self.enable_fractalstat_hybrid = self.config.get("enable_fractalstat_hybrid", False)
        self.default_weight_semantic = self.config.get("default_weight_semantic", 0.6)
        self.default_weight_fractalstat = self.config.get("default_weight_fractalstat", 0.4)

        # Retrieval cache (for performance)
        self.query_cache: Dict[str, ContextAssembly] = {}
        self.cache_ttl_seconds = self.config.get("cache_ttl_seconds", 300)  # 5 minutes

        # Document FractalStat assignments cache (for rapid re-retrieval)
        self.document_fractalstat_cache: Dict[str, Dict[str, Any]] = {}

        # Simple in-memory document store for ingestion
        self._context_store: Dict[str, Dict[str, Any]] = {}

        # Metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "hybrid_queries": 0,
            "average_results_per_query": 0.0,
            "average_retrieval_time_ms": 0.0,
            "quality_distribution": {"high": 0, "medium": 0, "low": 0},
        }

    def retrieve_context(self, query: Union[RetrievalQuery, Dict[str, Any]]) -> ContextAssembly:
        """
        Main retrieval method - assemble context based on query.

        Args:
            query: RetrievalQuery object or dict with query parameters

        Returns:
            ContextAssembly with retrieved and assembled context
        """
        start_time = time.time()

        # Convert dict to RetrievalQuery if needed
        if isinstance(query, dict):
            query = self._dict_to_query(query)

        self.metrics["total_queries"] += 1

        # Check cache first
        cache_key = self._generate_cache_key(query)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.metrics["cache_hits"] += 1
            return cached_result

        self.metrics["cache_misses"] += 1

        # Perform retrieval based on mode
        results = []

        if query.mode == RetrievalMode.SEMANTIC_SIMILARITY:
            results = self._retrieve_semantic_similarity(query)
        elif query.mode == RetrievalMode.TEMPORAL_SEQUENCE:
            results = self._retrieve_temporal_sequence(query)
        elif query.mode == RetrievalMode.ANCHOR_NEIGHBORHOOD:
            results = self._retrieve_anchor_neighborhood(query)
        elif query.mode == RetrievalMode.PROVENANCE_CHAIN:
            results = self._retrieve_provenance_chain(query)
        elif query.mode == RetrievalMode.CONFLICT_AWARE:
            results = self._retrieve_conflict_aware(query)
        elif query.mode == RetrievalMode.COMPOSITE:
            results = self._retrieve_composite(query)
        else:
            # Default to semantic similarity
            results = self._retrieve_semantic_similarity(query)

        # Filter and rank results
        filtered_results = self._filter_and_rank_results(results, query)

        # Assemble final context
        assembly = self._assemble_context(query, filtered_results)

        # Cache result
        self._cache_result(cache_key, assembly)

        # Update metrics
        elapsed_ms = (time.time() - start_time) * 1000
        self._update_metrics(assembly, elapsed_ms)

        return assembly

    def query_semantic_anchors(
        self, query_text: str, max_results: int = 5
    ) -> List[RetrievalResult]:
        """
        Quick semantic anchor query for simple use cases.

        Args:
            query_text: Text to find similar anchors for
            max_results: Maximum number of results

        Returns:
            List of RetrievalResult objects for matching anchors
        """
        query = RetrievalQuery(
            query_id=f"quick_{int(time.time())}",
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query=query_text,
            max_results=max_results,
        )

        assembly = self.retrieve_context(query)
        return assembly.results

    def get_anchor_context(self, anchor_id: str, context_radius: int = 3) -> ContextAssembly:
        """
        Get context around a specific anchor.

        Args:
            anchor_id: ID of anchor to get context for
            context_radius: How many related items to include

        Returns:
            ContextAssembly with anchor neighborhood context
        """
        query = RetrievalQuery(
            query_id=f"anchor_ctx_{anchor_id}_{int(time.time())}",
            mode=RetrievalMode.ANCHOR_NEIGHBORHOOD,
            anchor_ids=[anchor_id],
            max_results=context_radius * 2,
        )

        return self.retrieve_context(query)

    def trace_provenance(self, content_id: str, max_depth: int = 5) -> ContextAssembly:
        """
        Trace provenance chain for a piece of content.

        Args:
            content_id: ID of content to trace
            max_depth: Maximum provenance depth

        Returns:
            ContextAssembly with provenance chain
        """
        query = RetrievalQuery(
            query_id=f"prov_{content_id}_{int(time.time())}",
            mode=RetrievalMode.PROVENANCE_CHAIN,
            anchor_ids=[content_id],
            max_results=max_depth,
        )

        return self.retrieve_context(query)

    def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any] = None,
        embedding: Optional[List[float]] = None,
        fractalstat_coordinates: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add a document to the context store for retrieval.

        Args:
            doc_id: Unique document identifier
            content: Document content
            metadata: Optional metadata (realm, type, etc.)
            embedding: Optional pre-computed embedding vector
            fractalstat_coordinates: Optional pre-computed FractalStat coordinates

        Returns:
            True if added successfully
        """
        if doc_id in self._context_store:
            return False  # Document already exists

        doc_entry = {
            "content": content,
            "metadata": metadata or {},
            "added_at": time.time(),
            "length": len(content),
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
        }

        if embedding is None and self.embedding_provider:
            embedding = self.embedding_provider.embed_text(content)

        if embedding:
            doc_entry["embedding"] = embedding

        if (
            fractalstat_coordinates is None
            and embedding
            and hasattr(self.embedding_provider, "compute_fractalstat_from_embedding")
        ):
            fractalstat_coordinates = self.embedding_provider.compute_fractalstat_from_embedding(embedding)

        if fractalstat_coordinates:
            doc_entry["fractalstat_coordinates"] = fractalstat_coordinates

        self._context_store[doc_id] = doc_entry
        return True

    def get_context_store_size(self) -> int:
        """Get number of documents in context store."""
        return len(self._context_store)

    def get_retrieval_metrics(self) -> Dict[str, Any]:
        """Get retrieval performance and usage metrics."""
        return {
            "retrieval_metrics": self.metrics.copy(),
            "cache_performance": {
                "hit_rate": self._calculate_cache_hit_rate(),
                "cache_size": len(self.query_cache),
                "cache_efficiency": self._calculate_cache_efficiency(),
            },
            "context_store_size": self.get_context_store_size(),
            "system_health": {
                "components_available": self._check_component_availability(),
                "average_quality": self._calculate_average_quality(),
                "retrieval_success_rate": self._calculate_success_rate(),
            },
        }

    def _dict_to_query(self, query_dict: Dict[str, Any]) -> RetrievalQuery:
        """Convert dictionary to RetrievalQuery object."""
        return RetrievalQuery(
            query_id=query_dict.get("query_id", f"query_{int(time.time())}"),
            mode=RetrievalMode(query_dict.get("mode", "semantic_similarity")),
            anchor_ids=query_dict.get("anchor_ids"),
            semantic_query=query_dict.get("semantic_query"),
            temporal_range=query_dict.get("temporal_range"),
            max_results=query_dict.get("max_results", self.default_max_results),
            confidence_threshold=query_dict.get("confidence_threshold", 0.6),
            exclude_conflicts=query_dict.get("exclude_conflicts", True),
            include_provenance=query_dict.get("include_provenance", True),
            fractalstat_hybrid=query_dict.get("fractalstat_hybrid", self.enable_fractalstat_hybrid),
            fractalstat_address=query_dict.get("fractalstat_address"),
            weight_semantic=query_dict.get("weight_semantic", self.default_weight_semantic),
            weight_fractalstat=query_dict.get("weight_fractalstat", self.default_weight_fractalstat),
        )

    def _retrieve_semantic_similarity(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieve content based on semantic similarity."""
        results = []

        if not query.semantic_query:
            return results

        # DEBUG
        import sys

        print(
            f"DEBUG: _retrieve_semantic_similarity called with query='{query.semantic_query}'",
            file=sys.stderr,
        )
        print(
            f"DEBUG: embedding_provider={self.embedding_provider}, "
            f"semantic_anchors={self.semantic_anchors}",
            file=sys.stderr,
        )
        print(f"DEBUG: context_store size={len(self._context_store)}", file=sys.stderr)

        # If embedding provider available, use it
        if self.embedding_provider:
            # Get query embedding
            try:
                query_embedding = self.embedding_provider.embed_text(query.semantic_query)
            except OSError:
                return results

        # Search semantic anchors
        if self.semantic_anchors:
            for anchor_id, anchor in self.semantic_anchors.anchors.items():
                if anchor.embedding:
                    query_embedding = self.embedding_provider.embed_text(query.semantic_query)
                    similarity = self.embedding_provider.calculate_similarity(
                        query_embedding, anchor.embedding
                    )

                    if similarity >= query.confidence_threshold:
                        result = RetrievalResult(
                            result_id=f"anchor_{anchor_id}",
                            content_type="anchor",
                            content_id=anchor_id,
                            content=anchor.concept_text,
                            relevance_score=similarity,
                            temporal_distance=self._calculate_temporal_distance(
                                anchor.provenance.first_seen, query.query_timestamp
                            ),
                            anchor_connections=[anchor_id],
                            provenance_depth=1,
                            conflict_flags=[],
                            metadata={
                                "heat": anchor.heat,
                                "updates": anchor.provenance.update_count,
                                "semantic_drift": anchor.semantic_drift,
                            },
                        )
                        results.append(result)

        # Search micro-summaries if available
        if self.summarization_ladder:
            for micro in self.summarization_ladder.micro_summaries:
                if micro.semantic_centroid:
                    similarity = self.embedding_provider.calculate_similarity(
                        query_embedding, micro.semantic_centroid
                    )

                    if similarity >= query.confidence_threshold:
                        result = RetrievalResult(
                            result_id=f"micro_{micro.summary_id}",
                            content_type="micro_summary",
                            content_id=micro.summary_id,
                            content=micro.compressed_text,
                            relevance_score=similarity,
                            temporal_distance=self._calculate_temporal_distance(
                                micro.creation_timestamp, query.query_timestamp
                            ),
                            anchor_connections=[],
                            provenance_depth=2,
                            conflict_flags=[],
                            metadata={
                                "window_size": micro.window_size,
                                "heat_aggregate": micro.heat_aggregate,
                                "fragments": micro.window_fragments,
                            },
                        )
                        results.append(result)

        # Always search context store (uses embeddings if available, falls back to keyword)
        context_results = self._search_context_store(query)
        results.extend(context_results)

        return results

    def _search_context_store(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """
        Search context store using embeddings (semantic) or keyword fallback.
        Prefers embedding-based semantic search when available.
        """
        results = []

        if not query.semantic_query or not self._context_store:
            return results

        try:
            if self.embedding_provider and hasattr(self.embedding_provider, "semantic_search"):
                return self._search_context_store_semantic(query)
        except OSError:
            pass

        return self._search_context_store_keyword(query)

    def _search_context_store_semantic(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Search context store using semantic embeddings."""
        results = []

        if not query.semantic_query:
            return results

        embeddings_list = []
        doc_ids = []

        for doc_id, doc_data in self._context_store.items():
            if "embedding" in doc_data:
                embeddings_list.append(doc_data["embedding"])
                doc_ids.append(doc_id)

        if not embeddings_list:
            return self._search_context_store_keyword(query)

        try:
            similarities = self.embedding_provider.semantic_search(
                query.semantic_query, embeddings_list, top_k=query.max_results
            )

            for doc_idx, sim_score in similarities:
                if sim_score >= query.confidence_threshold:
                    doc_id = doc_ids[doc_idx]
                    doc_data = self._context_store[doc_id]

                    fractalstat_resonance = 0.0
                    if "fractalstat_coordinates" in doc_data and query.fractalstat_hybrid:
                        fractalstat_resonance = self._calculate_fractalstat_resonance(
                            doc_data["fractalstat_coordinates"], query.fractalstat_address
                        )

                    hybrid_score = sim_score
                    if query.fractalstat_hybrid:
                        hybrid_score = (
                            query.weight_semantic * sim_score + query.weight_fractalstat * fractalstat_resonance
                        )

                    result = RetrievalResult(
                        result_id=f"ctx_{doc_id}",
                        content_type="context_store",
                        content_id=doc_id,
                        content=doc_data.get("content", "")[:500],
                        relevance_score=hybrid_score,
                        temporal_distance=0.0,
                        anchor_connections=[],
                        provenance_depth=1,
                        conflict_flags=[],
                        metadata=doc_data.get("metadata", {}),
                        semantic_similarity=sim_score,
                        fractalstat_resonance=fractalstat_resonance,
                    )
                    results.append(result)
        except OSError:
            return self._search_context_store_keyword(query)

        return results

    def _search_context_store_keyword(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Fallback keyword-based search of context store."""
        results = []

        if not query.semantic_query:
            return results

        query_terms = query.semantic_query.lower().split()
        scored_docs = []

        for doc_id, doc_data in self._context_store.items():
            content = doc_data.get("content", "").lower()
            matches = sum(1 for term in query_terms if term in content)

            if matches > 0:
                relevance_score = (matches / len(query_terms)) ** 0.5
                scored_docs.append((doc_id, doc_data, relevance_score))

        scored_docs.sort(key=lambda x: x[2], reverse=True)

        for doc_id, doc_data, relevance_score in scored_docs[: query.max_results]:
            if relevance_score >= query.confidence_threshold:
                result = RetrievalResult(
                    result_id=f"ctx_{doc_id}",
                    content_type="context_store",
                    content_id=doc_id,
                    content=doc_data.get("content", "")[:500],
                    relevance_score=relevance_score,
                    temporal_distance=0.0,
                    anchor_connections=[],
                    provenance_depth=1,
                    conflict_flags=[],
                    metadata=doc_data.get("metadata", {}),
                    semantic_similarity=relevance_score,
                )
                results.append(result)

        return results

    def _calculate_fractalstat_resonance(
        self, doc_fractalstat: Dict[str, Any], query_fractalstat: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate 8D FractalStat resonance between document and query coordinates."""
        if not query_fractalstat or not doc_fractalstat:
            return 0.5

        try:
            # 7 dimensions from original FractalStat plus alignment (8th dimension)
            lineage_dist = abs(doc_fractalstat.get("lineage", 0.5) - query_fractalstat.get("lineage", 0.5))
            adjacency_dist = abs(
                doc_fractalstat.get("adjacency", 0.5) - query_fractalstat.get("adjacency", 0.5)
            )
            luminosity_dist = abs(
                doc_fractalstat.get("luminosity", 70.0) - query_fractalstat.get("luminosity", 70.0)
            ) / 100.0  # Normalize to 0-1 scale
            polarity_dist = abs(
                doc_fractalstat.get("polarity", 0.0) - query_fractalstat.get("polarity", 0.0)
            ) / 2.0  # Normalize from [-1,1] to [0,1]
            dimensionality_dist = abs(
                doc_fractalstat.get("dimensionality", 3) - query_fractalstat.get("dimensionality", 3)
            ) / 7.0  # Normalize from [1,8] to [0,1]

            # 8th dimension: Alignment resonance with social dynamics
            doc_alignment = doc_fractalstat.get("alignment", {}).get("type", "true_neutral")
            query_alignment = query_fractalstat.get("alignment", {}).get("type", "true_neutral")

            # Alignment synergy matrix for social coordination patterns - stricter resonance
            alignment_synergy = {
                ("harmonic", "harmonic"): 1.0,
                ("harmonic", "symbiotic"): 0.9,
                ("symbiotic", "symbiotic"): 1.0,
                ("harmonic", "entropic"): 0.3,  # Much lower for opposing dynamics
                ("entropic", "entropic"): 1.0,
                ("true_neutral", "true_neutral"): 0.7,
                ("balanced", "balanced"): 0.7,
                ("chaotic", "chaotic"): 1.0,
                ("harmonic", "chaotic"): 0.2,  # Very low for harmonic-chaotic
                ("symbiotic", "chaotic"): 0.3,
                ("chaotic", "entropic"): 0.8,
            }.get((doc_alignment, query_alignment), 0.4)  # Lower default

            alignment_resonance = alignment_synergy

            # Calculate average distance across 7 core dimensions (original FractalStat)
            core_avg_distance = (
                lineage_dist
                + adjacency_dist
                + luminosity_dist
                + polarity_dist
                + dimensionality_dist
            ) / 5.0

            # Combine core dimensions with alignment synergy - extremely strict for significant differences
            # When core distances are significant (>0.25), heavily penalize coherence
            if core_avg_distance > 0.7:
                # Very different: almost no core contribution
                core_weight = 0.001  # Minimal core contribution
                alignment_weight = 0.999  # Dominated by alignment, even if same
            elif core_avg_distance > 0.25:
                # Different: heavy core penalty
                core_weight = 0.01
                alignment_weight = 0.99
            else:
                # Moderate differences: balanced weights
                core_weight = 0.8
                alignment_weight = 0.2

            total_resonance = (core_weight * (1.0 - core_avg_distance) + alignment_weight * alignment_resonance)
            resonance = max(0.0, min(1.0, total_resonance ** 3.0))  # Even stronger decay

            return resonance
        except OSError:
            return 0.5

    def _retrieve_temporal_sequence(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieve content based on temporal sequence."""
        results = []

        if not query.temporal_range:
            # Default to last 24 hours
            end_time = query.query_timestamp
            start_time = end_time - (24 * 3600)
            temporal_range = (start_time, end_time)
        else:
            temporal_range = query.temporal_range

        # Collect items in temporal range
        temporal_items = []

        # Add anchors
        if self.semantic_anchors:
            for anchor_id, anchor in self.semantic_anchors.anchors.items():
                if temporal_range[0] <= anchor.provenance.first_seen <= temporal_range[1]:
                    temporal_items.append(
                        ("anchor", anchor_id, anchor.provenance.first_seen, anchor)
                    )

        # Add micro-summaries
        if self.summarization_ladder:
            for micro in self.summarization_ladder.micro_summaries:
                if temporal_range[0] <= micro.creation_timestamp <= temporal_range[1]:
                    temporal_items.append(
                        ("micro_summary", micro.summary_id, micro.creation_timestamp, micro)
                    )

        # Sort by timestamp
        temporal_items.sort(key=lambda x: x[2])

        # Convert to results
        for item_type, item_id, timestamp, item_data in temporal_items[: query.max_results]:
            if item_type == "anchor":
                anchor = item_data
                result = RetrievalResult(
                    result_id=f"temporal_anchor_{item_id}",
                    content_type="anchor",
                    content_id=item_id,
                    content=anchor.concept_text,
                    relevance_score=self._calculate_temporal_relevance(
                        timestamp, query.query_timestamp
                    ),
                    temporal_distance=abs(timestamp - query.query_timestamp),
                    anchor_connections=[item_id],
                    provenance_depth=1,
                    conflict_flags=[],
                    metadata={"timestamp": timestamp, "heat": anchor.heat},
                )
                results.append(result)
            elif item_type == "micro_summary":
                micro = item_data
                result = RetrievalResult(
                    result_id=f"temporal_micro_{item_id}",
                    content_type="micro_summary",
                    content_id=item_id,
                    content=micro.compressed_text,
                    relevance_score=self._calculate_temporal_relevance(
                        timestamp, query.query_timestamp
                    ),
                    temporal_distance=abs(timestamp - query.query_timestamp),
                    anchor_connections=[],
                    provenance_depth=2,
                    conflict_flags=[],
                    metadata={"timestamp": timestamp, "window_size": micro.window_size},
                )
                results.append(result)

        return results

    def _retrieve_anchor_neighborhood(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieve content in the neighborhood of specific anchors."""
        results = []

        if not query.anchor_ids or not self.semantic_anchors:
            return results

        for anchor_id in query.anchor_ids:
            if anchor_id not in self.semantic_anchors.anchors:
                continue

            target_anchor = self.semantic_anchors.anchors[anchor_id]

            # Find semantically similar anchors
            for other_id, other_anchor in self.semantic_anchors.anchors.items():
                if other_id == anchor_id:
                    continue

                if target_anchor.embedding and other_anchor.embedding:
                    similarity = self.embedding_provider.calculate_similarity(
                        target_anchor.embedding, other_anchor.embedding
                    )

                    if similarity >= query.confidence_threshold:
                        result = RetrievalResult(
                            result_id=f"neighbor_{other_id}",
                            content_type="anchor",
                            content_id=other_id,
                            content=other_anchor.concept_text,
                            relevance_score=similarity,
                            temporal_distance=abs(
                                target_anchor.provenance.first_seen
                                - other_anchor.provenance.first_seen
                            ),
                            anchor_connections=[anchor_id, other_id],
                            provenance_depth=1,
                            conflict_flags=[],
                            metadata={"neighbor_of": anchor_id, "similarity": similarity},
                        )
                        results.append(result)

        return results

    def _retrieve_provenance_chain(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieve content following provenance relationships."""
        results = []

        # This would trace through the provenance chain of anchors, micro-summaries, etc.
        # For now, implement a simplified version

        if query.anchor_ids and self.semantic_anchors:
            for anchor_id in query.anchor_ids:
                if anchor_id in self.semantic_anchors.anchors:
                    anchor = self.semantic_anchors.anchors[anchor_id]

                    # Include the anchor itself
                    result = RetrievalResult(
                        result_id=f"prov_root_{anchor_id}",
                        content_type="anchor",
                        content_id=anchor_id,
                        content=anchor.concept_text,
                        relevance_score=1.0,
                        temporal_distance=0,
                        anchor_connections=[anchor_id],
                        provenance_depth=0,
                        conflict_flags=[],
                        metadata={
                            "provenance_role": "root",
                            "updates": anchor.provenance.update_count,
                        },
                    )
                    results.append(result)

                    # Add related content from update history
                    for i, update in enumerate(anchor.provenance.update_history):
                        if i >= query.max_results - 1:
                            break

                        result = RetrievalResult(
                            result_id=f"prov_update_{anchor_id}_{i}",
                            content_type="provenance_update",
                            content_id=f"{anchor_id}_update_{i}",
                            content=(
                                f"Update: {update.get('context', {}).get('mist_id', 'unknown')}"
                            ),
                            relevance_score=0.8 - (i * 0.1),
                            temporal_distance=abs(update["timestamp"] - query.query_timestamp),
                            anchor_connections=[anchor_id],
                            provenance_depth=i + 1,
                            conflict_flags=[],
                            metadata={"update_context": update.get("context", {})},
                        )
                        results.append(result)

        return results

    def _retrieve_conflict_aware(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieve content while avoiding conflicts."""
        # First get base results
        base_results = self._retrieve_semantic_similarity(query)

        if not query.exclude_conflicts or not self.conflict_detector:
            return base_results

        # Filter out conflicting content
        filtered_results = []

        for result in base_results:
            conflicts = []

            # Check for conflicts involving this content
            if hasattr(self.conflict_detector, "get_conflict_analysis"):
                conflict_analysis = self.conflict_detector.get_conflict_analysis(result.content_id)
                if conflict_analysis.get("conflicts_found", 0) > 0:
                    conflicts = [
                        f"conflict_confidence_{conflict_analysis.get('max_confidence', 0):.2f}"
                    ]

            # Include result but flag conflicts
            result.conflict_flags = conflicts
            if not conflicts or not query.exclude_conflicts:
                filtered_results.append(result)

        return filtered_results

    def _retrieve_composite(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieve using multiple modes and combine results."""
        all_results = []

        # Semantic similarity results (highest weight)
        semantic_results = self._retrieve_semantic_similarity(query)
        for result in semantic_results:
            result.relevance_score *= 1.0  # Full weight
        all_results.extend(semantic_results)

        # Temporal sequence results (medium weight)
        temporal_results = self._retrieve_temporal_sequence(query)
        for result in temporal_results:
            result.relevance_score *= 0.7  # Reduced weight
        all_results.extend(temporal_results)

        # Anchor neighborhood results (lower weight)
        if query.anchor_ids:
            neighborhood_results = self._retrieve_anchor_neighborhood(query)
            for result in neighborhood_results:
                result.relevance_score *= 0.5  # Lower weight
            all_results.extend(neighborhood_results)

        # Remove duplicates (by content_id)
        seen_content_ids = set()
        unique_results = []
        for result in all_results:
            if result.content_id not in seen_content_ids:
                unique_results.append(result)
                seen_content_ids.add(result.content_id)

        return unique_results

    def _filter_and_rank_results(
        self, results: List[RetrievalResult], query: RetrievalQuery
    ) -> List[RetrievalResult]:
        """Filter and rank results based on query parameters."""
        # Apply FractalStat hybrid scoring if enabled
        if query.fractalstat_hybrid:
            results = self._apply_hybrid_scoring(results, query)
            self.metrics["hybrid_queries"] += 1

        # Filter by confidence threshold
        filtered = [r for r in results if r.relevance_score >= query.confidence_threshold]

        # Apply temporal decay
        for result in filtered:
            age_hours = result.temporal_distance / 3600
            decay_factor = max(0.1, 1.0 - (age_hours / self.temporal_decay_hours))
            result.relevance_score *= decay_factor

        # Sort by relevance score
        filtered.sort(key=lambda x: x.relevance_score, reverse=True)

        # Limit results
        return filtered[: query.max_results]

    def _assemble_context(
        self, query: RetrievalQuery, results: List[RetrievalResult]
    ) -> ContextAssembly:
        """Assemble final context from filtered results."""
        if not results:
            # Empty assembly
            return ContextAssembly(
                assembly_id=f"empty_{query.query_id}",
                query=query,
                results=[],
                total_relevance=0.0,
                temporal_span_hours=0.0,
                anchor_coverage=[],
                assembly_quality=0.0,
                conflict_summary={},
                retrieval_timestamp=time.time(),
            )

        # Calculate metrics
        total_relevance = sum(r.relevance_score for r in results)

        # Temporal span
        timestamps = [r.temporal_distance for r in results]
        temporal_span_hours = (
            (max(timestamps) - min(timestamps)) / 3600 if len(timestamps) > 1 else 0
        )

        # Anchor coverage
        anchor_coverage = []
        for result in results:
            anchor_coverage.extend(result.anchor_connections)
        anchor_coverage = list(set(anchor_coverage))

        # Assembly quality score
        assembly_quality = self._calculate_assembly_quality(results, query)

        # Conflict summary
        conflict_summary = {}
        for result in results:
            for flag in result.conflict_flags:
                conflict_summary[flag] = conflict_summary.get(flag, 0) + 1

        return ContextAssembly(
            assembly_id=f"assembly_{query.query_id}_{int(time.time())}",
            query=query,
            results=results,
            total_relevance=total_relevance,
            temporal_span_hours=temporal_span_hours,
            anchor_coverage=anchor_coverage,
            assembly_quality=assembly_quality,
            conflict_summary=conflict_summary,
            retrieval_timestamp=time.time(),
        )

    def _calculate_temporal_distance(self, timestamp: float, reference_time: float) -> float:
        """Calculate temporal distance between two timestamps."""
        return abs(timestamp - reference_time)

    def _calculate_temporal_relevance(self, timestamp: float, reference_time: float) -> float:
        """Calculate relevance based on temporal proximity."""
        distance_seconds = abs(timestamp - reference_time)
        distance_hours = distance_seconds / 3600

        # Exponential decay over 24 hours
        return max(0.1, 1.0 - (distance_hours / 24.0))

    def _calculate_assembly_quality(
        self, results: List[RetrievalResult], query: RetrievalQuery
    ) -> float:
        """Calculate overall quality score for assembled context."""
        if not results:
            return 0.0

        # Average relevance score
        avg_relevance = sum(r.relevance_score for r in results) / len(results)

        # Coverage score (how well we covered the query)
        coverage_score = min(len(results) / query.max_results, 1.0)

        # Conflict penalty
        total_conflicts = sum(len(r.conflict_flags) for r in results)
        conflict_penalty = max(0, 1.0 - (total_conflicts * 0.1))

        # Diversity score (different content types)
        content_types = set(r.content_type for r in results)
        diversity_score = min(len(content_types) / 3.0, 1.0)  # Max 3 types

        # Weighted average
        quality = (
            avg_relevance * 0.4
            + coverage_score * 0.2
            + conflict_penalty * 0.2
            + diversity_score * 0.2
        )

        return quality

    def _generate_cache_key(self, query: RetrievalQuery) -> str:
        """Generate cache key for query."""
        key_parts = [
            query.query_id,
            query.mode.value,
            str(query.anchor_ids) if query.anchor_ids else "none",
            query.semantic_query or "none",
            str(query.temporal_range) if query.temporal_range else "none",
            str(query.max_results),
            str(query.confidence_threshold),
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[ContextAssembly]:
        """Get cached result if still valid."""
        if cache_key in self.query_cache:
            assembly = self.query_cache[cache_key]
            age_seconds = time.time() - assembly.retrieval_timestamp
            if age_seconds < self.cache_ttl_seconds:
                return assembly
            else:
                # Remove stale cache entry
                del self.query_cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, assembly: ContextAssembly):
        """Cache retrieval result."""
        self.query_cache[cache_key] = assembly

        # Cleanup old cache entries
        current_time = time.time()
        stale_keys = [
            key
            for key, cached_assembly in self.query_cache.items()
            if current_time - cached_assembly.retrieval_timestamp > self.cache_ttl_seconds
        ]
        for key in stale_keys:
            del self.query_cache[key]

    def _update_metrics(self, assembly: ContextAssembly, elapsed_ms: float):
        """Update performance metrics."""
        self.metrics["average_results_per_query"] = (
            self.metrics["average_results_per_query"] * (self.metrics["total_queries"] - 1)
            + len(assembly.results)
        ) / self.metrics["total_queries"]

        self.metrics["average_retrieval_time_ms"] = (
            self.metrics["average_retrieval_time_ms"] * (self.metrics["total_queries"] - 1)
            + elapsed_ms
        ) / self.metrics["total_queries"]

        # Quality distribution
        if assembly.assembly_quality >= 0.8:
            self.metrics["quality_distribution"]["high"] += 1
        elif assembly.assembly_quality >= 0.6:
            self.metrics["quality_distribution"]["medium"] += 1
        else:
            self.metrics["quality_distribution"]["low"] += 1

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total_requests == 0:
            return 0.0
        return self.metrics["cache_hits"] / total_requests

    def _calculate_cache_efficiency(self) -> float:
        """Calculate cache efficiency score."""
        hit_rate = self._calculate_cache_hit_rate()
        cache_size_penalty = min(len(self.query_cache) / 100.0, 0.2)  # Penalty for large cache
        return max(0, hit_rate - cache_size_penalty)

    def _check_component_availability(self) -> Dict[str, bool]:
        """Check availability of dependent components."""
        return {
            "semantic_anchors": self.semantic_anchors is not None,
            "summarization_ladder": self.summarization_ladder is not None,
            "conflict_detector": self.conflict_detector is not None,
            "embedding_provider": self.embedding_provider is not None,
            "fractalstat_bridge": self.fractalstat_bridge is not None,
        }

    def _calculate_average_quality(self) -> float:
        """Calculate average assembly quality."""
        total_quality = sum(self.metrics["quality_distribution"].values())
        if total_quality == 0:
            return 0.0

        weighted_quality = (
            self.metrics["quality_distribution"]["high"] * 1.0
            + self.metrics["quality_distribution"]["medium"] * 0.7
            + self.metrics["quality_distribution"]["low"] * 0.3
        )

        return weighted_quality / total_quality

    def _calculate_success_rate(self) -> float:
        """Calculate retrieval success rate."""
        successful_retrievals = (
            self.metrics["quality_distribution"]["high"]
            + self.metrics["quality_distribution"]["medium"]
        )
        total_retrievals = sum(self.metrics["quality_distribution"].values())

        if total_retrievals == 0:
            return 1.0

        return successful_retrievals / total_retrievals

    # ========================================================================
    # FractalStat Hybrid Scoring Support (Phase 2)
    # ========================================================================

    def _auto_assign_fractalstat_address(
        self, content_id: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Auto-assign FractalStat address to content based on metadata.

        Supports fallback to default if metadata incomplete.

        Args:
            content_id: ID of the content being assigned
            metadata: Document metadata with optional realm, lineage, etc.

        Returns:
            FractalStat address dictionary with all 8 dimensions
        """
        # Check cache first
        if content_id in self.document_fractalstat_cache:
            return self.document_fractalstat_cache[content_id]

        # Extract from metadata or use defaults
        realm_type = metadata.get("realm_type", "data")
        realm_label = metadata.get("realm_label", "content")
        lineage = metadata.get("lineage", 0)

        # Compute adjacency from connectivity hints
        adjacency = min(1.0, metadata.get("connection_count", 0) / 10.0)

        # Horizon from lifecycle stage
        lifecycle = metadata.get("lifecycle_stage", "scene")
        horizon_map = {
            "genesis": "logline",
            "emergence": "outline",
            "peak": "scene",
            "decay": "panel",
        }
        horizon = horizon_map.get(lifecycle, "scene")

        # Luminosity from activity/heat
        luminosity = min(1.0, max(0.0, metadata.get("activity_level", 0.5)))

        # Polarity from update frequency / resonance
        polarity = min(1.0, metadata.get("resonance_factor", 0.5))

        # Dimensionality from thread count
        thread_count = metadata.get("thread_count", 3)
        dimensionality = min(8, max(1, thread_count))  # Updated to allow up to 8

        # Alignment from social/coordination hints
        alignment_type = metadata.get("alignment_type", "true_neutral")

        fractalstat_address = {
            "realm": {"type": realm_type, "label": realm_label},
            "lineage": lineage,
            "adjacency": round(adjacency, 2),
            "horizon": horizon,
            "luminosity": round(luminosity, 2),
            "polarity": round(polarity, 2),
            "dimensionality": dimensionality,
            "alignment": {"type": alignment_type},
        }

        # Cache the assignment
        self.document_fractalstat_cache[content_id] = fractalstat_address
        return fractalstat_address

    def _apply_hybrid_scoring(
        self, results: List[RetrievalResult], query: RetrievalQuery
    ) -> List[RetrievalResult]:
        """
        Apply FractalStat hybrid scoring to retrieval results.

        Combines semantic similarity with FractalStat resonance scoring.
        Updates relevance_score to reflect hybrid score.

        Args:
            results: Initial retrieval results with semantic scores
            query: Query object with FractalStat address and weights

        Returns:
            Results with updated hybrid relevance scores
        """
        if not query.fractalstat_hybrid or not self.fractalstat_bridge:
            return results  # No hybrid scoring if not enabled or bridge missing

        try:
            from warbler_cda.fractalstat_rag_bridge import FractalStatAddress as FractalStatAddress, Realm
        except ImportError:
            # Fallback if bridge not available
            return results

        # Convert query FractalStat dict to FractalStatAddress object
        if not query.fractalstat_address:
            return results

        try:
            q_fractalstat_dict = query.fractalstat_address
            query_realm = Realm(
                type=q_fractalstat_dict["realm"]["type"], label=q_fractalstat_dict["realm"]["label"]
            )
            # Get alignment from query address or default to true_neutral
            query_alignment_type = q_fractalstat_dict.get("alignment", {}).get("type", "true_neutral")
            from warbler_cda.fractalstat_rag_bridge import Alignment as BridgeAlignment
            query_alignment = BridgeAlignment(type=query_alignment_type)

            query_fractalstat = FractalStatAddress(
                realm=query_realm,
                lineage=q_fractalstat_dict["lineage"],
                adjacency=q_fractalstat_dict["adjacency"],
                horizon=q_fractalstat_dict["horizon"],
                luminosity=q_fractalstat_dict["luminosity"],
                polarity=q_fractalstat_dict["polarity"],
                dimensionality=q_fractalstat_dict["dimensionality"],
                alignment=query_alignment,
            )
        except OSError:
            # Invalid FractalStat address, fall back to semantic
            return results

        # Apply hybrid scoring to each result
        for result in results:
            # Get or compute FractalStat address for this result's content
            if "fractalstat" not in result.metadata:
                # Auto-assign if not already present
                result.metadata["fractalstat"] = self._auto_assign_fractalstat_address(
                    result.content_id, result.metadata
                )

            # Extract document FractalStat address
            doc_fractalstat_dict = result.metadata.get("fractalstat", {})
            if not doc_fractalstat_dict:
                continue

            try:
                doc_realm = Realm(
                    type=doc_fractalstat_dict["realm"]["type"], label=doc_fractalstat_dict["realm"]["label"]
                )
                # Get alignment from document address or default to true_neutral
                doc_alignment_type = doc_fractalstat_dict.get("alignment", {}).get("type", "true_neutral")
                doc_alignment = BridgeAlignment(type=doc_alignment_type)

                doc_fractalstat = FractalStatAddress(
                    realm=doc_realm,
                    lineage=doc_fractalstat_dict["lineage"],
                    adjacency=doc_fractalstat_dict["adjacency"],
                    horizon=doc_fractalstat_dict["horizon"],
                    luminosity=doc_fractalstat_dict["luminosity"],
                    polarity=doc_fractalstat_dict["polarity"],
                    dimensionality=doc_fractalstat_dict["dimensionality"],
                    alignment=doc_alignment,
                )
            except OSError:
                # Skip if document FractalStat invalid
                continue

            # Compute FractalStat resonance score
            fractalstat_res = self.fractalstat_bridge.fractalstat_resonance(query_fractalstat, doc_fractalstat)
            result.fractalstat_resonance = fractalstat_res

            # Compute semantic similarity (if available)
            semantic_sim = result.relevance_score  # Current score is semantic
            result.semantic_similarity = semantic_sim

            # Combine into hybrid score
            hybrid = (query.weight_semantic * semantic_sim) + (query.weight_fractalstat * fractalstat_res)
            result.relevance_score = max(0.0, min(hybrid, 1.0))

        return results

    def _get_fractalstat_address_for_content(
        self, content_id: str, metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get or compute FractalStat address for content with caching.

        Args:
            content_id: ID of content
            metadata: Content metadata

        Returns:
            FractalStat address dictionary or None
        """
        if content_id in self.document_fractalstat_cache:
            return self.document_fractalstat_cache[content_id]

        return self._auto_assign_fractalstat_address(content_id, metadata)
