"""
Base classes and shared utilities for Warbler dataset transformers.
"""

import io
import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod



try:
    import pdfplumber

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


logger = logging.getLogger(__name__)


class BaseWarblerTransformer(ABC):
    """Base class for all dataset transformers."""

    def __init__(
        self, tokenizer_name: str = "microsoft/DialoGPT-medium", max_pdf_pages: Optional[int] = None
    ):
        """Initialize the transformer."""
        self.max_pdf_pages = max_pdf_pages

    @abstractmethod
    def transform(self, dataset_name: str = None) -> List[Dict[str, Any]]:
        """Transform dataset into Warbler documents."""
        pass

    def has_pdf_support(self) -> bool:
        """Check if PDF extraction is available."""
        return PDF_AVAILABLE

    def extract_pdf_text(self, pdf_data: Any, max_pages: Optional[int] = None) -> Optional[str]:
        """
        Extract text from PDF data (bytes, file path, PDF object, or file-like object).

        Args:
            pdf_data: PDF data in various formats (bytes, file path, PDF object, file-like)
            max_pages: Maximum number of pages to extract (default: None for unlimited)

        Returns:
            Extracted text or None if extraction fails
        """
        if not PDF_AVAILABLE:
            logger.debug("PDF extraction unavailable - pdfplumber not installed")
            return None

        try:
            if hasattr(pdf_data, "pages") and hasattr(pdf_data, "metadata"):
                logger.info("PDF data is already a pdfplumber.PDF object, extracting text...")
                text_parts = []
                total_pages = len(pdf_data.pages)

                if max_pages is None:
                    logger.info(f"PDF has {total_pages} pages, extracting all pages")
                else:
                    logger.info(f"PDF has {total_pages} pages, extracting up to {max_pages} pages")

                try:
                    for page_num, page in enumerate(pdf_data.pages, 1):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text_parts.append(page_text)
                                logger.debug(
                                    f"Extracted {len(page_text)} chars from page {page_num}"
                                )
                            else:
                                logger.debug(f"Page {page_num} has no extractable text")
                        except Exception as page_error:
                            logger.warning(f"Error extracting page {page_num}: {page_error}")
                            continue

                        if max_pages is not None and page_num >= max_pages:
                            logger.info(
                                f"Truncated PDF extraction at {page_num} pages (max: {max_pages})"
                            )
                            break

                    extracted_text = "\n\n".join(text_parts) if text_parts else None
                    if extracted_text:
                        logger.info(
                            f"Successfully extracted {len(extracted_text)} total "
                            f"characters from {len(text_parts)} pages"
                        )
                    else:
                        logger.warning("No text could be extracted from PDF object")
                    return extracted_text
                except Exception as e:
                    logger.warning(f"Error extracting from PDF object: {type(e).__name__}: {e}")
                    return None

            if isinstance(pdf_data, dict) and "bytes" in pdf_data:
                logger.info(
                    f"PDF data is dict with 'bytes' key, extracting {len(pdf_data['bytes'])} bytes"
                )
                return self.extract_pdf_text(pdf_data["bytes"], max_pages)

            pdf_file = None
            if isinstance(pdf_data, bytes):
                logger.info(f"PDF data is bytes ({len(pdf_data)} bytes), creating BytesIO")
                pdf_file = io.BytesIO(pdf_data)
            elif isinstance(pdf_data, str) and os.path.exists(pdf_data):
                logger.info(f"PDF data is file path: {pdf_data}")
                pdf_file = pdf_data
            elif hasattr(pdf_data, "read"):
                logger.info(f"PDF data is file-like object: {type(pdf_data)}")
                pdf_file = pdf_data
            else:
                logger.warning(f"Unknown PDF data type: {type(pdf_data)}, cannot extract")
                return None

            text_parts = []
            with pdfplumber.open(pdf_file) as pdf:
                total_pages = len(pdf.pages)

                if max_pages is None:
                    logger.info(f"Opened PDF with {total_pages} pages, extracting all pages")
                else:
                    logger.info(
                        f"Opened PDF with {total_pages} pages, extracting up to {max_pages} pages"
                    )

                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                            logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")
                        else:
                            logger.debug(f"Page {page_num} has no extractable text")
                    except Exception as page_error:
                        logger.warning(f"Error extracting page {page_num}: {page_error}")
                        continue

                    if max_pages is not None and page_num >= max_pages:
                        logger.info(
                            f"Truncated PDF extraction at {page_num} pages (max: {max_pages})"
                        )
                        break

            extracted_text = "\n\n".join(text_parts) if text_parts else None
            if extracted_text:
                logger.info(
                    f"Successfully extracted {len(extracted_text)} total "
                    f"characters from {len(text_parts)} pages"
                )
            else:
                logger.warning("No text could be extracted from PDF")
            return extracted_text

        except Exception as e:
            logger.error(f"PDF extraction error: {type(e).__name__}: {e}")
            return None

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks."""
        if not text:
            return []
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    def extract_dataset_items(self, dataset: Any) -> List[Dict[str, Any]]:
        """
        Safely extract items from a dataset, handling both real and mocked datasets.

        Tries direct iteration first, then checks for split keys.
        """
        if isinstance(dataset, list):
            return dataset

        try:
            items = list(dataset)
            if items and not all(isinstance(item, str) for item in items):
                return items
        except (TypeError, StopIteration):
            pass

        try:
            if hasattr(dataset, "keys") and callable(getattr(dataset, "keys", None)):
                keys = list(dataset.keys())
                if keys:
                    first_split = keys[0]
                    split_data = dataset[first_split]

                    if isinstance(split_data, (list, tuple)):
                        return split_data
                    else:
                        try:
                            items = list(split_data)
                            return items
                        except (TypeError, StopIteration):
                            pass
        except (TypeError, AttributeError, KeyError):
            pass

        return []


class WarblerPackBuilder:
    """Build and save Warbler packs."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the composite transformer."""
        if output_dir is None:
            output_dir = Path(__file__).resolve().parent.parent / "results" / "hf_ingest"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def create_pack(
        self, docs: List[Dict[str, Any]], pack_name: str, max_docs_per_chunk: int = 50000
    ) -> str:
        """Create a Warbler pack from documents."""
        if not docs:
            raise ValueError("Cannot create pack with empty documents list")

        pack_dir = self.output_dir / pack_name
        pack_dir.mkdir(exist_ok=True, parents=True)

        total_docs = len(docs)

        if max_docs_per_chunk == float("inf") or total_docs <= max_docs_per_chunk:
            pack_file = pack_dir / f"{pack_name}.jsonl"

            with open(pack_file, "w", encoding="utf-8") as f:
                for doc in docs:
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")

            metadata = {
                "name": pack_name,
                "version": "1.0.0",
                "description": "Warbler pack generated from HuggingFace datasets",
                "created_at": datetime.now().isoformat(),
                "document_count": total_docs,
                "source": "HuggingFace",
                "content_types": list(set(doc["metadata"]["dialogue_type"] for doc in docs)),
                "chunked": False,
            }

            logger.info(
                f"✓ Created Warbler pack: {pack_name} with {total_docs} documents (single file)"
            )
        else:
            chunk_count = (total_docs + max_docs_per_chunk - 1) // max_docs_per_chunk

            logger.info(
                f"Creating chunked pack: {pack_name} with {total_docs} "
                f"documents across {chunk_count} chunks"
            )

            for chunk_idx in range(chunk_count):
                start_idx = chunk_idx * max_docs_per_chunk
                end_idx = min(start_idx + max_docs_per_chunk, total_docs)
                chunk_docs = docs[start_idx:end_idx]

                chunk_file = pack_dir / f"{pack_name}-chunk-{chunk_idx + 1:03d}.jsonl"

                with open(chunk_file, "w", encoding="utf-8") as f:
                    for doc in chunk_docs:
                        f.write(json.dumps(doc, ensure_ascii=False) + "\n")

                logger.info(
                    f"  ✓ Wrote chunk {chunk_idx + 1}/{chunk_count}: "
                    f"{len(chunk_docs)} documents to {chunk_file.name}"
                )

            metadata = {
                "name": pack_name,
                "version": "1.0.0",
                "description": "Warbler pack generated from HuggingFace datasets (chunked)",
                "created_at": datetime.now().isoformat(),
                "document_count": total_docs,
                "source": "HuggingFace",
                "content_types": list(set(doc["metadata"]["dialogue_type"] for doc in docs)),
                "chunked": True,
                "chunk_count": chunk_count,
                "docs_per_chunk": max_docs_per_chunk,
                "chunk_pattern": f"{pack_name}-chunk-*.jsonl",
            }

            logger.info(
                f"✓ Created chunked Warbler pack: {pack_name} with "
                f"{total_docs} documents across {chunk_count} chunks"
            )

        metadata_file = pack_dir / "package.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            f.write("\n")

        return str(pack_dir)

    def save_report(self, results: Dict[str, Any]) -> str:
        """Save detailed ingestion report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "total_documents": sum(
                result.get("documents", 0) if isinstance(result, dict) else len(result)
                for result in results.values()
            ),
            "packs_created": len(results),
        }

        report_file = (
            self.output_dir / f"ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")

        logger.info(f"✓ Saved ingestion report: {report_file}")
        return str(report_file)
