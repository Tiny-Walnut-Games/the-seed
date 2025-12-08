"""arXiv papers dataset transformer."""

import logging
from typing import List, Dict, Any, Optional

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class ArxivTransformer(BaseWarblerTransformer):
    """Transform nick007x/arxiv-papers dataset."""

    def transform(
        self, dataset_name: str = "nick007x/arxiv-papers", limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Transform nick007x/arxiv-papers dataset.

        ⚠️  CRITICAL: HuggingFace 1GB storage limit enforced!
           This transformer is capped at processing first 250,000 documents
           (5 chunks at 50,000 docs/chunk) regardless of the limit parameter.
        """
        # 🔐 CRITICAL: Enforce HuggingFace 1GB storage limit
        # Only process first 250,000 documents to stay within 1GB limit
        HF_STORAGE_LIMIT = 250000

        # If no limit specified or limit is higher than allowed, use storage limit
        if limit is None or limit > HF_STORAGE_LIMIT:
            limit = HF_STORAGE_LIMIT
            logger.warning(f"ArXiv dataset limited to {HF_STORAGE_LIMIT} documents for 1GB storage compliance")

        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []
        count = 0

        for split in dataset.keys():
            for item in dataset[split]:
                if limit and count >= limit:
                    break

                doc = {
                    "content_id": (
                        f"arxiv/{item.get('arxiv_id', hash(item.get('title', '')) % 10000)}"
                    ),
                    "content": self._create_content(item),
                    "metadata": {
                        "pack": "warbler-pack-arxiv",
                        "source_dataset": dataset_name,
                        "arxiv_id": item.get("arxiv_id", ""),
                        "title": item.get("title", "")[:150],
                        "authors": item.get("authors", "")[:200],
                        "year": item.get("year", 2023),
                        "categories": item.get("categories", ""),
                        "realm_type": "scholarly",
                        "realm_label": "arxiv",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.7,
                        "dialogue_type": "scholarly_discussion",
                        "license": "MIT",
                    },
                }
                warbler_docs.append(doc)
                count += 1

        logger.info(f"✓ Transformed {len(warbler_docs)} arXiv papers")
        return warbler_docs

    @staticmethod
    def _create_content(item: Dict[str, Any]) -> str:
        """Create content string for arXiv paper."""
        return f"""Title: {item.get('title', 'Untitled')}
Authors: {item.get('authors', 'Unknown')}
Year: {item.get('year', 'Unknown')}
Categories: {item.get('categories', 'Unknown')}

Abstract:
{item.get('abstract', 'No abstract available')}

This scholarly work contributes to the knowledge base of academic research."""
