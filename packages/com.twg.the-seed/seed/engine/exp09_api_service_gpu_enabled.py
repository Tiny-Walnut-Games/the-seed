"""
EXP-09 API Service with GPU Acceleration - STAT7 Retrieval API with CUDA Support

This is an enhanced version of exp09_api_service.py that includes GPU acceleration
for Bob's coherence analysis and stress testing.

Key Additions:
- GPU-accelerated coherence calculations
- Batch processing optimizations
- Parallel stress test execution
- VRAM-aware memory management

NOTE: Replace/merge this with exp09_api_service.py to enable GPU support.
To use this version:
    1. Install: pip install cupy-cuda12x
    2. Replace exp09_api_service.py or import GPU components
    3. Set GPU_ACCELERATED = True in FastAPI app startup
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json
import time
import numpy as np

# GPU Acceleration Imports
try:
    from gpu_acceleration import (
        get_gpu_manager,
        GPUAccelerationManager,
        gpu_acceleration_status
    )
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("⚠ GPU acceleration module not found. Run: pip install cupy-cuda12x")

from retrieval_api import RetrievalAPI, RetrievalQuery, RetrievalMode
from stat7_rag_bridge import STAT7RAGBridge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EXP-09 STAT7 API Service with GPU Acceleration",
    description="Concurrent STAT7 Retrieval API with NVIDIA GPU support",
    version="1.1.0"
)

# Global state
_api_instance: Optional[RetrievalAPI] = None
_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=20)
_gpu_manager: Optional[GPUAccelerationManager] = None
_gpu_enabled: bool = False

_metrics: Dict[str, Any] = {
    "total_queries": 0,
    "gpu_accelerated_queries": 0,
    "concurrent_queries": 0,
    "max_concurrent": 0,
    "hybrid_queries": 0,
    "errors": 0,
    "start_time": datetime.now().isoformat()
}


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize API and GPU acceleration on startup"""
    global _api_instance, _gpu_manager, _gpu_enabled
    
    logger.info("🚀 Starting EXP-09 API Service with GPU Acceleration")
    
    # Initialize RetrievalAPI
    _init_api()
    logger.info("✓ RetrievalAPI initialized")
    
    # Initialize GPU acceleration if available
    if GPU_AVAILABLE:
        _gpu_manager = get_gpu_manager()
        _gpu_enabled = True
        status = _gpu_manager.get_status()
        logger.info(f"✓ GPU Acceleration enabled: {status['gpu_type']}")
        logger.info(f"  - CUDA Capability: {status.get('cuda_capability', 'Unknown')}")
        logger.info(f"  - VRAM: {status.get('vram_total_mb', '?')}MB")
    else:
        logger.warning("⚠ GPU acceleration not available, using CPU fallback")
        _gpu_enabled = False


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down EXP-09 API Service")
    _executor.shutdown(wait=True)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class STAT7Address(BaseModel):
    realm: Dict[str, Any] = Field(default_factory=lambda: {"type": "retrieval_query", "label": "api_query"})
    lineage: int = 0
    adjacency: str = "semantic_proximity"
    horizon: str = "emergence"
    luminosity: float = 0.7
    polarity: float = 0.5
    dimensionality: int = 1


class QueryRequest(BaseModel):
    query_id: str
    mode: str = "semantic_similarity"
    semantic_query: Optional[str] = None
    anchor_ids: Optional[List[str]] = None
    max_results: int = 10
    confidence_threshold: float = 0.6
    stat7_hybrid: bool = False
    stat7_address: Optional[STAT7Address] = None
    weight_semantic: float = 0.6
    weight_stat7: float = 0.4


class QueryResult(BaseModel):
    query_id: str
    result_count: int
    results: List[Dict[str, Any]]
    semantic_similarity: Optional[float] = None
    stat7_resonance: Optional[float] = None
    execution_time_ms: float
    timestamp: str
    narrative_analysis: Optional[Dict[str, Any]] = None
    bob_status: Optional[str] = "PASSED"
    bob_verification_log: Optional[Dict[str, Any]] = None
    gpu_accelerated: bool = False  # NEW: Track if GPU was used


