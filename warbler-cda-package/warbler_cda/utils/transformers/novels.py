"""Novels dataset transformer with PDF extraction support."""

import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class NovelsTransformer(BaseWarblerTransformer):
    """Transform GOAT-AI/generated-novels dataset."""

    def transform(self, dataset_name: str = "GOAT-AI/generated-novels") -> List[Dict[str, Any]]:
        """
        Transform GOAT-AI/generated-novels dataset.

        Format: Full-length generated novels (PDF-based, treated as narrative metadata)
        """
        logger.info(f"Loading {dataset_name}...")
        try:
            dataset = load_dataset(dataset_name)
        except Exception as e:
            logger.warning(f"Failed to load {dataset_name}: {e}")
            logger.info("Creating placeholder entries for novel dataset")
            return self._create_placeholders(20)

        warbler_docs = []
        chunk_size = 1000

        items = []
        try:
            if hasattr(dataset, "__getitem__") and "train" in dataset:
                items = list(dataset["train"])
                logger.info(f"Loaded {len(items)} items from 'train' split")
            else:
                items = self.extract_dataset_items(dataset)
                logger.info(f"Extracted {len(items)} items from dataset")
        except Exception as e:
            logger.warning(f"Error accessing dataset: {e}")
            items = self.extract_dataset_items(dataset)

        for idx, item in enumerate(items):
            if isinstance(item, str):
                logger.warning(f"Novel {idx + 1}: Item is a string, skipping")
                continue

            if isinstance(item, dict) or hasattr(item, "__getitem__"):
                text = None
                item_keys = []
                try:
                    if isinstance(item, dict):
                        item_keys = list(item.keys())
                    elif hasattr(item, "keys") and callable(item.keys):
                        item_keys = list(item.keys())
                except Exception:
                    item_keys = []

                for field in ["text", "story", "content", "novel", "body", "full_text"]:
                    try:
                        if isinstance(item, dict):
                            if field in item and item[field]:
                                text = item[field]
                                break
                        elif hasattr(item, "__getitem__"):
                            if field in item and item[field]:
                                text = item[field]
                                break
                    except (KeyError, TypeError):
                        continue

                if not text and self.has_pdf_support():
                    logger.info(
                        f"Novel {idx + 1}: No text field found, attempting PDF extraction..."
                    )
                    for pdf_field in ["pdf", "file", "document", "content", "data"]:
                        try:
                            pdf_data = None
                            if isinstance(item, dict):
                                if pdf_field in item and item[pdf_field]:
                                    pdf_data = item[pdf_field]
                            elif hasattr(item, "__getitem__"):
                                if pdf_field in item and item[pdf_field]:
                                    pdf_data = item[pdf_field]

                            if pdf_data:
                                logger.info(
                                    f"Novel {idx + 1}: Found PDF data in field "
                                    f"'{pdf_field}' (type: {type(pdf_data).__name__})"
                                )
                                text = self.extract_pdf_text(pdf_data, max_pages=self.max_pdf_pages)
                                if text:
                                    logger.info(
                                        f"Novel {idx + 1}: Successfully extracted "
                                        f"{len(text)} chars from PDF field '{pdf_field}'"
                                    )
                                    break
                                else:
                                    logger.warning(
                                        f"Novel {idx + 1}: PDF field '{pdf_field}' "
                                        f"extraction returned no text"
                                    )
                        except Exception as e:
                            logger.warning(
                                f"Novel {idx + 1}: PDF extraction from field "
                                f"'{pdf_field}' failed: {type(e).__name__}: {e}"
                            )

                if not text:
                    logger.warning(
                        f"Novel {idx + 1}: No text content found. Available fields: {item_keys}"
                    )
                    pdf_status = (
                        "Enabled"
                        if self.has_pdf_support()
                        else "Not available (install pdfplumber)"
                    )
                    text = f"""[Novel Content Extraction Failed]

This novel (#{idx + 1}) is part of the GOAT-AI/generated-novels dataset.
The original content is stored in PDF format but could not be extracted.

Dataset fields available: {', '.join(item_keys) if item_keys else 'Unknown'}
PDF extraction support: {pdf_status}

Note: The GOAT-AI/generated-novels repository does not have a README to guide extraction.
Complete conversion from PDF to text may be required for this dataset.

This entry serves as a placeholder for retrieval system testing."""

                title = f"Generated Novel #{idx + 1}"
                try:
                    if isinstance(item, dict):
                        title = item.get("title", item.get("name", f"Generated Novel #{idx + 1}"))
                    elif hasattr(item, "get"):
                        title = item.get("title", item.get("name", f"Generated Novel #{idx + 1}"))
                    elif hasattr(item, "__getitem__"):
                        title = (
                            item.get("title", f"Generated Novel #{idx + 1}")
                            if "title" in item
                            else (
                                item.get("name", f"Generated Novel #{idx + 1}")
                                if "name" in item
                                else f"Generated Novel #{idx + 1}"
                            )
                        )
                except Exception:
                    title = f"Generated Novel #{idx + 1}"

                chunks = self.chunk_text(text, chunk_size)

                for chunk_idx, chunk in enumerate(chunks):
                    doc = {
                        "content_id": f"novel/{idx}-chunk{chunk_idx}",
                        "content": self._create_content(title, chunk, chunk_idx, len(chunks)),
                        "metadata": {
                            "pack": "warbler-pack-novels",
                            "source_dataset": dataset_name,
                            "novel_title": title[:100],
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks),
                            "realm_type": "narrative",
                            "realm_label": "generated_fiction",
                            "lifecycle_stage": "emergence",
                            "activity_level": 0.6,
                            "dialogue_type": "narrative_content",
                            "license": "MIT",
                            "content_available": bool(text and len(text) > 100),
                        },
                    }
                    warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} novel chunks from {len(items)} novels")
        return warbler_docs

    @staticmethod
    def _create_content(title: str, text_chunk: str, chunk_idx: int, total_chunks: int) -> str:
        """Create content string for novel chunk."""
        return f"""Novel: {title}
Part: {chunk_idx + 1} of {total_chunks}

{text_chunk}

This represents a narrative segment from a generated novel."""

    @staticmethod
    def _create_placeholders(count: int) -> List[Dict[str, Any]]:
        """Create placeholder novel entries when dataset is unavailable."""
        docs = []
        for i in range(count):
            doc = {
                "content_id": f"novel/{i}-chunk0",
                "content": f"""Novel: Generated Novel #{i + 1}
Part: 1 of 1

[Content Unavailable - Dataset Loading Failed]

This is a placeholder entry for the GOAT-AI/generated-novels dataset.
The actual novel content could not be loaded from the source.

This entry can be used for retrieval system structure testing.""",
                "metadata": {
                    "pack": "warbler-pack-novels",
                    "source_dataset": "GOAT-AI/generated-novels",
                    "novel_title": f"Generated Novel #{i + 1}",
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "realm_type": "narrative",
                    "realm_label": "generated_fiction",
                    "lifecycle_stage": "emergence",
                    "activity_level": 0.6,
                    "dialogue_type": "narrative_content",
                    "license": "MIT",
                    "content_available": False,
                },
            }
            docs.append(doc)
        return docs
