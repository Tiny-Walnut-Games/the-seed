"""
EXP-09 CLI API Service - FractalStat Retrieval API with Concurrency Support.

FastAPI service wrapping RetrievalAPI for concurrent queries in containerized environments.
Used for EXP-10 (Narrative Preservation) testing under concurrent load.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple, cast
from contextlib import asynccontextmanager
import asyncio
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from warbler_cda.retrieval_api import RetrievalAPI, RetrievalQuery, RetrievalMode
from warbler_cda.fractalstat_rag_bridge import FractalStatRAGBridge
from warbler_cda.pack_loader import PackLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    _init_api()
    _auto_load_packs()  # Auto-load Warbler packs on startup
    logger.info("EXP-09 API Service started")
    yield
    # Shutdown (currently no cleanup needed)


app = FastAPI(
    title="EXP-09 FractalStat CLI API Service",
    description="Concurrent FractalStat Retrieval API for EXP-10 Narrative Preservation Testing",
    version="1.0.0",
    lifespan=lifespan,
)

# Global state
_api_instance: Optional[RetrievalAPI] = None
_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=20)
_metrics: Dict[str, Any] = {
    "total_queries": 0,
    "concurrent_queries": 0,
    "max_concurrent": 0,
    "hybrid_queries": 0,
    "errors": 0,
    "start_time": datetime.now().isoformat(),
}


# Pydantic models for API contracts
class FractalStatAddress(BaseModel):
    """FractalStat coordinate specification."""

    realm: Dict[str, Any] = Field(
        default_factory=lambda: {"type": "retrieval_query", "label": "api_query"}
    )
    lineage: int = 0
    adjacency: str = "semantic_proximity"
    horizon: str = "emergence"
    luminosity: float = 0.7
    polarity: float = 0.5
    dimensionality: int = 1


class QueryRequest(BaseModel):
    """Request model for retrieval queries."""

    query_id: str
    mode: str = "semantic_similarity"
    semantic_query: Optional[str] = None
    anchor_ids: Optional[List[str]] = None
    max_results: int = 10
    confidence_threshold: float = 0.6
    fractalstat_hybrid: bool = False
    fractalstat_address: Optional[FractalStatAddress] = None
    weight_semantic: float = 0.6
    weight_fractalstat: float = 0.4


class QueryResult(BaseModel):
    """Response model for retrieval results."""

    query_id: str
    result_count: int
    results: List[Dict[str, Any]]
    semantic_similarity: Optional[float] = None
    fractalstat_resonance: Optional[float] = None
    execution_time_ms: float
    timestamp: str
    narrative_analysis: Optional[Dict[str, Any]] = None
    bob_status: Optional[str] = "PASSED"  # PASSED, VERIFIED, QUARANTINED
    bob_verification_log: Optional[Dict[str, Any]] = None  # Details of Bob's investigation


class BulkQueryRequest(BaseModel):
    """Request for concurrent bulk queries."""

    queries: List[QueryRequest]
    concurrency_level: int = 5
    include_narrative_analysis: bool = False


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    uptime_seconds: float
    total_queries: int
    concurrent_queries: int
    max_concurrent_observed: int
    hybrid_queries: int
    errors: int


def _init_api():
    """Initialize the RetrievalAPI instance."""
    global _api_instance
    if _api_instance is None:
        logger.info("Initializing RetrievalAPI with FractalStat support...")
        # Initialize with FractalStat bridge
        fractalstat_bridge = FractalStatRAGBridge()
        _api_instance = RetrievalAPI(
            fractalstat_bridge=fractalstat_bridge,
            config={
                "enable_fractalstat_hybrid": True,
                "default_weight_semantic": 0.6,
                "default_weight_fractalstat": 0.4,
            },
        )
        logger.info("RetrievalAPI initialized successfully")
    return _api_instance


def _auto_load_packs():
    """Automatically discover and load documents from Warbler packs."""
    try:
        logger.info("📚 Auto-loading Warbler packs...")

        # Initialize API instance first
        api = _init_api()

        # Create pack loader
        pack_loader = PackLoader()

        # Discover and load all documents
        documents = pack_loader.discover_documents()

        if not documents:
            logger.warning("No documents found in packs directory")
            return

        logger.info(f"Found {len(documents)} documents across {len([d for d in documents if d['id'].count('/') >= 1])} unique packs")

        # Ingest documents into API
        ingested = 0
        pack_counts = {}

        for doc in documents:
            try:
                content_id = doc["id"]
                content = doc["content"]
                metadata = doc.get("metadata", {})

                # Track pack statistics
                pack_name = metadata.get("pack", "unknown")
                pack_counts[pack_name] = pack_counts.get(pack_name, 0) + 1

                # Ingest document
                success = api.add_document(doc_id=content_id, content=content, metadata=metadata)
                if success:
                    ingested += 1

            except Exception as e:
                logger.error(f"Failed to ingest document {content_id}: {e}")

        # Log results
        total_docs = len(documents)
        logger.info(f"✓ Auto-ingested {ingested}/{total_docs} documents")

        # Log pack statistics
        for pack_name, count in sorted(pack_counts.items()):
            logger.info(f"  📦 {pack_name}: {count} documents")

        logger.info(f"🚀 Warbler CDA API ready with {api.get_context_store_size()} documents!")

    except Exception as e:
        logger.error(f"Error during auto-pack loading: {e}")
        logger.warning("Continuing with empty document store")


def _analyze_narrative_coherence(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze narrative coherence across results.

    Used to validate that meaning/story threads survive concurrent access.

    For RAG systems, narrative coherence measures:
    - Result Quality: Are retrieved results actually relevant? (primary signal)
    - Semantic Consistency: Do results cluster around similar meaning?
    - FractalStat Entanglement: Are results connected in FractalStat space?
    - Focus: Can the system concentrate results when they're relevant? (not penalize focus)

    CRITICAL INSIGHT: Good retrieval = high quality + semantic consistency.
    Diversity is only valuable if quality doesn't suffer. Don't penalize
    a system for returning 5 perfect results from one pack over 5 mediocre
    results from 5 packs.
    """
    if not results:
        return {
            "coherence_score": 0.0,
            "narrative_threads": 0,
            "avg_semantic_similarity": 0.0,
            "avg_fractalstat_resonance": 0.0,
            "avg_relevance": 0.0,
            "semantic_coherence": 0.0,
            "fractalstat_coherence": 0.0,
            "focus_coherence": 1.0,  # Perfect focus when no results (nothing to dilute)
            "result_count": 0,
            "analysis": "No results to analyze",
        }

    # Extract narrative threads from content metadata
    narrative_threads = set()
    semantic_scores = []
    fractalstat_resonances = []
    relevance_scores = []

    for result in results:
        # Primary thread identifier: use metadata.pack if available, else content_id
        pack_info = result.get("metadata", {}).get("pack", None)
        thread_id = pack_info if pack_info else result.get("id", "unknown")
        narrative_threads.add(thread_id)

        # Collect metrics
        semantic_scores.append(result.get("semantic_similarity", 0.0))
        fractalstat_resonances.append(result.get("fractalstat_resonance", 0.0))
        relevance_scores.append(result.get("relevance_score", 0.0))

    # Calculate coherence components
    avg_semantic = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0.0
    avg_fractalstat = sum(fractalstat_resonances) / len(fractalstat_resonances) if fractalstat_resonances else 0.0
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

    # 1. RESULT QUALITY (50% weight): Average relevance of all results
    # This is the primary signal - if results aren't relevant, nothing else matters
    quality_score = avg_relevance

    # 2. SEMANTIC COHERENCE (30% weight): How consistent are the semantic_similarity scores?
    # High consistency = results are semantically related to each other (not noise)
    # Uses harmonic mean of variance (robust to outliers)
    semantic_variance = sum((s - avg_semantic) ** 2 for s in semantic_scores) / max(
        1, len(semantic_scores)
    )
    semantic_coherence = 1.0 / (1.0 + semantic_variance) if semantic_variance < 1.0 else 0.0

    # 3. FractalStat ENTANGLEMENT (10% weight): Are results connected in FractalStat space?
    fractalstat_coherence = avg_fractalstat

    # 4. FOCUS COHERENCE (10% weight): Can results stay focused when relevant?
    # Instead of penalizing focused results, reward systems that produce tight, relevant clusters.
    # If avg_relevance is high, being focused is good. If low, it's neutral.
    # Focus = opposite of diversity. With high relevance, focus is a FEATURE not a bug.
    if avg_relevance > 0.8:
        # Results are highly relevant - reward focus/concentration
        # Fewer threads = tighter focus = better (when relevant)
        focus_coherence = 1.0 / (1.0 + len(narrative_threads) * 0.01)
    else:
        # Results are lower quality - diversity might help, but don't penalize either way
        focus_coherence = 0.5 + (0.5 * avg_relevance)

    # Final coherence: weighted combination prioritizing quality and consistency
    # Quality (50%) + Semantic Coherence (30%) + FractalStat (10%) + Focus (10%)
    coherence_score = (
        quality_score * 0.5
        + semantic_coherence * 0.3
        + fractalstat_coherence * 0.1
        + focus_coherence * 0.1
    )
    coherence_score = min(1.0, max(0.0, coherence_score))

    # Diagnostic logging for debugging
    if len(results) > 50:  # Only log for bulk operations
        logger.info(
            f"Coherence analysis for {len(results)} results: "
            f"quality={quality_score:.3f}, semantic_coh={semantic_coherence:.3f} (var={semantic_variance:.4f}), "
            f"fractalstat={fractalstat_coherence:.3f}, focus={focus_coherence:.3f}, "
            f"threads={len(narrative_threads)}, final={coherence_score:.3f}"
        )

    return {
        "coherence_score": coherence_score,
        "narrative_threads": len(narrative_threads),
        "avg_semantic_similarity": avg_semantic,
        "avg_fractalstat_resonance": avg_fractalstat,
        "avg_relevance": avg_relevance,
        "quality_score": quality_score,
        "semantic_coherence": semantic_coherence,
        "fractalstat_coherence": fractalstat_coherence,
        "focus_coherence": focus_coherence,
        "result_count": len(results),
        "analysis": f"Found {len(narrative_threads)} threads across {len(results)} results (quality={quality_score:.3f}, semantic={semantic_coherence:.3f}, focus={focus_coherence:.3f})",
    }


