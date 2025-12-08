"""Multi-character dialogue dataset transformer."""

import json
import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class MultiCharacterTransformer(BaseWarblerTransformer):
    """Transform agentlans/multi-character-dialogue dataset."""

    def transform(
        self, dataset_name: str = "agentlans/multi-character-dialogue"
    ) -> List[Dict[str, Any]]:
        """
        Transform agentlans/multi-character-dialogue dataset.

        Format: setting, characters, conversation, setting_after_interaction
        """
        logger.info(f"Loading {dataset_name}...")
        try:
            dataset = load_dataset(dataset_name)
        except Exception as e:
            logger.warning(f"Failed to load {dataset_name}: {e}")
            return []

        warbler_docs = []

        try:
            if "train" not in dataset:
                logger.warning("Multi-char: No 'train' split found in dataset")
                return []

            train_data = dataset["train"]
            total_items = len(train_data) if hasattr(train_data, "__len__") else 0
            logger.info(f"Processing {total_items} multi-character dialogue items...")

            for idx, item in enumerate(train_data):
                if idx > 0 and idx % 1000 == 0:
                    logger.info(
                        f"Processed {idx}/{total_items} items, created "
                        f"{len(warbler_docs)} documents"
                    )

                try:
                    if item is None:
                        logger.warning(f"Multi-char {idx + 1}: Item is None, skipping")
                        continue

                    if not isinstance(item, dict):
                        logger.warning(
                            f"Multi-char {idx + 1}: Item is not a dict "
                            f"(type: {type(item)}), skipping"
                        )
                        continue

                    setting = item.get("setting", "")
                    characters = item.get("characters", [])
                    conversation = item.get("conversation", [])

                    if not isinstance(setting, str):
                        setting = str(setting) if setting is not None else ""
                    if not isinstance(characters, list):
                        characters = [] if characters is None else [characters]
                    if not isinstance(conversation, list):
                        conversation = [] if conversation is None else [conversation]

                    if not setting and not conversation:
                        logger.warning(f"Multi-char {idx + 1}: Missing essential data, skipping")
                        continue

                    if conversation and not all(
                        isinstance(msg, (dict, str)) for msg in conversation[:10]
                    ):
                        logger.warning(
                            f"Multi-char {idx + 1}: Invalid conversation structure, skipping"
                        )
                        continue

                    try:
                        content = self._create_content(item)
                    except Exception as content_error:
                        logger.warning(
                            f"Multi-char {idx + 1}: Error creating content: "
                            f"{content_error}, using fallback"
                        )
                        setting_preview = setting[:100]
                        content = (
                            f"[Multi-character dialogue content unavailable]\n"
                            f"Setting: {setting_preview}"
                        )

                    doc = {
                        "content_id": f"multi-char/{hash(setting) % 10000 if setting else idx}",
                        "content": content,
                        "metadata": {
                            "pack": "warbler-pack-multi-character",
                            "source_dataset": dataset_name,
                            "setting": setting[:150] + "..." if len(setting) > 150 else setting,
                            "character_count": (
                                len(characters) if isinstance(characters, list) else 0
                            ),
                            "conversation_length": (
                                len(conversation) if isinstance(conversation, list) else 0
                            ),
                            "realm_type": "narrative",
                            "realm_label": "multi_character_dialogue",
                            "lifecycle_stage": "emergence",
                            "activity_level": 0.7,
                            "dialogue_type": "multi_character_interaction",
                        },
                    }
                    warbler_docs.append(doc)

                except MemoryError as mem_err:
                    logger.error(
                        f"Multi-char {idx + 1}: Memory error - {mem_err}. "
                        f"Stopping processing to prevent crash."
                    )
                    break
                except RecursionError as rec_err:
                    logger.error(
                        f"Multi-char {idx + 1}: Recursion error - {rec_err}. Skipping item."
                    )
                    continue
                except (KeyboardInterrupt, SystemExit):
                    logger.warning(f"Multi-char: Processing interrupted at item {idx + 1}")
                    raise
                except Exception as e:
                    logger.warning(
                        f"Multi-char {idx + 1}: Error processing item: {type(e).__name__}: {e}"
                    )
                    continue

        except (MemoryError, RecursionError) as critical_error:
            logger.error(
                f"Multi-char: Critical error during iteration: "
                f"{type(critical_error).__name__}: {critical_error}"
            )
            logger.info(f"Returning {len(warbler_docs)} documents processed before error")
        except (KeyboardInterrupt, SystemExit):
            logger.warning(
                f"Multi-char: Processing interrupted, returning {len(warbler_docs)} documents"
            )
            raise
        except Exception as outer_error:
            logger.error(
                f"Multi-char: Unexpected error during dataset iteration: "
                f"{type(outer_error).__name__}: {outer_error}"
            )
            logger.info(f"Returning {len(warbler_docs)} documents processed before error")

        logger.info(f"✓ Transformed {len(warbler_docs)} multi-character entries")
        return warbler_docs

    @staticmethod
    def _create_content(item: Dict[str, Any]) -> str:
        """Create content string for multi-character dialogue with comprehensive error handling."""
        if not isinstance(item, dict):
            return "[Invalid item format - not a dictionary]"

        conversation = item.get("conversation", [])
        conversation_lines = []
        max_conversation_items = 1000

        if isinstance(conversation, list):
            conversation_subset = conversation[:max_conversation_items]

            for msg_idx, msg in enumerate(conversation_subset):
                try:
                    if msg is None:
                        continue

                    if isinstance(msg, dict):
                        from_field = msg.get("from", "Unknown")
                        message_field = msg.get("message", "")

                        if not isinstance(from_field, str):
                            from_field = str(from_field) if from_field is not None else "Unknown"
                        if not isinstance(message_field, str):
                            message_field = str(message_field) if message_field is not None else ""

                        if len(message_field) > 5000:
                            message_field = message_field[:5000] + "... [truncated]"

                        conversation_lines.append(f"{from_field}: {message_field}")

                    elif isinstance(msg, str):
                        if len(msg) > 5000:
                            msg = msg[:5000] + "... [truncated]"
                        conversation_lines.append(msg)

                    else:
                        conversation_lines.append(f"[Message {msg_idx + 1}: {type(msg).__name__}]")

                except (RecursionError, MemoryError) as critical_err:
                    logger.warning(
                        f"Critical error processing conversation message {msg_idx}: {critical_err}"
                    )
                    break
                except Exception as msg_err:
                    logger.debug(f"Error processing conversation message {msg_idx}: {msg_err}")
                    continue

            if len(conversation) > max_conversation_items:
                conversation_lines.append(
                    f"\n[... {len(conversation) - max_conversation_items} more messages truncated]"
                )

        conversation_text = (
            "\n".join(conversation_lines) if conversation_lines else "[No conversation available]"
        )

        setting = item.get("setting", "[No setting provided]")
        if not isinstance(setting, str):
            setting = str(setting) if setting is not None else "[No setting provided]"

        if len(setting) > 2000:
            setting = setting[:2000] + "... [truncated]"

        characters = item.get("characters", [])
        if not isinstance(characters, list):
            characters = [] if characters is None else [characters]

        setting_after = item.get(
            "setting after interaction", "[No setting after interaction provided]"
        )
        if not isinstance(setting_after, str):
            setting_after = (
                str(setting_after)
                if setting_after is not None
                else "[No setting after interaction provided]"
            )

        if len(setting_after) > 2000:
            setting_after = setting_after[:2000] + "... [truncated]"

        characters_str = "[]"
        try:
            if len(characters) > 100:
                characters = characters[:100]
                characters_str = (
                    json.dumps(characters, indent=2, ensure_ascii=False) + "\n[... truncated]"
                )
            else:
                characters_str = (
                    json.dumps(characters, indent=2, ensure_ascii=False) if characters else "[]"
                )
        except (TypeError, ValueError, RecursionError) as json_err:
            logger.debug(f"Error serializing characters to JSON: {json_err}")
            try:
                characters_str = str(characters)[:500] if characters else "[]"
            except Exception:
                characters_str = "[Error formatting characters]"

        try:
            content = f"""Setting: {setting}
Characters: {characters_str}
Conversation:
{conversation_text}

After Interaction: {setting_after}

This represents a multi-character narrative scenario for NPC interaction training."""

            if len(content) > 50000:
                content = content[:50000] + "\n\n[Content truncated due to size]"

            return content
        except Exception as final_err:
            logger.warning(f"Error building final content: {final_err}")
            return f"[Error creating multi-character content: {type(final_err).__name__}]"
