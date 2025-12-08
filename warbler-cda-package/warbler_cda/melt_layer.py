"""Melt Layer: Manages semantic anchor persistence and state transitions."""

from __future__ import annotations
from typing import Dict, Any, List
import time, hashlib


class MeltLayer:
    """Melt Layer: retires clusters into molten glyphs.

    Append-only; never mutate an existing glyph in-place.
    """

    def __init__(self, magma_store: "MagmaStore", embed_fn=None):
        """Initialize the melt layer."""
        self.magma_store = magma_store
        self.embed_fn = embed_fn or (lambda frags: [0.0])

    def retire_cluster(self, cluster: Dict[str, Any]) -> Dict[str, Any]:
        """Process the melt layer."""
        fragments: List[Dict[str, Any]] = cluster.get("fragments", [])
        summary = self._summarize(fragments)
        glyph_id = self._glyph_id(summary)
        glyph = {
            "id": glyph_id,
            "source_ids": [f.get("id") for f in fragments if f.get("id")],
            "compressed_summary": summary,
            "embedding": self.embed_fn([f.get("text", "") for f in fragments]),
            "affect": {"awe": 0.1, "humor": 0.05, "tension": 0.05},
            "resolution_state": "retired",
            "heat_seed": 0.55,
            "provenance_hash": self._prov_hash(fragments),
            "created_epoch": int(time.time()),
        }
        self.magma_store.add_glyph(glyph)
        return glyph

    def _glyph_id(self, summary: str) -> str:
        return "mglyph_" + hashlib.sha256(summary.encode()).hexdigest()[:12]

    def _summarize(self, fragments: List[Dict[str, Any]]) -> str:
        """Summarize the cluster by combining the first few text fragments."""
        if not fragments:
            return "(empty cluster)"
        texts = [f.get("text", "").strip() for f in fragments if f.get("text", "").strip()]
        if not texts:
            return "(empty cluster)"
        # Take first text as primary summary, combine others with separator
        summary = texts[0]
        if len(texts) > 1:
            additional = " | ".join(texts[1:])
            # Check if truncation needed
            if len(texts[0]) > 100 or len(additional) > 50:
                summary = f"{texts[0][:100]}... ({additional[:50]}...)"
            else:
                summary = f"{texts[0]} | {additional}"
        return summary[:200] or "(empty cluster)"

    def _prov_hash(self, fragments: List[Dict[str, Any]]) -> str:
        concat = "".join(f.get("text", "") for f in fragments)
        return "sha256:" + hashlib.sha256(concat.encode()).hexdigest()


class MagmaStore:
    """Stores glyphs for the melt layer."""
    def __init__(self):
        """Initialize the glyph store."""
        self.glyphs = []

    def add_glyph(self, glyph: Dict[str, Any]):
        """Add a glyph to the store."""
        self.glyphs.append(glyph)

    def select_hot(self, limit: int) -> List[Dict[str, Any]]:
        """Get the hottest glyphs based on heat score (recency and base heat)."""
        if limit <= 0:
            return []
        # Sort by calculated heat score, descending
        now = int(time.time())
        for glyph in self.glyphs:
            glyph["heat"] = self._calculate_heat(glyph, now)
        self.glyphs.sort(key=lambda g: g["heat"], reverse=True)
        return self.glyphs[:limit]

    def _calculate_heat(self, glyph: Dict[str, Any], current_time: int) -> float:
        """Calculate current heat score, decaying over time."""
        base_heat = glyph.get("heat_seed", 0.5)
        created = glyph.get("created_epoch", current_time)
        # Decay by 10% per hour
        hours_elapsed = (current_time - created) / 3600.0
        decay_factor = 0.9 ** hours_elapsed
        return base_heat * decay_factor