# ============================================================================
# BOB THE SKEPTIC: Anti-Cheat Information Validation
# ============================================================================
# Bob detects suspiciously perfect results (high coherence + low entanglement)
# and stress-tests them using orthogonal retrieval methods to verify their validity.
# ============================================================================


class BobSkepticConfig:
    """Tunable thresholds for Bob's suspicion detection."""

    COHERENCE_HIGH_THRESHOLD = 0.85  # Suspiciously high coherence
    ENTANGLEMENT_LOW_THRESHOLD = 0.3  # But low entanglement = suspicious
    STRESS_TEST_DIVERGENCE_THRESHOLD = 0.15  # Results differ >15% across methods = quarantine


async def _stress_test_result(
    api: RetrievalAPI,
    query: RetrievalQuery,
    original_results: List[Dict[str, Any]],
    narrative_analysis: Dict[str, Any],
) -> Tuple[bool, Dict[str, Any]]:
    """
    Stress test a suspicious result by re-querying using orthogonal retrieval methods.

    Returns: (is_consistent, verification_log)
    - is_consistent: True if results converge across methods, False if divergent
    - verification_log: Details of what was tested and findings
    """
    log = {
        "stress_test_started": datetime.now().isoformat(),
        "original_result_ids": [r.get("result_id") for r in original_results[:5]],
        "tests_run": [],
        "verdict": "UNKNOWN",
        "consistency_score": 0.0,
    }

    try:
        # Get original result IDs for comparison
        original_ids = set(r.get("result_id") for r in original_results)

        # Test 1: Pure semantic retrieval (if hybrid was used)
        if query.fractalstat_hybrid and query.semantic_query:
            logger.info(f"Bob Test 1: Pure semantic retrieval for query {query.query_id}")
            semantic_query = RetrievalQuery(
                query_id=f"{query.query_id}_bob_semantic",
                mode=RetrievalMode.SEMANTIC_SIMILARITY,
                semantic_query=query.semantic_query,
                max_results=query.max_results,
                confidence_threshold=query.confidence_threshold,
            )
            semantic_assembly = api.retrieve_context(semantic_query)
            semantic_ids = set(r.content_id for r in semantic_assembly.results)
            semantic_overlap = len(original_ids & semantic_ids) / max(1, len(original_ids))

            log["tests_run"].append(
                {
                    "test": "SEMANTIC_ONLY",
                    "overlap_ratio": semantic_overlap,
                    "result_count": len(semantic_assembly.results),
                }
            )

        # Test 2: Pure FractalStat retrieval (if hybrid was used)
        if query.fractalstat_hybrid and query.fractalstat_address:
            logger.info(f"Bob Test 2: Pure FractalStat retrieval for query {query.query_id}")
            fractalstat_query = RetrievalQuery(
                query_id=f"{query.query_id}_bob_fractalstat",
                mode=RetrievalMode.COMPOSITE,
                fractalstat_address=query.fractalstat_address,
                max_results=query.max_results,
                confidence_threshold=query.confidence_threshold,
            )
            fractalstat_assembly = api.retrieve_context(fractalstat_query)
            fractalstat_ids = set(r.content_id for r in fractalstat_assembly.results)
            fractalstat_overlap = len(original_ids & fractalstat_ids) / max(1, len(original_ids))

            log["tests_run"].append(
                {
                    "test": "FractalStat_ONLY",
                    "overlap_ratio": fractalstat_overlap,
                    "result_count": len(fractalstat_assembly.results),
                }
            )

        # Test 3: Higher confidence threshold (should return fewer, but same top results)
        if query.confidence_threshold < 0.8:
            logger.info(f"Bob Test 3: Higher confidence threshold for query {query.query_id}")
            high_conf_query = RetrievalQuery(
                query_id=f"{query.query_id}_bob_high_conf",
                mode=query.mode,
                semantic_query=query.semantic_query,
                anchor_ids=query.anchor_ids,
                max_results=query.max_results,
                confidence_threshold=min(0.85, query.confidence_threshold + 0.2),
                fractalstat_hybrid=query.fractalstat_hybrid,
                fractalstat_address=query.fractalstat_address,
            )
            high_conf_assembly = api.retrieve_context(high_conf_query)
            high_conf_ids = set(r.content_id for r in high_conf_assembly.results)
            high_conf_overlap = len(original_ids & high_conf_ids) / max(
                1, min(len(original_ids), len(high_conf_ids))
            )

            log["tests_run"].append(
                {
                    "test": "HIGH_CONFIDENCE",
                    "overlap_ratio": high_conf_overlap,
                    "result_count": len(high_conf_assembly.results),
                }
            )

        # Determine consistency: if all test overlaps are >85%, results are consistent
        if log["tests_run"]:
            consistency_scores = [t["overlap_ratio"] for t in log["tests_run"]]
            avg_consistency = sum(consistency_scores) / len(consistency_scores)
            log["consistency_score"] = avg_consistency

            if avg_consistency >= (1.0 - BobSkepticConfig.STRESS_TEST_DIVERGENCE_THRESHOLD):
                log["verdict"] = "CONSISTENT"
                is_consistent = True
            else:
                log["verdict"] = "DIVERGENT"
                is_consistent = False
        else:
            # No stress tests possible (semantic-only query), assume consistent
            log["verdict"] = "NO_TESTS_APPLICABLE"
            is_consistent = True

        log["stress_test_completed"] = datetime.now().isoformat()

    except Exception as e:
        logger.error(f"Error during Bob's stress test for {query.query_id}: {str(e)}")
        log["error"] = str(e)
        log["verdict"] = "ERROR_DURING_TEST"
        is_consistent = False  # Err on side of caution

    return is_consistent, log


