#!/usr/bin/env python3
"""
GPU-Accelerated RAG System for Bob Stress Testing

Leverages RTX 2060 SUPER (8GB VRAM) for high-performance
retrieval and embedding calculations.
"""

import torch
import numpy as np
import faiss
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

# Try to import sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available. Using fallback embeddings.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GPUAcceleratedConfig:
    """Configuration for GPU-accelerated RAG"""
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size: int = 32
    embedding_dim: int = 384
    max_gpu_memory_gb: float = 6.0  # Leave 2GB for system
    use_faiss_gpu: bool = True

class GPUAcceleratedRAG:
    """GPU-accelerated Retrieval-Augmented Generation system"""

    def __init__(self, config: GPUAcceleratedConfig = None):
        self.config = config or GPUAcceleratedConfig()
        self.device = torch.device(self.config.device)

        # Check GPU availability and memory
        self._check_gpu_capabilities()

        # Initialize embedding model
        self.embedding_model = None
        self._initialize_embedding_model()

        # Initialize FAISS index
        self.index = None
        self.documents = []
        self._initialize_faiss_index()

        logger.info(f"🚀 GPU-Accelerated RAG initialized on {self.device}")
        logger.info(f"   Device: {torch.cuda.get_device_name() if torch.cuda.is_available() else 'CPU'}")
        logger.info(f"   Memory: {self._get_memory_info()}")

    def _check_gpu_capabilities(self):
        """Check GPU capabilities and memory"""
        if not torch.cuda.is_available():
            logger.warning("⚠️ CUDA not available, falling back to CPU")
            self.config.device = "cpu"
            self.device = torch.device("cpu")
            return

        # Check GPU memory
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
        logger.info(f"🎮 GPU Memory: {gpu_memory:.1f}GB available")

        if gpu_memory < self.config.max_gpu_memory_gb:
            logger.warning(f"⚠️ GPU memory ({gpu_memory:.1f}GB) below recommended ({self.config.max_gpu_memory_gb}GB)")

        # Check if FAISS GPU is available
        try:
            import faiss
            if hasattr(faiss, 'StandardGpuResources'):
                logger.info("✅ FAISS GPU support available")
            else:
                logger.warning("⚠️ FAISS GPU support not available")
                self.config.use_faiss_gpu = False
        except ImportError:
            logger.error("❌ FAISS not available")
            self.config.use_faiss_gpu = False

    def _get_memory_info(self) -> str:
        """Get memory usage information"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            cached = torch.cuda.memory_reserved(0) / (1024**3)
            return f"Allocated: {allocated:.2f}GB, Cached: {cached:.2f}GB"
        return "CPU Memory Only"

    def _initialize_embedding_model(self):
        """Initialize sentence transformer model"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error("❌ sentence-transformers not available. Install with: pip install sentence-transformers")
            return

        try:
            # Use a lightweight model for fast inference
            model_name = "all-MiniLM-L6-v2"  # 384 dimensions, fast

            logger.info(f"📥 Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
            self.embedding_model.to(self.device)

            # Test embedding
            test_text = "Test embedding for GPU acceleration"
            with torch.no_grad():
                embedding = self.embedding_model.encode([test_text], convert_to_tensor=True)
                embedding = embedding.to(self.device)
                logger.info(f"✅ Embedding model loaded. Test embedding shape: {embedding.shape}")

        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.embedding_model = None

    def _initialize_faiss_index(self):
        """Initialize FAISS index for fast similarity search"""
        try:
            # Create index based on device availability
            if self.config.use_faiss_gpu and torch.cuda.is_available():
                # GPU index for faster search
                self.index = faiss.IndexFlatL2(self.config.embedding_dim)
                # Move to GPU if available
                try:
                    res = faiss.StandardGpuResources()
                    self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
                    logger.info("✅ FAISS GPU index initialized")
                except Exception as e:
                    logger.warning(f"⚠️ FAISS GPU index failed, using CPU: {e}")
                    self.index = faiss.IndexFlatL2(self.config.embedding_dim)
            else:
                # CPU index
                self.index = faiss.IndexFlatL2(self.config.embedding_dim)
                logger.info("✅ FAISS CPU index initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize FAISS index: {e}")
            self.index = None

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the RAG system"""
        if not self.embedding_model or not self.index:
            logger.error("❌ RAG system not properly initialized")
            return

        logger.info(f"📚 Adding {len(documents)} documents to GPU-accelerated RAG")

        # Extract texts and metadata
        texts = [doc.get('content', '') for doc in documents]

        # Generate embeddings in batches for GPU efficiency
        embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch_texts = texts[i:i + self.config.batch_size]

            with torch.no_grad():
                batch_embeddings = self.embedding_model.encode(
                    batch_texts,
                    convert_to_tensor=True,
                    batch_size=self.config.batch_size,
                    normalize_embeddings=True
                )
                embeddings.append(batch_embeddings)

            if (i // self.config.batch_size + 1) % 10 == 0:
                logger.info(f"   Processed {min(i + self.config.batch_size, len(texts))}/{len(texts)} documents")

        # Concatenate all embeddings
        all_embeddings = torch.cat(embeddings, dim=0).cpu().numpy()

        # Add to FAISS index
        self.index.add(all_embeddings)

        # Store documents
        self.documents.extend(documents)

        logger.info(f"✅ Added {len(documents)} documents to RAG system")
        logger.info(f"   Index size: {self.index.ntotal}")
        logger.info(f"   Memory usage: {self._get_memory_info()}")

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar documents using GPU acceleration"""
        if not self.embedding_model or not self.index:
            logger.error("❌ RAG system not properly initialized")
            return []

        start_time = time.time()

        # Generate query embedding
        with torch.no_grad():
            query_embedding = self.embedding_model.encode(
                [query],
                convert_to_tensor=True,
                normalize_embeddings=True
            ).cpu().numpy()

        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['similarity_score'] = float(1.0 / (1.0 + distance))  # Convert distance to similarity
                doc['rank'] = i + 1
                results.append(doc)

        search_time = time.time() - start_time
        logger.info(f"🔍 Search completed in {search_time:.4f}s for {len(results)} results")

        return results

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {
            "device": str(self.device),
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.config.embedding_dim,
            "gpu_available": torch.cuda.is_available(),
            "faiss_gpu_enabled": self.config.use_faiss_gpu,
            "memory_info": self._get_memory_info()
        }

        if torch.cuda.is_available():
            stats.update({
                "gpu_name": torch.cuda.get_device_name(),
                "gpu_memory_total": torch.cuda.get_device_properties(0).total_memory / (1024**3),
                "gpu_memory_allocated": torch.cuda.memory_allocated(0) / (1024**3),
                "gpu_memory_cached": torch.cuda.memory_reserved(0) / (1024**3)
            })

        return stats

def test_gpu_acceleration():
    """Test GPU acceleration capabilities"""
    print("🚀 GPU-Accelerated RAG System Test")
    print("=" * 50)

    # Initialize system
    config = GPUAcceleratedConfig()
    rag = GPUAcceleratedRAG(config)

    # Test documents
    test_docs = [
        {
            "content_id": f"gpu_test_{i}",
            "content": f"This is test document {i} for GPU acceleration testing. " +
                      f"It contains various content about machine learning, GPU computing, " +
                      f"and high-performance retrieval systems.",
            "metadata": {"type": "test", "index": i}
        }
        for i in range(1000)
    ]

    # Add documents
    print("\n📚 Adding test documents...")
    rag.add_documents(test_docs)

    # Test searches
    test_queries = [
        "machine learning and GPU acceleration",
        "high-performance computing",
        "retrieval augmented generation",
        "FAISS index optimization",
        "CUDA memory management"
    ]

    print("\n🔍 Testing search performance...")
    for query in test_queries:
        results = rag.search(query, top_k=5)
        print(f"\nQuery: {query}")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. Score: {result['similarity_score']:.4f} | {result['content_id']}")

    # Performance stats
    print("\n📊 Performance Statistics:")
    stats = rag.get_performance_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print(f"\n✅ GPU Acceleration Test Complete!")
    return rag

if __name__ == "__main__":
    test_gpu_acceleration()
