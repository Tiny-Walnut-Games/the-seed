"""System chat dataset transformer."""

import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class SystemChatTransformer(BaseWarblerTransformer):
    """Transform abacusai/SystemChat dataset."""

    def transform(self, dataset_name: str = "abacusai/SystemChat") -> List[Dict[str, Any]]:
        """
        Transform abacusai/SystemChat dataset.

        Format: conversations with system prompts
        """
        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []

        for item in dataset["train"]:
            conversations = item["conversations"]

            system_msg = next(
                (msg["value"] for msg in conversations if msg["from"] == "system"), ""
            )
            human_msg = next((msg["value"] for msg in conversations if msg["from"] == "human"), "")
            ai_msg = next((msg["value"] for msg in conversations if msg["from"] == "gpt"), "")

            if system_msg and human_msg and ai_msg:
                doc = {
                    "content_id": f"system-chat/{hash(system_msg) % 10000}",
                    "content": self._create_content(system_msg, human_msg, ai_msg),
                    "metadata": {
                        "pack": "warbler-pack-system-chat",
                        "source_dataset": dataset_name,
                        "system_role": (
                            system_msg[:100] + "..." if len(system_msg) > 100 else system_msg
                        ),
                        "conversation_length": len(conversations),
                        "realm_type": "instructional",
                        "realm_label": "system_chat",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.6,
                        "dialogue_type": "instruction_following",
                        "license": "unknown",
                    },
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} system chat entries")
        return warbler_docs

    @staticmethod
    def _create_content(system: str, human: str, ai: str) -> str:
        """Create content string for system chat."""
        return f"""System: {system}
Human: {human}
AI: {ai}

This represents an instruction-following pattern for NPC behavior training."""
