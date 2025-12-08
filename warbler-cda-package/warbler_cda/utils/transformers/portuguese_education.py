"""Portuguese language education dataset transformer."""

import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer, PDF_AVAILABLE


logger = logging.getLogger(__name__)


class PortugueseEducationTransformer(BaseWarblerTransformer):
    """Transform Solshine/Portuguese_Language_Education_Texts dataset."""

    def transform(
        self, dataset_name: str = "Solshine/Portuguese_Language_Education_Texts"
    ) -> List[Dict[str, Any]]:
        """
        Transform Solshine/Portuguese_Language_Education_Texts dataset.

        Format: Portuguese language educational content (multilingual)
        """
        logger.info(f"Loading {dataset_name}...")
        try:
            dataset = load_dataset(dataset_name, split="train")
            items = list(dataset)
            logger.info(f"Loaded {len(items)} items from 'train' split")
        except Exception as e:
            logger.warning(f"Failed to load with split='train': {e}")
            try:
                dataset = load_dataset(dataset_name)
                items = []
                if hasattr(dataset, "__getitem__") and "train" in dataset:
                    items = list(dataset["train"])
                    logger.info(f"Loaded {len(items)} items from dataset['train']")
                else:
                    items = self.extract_dataset_items(dataset)
                    logger.info(f"Extracted {len(items)} items from dataset")
            except Exception as e2:
                logger.warning(f"Failed to load {dataset_name}: {e2}")
                return []

        warbler_docs = []

        for idx, item in enumerate(items):
            if isinstance(item, str):
                logger.warning(f"Portuguese doc {idx + 1}: Item is a string, skipping")
                continue

            if isinstance(item, dict) or hasattr(item, "__getitem__"):
                item_keys = []
                try:
                    if isinstance(item, dict):
                        item_keys = list(item.keys())
                    elif hasattr(item, "keys") and callable(item.keys):
                        item_keys = list(item.keys())
                except Exception:
                    item_keys = []

                content = None
                for field in ["content", "text", "body", "document", "passage"]:
                    try:
                        if isinstance(item, dict):
                            if field in item and item[field]:
                                content = item[field]
                                break
                        elif hasattr(item, "__getitem__"):
                            if field in item and item[field]:
                                content = item[field]
                                break
                    except (KeyError, TypeError):
                        continue

                if not content and PDF_AVAILABLE:
                    for pdf_field in ["pdf", "file", "document"]:
                        try:
                            pdf_data = None
                            if isinstance(item, dict):
                                if pdf_field in item and item[pdf_field]:
                                    pdf_data = item[pdf_field]
                            elif hasattr(item, "__getitem__"):
                                if pdf_field in item and item[pdf_field]:
                                    pdf_data = item[pdf_field]

                            if pdf_data:
                                if isinstance(pdf_data, dict) and "bytes" in pdf_data:
                                    pdf_bytes = pdf_data["bytes"]
                                    logger.info(
                                        f"Portuguese doc {idx + 1}: Found PDF bytes "
                                        f"({len(pdf_bytes)} bytes), extracting..."
                                    )
                                    content = self.extract_pdf_text(
                                        pdf_bytes, max_pages=self.max_pdf_pages
                                    )
                                elif isinstance(pdf_data, bytes):
                                    logger.info(
                                        f"Portuguese doc {idx + 1}: Found PDF bytes "
                                        f"({len(pdf_data)} bytes), extracting..."
                                    )
                                    content = self.extract_pdf_text(
                                        pdf_data, max_pages=self.max_pdf_pages
                                    )
                                else:
                                    logger.info(
                                        f"Portuguese doc {idx + 1}: Found PDF data "
                                        f"(type: {type(pdf_data)}), attempting extraction..."
                                    )
                                    content = self.extract_pdf_text(
                                        pdf_data, max_pages=self.max_pdf_pages
                                    )

                                if content:
                                    logger.info(
                                        f"Portuguese doc {idx + 1}: Successfully extracted "
                                        f"{len(content)} chars from PDF"
                                    )
                                    break
                                else:
                                    logger.warning(
                                        f"Portuguese doc {idx + 1}: PDF extraction returned no text"
                                    )
                        except Exception as e:
                            logger.warning(
                                f"Portuguese doc {idx + 1}: PDF extraction error: "
                                f"{type(e).__name__}: {e}"
                            )

                if not content:
                    logger.warning(
                        f"Portuguese doc {idx + 1}: No content found. Available fields: {item_keys}"
                    )
                    content = f"""[Conteúdo Indisponível]

Este documento (#{idx + 1}) faz parte do dataset Solshine/Portuguese_Language_Education_Texts.
O conteúdo original pode requerer extração especial.

Campos disponíveis: {', '.join(item_keys) if item_keys else 'Unknown'}

Esta entrada serve como placeholder para testes do sistema de recuperação."""

                title = ""
                try:
                    if isinstance(item, dict):
                        title = item.get("title", item.get("name", ""))
                    elif hasattr(item, "get"):
                        title = item.get("title", item.get("name", ""))
                    elif hasattr(item, "__getitem__"):
                        title = (
                            item["title"]
                            if "title" in item
                            else (item["name"] if "name" in item else "")
                        )
                except Exception:
                    title = ""

                content_id = f"portuguese/{idx}"

                item_with_content = {}
                try:
                    if isinstance(item, dict):
                        item_with_content = item.copy()
                    else:
                        item_with_content = {}
                        for key in item_keys:
                            try:
                                item_with_content[key] = item[key]
                            except (KeyError, TypeError):
                                pass
                except Exception as e:
                    logger.warning(f"Portuguese doc {idx + 1}: Could not convert item to dict: {e}")
                    item_with_content = {}

                item_with_content["content"] = content

                language = "pt"
                try:
                    if isinstance(item, dict):
                        language = item.get("language", "pt")
                    elif hasattr(item, "get"):
                        language = item.get("language", "pt")
                    elif hasattr(item, "__getitem__") and "language" in item:
                        language = item["language"]
                except Exception:
                    language = "pt"

                doc = {
                    "content_id": content_id,
                    "content": self._create_content(item_with_content),
                    "metadata": {
                        "pack": "warbler-pack-portuguese-edu",
                        "source_dataset": dataset_name,
                        "language": language,
                        "title": title[:150] if title else f"Documento {idx + 1}",
                        "document_index": idx,
                        "realm_type": "educational",
                        "realm_label": "portuguese_language",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.6,
                        "dialogue_type": "educational_content",
                        "license": "MIT",
                        "content_available": bool(content and len(content) > 50),
                    },
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} Portuguese education entries")
        return warbler_docs

    @staticmethod
    def _create_content(item: Dict[str, Any]) -> str:
        """Create content string for Portuguese education text."""
        return f"""Título: {item.get('title', 'Sem título')}
Língua: {item.get('language', 'pt')}

Conteúdo:
{item.get('content', 'Conteúdo não disponível')}

Este documento contribui para o ensino da língua portuguesa."""