async def _bob_skeptic_filter(
    narrative_analysis: Dict[str, Any],
    results_data: List[Dict[str, Any]],
    query: RetrievalQuery,
    api: RetrievalAPI,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Bob the Skeptic: Detect and verify suspiciously perfect results.

    Returns: (bob_status, verification_log)
    - bob_status: "PASSED" (normal), "VERIFIED" (suspicious but confirmed), or "QUARANTINED" (suspicious and divergent)
    - verification_log: Details of investigation (or None if no investigation needed)
    """
    coherence = narrative_analysis.get("coherence_score", 0.0)
    entanglement = narrative_analysis.get("fractalstat_coherence", 0.0)

    # Check if results are suspiciously perfect
    if (
        coherence > BobSkepticConfig.COHERENCE_HIGH_THRESHOLD
        and entanglement < BobSkepticConfig.ENTANGLEMENT_LOW_THRESHOLD
    ):
        logger.warning(
            f"🔍 BOB ALERT: Suspicious result for query {query.query_id} "
            f"(coherence={coherence:.3f}, entanglement={entanglement:.3f}). "
            f"Initiating stress test..."
        )

        # Stress test the result
        is_consistent, verification_log = await _stress_test_result(
            api=api,
            query=query,
            original_results=results_data,
            narrative_analysis=narrative_analysis,
        )

        if is_consistent:
            # Results are verified despite low entanglement
            logger.info(
                f"✅ BOB VERIFIED: Query {query.query_id} is consistent across stress tests. "
                f"High coherence is genuine, not an artifact. (consistency={verification_log.get('consistency_score', 0.0):.3f})"
            )
            return "VERIFIED", verification_log
        else:
            # Results diverge under stress testing = quarantine
            logger.warning(
                f"🚨 BOB QUARANTINE: Query {query.query_id} FAILED stress tests. "
                f"High coherence appears to be artifact or dataset bias. (consistency={verification_log.get('consistency_score', 0.0):.3f}) "
                f"Escalating to Faculty for review."
            )
            return "QUARANTINED", verification_log

    # Results are normal - no investigation needed
    return "PASSED", None



@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = (datetime.now() - datetime.fromisoformat(_metrics["start_time"])).total_seconds()

    return HealthResponse(
        status="healthy",
        uptime_seconds=uptime,
        total_queries=_metrics["total_queries"],
        concurrent_queries=_metrics["concurrent_queries"],
        max_concurrent_observed=_metrics["max_concurrent"],
        hybrid_queries=_metrics["hybrid_queries"],
        errors=_metrics["errors"],
    )


@app.post("/query", response_model=QueryResult)
async def single_query(request: QueryRequest):
    """Execute a single retrieval query."""
    api = _init_api()
    _metrics["total_queries"] += 1
    _metrics["concurrent_queries"] += 1
    _metrics["max_concurrent"] = max(_metrics["max_concurrent"], _metrics["concurrent_queries"])

    if request.fractalstat_hybrid:
        _metrics["hybrid_queries"] += 1

    try:
        start_time = datetime.now()

        # Convert request to RetrievalQuery
        mode = RetrievalMode[
            request.mode.upper().replace("_", "").replace("SIMILARITY", "_SIMILARITY")
        ]

        fractalstat_addr = None
        if request.fractalstat_address:
            fractalstat_addr = request.fractalstat_address.model_dump()

        query = RetrievalQuery(
            query_id=request.query_id,
            mode=mode,
            semantic_query=request.semantic_query,
            anchor_ids=request.anchor_ids,
            max_results=request.max_results,
            confidence_threshold=request.confidence_threshold,
            fractalstat_hybrid=request.fractalstat_hybrid,
            fractalstat_address=fractalstat_addr,
            weight_semantic=request.weight_semantic,
            weight_fractalstat=request.weight_fractalstat,
        )

        # Execute query
        assembly = api.retrieve_context(query)

        execution_time = (datetime.now() - start_time).total_seconds() * 1000  # Convert to ms

        # Extract results
        results_data = [
            {
                "id": result.content_id,
                "result_id": result.result_id,
                "content_type": result.content_type,
                "relevance_score": result.relevance_score,
                "semantic_similarity": result.semantic_similarity,
                "fractalstat_resonance": result.fractalstat_resonance,
                "content": result.content[:200] if result.content else None,
                "temporal_distance": result.temporal_distance,
                "anchor_connections": result.anchor_connections,
                "provenance_depth": result.provenance_depth,
                "conflict_flags": result.conflict_flags,
                "metadata": result.metadata,
            }
            for result in assembly.results
        ]

        # Analyze narrative coherence
        narrative_analysis = _analyze_narrative_coherence(results_data)

        # Bob the Skeptic: Verify suspiciously perfect results
        bob_status, bob_verification_log = await _bob_skeptic_filter(
            narrative_analysis=narrative_analysis, results_data=results_data, query=query, api=api
        )

        return QueryResult(
            query_id=request.query_id,
            result_count=len(results_data),
            results=results_data,
            semantic_similarity=(
                results_data[0].get("semantic_similarity") if results_data else None
            ),
            fractalstat_resonance=results_data[0].get("fractalstat_resonance") if results_data else None,
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat(),
            narrative_analysis=narrative_analysis,
            bob_status=bob_status,
            bob_verification_log=bob_verification_log,
        )

    except Exception as e:
        _metrics["errors"] += 1
        logger.error(f"Error executing query {request.query_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        _metrics["concurrent_queries"] -= 1


@app.post("/bulk_query")
async def bulk_concurrent_queries(request: BulkQueryRequest):
    """Execute multiple queries concurrently."""
    logger.info(
        f"Executing {len(request.queries)} queries with concurrency level {request.concurrency_level}"
    )

    semaphore = asyncio.Semaphore(request.concurrency_level)

    async def execute_with_semaphore(query_req: QueryRequest):
        async with semaphore:
            return await single_query(query_req)

    try:
        # Execute all queries concurrently
        tasks = [execute_with_semaphore(q) for q in request.queries]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Separate successful results from errors
        successful_results: List[QueryResult] = [r for r in batch_results if not isinstance(r, Exception)]

        errors = [
            {"query_id": request.queries[i].query_id, "error": str(r)}
            for i, r in enumerate(batch_results)
            if isinstance(r, Exception)
        ]

        # Aggregate narrative coherence across entire batch
        all_results_flat = []
        for result in successful_results:
            all_results_flat.extend(result.results)

        batch_narrative_analysis = _analyze_narrative_coherence(all_results_flat)

        return {
            "batch_id": f"batch_{int(time.time() * 1000)}",
            "total_queries": len(request.queries),
            "successful": len(successful_results),
            "failed": len(errors),
            "execution_time_ms": sum(r.execution_time_ms for r in successful_results),
            "avg_query_time_ms": sum(r.execution_time_ms for r in successful_results)
            / max(1, len(successful_results)),
            "results": successful_results,
            "errors": errors,
            "batch_narrative_analysis": batch_narrative_analysis,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        _metrics["errors"] += 1
        logger.error(f"Error executing bulk query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest_documents(request: Dict[str, Any]):
    """Ingest documents into the RetrievalAPI."""
    api = _init_api()

    documents = request.get("documents", [])
    if not documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    try:
        ingested = 0
        failed = []

        for doc in documents:
            content_id = doc.get("content_id")
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})

            if not content_id:
                failed.append({"doc": doc, "error": "Missing content_id"})
                continue

            # Use the new add_document method
            success = api.add_document(doc_id=content_id, content=content, metadata=metadata)

            if success:
                ingested += 1
                logger.info(f"✓ Ingested: {content_id}")
            else:
                failed.append({"doc_id": content_id, "error": "Document already exists"})
                logger.warning(f"Document already exists: {content_id}")

        logger.info(
            f"Ingested {ingested}/{len(documents)} documents (context store now has {api.get_context_store_size()} total)"
        )

        response = {
            "status": "success",
            "ingested": ingested,
            "total_requested": len(documents),
            "failed": len(failed),
            "context_store_size": api.get_context_store_size(),
            "timestamp": datetime.now().isoformat(),
        }

        if failed:
            response["failed_documents"] = failed

        return response

    except Exception as e:
        _metrics["errors"] += 1
        logger.error(f"Error ingesting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get current metrics and performance data."""
    return {"timestamp": datetime.now().isoformat(), **_metrics}


@app.post("/metrics/reset")
async def reset_metrics():
    """Reset metrics counters."""
    global _metrics
    _metrics = {
        "total_queries": 0,
        "concurrent_queries": 0,
        "max_concurrent": 0,
        "hybrid_queries": 0,
        "errors": 0,
        "start_time": datetime.now().isoformat(),
    }
    return {"status": "metrics reset"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