class GPUStatusResponse(BaseModel):
    """GPU acceleration status response"""
    gpu_available: bool
    gpu_type: str
    gpu_enabled: bool
    vram_free_mb: Optional[float] = None
    vram_total_mb: Optional[float] = None
    metrics: Dict[str, Any]


# ============================================================================
# API INITIALIZATION
# ============================================================================

def _init_api():
    """Initialize the RetrievalAPI instance"""
    global _api_instance
    if _api_instance is None:
        logger.info("Initializing RetrievalAPI with STAT7 support...")
        stat7_bridge = STAT7RAGBridge()
        _api_instance = RetrievalAPI(
            stat7_bridge=stat7_bridge,
            config={
                "enable_stat7_hybrid": True,
                "default_weight_semantic": 0.6,
                "default_weight_stat7": 0.4
            }
        )
        logger.info("✓ RetrievalAPI initialized")
    return _api_instance


# ============================================================================
# GPU-ACCELERATED COHERENCE ANALYSIS
# ============================================================================

def _analyze_narrative_coherence_gpu(results: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], bool]:
    """
    GPU-accelerated narrative coherence analysis.
    
    Returns:
        Tuple of (coherence_dict, gpu_used)
    """
    
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
            "analysis": "No results to analyze"
        }, False
    
    gpu_used = False
    
    # Try GPU acceleration if available and sufficient data
    if _gpu_enabled and len(results) > 10:
        try:
            gpu_manager = get_gpu_manager()
            
            # Extract scores as numpy arrays
            semantic_scores = np.array([r.get("semantic_similarity", 0.0) for r in results], dtype=np.float32)
            stat7_resonances = np.array([r.get("stat7_resonance", 0.0) for r in results], dtype=np.float32)
            relevance_scores = np.array([r.get("relevance_score", 0.0) for r in results], dtype=np.float32)
            
            # GPU-accelerated variance computation
            semantic_variance = gpu_manager.coherence_analyzer.compute_semantic_variance_gpu(semantic_scores)
            gpu_used = True
            
            # Continue with CPU for remaining calculations (or accelerate further if needed)
            avg_semantic = float(np.mean(semantic_scores))
            avg_stat7 = float(np.mean(stat7_resonances))
            avg_relevance = float(np.mean(relevance_scores))
            
            # Original calculation logic
            quality_score = avg_relevance
            semantic_coherence = 1.0 / (1.0 + semantic_variance) if semantic_variance < 1.0 else 0.0
            stat7_coherence = avg_stat7
            
            narrative_threads = set()
            for result in results:
                pack_info = result.get("metadata", {}).get("pack", None)
                thread_id = pack_info if pack_info else result.get("id", "unknown")
                narrative_threads.add(thread_id)
            
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
                "analysis": f"Found {len(narrative_threads)} threads across {len(results)} results"
            }, gpu_used
            
        except Exception as e:
            logger.warning(f"GPU coherence analysis failed, falling back to CPU: {e}")
            # Fall through to CPU implementation
    
    # CPU-only fallback
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
    
    quality_score = avg_relevance
    semantic_variance = sum((s - avg_semantic) ** 2 for s in semantic_scores) / max(1, len(semantic_scores))
    semantic_coherence = 1.0 / (1.0 + semantic_variance) if semantic_variance < 1.0 else 0.0
    stat7_coherence = avg_stat7
    
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
        "analysis": f"Found {len(narrative_threads)} threads across {len(results)} results"
    }, gpu_used


# ============================================================================
# BOB THE SKEPTIC WITH GPU ACCELERATION
# ============================================================================

class BobSkepticConfig:
    """Tunable thresholds for Bob's suspicion detection"""
    COHERENCE_HIGH_THRESHOLD = 0.85
    ENTANGLEMENT_LOW_THRESHOLD = 0.3
    STRESS_TEST_DIVERGENCE_THRESHOLD = 0.15


