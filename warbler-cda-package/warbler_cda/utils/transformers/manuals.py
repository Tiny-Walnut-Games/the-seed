"""Technical manuals dataset transformer."""

import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class ManualsTransformer(BaseWarblerTransformer):
    """Transform nlasso/anac-manuals-23 dataset."""

    def transform(self, dataset_name: str = "nlasso/anac-manuals-23") -> List[Dict[str, Any]]:
        """
        Transform nlasso/anac-manuals-23 dataset.

        Format: Technical procedure and instruction manuals
        """
        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []

        if isinstance(dataset, list):
            items = dataset
        elif hasattr(dataset, "keys"):
            items = []
            for split in dataset.keys():
                items.extend(dataset[split])
        else:
            items = dataset

        for item in items:
            if isinstance(item, dict):
                doc = {
                    "content_id": f"manual/{item.get('id', hash(item.get('title', '')) % 10000)}",
                    "content": self._create_content(item),
                    "metadata": {
                        "pack": "warbler-pack-manuals",
                        "source_dataset": dataset_name,
                        "title": item.get("title", "")[:150],
                        "sections": len(item.get("sections", [])),
                        "realm_type": "procedural",
                        "realm_label": "technical_manual",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.7,
                        "dialogue_type": "instructional_content",
                        "license": "MIT",
                    },
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} manual entries")
        return warbler_docs

    @staticmethod
    def _create_content(item: Dict[str, Any]) -> str:
        """Create content string for technical manual."""
        sections = item.get("sections", [])
        sections_str = "\n".join(f"- {s}" for s in sections) if sections else "No sections listed"

        return f"""Manual: {item.get('title', 'Untitled')}

Sections:
{sections_str}

Content:
{item.get('content', 'No content available')}

This manual provides technical guidance and procedures."""
