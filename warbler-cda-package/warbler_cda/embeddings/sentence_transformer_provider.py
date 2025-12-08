"""SentenceTransformer Embedding Provider - GPU-Accelerated Semantic Grounding.

High-quality embeddings using pre-trained transformer models with CUDA support
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from .base_provider import EmbeddingProvider

if TYPE_CHECKING:
    from sentence_transformers import (
        SentenceTransformer as SentenceTransformerType,
    )

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """GPU-accelerated embedding provider using SentenceTransformers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        model_name_default = "all-MiniLM-L6-v2"
        self.model_name: str = (
            config.get("model_name", model_name_default)
            if config
            else model_name_default
        )
        self.batch_size: int = config.get("batch_size", 32) if config else 32
        cache_dir_default = ".embedding_cache"
        self.cache_dir: str = (
            config.get("cache_dir", cache_dir_default) if config else cache_dir_default
        )

        self.model: Optional["SentenceTransformerType"] = None
        self.device: Optional[str] = None
        self.dimension: Optional[int] = None
        self.cache: Dict[str, List[float]] = {}
        self.cache_stats: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "total_embeddings": 0,
        }

        self._initialize_model()
        self._load_cache()

    def _initialize_model(self) -> None:
        """Initialize the SentenceTransformer model with device detection."""
        try:
            from sentence_transformers import SentenceTransformer

            import torch

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = SentenceTransformer(self.model_name, device=self.device)
            if self.model is not None:
                self.dimension = self.model.get_sentence_embedding_dimension()

        except ImportError:
            self.model = None
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        cache_key = self._get_cache_key(text)

        if cache_key in self.cache:
            self.cache_stats["hits"] += 1
            return self.cache[cache_key]

        self.cache_stats["misses"] += 1
        if self.model is None:
            raise RuntimeError("Model not initialized. Call _initialize_model first.")
        embedding: Any = self.model.encode(text, convert_to_tensor=False)

        embedding_list: List[float] = (
            embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
        )
        self.cache[cache_key] = embedding_list
        self.cache_stats["total_embeddings"] += 1

        return embedding_list

    def embed_batch(
        self, texts: List[str], show_progress: bool = False
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts with batching and caching."""
        # Check model initialization first, before processing
        if texts and self.model is None:
            raise RuntimeError("Model not initialized. Call _initialize_model first.")

        embeddings: List[List[float]] = []
        texts_to_embed: List[str] = []
        cache_keys: List[str] = []
        indices_to_embed: List[int] = []

        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            cache_keys.append(cache_key)

            if cache_key in self.cache:
                embeddings.append(self.cache[cache_key])
                self.cache_stats["hits"] += 1
            else:
                texts_to_embed.append(text)
                indices_to_embed.append(i)

        if texts_to_embed:
            self.cache_stats["misses"] += len(texts_to_embed)
            if self.model is not None:
                # Generate embeddings for batch with caching
                if SentenceTransformer is not None and not isinstance(
                    self.model, SentenceTransformer
                ):
                    raise ValueError("Model is not an instance of SentenceTransformer")
                elif SentenceTransformer is None:
                    raise RuntimeError("SentenceTransformer not available but model is set")
            batch_embeddings: Any = self.model.encode(
                texts_to_embed,
                batch_size=self.batch_size,
                convert_to_tensor=False,
                show_progress_bar=show_progress,
            )

            for idx, batch_idx in enumerate(indices_to_embed):
                embedding: Any = batch_embeddings[idx]
                embedding_list: List[float] = (
                    embedding.tolist()
                    if hasattr(embedding, "tolist")
                    else list(embedding)
                )
                self.cache[cache_keys[batch_idx]] = embedding_list
                self.cache_stats["total_embeddings"] += 1

            self._save_cache()

        result: List[List[float]] = []
        for cache_key in cache_keys:
            result.append(self.cache[cache_key])

        return result

    def semantic_search(
        self, query_text: str, embeddings: List[List[float]], top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """Find k semantically similar embeddings from a list."""
        query_embedding: List[float] = self.embed_text(query_text)

        similarities: List[Tuple[int, float]] = []
        for i, emb in enumerate(embeddings):
            sim: float = self.calculate_similarity(query_embedding, emb)
            similarities.append((i, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self.dimension is None:
            raise RuntimeError(
                "Dimension not initialized. Call _initialize_model first."
            )
        return self.dimension

    def get_provider_info(self) -> Dict[str, Any]:
        """Get detailed provider information."""
        info = super().get_provider_info()
        info.update(
            {
                "model_name": self.model_name,
                "device": self.device,
                "batch_size": self.batch_size,
                "cache_stats": self.cache_stats.copy(),
                "cache_size": len(self.cache),
                "cache_dir": self.cache_dir,
            }
        )
        return info

    def _get_cache_key(self, text: str) -> str:
        """Generate consistent cache key for text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _load_cache(self) -> None:
        """Load embeddings from disk cache."""
        cache_file = Path(self.cache_dir) / (
            f"{self.model_name.replace('/', '_')}_cache.json"
        )

        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    self.cache = json.load(f)
                    self.cache_stats["total_embeddings"] = len(self.cache)
            except Exception as e:
                print(f"Warning: Could not load cache from {cache_file}: {e}")

    def _save_cache(self) -> None:
        """Save embeddings to disk cache."""
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        cache_file = Path(self.cache_dir) / (
            f"{self.model_name.replace('/', '_')}_cache.json"
        )

        try:
            with open(cache_file, "w") as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Warning: Could not save cache to {cache_file}: {e}")

    def compute_fractalstat_from_embedding(self, embedding: List[float]) -> Dict[str, Any]:
        """
        Compute 8D FractalStat coordinates from embedding vector.

        Maps 384D embedding to 8D FractalStat addressing space using robust
        statistical features. Includes the new alignment dimension for
        social/coordination dynamics.

        Returns coordinates for the 8 dimensions:
        - lineage: Generation/progression (0.0+)
        - adjacency: Semantic proximity score (-1.0 to 1.0)
        - luminosity: Activity/coherence level (0.0 to 100.0)
        - polarity: Resonance/affinity balance (-1.0 to 1.0)
        - dimensionality: Complexity depth (scaled to 1-8)
        - horizon: Lifecycle stage ("scene" derived)
        - realm: Domain classification ("semantic" derived)
        - alignment: Social coordination dynamics (harmonic, chaotic, etc.)
        """
        import numpy as np

        emb_array = np.array(embedding)
        dim = len(embedding)

        if dim == 0:
            return {
                "lineage": 0.5,
                "adjacency": 0.5,
                "luminosity": 70.0,  # Scale to 0-100 range
                "polarity": 0.0,
                "dimensionality": 3,  # Scale to 1-8 range
                "horizon": "scene",
                "realm": {"type": "semantic", "label": "embedding-derived"},
                "alignment": {"type": "true_neutral"},  # Default neutral alignment
            }

        abs_emb = np.abs(emb_array)

        # Divide embedding into 8 segments for 8D mapping
        seg_size = dim // 8

        seg0 = emb_array[:seg_size]          # lineage
        seg1 = emb_array[seg_size : 2 * seg_size]    # adjacency
        seg2 = emb_array[2 * seg_size : 3 * seg_size] # luminosity
        seg3 = emb_array[3 * seg_size : 4 * seg_size] # polarity
        seg4 = emb_array[4 * seg_size : 5 * seg_size] # dimensionality
        seg5 = emb_array[5 * seg_size : 6 * seg_size] # alignment (social dynamics)
        seg6 = emb_array[6 * seg_size : 7 * seg_size] # horizon energy
        seg7 = emb_array[7 * seg_size :]    # realm characterization

        # Lineage: Generation/progression from energy patterns
        lineage = float(np.mean(seg0**2))

        # Adjacency: Semantic connectivity through correlations
        if len(seg1) > 1 and len(seg2) > 1 and len(seg3) > 1:
            def safe_corrcoef(a, b):
                if np.std(a) > 1e-10 and np.std(b) > 1e-10:
                    corr = np.corrcoef(a, b)[0, 1]
                    return corr if not np.isnan(corr) else 0.0
                return 0.0

            corr_12 = safe_corrcoef(seg1, seg2)
            corr_23 = safe_corrcoef(seg2, seg3)
            corr_34 = safe_corrcoef(seg3, seg4) if len(seg4) > 1 else 0.0
            # Only compute corr_56 if both segments have the same length
            if len(seg5) > 1 and len(seg6) > 1 and len(seg5) == len(seg6):
                corr_56 = safe_corrcoef(seg5, seg6)
            else:
                corr_56 = 0.0

            adjacency = float((corr_12 + corr_23 + corr_34 + corr_56) / 4.0)
        else:
            adjacency = 0.0

        # Luminosity: Activity/energy level (0-100 scale)
        luminosity = float(np.mean(abs_emb[2 * seg_size : 3 * seg_size]) * 100.0)

        # Polarity: Resonance balance from directional preferences
        polarity_part1 = float(np.mean(seg3 > np.median(emb_array)))
        polarity_part2 = float(np.mean(seg5 > np.median(emb_array)) / 2.0)
        polarity_balance = polarity_part1 + polarity_part2

        # Add directional bias from alignment segment
        if len(seg6) > 1:
            alignment_direction = np.mean(seg6) - np.median(seg6)
            polarity_balance += alignment_direction * 0.1

        polarity = polarity_balance

        # Dimensionality: Complexity/depth score (1-8 scale)
        chunk_size = 12
        num_chunks = dim // chunk_size
        if num_chunks > 0:
            chunk_sums: List[float] = [
                np.sum(abs_emb[i * chunk_size : (i + 1) * chunk_size])
                for i in range(num_chunks)
            ]
            chunk_entropy = float(np.std(chunk_sums) / (np.mean(chunk_sums) + 1e-8))
        else:
            chunk_entropy = 0.0

        high_magnitude = float(np.sum(abs_emb > np.percentile(abs_emb, 75)) / dim)
        dimensionality_raw = (high_magnitude + min(1.0, chunk_entropy * 0.2)) / 2.0
        dimensionality = max(1, min(8, int(np.round(dimensionality_raw * 7 + 1))))

        # Alignment: Social/coordination dynamics (8th dimension)
        # Based on coordination patterns in the alignment segment
        if len(seg5) > 1:
            # Measure coordination through cross-correlations between alignment features
            alignment_stability = float(np.std(seg5) / (np.mean(np.abs(seg5)) + 1e-8))
            alignment_coherence = safe_corrcoef(seg4, seg6) if len(seg6) > 1 else 0.0
            alignment_social = (1.0 - alignment_stability) * (alignment_coherence + 1.0) / 2.0

            # Map to alignment types based on social dynamics score
            alignment_score = alignment_social * 100.0
            if alignment_score > 70.0:
                alignment_type = "harmonic"
            elif alignment_score > 40.0:
                alignment_type = "symbiotic"
            elif alignment_score > 10.0:
                alignment_type = "true_neutral"
            elif alignment_score > -20.0:
                alignment_type = "balanced"
            elif alignment_score > -50.0:
                alignment_type = "entropic"
            else:
                alignment_type = "chaotic"
        else:
            alignment_type = "true_neutral"

        # Hybrid normalization preserving fractal structure:
        # - Fractal dimensions (lineage, dimensionality): unbounded/scaled appropriately
        # - Relational dimensions (adjacency, polarity): symmetric [-1, 1]
        # - Intensity dimensions (luminosity): asymmetric [0, 100]
        adjacency = float(np.clip(adjacency, -1.0, 1.0))
        luminosity = float(np.clip(luminosity, 0.0, 100.0))
        polarity = float(np.clip(polarity, -1.0, 1.0))

        return {
            "lineage": lineage,
            "adjacency": adjacency,
            "luminosity": luminosity,
            "polarity": polarity,
            "dimensionality": dimensionality,
            "horizon": "scene",
            "realm": {"type": "semantic", "label": "embedding-derived"},
            "alignment": {"type": alignment_type},
        }