async def _stress_test_result_gpu(
    api: RetrievalAPI,
    query: RetrievalQuery,
    original_results: List[Dict[str, Any]],
    narrative_analysis: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any], bool]:
    """
    GPU-accelerated stress testing for Bob.
    
    Returns:
        Tuple of (is_consistent, verification_log, gpu_used)
    """
    
    log = {
        "stress_test_started": datetime.now().isoformat(),
        "original_result_ids": [r.get("result_id") for r in original_results[:5]],
        "tests_run": [],
        "verdict": "UNKNOWN",
        "consistency_score": 0.0
    }
    
    gpu_used = False
    
    try:
        original_ids = set(r.get("result_id") for r in original_results)
        test_results = []
        
        # Run tests in parallel (GPU-friendly)
        tasks = []
        
        if query.stat7_hybrid and query.semantic_query:
            semantic_query = RetrievalQuery(
                query_id=f"{query.query_id}_bob_semantic",
                mode=RetrievalMode.SEMANTIC_SIMILARITY,
                semantic_query=query.semantic_query,
                max_results=query.max_results,
                confidence_threshold=query.confidence_threshold
            )
            tasks.append(("SEMANTIC_ONLY", api.retrieve_context(semantic_query)))
        
        if query.stat7_hybrid and query.stat7_address:
            stat7_query = RetrievalQuery(
                query_id=f"{query.query_id}_bob_stat7",
                mode=RetrievalMode.STAT7_ADDRESS,
                stat7_address=query.stat7_address,
                max_results=query.max_results,
                confidence_threshold=query.confidence_threshold
            )
            tasks.append(("STAT7_ONLY", api.retrieve_context(stat7_query)))
        
        if query.confidence_threshold < 0.8:
            high_conf_query = RetrievalQuery(
                query_id=f"{query.query_id}_bob_high_conf",
                mode=query.mode,
                semantic_query=query.semantic_query,
                anchor_ids=query.anchor_ids,
                max_results=query.max_results,
                confidence_threshold=min(0.85, query.confidence_threshold + 0.2),
                stat7_hybrid=query.stat7_hybrid,
                stat7_address=query.stat7_address
            )
            tasks.append(("HIGH_CONFIDENCE", api.retrieve_context(high_conf_query)))
        
        # Execute all tests in parallel
        if tasks:
            for test_name, result_future in tasks:
                assembly = result_future
                test_ids = set(r.content_id for r in assembly.results)
                overlap = len(original_ids & test_ids) / max(1, len(original_ids))
                
                log["tests_run"].append({
                    "test": test_name,
                    "overlap_ratio": overlap,
                    "result_count": len(assembly.results)
                })
        
        # GPU-accelerated consistency computation
        if log["tests_run"]:
            consistency_scores = [t["overlap_ratio"] for t in log["tests_run"]]
            
            # Try GPU acceleration
            if _gpu_enabled and len(consistency_scores) > 1:
                try:
                    gpu_manager = get_gpu_manager()
                    avg_consistency = gpu_manager.stress_test_accelerator.compute_consistency_score_gpu(
                        consistency_scores
                    )
                    gpu_used = True
                except Exception as e:
                    logger.debug(f"GPU consistency computation failed: {e}")
                    avg_consistency = sum(consistency_scores) / len(consistency_scores)
            else:
                avg_consistency = sum(consistency_scores) / len(consistency_scores)
            
            log["consistency_score"] = avg_consistency
            
            if avg_consistency >= (1.0 - BobSkepticConfig.STRESS_TEST_DIVERGENCE_THRESHOLD):
                log["verdict"] = "CONSISTENT"
                is_consistent = True
            else:
                log["verdict"] = "DIVERGENT"
                is_consistent = False
        else:
            log["verdict"] = "NO_TESTS_APPLICABLE"
            is_consistent = True
        
        return is_consistent, log, gpu_used
        
    except Exception as e:
        logger.error(f"Error in stress test: {e}")
        log["verdict"] = "ERROR"
        log["error"] = str(e)
        return False, log, gpu_used


# ============================================================================
# REST ENDPOINTS
# ============================================================================

