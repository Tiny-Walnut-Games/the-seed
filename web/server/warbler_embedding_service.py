"""
Warbler Embedding Service - Semantic Similarity Search with FAISS

Converts Warbler pack templates into embeddings and enables semantic
similarity search to retrieve contextually appropriate NPC dialogue.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
import pickle

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    raise ImportError(
        "Missing dependencies. Install with:\n"
        "  pip install sentence-transformers faiss-cpu\n"
        "  (or faiss-gpu for GPU support)"
    )

logger = logging.getLogger(__name__)


@dataclass
class EmbeddedTemplate:
    """Template with pre-computed embedding"""
    template_id: str
    content: str
    embedding: np.ndarray  # 384-dim for all-MiniLM-L6-v2
    metadata: Dict[str, Any]
    reputation_tier: Optional[str] = None
    tags: List[str] = None


class WarblerEmbeddingService:
    """
    Manages embeddings for Warbler packs using Sentence-Transformers.
    
    Uses 'all-MiniLM-L6-v2' (384 dims, permissive license) for:
    - Fast semantic similarity (~1-2ms per query)
    - Lightweight (~80MB model)
    - Excellent dialogue quality
    - MIT/Apache licensed
    """

    MODEL_NAME = "all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384
    BATCH_SIZE = 32

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize embedding service with optional caching"""
        self.model = SentenceTransformer(self.MODEL_NAME)
        self.cache_dir = cache_dir or Path.home() / ".cache" / "warbler_embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates: Dict[str, EmbeddedTemplate] = {}
        self.faiss_index: Optional[faiss.IndexFlatIP] = None
        self.template_ids: List[str] = []  # Maps FAISS index position to template_id
        self.templates_loaded = 0

    def embed_texts(self, texts: List[str], batch_size: int = BATCH_SIZE) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Process in batches for memory efficiency
            
        Returns:
            (N, 384) numpy array of embeddings
        """
        logger.debug(f"Embedding {len(texts)} texts with batch_size={batch_size}")
        embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
        return embeddings

    def add_template(
        self,
        template_id: str,
        content: str,
        metadata: Dict[str, Any],
        reputation_tier: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> EmbeddedTemplate:
        """
        Add a single template and compute its embedding.
        
        Args:
            template_id: Unique identifier (e.g., "greeting_formal_revered")
            content: Template text to embed
            metadata: Template metadata (pack, source, etc.)
            reputation_tier: Optional tier (revered, trusted, neutral, hostile)
            tags: Optional semantic tags (greeting, trade_inquiry, etc.)
            
        Returns:
            EmbeddedTemplate with computed embedding
        """
        embedding = self.embed_texts([content])[0]
        
        template = EmbeddedTemplate(
            template_id=template_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            reputation_tier=reputation_tier,
            tags=tags or []
        )
        
        self.templates[template_id] = template
        return template

    def add_templates_batch(self, templates_data: List[Dict[str, Any]]) -> List[EmbeddedTemplate]:
        """
        Efficiently add multiple templates and build FAISS index.
        
        Args:
            templates_data: List of dicts with:
                - template_id (str)
                - content (str)
                - metadata (dict)
                - reputation_tier (optional str)
                - tags (optional list)
                
        Returns:
            List of EmbeddedTemplate objects
        """
        logger.info(f"🔄 Embedding {len(templates_data)} templates...")
        
        # Extract texts for batch embedding
        template_ids = [t["template_id"] for t in templates_data]
        contents = [t["content"] for t in templates_data]
        
        # Compute embeddings in batches
        embeddings = self.embed_texts(contents, batch_size=self.BATCH_SIZE)
        
        # Create template objects
        embedded_templates = []
        for i, template_data in enumerate(templates_data):
            template = EmbeddedTemplate(
                template_id=template_data["template_id"],
                content=template_data["content"],
                embedding=embeddings[i],
                metadata=template_data.get("metadata", {}),
                reputation_tier=template_data.get("reputation_tier"),
                tags=template_data.get("tags", [])
            )
            self.templates[template_data["template_id"]] = template
            embedded_templates.append(template)
        
        logger.info(f"✓ Embedded {len(embedded_templates)} templates")
        
        # Build FAISS index
        self._build_faiss_index()
        
        return embedded_templates

    def _build_faiss_index(self) -> None:
        """Build FAISS index from loaded templates"""
        logger.info(f"🔄 Building FAISS index for {len(self.templates)} templates...")
        
        if not self.templates:
            logger.warning("No templates to index")
            return
        
        # Stack embeddings
        embeddings = np.stack([
            t.embedding for t in self.templates.values()
        ]).astype(np.float32)
        
        # Normalize for cosine similarity (FAISS IP on normalized = cosine)
        faiss.normalize_L2(embeddings)
        
        # Create index (inner product on normalized = cosine similarity)
        self.faiss_index = faiss.IndexFlatIP(self.EMBEDDING_DIM)
        self.faiss_index.add(embeddings)
        
        # Track mapping
        self.template_ids = list(self.templates.keys())
        
        logger.info(f"✓ Built FAISS index with {self.faiss_index.ntotal} templates")

    def search_semantic(
        self,
        query: str,
        top_k: int = 5,
        reputation_tier: Optional[str] = None,
        min_similarity: float = 0.3
    ) -> List[Tuple[str, float, EmbeddedTemplate]]:
        """
        Find semantically similar templates using FAISS.
        
        Args:
            query: Query text (player input)
            top_k: Number of results to return
            reputation_tier: Optional filter (return templates matching tier)
            min_similarity: Minimum similarity score (0-1)
            
        Returns:
            List of (template_id, similarity_score, template) tuples
        """
        if not self.faiss_index or not self.templates:
            logger.warning("No templates indexed for semantic search")
            return []
        
        # Embed query
        query_embedding = self.embed_texts([query])[0]
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.faiss_index.search(query_embedding, top_k * 2)
        
        # Post-process results
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(self.template_ids):
                continue
                
            template_id = self.template_ids[idx]
            template = self.templates[template_id]
            similarity = float(score)  # Normalized cosine similarity
            
            # Apply filters
            if similarity < min_similarity:
                continue
            if reputation_tier and template.reputation_tier != reputation_tier:
                continue
            
            results.append((template_id, similarity, template))
            
            if len(results) >= top_k:
                break
        
        return results

    def get_template(self, template_id: str) -> Optional[EmbeddedTemplate]:
        """Retrieve template by ID"""
        return self.templates.get(template_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics"""
        return {
            "templates_loaded": len(self.templates),
            "embedding_model": self.MODEL_NAME,
            "embedding_dim": self.EMBEDDING_DIM,
            "faiss_indexed": self.faiss_index is not None,
            "index_size": self.faiss_index.ntotal if self.faiss_index else 0,
            "cache_dir": str(self.cache_dir)
        }

    def save_index(self, path: Path) -> None:
        """
        Save FAISS index and metadata to disk.
        
        Useful for pre-computing embeddings at pack load time.
        """
        path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.faiss_index, str(path / "faiss.index"))
        
        # Save template metadata (not embeddings, to save space)
        metadata = {
            template_id: {
                "content": template.content,
                "metadata": template.metadata,
                "reputation_tier": template.reputation_tier,
                "tags": template.tags
            }
            for template_id, template in self.templates.items()
        }
        
        with open(path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        with open(path / "template_ids.json", "w") as f:
            json.dump(self.template_ids, f)
        
        logger.info(f"✓ Saved FAISS index to {path}")

    def load_index(self, path: Path) -> None:
        """Load pre-computed FAISS index from disk"""
        logger.info(f"🔄 Loading FAISS index from {path}...")
        
        # Load FAISS index
        self.faiss_index = faiss.read_index(str(path / "faiss.index"))
        
        # Load metadata
        with open(path / "metadata.json") as f:
            metadata = json.load(f)
        
        with open(path / "template_ids.json") as f:
            self.template_ids = json.load(f)
        
        # Reconstruct templates (without embeddings)
        for template_id in self.template_ids:
            data = metadata[template_id]
            self.templates[template_id] = EmbeddedTemplate(
                template_id=template_id,
                content=data["content"],
                embedding=np.zeros(self.EMBEDDING_DIM),  # Placeholder
                metadata=data["metadata"],
                reputation_tier=data["reputation_tier"],
                tags=data["tags"]
            )
        
        logger.info(f"✓ Loaded FAISS index with {len(self.templates)} templates")