"""Prompt report dataset transformer."""

import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class PromptReportTransformer(BaseWarblerTransformer):
    """Transform PromptSystematicReview/ThePromptReport dataset."""

    def transform(
        self, dataset_name: str = "PromptSystematicReview/ThePromptReport"
    ) -> List[Dict[str, Any]]:
        """
        Transform PromptSystematicReview/ThePromptReport dataset.

        Format: Prompt engineering documentation and analysis
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
                    "content_id": (
                        f"prompt-report/{item.get('id', hash(item.get('title', '')) % 10000)}"
                    ),
                    "content": self._create_content(item),
                    "metadata": {
                        "pack": "warbler-pack-prompt-report",
                        "source_dataset": dataset_name,
                        "title": item.get("title", "")[:150],
                        "category": item.get("category", "prompting"),
                        "realm_type": "methodological",
                        "realm_label": "prompt_engineering",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.8,
                        "dialogue_type": "technical_discussion",
                        "license": "MIT",
                    },
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} prompt report entries")
        return warbler_docs

    @staticmethod
    def _create_content(item: Dict[str, Any]) -> str:
        """Create content string for prompt report."""
        return f"""Title: {item.get('title', 'Untitled')}
Category: {item.get('category', 'Unknown')}

Content:
{item.get('text', 'No content available')}

This document contributes to the systematic study of prompting techniques."""
