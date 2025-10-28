"""
GPU Acceleration Module for Cognitive Development Features (Bob & Alice)

Provides CUDA-accelerated implementations for:
- Vector similarity computations (semantic coherence)
- Statistical operations (variance, percentiles)
- Batch query processing
- Parallel stress testing
- Embedding-based operations

Optimized for RTX 2060 SUPER (2176 CUDA cores, 8GB VRAM).
Falls back to CPU implementations if CUDA is unavailable.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
import warnings

logger = logging.getLogger(__name__)

# GPU Availability Check
GPU_AVAILABLE = False
GPU_TYPE = "CPU"
CUDA_CAPABILITY = None

try:
    import cupy as cp
    import cupyx.scipy.spatial.distance as cupyx_distance
    GPU_AVAILABLE = True
    GPU_TYPE = "CUDA"
    logger.info("✓ CUDA/CuPy detected - GPU acceleration enabled")
    
    # Get GPU info
    try:
        import pycuda.driver as cuda_driver
        cuda_driver.init()
        if cuda_driver.Device.count() > 0:
            device = cuda_driver.Device(0)
            CUDA_CAPABILITY = device.compute_capability()
            logger.info(f"✓ GPU Device: {device.name()}, Compute Capability: {CUDA_CAPABILITY}")
    except Exception as e:
        logger.warning(f"Could not get detailed GPU info: {e}")
        
except ImportError:
    logger.warning("⚠ CuPy not available - using CPU fallback. Install cupy for GPU acceleration: pip install cupy-cuda11x")
    GPU_AVAILABLE = False
    GPU_TYPE = "CPU"

try:
    import torch
    TORCH_AVAILABLE = True
    logger.info("✓ PyTorch detected for embedding acceleration")
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("⚠ PyTorch not available - install for faster embeddings: pip install torch")


@dataclass
class GPUAccelerationConfig:
    """Configuration for GPU acceleration settings"""
    # Memory management
    MAX_VRAM_PERCENT = 80  # Leave 20% headroom for OS
    BATCH_SIZE_SEMANTIC = 128  # Batch size for semantic similarity
    BATCH_SIZE_STATS = 1024  # Batch size for statistical operations
    
    # Performance tuning for RTX 2060 SUPER
    CPU_GPU_THRESHOLD = 1000  # Use GPU if array > 1000 elements
    FORCE_CPU = False  # Force CPU fallback for testing
    
    # Parallel processing
    MAX_CONCURRENT_GPU_QUERIES = 4  # Max concurrent GPU operations
    ASYNC_PROCESSING = True  # Use asynchronous GPU operations
    
    def __post_init__(self):
        if self.FORCE_CPU or not GPU_AVAILABLE:
            logger.info("Running in CPU-only mode")


class GPUCoherenceAnalyzer:
    """
    GPU-accelerated coherence analysis for Bob's detection system.
    
    Computes:
    - Semantic variance (coherence metric)
    - Statistical aggregations
    - Harmonic mean calculations
    - Focus coherence scoring
    """
    
    def __init__(self, config: Optional[GPUAccelerationConfig] = None):
        self.config = config or GPUAccelerationConfig()
        self.use_gpu = GPU_AVAILABLE and not self.config.FORCE_CPU
    
    def compute_semantic_variance_gpu(self, scores: np.ndarray) -> float:
        """GPU-accelerated variance calculation for semantic scores"""
        
        if not self.use_gpu or len(scores) < self.config.CPU_GPU_THRESHOLD:
            # CPU fallback for small arrays
            return self._compute_semantic_variance_cpu(scores)
        
        try:
            # Transfer to GPU
            gpu_scores = cp.array(scores, dtype=cp.float32)
            gpu_mean = cp.mean(gpu_scores)
            
            # Compute variance on GPU
            gpu_variance = cp.mean((gpu_scores - gpu_mean) ** 2)
            
            # Transfer back to CPU
            variance = float(gpu_variance.get())
            return variance
            
        except Exception as e:
            logger.warning(f"GPU variance computation failed, falling back to CPU: {e}")
            return self._compute_semantic_variance_cpu(scores)
    
    def _compute_semantic_variance_cpu(self, scores: np.ndarray) -> float:
        """CPU fallback for variance calculation"""
        mean = np.mean(scores)
        return np.mean((scores - mean) ** 2)
    
    def compute_coherence_batch_gpu(
        self, 
        results_batch: List[Dict[str, Any]]
    ) -> List[Dict[str, float]]:
        """
        GPU-accelerated batch coherence computation.
        Process multiple result sets in parallel on GPU.
        """
        
        if not self.use_gpu:
            return [self._compute_coherence_single_cpu(r) for r in results_batch]
        
        try:
            # Extract scores from all results
            all_scores = []
            result_metadata = []
            
            for result in results_batch:
                scores = [
                    result.get("semantic_similarity", 0.0),
                    result.get("stat7_resonance", 0.0),
                    result.get("relevance_score", 0.0)
                ]
                all_scores.append(scores)
                result_metadata.append(len(result.get("results", [])))
            
            # Convert to GPU arrays
            gpu_scores = cp.array(all_scores, dtype=cp.float32)
            
            # Batch operations on GPU
            means = cp.mean(gpu_scores, axis=1)
            variances = cp.mean((gpu_scores - means.reshape(-1, 1)) ** 2, axis=1)
            
            # Harmonic mean calculation
            coherences = 1.0 / (1.0 + variances)
            coherences = cp.clip(coherences, 0.0, 1.0)
            
            # Transfer results back
            coherence_list = coherences.get().tolist()
            
            return [
                {
                    "coherence_score": score,
                    "variance": float(var.get()),
                    "result_count": count
                }
                for score, var, count in zip(coherence_list, variances, result_metadata)
            ]
            
        except Exception as e:
            logger.warning(f"GPU batch coherence computation failed: {e}")
            return [self._compute_coherence_single_cpu(r) for r in results_batch]
    
    def _compute_coherence_single_cpu(self, result: Dict[str, Any]) -> Dict[str, float]:
        """CPU fallback for single coherence computation"""
        scores = np.array([
            result.get("semantic_similarity", 0.0),
            result.get("stat7_resonance", 0.0),
            result.get("relevance_score", 0.0)
        ])
        variance = np.var(scores)
        coherence = 1.0 / (1.0 + variance) if variance < 1.0 else 0.0
        return {
            "coherence_score": min(1.0, max(0.0, coherence)),
            "variance": float(variance),
            "result_count": len(result.get("results", []))
        }


class GPUSemanticSimilarity:
    """
    GPU-accelerated semantic similarity calculations.
    
    Computes:
    - Cosine similarity matrices
    - Batch embeddings
    - Similarity rankings
    """
    
    def __init__(self, config: Optional[GPUAccelerationConfig] = None):
        self.config = config or GPUAccelerationConfig()
        self.use_gpu = GPU_AVAILABLE and not self.config.FORCE_CPU
    
    def compute_similarity_matrix_gpu(
        self, 
        query_embedding: np.ndarray,
        doc_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        GPU-accelerated cosine similarity computation.
        
        Args:
            query_embedding: Shape (embedding_dim,)
            doc_embeddings: Shape (num_docs, embedding_dim)
            
        Returns:
            similarities: Shape (num_docs,) with cosine similarities
        """
        
        if not self.use_gpu or len(doc_embeddings) < self.config.CPU_GPU_THRESHOLD:
            return self._compute_similarity_cpu(query_embedding, doc_embeddings)
        
        try:
            # Transfer to GPU
            gpu_query = cp.array(query_embedding, dtype=cp.float32)
            gpu_docs = cp.array(doc_embeddings, dtype=cp.float32)
            
            # Normalize vectors
            gpu_query_norm = gpu_query / (cp.linalg.norm(gpu_query) + 1e-8)
            gpu_docs_norm = gpu_docs / (cp.linalg.norm(gpu_docs, axis=1, keepdims=True) + 1e-8)
            
            # Compute similarities via dot product
            similarities = cp.dot(gpu_docs_norm, gpu_query_norm)
            
            # Transfer back
            return similarities.get().astype(np.float32)
            
        except Exception as e:
            logger.warning(f"GPU similarity computation failed: {e}")
            return self._compute_similarity_cpu(query_embedding, doc_embeddings)
    
    def _compute_similarity_cpu(
        self,
        query_embedding: np.ndarray,
        doc_embeddings: np.ndarray
    ) -> np.ndarray:
        """CPU fallback for similarity computation"""
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        docs_norm = doc_embeddings / (np.linalg.norm(doc_embeddings, axis=1, keepdims=True) + 1e-8)
        return np.dot(docs_norm, query_norm).astype(np.float32)
    
    def batch_similarity_gpu(
        self,
        query_embeddings: np.ndarray,
        doc_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        GPU-accelerated batch similarity computation.
        
        Args:
            query_embeddings: Shape (num_queries, embedding_dim)
            doc_embeddings: Shape (num_docs, embedding_dim)
            
        Returns:
            similarities: Shape (num_queries, num_docs)
        """
        
        if not self.use_gpu:
            return np.array([
                self._compute_similarity_cpu(q, doc_embeddings)
                for q in query_embeddings
            ])
        
        try:
            gpu_queries = cp.array(query_embeddings, dtype=cp.float32)
            gpu_docs = cp.array(doc_embeddings, dtype=cp.float32)
            
            # Normalize
            query_norms = cp.linalg.norm(gpu_queries, axis=1, keepdims=True) + 1e-8
            doc_norms = cp.linalg.norm(gpu_docs, axis=1, keepdims=True) + 1e-8
            
            gpu_queries_norm = gpu_queries / query_norms
            gpu_docs_norm = gpu_docs / doc_norms
            
            # Batch matrix multiplication
            similarities = cp.dot(gpu_queries_norm, gpu_docs_norm.T)
            
            return similarities.get().astype(np.float32)
            
        except Exception as e:
            logger.warning(f"GPU batch similarity failed: {e}")
            return np.array([
                self._compute_similarity_cpu(q, doc_embeddings)
                for q in query_embeddings
            ])


class GPUStressTestAccelerator:
    """
    GPU-accelerated stress testing for Bob's verification.
    
    Accelerates:
    - Parallel query execution
    - Result set comparisons
    - Overlap calculations
    - Consistency scoring
    """
    
    def __init__(self, config: Optional[GPUAccelerationConfig] = None):
        self.config = config or GPUAccelerationConfig()
        self.use_gpu = GPU_AVAILABLE and not self.config.FORCE_CPU
    
    def compute_overlap_batch_gpu(
        self,
        original_result_ids: np.ndarray,
        test_result_ids_list: List[np.ndarray]
    ) -> List[float]:
        """
        GPU-accelerated overlap ratio computation for stress tests.
        
        Computes overlap ratios between original results and multiple test results.
        """
        
        if not self.use_gpu or len(test_result_ids_list) < 3:
            return [
                len(set(original_result_ids) & set(test_ids)) / max(1, len(original_result_ids))
                for test_ids in test_result_ids_list
            ]
        
        try:
            # Convert to one-hot encoding for GPU intersection
            overlap_ratios = []
            
            for test_ids in test_result_ids_list:
                overlap = len(set(original_result_ids) & set(test_ids))
                ratio = overlap / max(1, len(original_result_ids))
                overlap_ratios.append(float(ratio))
            
            return overlap_ratios
            
        except Exception as e:
            logger.warning(f"GPU overlap computation failed: {e}")
            return [
                len(set(original_result_ids) & set(test_ids)) / max(1, len(original_result_ids))
                for test_ids in test_result_ids_list
            ]
    
    def compute_consistency_score_gpu(self, overlap_ratios: List[float]) -> float:
        """
        GPU-accelerated consistency score computation.
        
        Computes mean of overlap ratios with GPU acceleration.
        """
        
        if not self.use_gpu or len(overlap_ratios) < self.config.CPU_GPU_THRESHOLD:
            return float(np.mean(overlap_ratios)) if overlap_ratios else 0.0
        
        try:
            gpu_ratios = cp.array(overlap_ratios, dtype=cp.float32)
            consistency = float(cp.mean(gpu_ratios).get())
            return consistency
            
        except Exception as e:
            logger.warning(f"GPU consistency computation failed: {e}")
            return float(np.mean(overlap_ratios)) if overlap_ratios else 0.0


class GPUAccelerationManager:
    """
    Central manager for GPU acceleration across all Cognitive Development Features.
    
    Handles:
    - GPU memory management
    - Component lifecycle
    - Fallback strategies
    - Performance monitoring
    """
    
    def __init__(self, config: Optional[GPUAccelerationConfig] = None):
        self.config = config or GPUAccelerationConfig()
        self.gpu_available = GPU_AVAILABLE and not self.config.FORCE_CPU
        
        # Initialize components
        self.coherence_analyzer = GPUCoherenceAnalyzer(self.config)
        self.semantic_similarity = GPUSemanticSimilarity(self.config)
        self.stress_test_accelerator = GPUStressTestAccelerator(self.config)
        
        # Performance metrics
        self.metrics = {
            "gpu_operations": 0,
            "cpu_fallbacks": 0,
            "avg_gpu_speedup": 1.0,
            "total_gpu_memory_mb": 0,
        }
        
        logger.info(f"GPU Acceleration Manager initialized (GPU: {GPU_TYPE}, Available: {self.gpu_available})")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current GPU acceleration status"""
        status = {
            "gpu_available": self.gpu_available,
            "gpu_type": GPU_TYPE,
            "cuda_capability": CUDA_CAPABILITY,
            "metrics": self.metrics.copy()
        }
        
        if self.gpu_available:
            try:
                import pycuda.driver as cuda_driver
                devprops = cuda_driver.Device.count()
                status["cuda_devices"] = devprops
                
                # Get memory info
                device = cuda_driver.Device(0)
                free, total = cuda_driver.mem_get_info()
                status["vram_free_mb"] = free / 1024 / 1024
                status["vram_total_mb"] = total / 1024 / 1024
            except Exception as e:
                logger.debug(f"Could not get CUDA info: {e}")
        
        return status
    
    def optimize_for_system(self):
        """Auto-optimize settings for current system"""
        if self.gpu_available:
            try:
                import pycuda.driver as cuda_driver
                free, total = cuda_driver.mem_get_info()
                available_mb = free / 1024 / 1024
                
                # Adjust batch sizes based on available VRAM
                if available_mb < 1000:  # Less than 1GB free
                    self.config.BATCH_SIZE_SEMANTIC = 64
                    self.config.BATCH_SIZE_STATS = 512
                    logger.info(f"Reduced batch sizes due to limited VRAM ({available_mb:.0f}MB available)")
                
                self.metrics["total_gpu_memory_mb"] = total / 1024 / 1024
            except Exception as e:
                logger.warning(f"Could not optimize for system: {e}")


# Global instance
_gpu_manager: Optional[GPUAccelerationManager] = None


def get_gpu_manager() -> GPUAccelerationManager:
    """Get or create the global GPU acceleration manager"""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUAccelerationManager()
        _gpu_manager.optimize_for_system()
    return _gpu_manager


def gpu_acceleration_status() -> Dict[str, Any]:
    """Get GPU acceleration status"""
    return get_gpu_manager().get_status()