"""NPC Dialogue dataset transformer."""

import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class NPCDialogueTransformer(BaseWarblerTransformer):
    """Transform amaydle/npc-dialogue dataset."""

    def transform(self, dataset_name: str = "amaydle/npc-dialogue") -> List[Dict[str, Any]]:
        """
        Transform amaydle/npc-dialogue dataset.

        Format: Name, Biography, Query, Response, Emotion
        """
        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []

        for split in dataset.keys():
            for item in dataset[split]:
                doc = {
                    "content_id": f"npc-dialogue/{item['Name'].lower().replace(' ', '-')}",
                    "content": self._create_content(item),
                    "metadata": {
                        "pack": "warbler-pack-npc-dialogue",
                        "source_dataset": dataset_name,
                        "character_name": item["Name"],
                        "character_biography": (
                            item["Biography"][:200] + "..."
                            if len(item["Biography"]) > 200
                            else item["Biography"]
                        ),
                        "emotion": item["Emotion"],
                        "realm_type": "character",
                        "realm_label": "npc_dialogue",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.8,
                        "dialogue_type": "character_interaction",
                    },
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} NPC dialogue entries")
        return warbler_docs

    @staticmethod
    def _create_content(item: Dict[str, Any]) -> str:
        """Create content string for NPC dialogue."""
        return f"""Character: {item['Name']}
Biography: {item['Biography']}
Query: {item['Query']}
Response: {item['Response']}
Emotion: {item['Emotion']}

This represents a complete character interaction pattern for NPC training."""
