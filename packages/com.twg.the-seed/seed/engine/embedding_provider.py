#!/usr/bin/env python3
"""
SentenceTransformer GPU-Accelerated Embedding Provider

Replaces TF-IDF LocalEmbeddingProvider with real semantic embeddings
using pre-trained transformer models. Embeddings are:
- GPU-accelerated via PyTorch/CUDA
- Semantic (understand meaning, not just bag-of-words)
- Compatible with STAT7 coordinate assignment
- Cached for efficiency

Models Available:
- all-MiniLM-L6-v2 (Fast, 384D, good accuracy) - DEFAULT
- all-mpnet-base-v2 (Better quality, 768D, slower)
- multi-qa-MiniLM-L6-cos-v1 (Question-answering optimized)
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import numpy as np
from pathlib import Path
import json
import hashlib
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")


class SentenceTransformerEmbeddingProvider:
    """
    GPU-accelerated embedding provider using SentenceTransformers.
    
    Features:
    - Real semantic embeddings (not TF-IDF)
    - GPU acceleration when available
    - Embedding caching for repeated texts
    - Batch processing support
    - STAT7 coordinate generation from embeddings
    """
    
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[Path] = None,
        use_gpu: bool = True,
        batch_size: int = 32,
    ):
        """
        Initialize embedding provider.
        
        Args:
            model_name: SentenceTransformer model name
            cache_dir: Directory to cache embeddings
            use_gpu: Use GPU if available
            batch_size: Batch size for processing
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")
        
        self.model_name = model_name
        self.cache_dir = cache_dir or Path.home() / ".cache" / "warbler_embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.batch_size = batch_size
        
        device = "cuda" if self.use_gpu else "cpu"
        logger.info(f"Loading SentenceTransformer model: {model_name} on device: {device}")
        
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"✓ Model loaded: {model_name} ({self.embedding_dim}D embeddings) on {device}")
        
        self._embedding_cache: Dict[str, List[float]] = {}
        self._load_cache()
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _load_cache(self):
        """Load cached embeddings from disk."""
        cache_file = self.cache_dir / f"{self.model_name.replace('/', '_')}_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self._embedding_cache = json.load(f)
                logger.info(f"Loaded {len(self._embedding_cache)} cached embeddings")
            except Exception as e:
                logger.warning(f"Failed to load embedding cache: {e}")
    
    def _save_cache(self):
        """Save embeddings cache to disk."""
        cache_file = self.cache_dir / f"{self.model_name.replace('/', '_')}_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self._embedding_cache, f)
        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not text:
            return [0.0] * self.embedding_dim
        
        cache_key = self._get_cache_key(text)
        
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        embedding = self.model.encode([text], convert_to_numpy=True)[0]
        embedding_list = embedding.tolist()
        
        self._embedding_cache[cache_key] = embedding_list
        
        return embedding_list
    
    def embed_batch(self, texts: List[str], show_progress: bool = False) -> List[List[float]]:
        """
        Embed multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            show_progress: Show progress bar
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self._embedding_cache:
                embeddings.append(self._embedding_cache[cache_key])
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        if uncached_texts:
            logger.info(f"Embedding {len(uncached_texts)} new texts (from {len(texts)} total)")
            
            batch_embeddings = self.model.encode(
                uncached_texts,
                batch_size=self.batch_size,
                convert_to_numpy=True,
                show_progress_bar=show_progress
            )
            
            for i, idx in enumerate(uncached_indices):
                embedding_list = batch_embeddings[i].tolist()
                cache_key = self._get_cache_key(uncached_texts[i])
                self._embedding_cache[cache_key] = embedding_list
                embeddings.insert(idx, embedding_list)
            
            self._save_cache()
        
        return embeddings
    
    def calculate_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Cosine similarity score [0, 1]
        """
        arr1 = np.array(emb1)
        arr2 = np.array(emb2)
        
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 < 1e-12 or norm2 < 1e-12:
            return 0.0
        
        similarity = np.dot(arr1, arr2) / (norm1 * norm2)
        return max(0.0, min(1.0, float(similarity)))
    
    def semantic_search(
        self, 
        query_embedding: List[float],
        document_embeddings: List[List[float]],
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Find k most similar documents to query.
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: List of document embeddings
            k: Number of results
            
        Returns:
            List of (doc_index, similarity_score) tuples
        """
        similarities = [
            (i, self.calculate_similarity(query_embedding, doc_emb))
            for i, doc_emb in enumerate(document_embeddings)
        ]
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:k]
    
    def compute_stat7_coordinates_from_embedding(
        self,
        embedding: List[float],
        realm: str = "narrative",
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compute STAT7 coordinates from an embedding vector.
        Maps embedding properties to 7D STAT7 space.
        
        Args:
            embedding: Embedding vector
            realm: STAT7 realm type
            content_metadata: Optional metadata for context
            
        Returns:
            Dictionary with STAT7 coordinates
        """
        arr = np.array(embedding)
        
        lineage = 0
        adjacency = float(np.linalg.norm(arr) / np.sqrt(len(arr)))
        
        variance = float(np.var(arr))
        entropy = float(np.sum(np.abs(arr) ** 2))
        luminosity = min(1.0, float(entropy / len(arr)))
        
        polarity = float(np.mean(arr[arr > 0]) if np.any(arr > 0) else 0.5)
        polarity = max(0.0, min(1.0, (polarity + 1.0) / 2.0))
        
        dimensionality = len(arr)
        
        horizon = "emergence"
        if content_metadata:
            if "lifecycle_stage" in content_metadata:
                horizon = content_metadata["lifecycle_stage"]
        
        return {
            "realm": {"type": realm, "label": "warbler_document"},
            "lineage": lineage,
            "adjacency": round(adjacency, 4),
            "horizon": horizon,
            "luminosity": round(luminosity, 4),
            "polarity": round(polarity, 4),
            "dimensionality": min(7, max(1, dimensionality // 50))
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model."""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "device": "cuda" if self.use_gpu else "cpu",
            "batch_size": self.batch_size,
            "cached_embeddings": len(self._embedding_cache),
            "cache_directory": str(self.cache_dir)
        }


class LocalEmbeddingProvider:
    """
    Deprecated TF-IDF based embedding provider.
    Kept for backward compatibility only.
    Use SentenceTransformerEmbeddingProvider instead.
    """
    
    def __init__(self):
        logger.warning("LocalEmbeddingProvider is deprecated. Use SentenceTransformerEmbeddingProvider instead.")
        self.embedding_dim = 384
    
    def embed_text(self, text: str) -> List[float]:
        """Fallback to dummy embeddings - DO NOT USE IN PRODUCTION."""
        logger.warning("LocalEmbeddingProvider returns dummy embeddings. Please use SentenceTransformerEmbeddingProvider.")
        return [0.0] * self.embedding_dim
    
    def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Fallback to dummy embeddings - DO NOT USE IN PRODUCTION."""
        return [[0.0] * self.embedding_dim for _ in texts]


def get_embedding_provider(
    use_gpu: bool = True,
    model_name: str = "all-MiniLM-L6-v2"
) -> SentenceTransformerEmbeddingProvider:
    """
    Factory function to get embedding provider.
    
    Args:
        use_gpu: Use GPU if available
        model_name: SentenceTransformer model name
        
    Returns:
        SentenceTransformerEmbeddingProvider instance
    """
    return SentenceTransformerEmbeddingProvider(
        model_name=model_name,
        use_gpu=use_gpu
    )


if __name__ == "__main__":
    provider = SentenceTransformerEmbeddingProvider()
    
    texts = [
        "The ancient library holds wisdom about dragons and treasure",
        "Warriors gather in the tavern to share tales of adventure",
        "A spell of great power requires three components to cast"
    ]
    
    print("Embedding texts...")
    embeddings = provider.embed_batch(texts)
    
    print(f"\nGenerated {len(embeddings)} embeddings of dimension {provider.embedding_dim}")
    
    print("\nSemantic search example:")
    query = "dragon treasure magic"
    query_emb = provider.embed_text(query)
    results = provider.semantic_search(query_emb, embeddings, k=2)
    
    for idx, sim in results:
        print(f"  {texts[idx][:60]}... (similarity: {sim:.4f})")
    
    print(f"\nModel info: {provider.get_model_info()}")
