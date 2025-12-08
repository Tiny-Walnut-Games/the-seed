"""ChatEnv enterprise dataset transformer."""

import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class EnterpriseTransformer(BaseWarblerTransformer):
    """Transform SustcZhangYX/ChatEnv dataset."""

    def transform(self, dataset_name: str = "SustcZhangYX/ChatEnv") -> List[Dict[str, Any]]:
        """
        Transform SustcZhangYX/ChatEnv dataset.

        Format: Software development chat conversations and collaborative coding scenarios

        Note: ChatEnv contains multi-agent software development conversations.
        """
        logger.info(f"Loading {dataset_name}...")
        items = []

        try:
            dataset = load_dataset(dataset_name)
            if hasattr(dataset, "__getitem__"):
                for split_name in ["train", "test", "validation", "default"]:
                    try:
                        if split_name in dataset:
                            items = list(dataset[split_name])
                            logger.info(f"Loaded {len(items)} items from '{split_name}' split")
                            break
                    except Exception as split_error:
                        logger.debug(f"Could not load split '{split_name}': {split_error}")
                        continue

                if not items:
                    items = self.extract_dataset_items(dataset)
                    if items:
                        logger.info(f"Extracted {len(items)} items from dataset")
        except Exception as e:
            logger.warning(f"Failed to load {dataset_name}: {e}")
            logger.info(f"Skipping {dataset_name} - dataset has loading issues")
            return []

        if not items:
            logger.warning(f"No items loaded from {dataset_name}")
            return []

        warbler_docs = []

        for idx, item in enumerate(items):
            if isinstance(item, dict) or hasattr(item, "__getitem__"):
                messages = []
                conversation = None

                for field in ["conversation", "messages", "chat", "dialogue"]:
                    try:
                        if isinstance(item, dict):
                            if field in item and item[field]:
                                conversation = item[field]
                                break
                        elif hasattr(item, "__getitem__") and field in item:
                            conversation = item[field]
                            break
                    except (KeyError, TypeError):
                        continue

                if conversation:
                    if isinstance(conversation, str):
                        messages = [conversation]
                    elif isinstance(conversation, list):
                        messages = conversation
                    else:
                        messages = [str(conversation)]

                messages_text = (
                    "\n".join(
                        (
                            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                            if isinstance(msg, dict)
                            else str(msg)
                        )
                        for msg in messages
                    )
                    if messages
                    else "[No conversation data available]"
                )

                task = (
                    item.get("task", item.get("scenario", "Software development chat"))
                    if isinstance(item, dict)
                    else "Software development chat"
                )
                scenario = (
                    item.get("scenario", item.get("task", f"ChatEnv Scenario #{idx + 1}"))
                    if isinstance(item, dict)
                    else f"ChatEnv Scenario #{idx + 1}"
                )

                doc = {
                    "content_id": f"chatenv/{idx}",
                    "content": self._create_content(
                        {
                            "scenario": scenario,
                            "task": task,
                            "labels": [],
                            "messages_preview": messages_text[:500],
                        }
                    ),
                    "metadata": {
                        "pack": "warbler-pack-chatenv",
                        "source_dataset": dataset_name,
                        "scenario": str(scenario)[:150],
                        "task": str(task)[:150],
                        "realm_type": "software_development",
                        "realm_label": "chatenv_collaboration",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.8,
                        "dialogue_type": "software_dev_chat",
                        "license": "MIT",
                    },
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} ChatEnv software development chat entries")
        return warbler_docs

    @staticmethod
    def _create_content(item: Dict[str, Any]) -> str:
        """Create content string for ChatEnv software development conversations."""
        labels = item.get("labels", [])
        labels_str = ", ".join(labels) if labels else "No labels specified"
        messages = item.get("messages_preview", "")

        content = f"""Scenario: {item.get('scenario', 'Unknown')}
Task: {item.get('task', 'Unknown')}
Labels: {labels_str}

This entry represents a software development collaboration scenario with
multi-agent conversations."""

        if messages:
            content += f"\n\nDevelopment Chat:\n{messages}"

        return content