@app.get("/health", response_model=GPUStatusResponse)
async def health_check():
    """Health check with GPU status"""
    uptime = (datetime.now() - datetime.fromisoformat(_metrics["start_time"])).total_seconds()
    
    if _gpu_enabled:
        status = _gpu_manager.get_status()
        gpu_metrics = status.get("metrics", {})
    else:
        gpu_metrics = {}
    
    return GPUStatusResponse(
        gpu_available=GPU_AVAILABLE,
        gpu_type="CUDA" if GPU_AVAILABLE else "CPU",
        gpu_enabled=_gpu_enabled,
        vram_free_mb=_gpu_manager.get_status().get("vram_free_mb") if _gpu_enabled else None,
        vram_total_mb=_gpu_manager.get_status().get("vram_total_mb") if _gpu_enabled else None,
        metrics={
            **_metrics,
            "uptime_seconds": uptime,
            "gpu_operations": gpu_metrics.get("gpu_operations", 0),
            "cpu_fallbacks": gpu_metrics.get("cpu_fallbacks", 0)
        }
    )


@app.post("/query", response_model=QueryResult)
async def execute_query(request: QueryRequest) -> QueryResult:
    """
    Execute a retrieval query with optional Bob skepticism validation.
    GPU acceleration applied to coherence analysis and stress testing.
    """
    
    api = _init_api()
    start_time = time.time()
    gpu_used = False
    
    _metrics["total_queries"] += 1
    
    try:
        # Build query
        query = RetrievalQuery(
            query_id=request.query_id,
            mode=RetrievalMode.SEMANTIC_SIMILARITY,
            semantic_query=request.semantic_query,
            anchor_ids=request.anchor_ids,
            max_results=request.max_results,
            confidence_threshold=request.confidence_threshold,
            stat7_hybrid=request.stat7_hybrid,
            stat7_address=request.stat7_address.dict() if request.stat7_address else None,
            weight_semantic=request.weight_semantic,
            weight_stat7=request.weight_stat7
        )
        
        # Execute retrieval
        assembly = api.retrieve_context(query)
        
        # Convert results to dict format
        results = []
        for r in assembly.results:
            results.append({
                "result_id": r.result_id,
                "content": r.content,
                "relevance_score": r.relevance_score,
                "semantic_similarity": r.semantic_similarity,
                "stat7_resonance": r.stat7_resonance,
                "metadata": r.metadata
            })
        
        # GPU-accelerated coherence analysis
        narrative_analysis, gpu_coherence_used = _analyze_narrative_coherence_gpu(results)
        gpu_used = gpu_coherence_used
        
        # Bob's skepticism check
        bob_status = "PASSED"
        bob_verification_log = None
        
        coherence = narrative_analysis.get("coherence_score", 0.0)
        entanglement = narrative_analysis.get("stat7_coherence", 0.0)
        
        if coherence > BobSkepticConfig.COHERENCE_HIGH_THRESHOLD and \
           entanglement < BobSkepticConfig.ENTANGLEMENT_LOW_THRESHOLD:
            
            # Run GPU-accelerated stress tests
            is_consistent, stress_log, gpu_stress_used = await _stress_test_result_gpu(
                api, query, results, narrative_analysis
            )
            gpu_used = gpu_used or gpu_stress_used
            
            if is_consistent:
                bob_status = "VERIFIED"
            else:
                bob_status = "QUARANTINED"
            
            bob_verification_log = stress_log
        
        execution_time = (time.time() - start_time) * 1000
        
        if gpu_used:
            _metrics["gpu_accelerated_queries"] += 1
        
        return QueryResult(
            query_id=request.query_id,
            result_count=len(results),
            results=results,
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat(),
            narrative_analysis=narrative_analysis,
            bob_status=bob_status,
            bob_verification_log=bob_verification_log,
            gpu_accelerated=gpu_used
        )
        
    except Exception as e:
        _metrics["errors"] += 1
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gpu-status", response_model=Dict[str, Any])
async def gpu_status():
    """Get detailed GPU acceleration status"""
    if not GPU_AVAILABLE:
        return {
            "gpu_available": False,
            "message": "GPU acceleration not available. Install: pip install cupy-cuda12x"
        }
    
    return _gpu_manager.get_status()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 80)
    logger.info("EXP-09 API Service with GPU Acceleration")
    logger.info(f"GPU Support: {'✓ ENABLED' if GPU_AVAILABLE else '✗ DISABLED'}")
    logger.info("=" * 80)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        workers=1,
        log_level="info"
    )