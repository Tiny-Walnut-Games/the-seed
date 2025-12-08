#!/usr/bin/env python3
"""
HuggingFace Warbler Pack Ingestion Pipeline

Imports HF datasets and transforms them into Warbler-compatible packs
for NPC intelligence training via the magma layer self-training system.
"""

import json
import os
import io
import click
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

try:
    from datasets import load_dataset
    from transformers import AutoTokenizer
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("pip install datasets transformers")
    exit(1)

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Warbler pack locations
BASE_DIR = Path(__file__).resolve().parent
PACKS_DIR = BASE_DIR.parents[1] / 'packs'
OUTPUT_DIR = BASE_DIR / 'results' / 'hf_ingest'

class HFWarblerIngestor:
    """Transform HF datasets into Warbler packs"""

    def __init__(self, tokenizer_name: str = "microsoft/DialoGPT-medium"):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def has_pdf_support(self) -> bool:
        """Check if PDF extraction is available"""
        return PDF_AVAILABLE

    def extract_pdf_text(self, pdf_bytes: bytes, max_chars: int = 5000) -> Optional[str]:
        """Extract text from PDF bytes with fallback"""
        if not PDF_AVAILABLE:
            return None
        
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            text_parts = []
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                        if sum(len(t) for t in text_parts) > max_chars:
                            break
            
            return " ".join(text_parts)[:max_chars] if text_parts else None
        except Exception as e:
            logger.debug(f"PDF extraction error: {e}")
            return None

    def create_novel_placeholders(self, count: int = 20) -> List[Dict[str, Any]]:
        """Create placeholder documents for unavailable novels"""
        docs = []
        for i in range(count):
            doc = {
                "content_id": f"novel/placeholder-{i}",
                "content": f"""[Novel Content Placeholder]

This is a placeholder for Novel #{i + 1} from GOAT-AI/generated-novels dataset.
The original content is stored in PDF format and requires pdfplumber for extraction.

To enable full novel ingestion, install: pip install pdfplumber

Dataset: GOAT-AI/generated-novels
License: MIT
Status: Available for retrieval testing""",
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
                    "note": "placeholder_entry"
                }
            }
            docs.append(doc)
        return docs

    def _extract_dataset_items(self, dataset: Any) -> List[Dict[str, Any]]:
        """
        Safely extract items from a dataset, handling both real and mocked datasets.
        Tries direct iteration first, then checks for split keys.
        """
        if isinstance(dataset, list):
            return dataset
        
        # Try direct iteration first (works for single split datasets)
        try:
            items = list(dataset)
            # Filter out string items (split names) - we want actual data rows
            if items and not all(isinstance(item, str) for item in items):
                return items
        except (TypeError, StopIteration):
            pass
        
        # If dataset has splits (like DatasetDict), access the actual data
        try:
            if hasattr(dataset, 'keys') and callable(getattr(dataset, 'keys', None)):
                keys = list(dataset.keys())
                if keys:
                    # Get the first split's data (usually 'train')
                    first_split = keys[0]
                    split_data = dataset[first_split]
                    
                    # Convert split data to list
                    if isinstance(split_data, (list, tuple)):
                        return split_data
                    else:
                        # Try to iterate the split data
                        try:
                            items = list(split_data)
                            return items
                        except (TypeError, StopIteration):
                            pass
        except (TypeError, AttributeError, KeyError):
            pass
        
        return []

    def transform_npc_dialogue(self, dataset_name: str = "amaydle/npc-dialogue") -> List[Dict[str, Any]]:
        """
        Transform amaydle/npc-dialogue dataset
        Format: Name, Biography, Query, Response, Emotion
        """
        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []

        for split in dataset.keys():
            for item in dataset[split]:
                # Create Warbler-compatible document
                doc = {
                    "content_id": f"npc-dialogue/{item['Name'].lower().replace(' ', '-')}",
                    "content": self._create_npc_content(item),
                    "metadata": {
                        "pack": "warbler-pack-npc-dialogue",
                        "source_dataset": dataset_name,
                        "character_name": item['Name'],
                        "character_biography": item['Biography'][:200] + "..." if len(item['Biography']) > 200 else item['Biography'],
                        "emotion": item['Emotion'],
                        "realm_type": "character",
                        "realm_label": "npc_dialogue",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.8,
                        "dialogue_type": "character_interaction"
                    }
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} NPC dialogue entries")
        return warbler_docs

    def transform_multi_character(self, dataset_name: str = "agentlans/multi-character-dialogue") -> List[Dict[str, Any]]:
        """
        Transform agentlans/multi-character-dialogue dataset
        Format: setting, characters, conversation, setting_after_interaction
        """
        logger.info(f"Loading {dataset_name}...")
        try:
            dataset = load_dataset(dataset_name)
        except Exception as e:
            logger.warning(f"Failed to load {dataset_name}: {e}")
            return []

        warbler_docs = []
        
        # Wrap entire iteration in comprehensive error handling
        try:
            # Safely get the train split with bounds checking
            if 'train' not in dataset:
                logger.warning(f"Multi-char: No 'train' split found in dataset")
                return []
            
            train_data = dataset['train']
            total_items = len(train_data) if hasattr(train_data, '__len__') else 0
            logger.info(f"Processing {total_items} multi-character dialogue items...")
            
            for idx, item in enumerate(train_data):
                # Add periodic progress logging to detect where crashes occur
                if idx > 0 and idx % 1000 == 0:
                    logger.info(f"Processed {idx}/{total_items} items, created {len(warbler_docs)} documents")
                
                try:
                    # Validate item is not None and is dict-like
                    if item is None:
                        logger.warning(f"Multi-char {idx + 1}: Item is None, skipping")
                        continue
                    
                    if not isinstance(item, dict):
                        logger.warning(f"Multi-char {idx + 1}: Item is not a dict (type: {type(item)}), skipping")
                        continue
                    
                    # Safely get required fields with defaults and type validation
                    setting = item.get('setting', '')
                    characters = item.get('characters', [])
                    conversation = item.get('conversation', [])
                    
                    # Validate and sanitize field types
                    if not isinstance(setting, str):
                        setting = str(setting) if setting is not None else ''
                    if not isinstance(characters, list):
                        characters = [] if characters is None else [characters]
                    if not isinstance(conversation, list):
                        conversation = [] if conversation is None else [conversation]
                    
                    # Skip if essential data is missing
                    if not setting and not conversation:
                        logger.warning(f"Multi-char {idx + 1}: Missing essential data, skipping")
                        continue
                    
                    # Validate conversation structure before processing
                    if conversation and not all(isinstance(msg, (dict, str)) for msg in conversation[:10]):
                        logger.warning(f"Multi-char {idx + 1}: Invalid conversation structure, skipping")
                        continue
                    
                    # Create Warbler-compatible document with additional safety
                    try:
                        content = self._create_multi_char_content(item)
                    except Exception as content_error:
                        logger.warning(f"Multi-char {idx + 1}: Error creating content: {content_error}, using fallback")
                        content = f"[Multi-character dialogue content unavailable]\nSetting: {setting[:100]}"
                    
                    doc = {
                        "content_id": f"multi-char/{hash(setting) % 10000 if setting else idx}",
                        "content": content,
                        "metadata": {
                            "pack": "warbler-pack-multi-character",
                            "source_dataset": dataset_name,
                            "setting": setting[:150] + "..." if len(setting) > 150 else setting,
                            "character_count": len(characters) if isinstance(characters, list) else 0,
                            "conversation_length": len(conversation) if isinstance(conversation, list) else 0,
                            "realm_type": "narrative",
                            "realm_label": "multi_character_dialogue",
                            "lifecycle_stage": "emergence",
                            "activity_level": 0.7,
                            "dialogue_type": "multi_character_interaction"
                        }
                    }
                    warbler_docs.append(doc)
                    
                except MemoryError as mem_err:
                    logger.error(f"Multi-char {idx + 1}: Memory error - {mem_err}. Stopping processing to prevent crash.")
                    break
                except RecursionError as rec_err:
                    logger.error(f"Multi-char {idx + 1}: Recursion error - {rec_err}. Skipping item.")
                    continue
                except (KeyboardInterrupt, SystemExit):
                    logger.warning(f"Multi-char: Processing interrupted at item {idx + 1}")
                    raise
                except Exception as e:
                    logger.warning(f"Multi-char {idx + 1}: Error processing item: {type(e).__name__}: {e}")
                    continue
                    
        except (MemoryError, RecursionError) as critical_error:
            logger.error(f"Multi-char: Critical error during iteration: {type(critical_error).__name__}: {critical_error}")
            logger.info(f"Returning {len(warbler_docs)} documents processed before error")
        except (KeyboardInterrupt, SystemExit):
            logger.warning(f"Multi-char: Processing interrupted, returning {len(warbler_docs)} documents")
            raise
        except Exception as outer_error:
            logger.error(f"Multi-char: Unexpected error during dataset iteration: {type(outer_error).__name__}: {outer_error}")
            logger.info(f"Returning {len(warbler_docs)} documents processed before error")

        logger.info(f"✓ Transformed {len(warbler_docs)} multi-character entries")
        return warbler_docs

    def transform_system_chat(self, dataset_name: str = "abacusai/SystemChat") -> List[Dict[str, Any]]:
        """
        Transform abacusai/SystemChat dataset
        Format: conversations with system prompts
        """
        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []

        for item in dataset['train']:
            conversations = item['conversations']

            # Extract system prompt and first exchange
            system_msg = next((msg['value'] for msg in conversations if msg['from'] == 'system'), '')
            human_msg = next((msg['value'] for msg in conversations if msg['from'] == 'human'), '')
            ai_msg = next((msg['value'] for msg in conversations if msg['from'] == 'gpt'), '')

            if system_msg and human_msg and ai_msg:
                doc = {
                    "content_id": f"system-chat/{hash(system_msg) % 10000}",
                    "content": self._create_system_chat_content(system_msg, human_msg, ai_msg),
                    "metadata": {
                        "pack": "warbler-pack-system-chat",
                        "source_dataset": dataset_name,
                        "system_role": system_msg[:100] + "..." if len(system_msg) > 100 else system_msg,
                        "conversation_length": len(conversations),
                        "realm_type": "instructional",
                        "realm_label": "system_chat",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.6,
                        "dialogue_type": "instruction_following",
                        "license": "unknown"
                    }
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} system chat entries")
        return warbler_docs

    def transform_arxiv(self, dataset_name: str = "nick007x/arxiv-papers", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Transform nick007x/arxiv-papers dataset
        Format: arXiv academic papers with metadata
        """
        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []
        count = 0

        for split in dataset.keys():
            for item in dataset[split]:
                if limit and count >= limit:
                    break

                doc = {
                    "content_id": f"arxiv/{item.get('arxiv_id', hash(item.get('title', '')) % 10000)}",
                    "content": self._create_arxiv_content(item),
                    "metadata": {
                        "pack": "warbler-pack-arxiv",
                        "source_dataset": dataset_name,
                        "arxiv_id": item.get('arxiv_id', ''),
                        "title": item.get('title', '')[:150],
                        "authors": item.get('authors', '')[:200],
                        "year": item.get('year', 2023),
                        "categories": item.get('categories', ''),
                        "realm_type": "scholarly",
                        "realm_label": "arxiv",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.7,
                        "dialogue_type": "scholarly_discussion",
                        "license": "MIT"
                    }
                }
                warbler_docs.append(doc)
                count += 1

        logger.info(f"✓ Transformed {len(warbler_docs)} arXiv papers")
        return warbler_docs

    def transform_prompt_report(self, dataset_name: str = "PromptSystematicReview/ThePromptReport") -> List[Dict[str, Any]]:
        """
        Transform PromptSystematicReview/ThePromptReport dataset
        Format: Prompt engineering documentation and analysis
        """
        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []

        if isinstance(dataset, list):
            items = dataset
        elif hasattr(dataset, 'keys'):
            items = []
            for split in dataset.keys():
                items.extend(dataset[split])
        else:
            items = dataset

        for item in items:
            if isinstance(item, dict):
                doc = {
                    "content_id": f"prompt-report/{item.get('id', hash(item.get('title', '')) % 10000)}",
                    "content": self._create_prompt_report_content(item),
                    "metadata": {
                        "pack": "warbler-pack-prompt-report",
                        "source_dataset": dataset_name,
                        "title": item.get('title', '')[:150],
                        "category": item.get('category', 'prompting'),
                        "realm_type": "methodological",
                        "realm_label": "prompt_engineering",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.8,
                        "dialogue_type": "technical_discussion",
                        "license": "MIT"
                    }
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} prompt report entries")
        return warbler_docs

    def transform_novels(self, dataset_name: str = "GOAT-AI/generated-novels") -> List[Dict[str, Any]]:
        """
        Transform GOAT-AI/generated-novels dataset
        Format: Full-length generated novels (PDF-based, treated as narrative metadata)
        """
        logger.info(f"Loading {dataset_name}...")
        try:
            dataset = load_dataset(dataset_name)
        except Exception as e:
            logger.warning(f"Failed to load {dataset_name}: {e}")
            logger.info("Creating placeholder entries for novel dataset")
            return self.create_novel_placeholders(20)

        warbler_docs = []
        chunk_size = 1000

        # Try to access dataset directly first, then fall back to extraction
        items = []
        try:
            # Try accessing 'train' split directly
            if hasattr(dataset, '__getitem__') and 'train' in dataset:
                items = list(dataset['train'])
                logger.info(f"Loaded {len(items)} items from 'train' split")
            else:
                items = self._extract_dataset_items(dataset)
                logger.info(f"Extracted {len(items)} items from dataset")
        except Exception as e:
            logger.warning(f"Error accessing dataset: {e}")
            items = self._extract_dataset_items(dataset)

        for idx, item in enumerate(items):
            # Skip non-dict items (like strings)
            if isinstance(item, str):
                logger.warning(f"Novel {idx + 1}: Item is a string, skipping")
                continue
            
            if isinstance(item, dict) or hasattr(item, '__getitem__'):
                text = None
                # Safely get item keys for logging
                item_keys = []
                try:
                    if isinstance(item, dict):
                        item_keys = list(item.keys())
                    elif hasattr(item, 'keys') and callable(item.keys):
                        item_keys = list(item.keys())
                except Exception:
                    item_keys = []
                
                # Try to extract text from various fields
                for field in ['text', 'story', 'content', 'novel', 'body', 'full_text']:
                    try:
                        if isinstance(item, dict):
                            if field in item and item[field]:
                                text = item[field]
                                break
                        elif hasattr(item, '__getitem__'):
                            if field in item and item[field]:
                                text = item[field]
                                break
                    except (KeyError, TypeError):
                        continue
                
                if not text and self.has_pdf_support():
                    logger.info(f"Novel {idx + 1}: No text field found, attempting PDF extraction...")
                    for pdf_field in ['pdf', 'file', 'document', 'content', 'data']:
                        try:
                            pdf_data = None
                            if isinstance(item, dict):
                                if pdf_field in item and item[pdf_field]:
                                    pdf_data = item[pdf_field]
                            elif hasattr(item, '__getitem__'):
                                if pdf_field in item and item[pdf_field]:
                                    pdf_data = item[pdf_field]
                            
                            if pdf_data:
                                logger.info(f"Novel {idx + 1}: Found PDF data in field '{pdf_field}' (type: {type(pdf_data).__name__})")
                                text = self._extract_pdf_text(pdf_data)
                                if text:
                                    logger.info(f"Novel {idx + 1}: Successfully extracted {len(text)} chars from PDF field '{pdf_field}'")
                                    break
                                else:
                                    logger.warning(f"Novel {idx + 1}: PDF field '{pdf_field}' extraction returned no text")
                        except Exception as e:
                            logger.warning(f"Novel {idx + 1}: PDF extraction from field '{pdf_field}' failed: {type(e).__name__}: {e}")
                
                if not text:
                    logger.warning(f"Novel {idx + 1}: No text content found. Available fields: {item_keys}")
                    pdf_status = 'Enabled' if self.has_pdf_support() else 'Not available (install pdfplumber)'
                    text = f"""[Novel Content Extraction Failed]

This novel (#{idx + 1}) is part of the GOAT-AI/generated-novels dataset.
The original content is stored in PDF format but could not be extracted.

Dataset fields available: {', '.join(item_keys) if item_keys else 'Unknown'}
PDF extraction support: {pdf_status}

Note: The GOAT-AI/generated-novels repository does not have a README to guide extraction.
Complete conversion from PDF to text may be required for this dataset.

This entry serves as a placeholder for retrieval system testing."""
                
                # Safely get title
                title = f'Generated Novel #{idx + 1}'
                try:
                    if isinstance(item, dict):
                        title = item.get('title', item.get('name', f'Generated Novel #{idx + 1}'))
                    elif hasattr(item, 'get'):
                        title = item.get('title', item.get('name', f'Generated Novel #{idx + 1}'))
                    elif hasattr(item, '__getitem__'):
                        title = item.get('title', f'Generated Novel #{idx + 1}') if 'title' in item else (item.get('name', f'Generated Novel #{idx + 1}') if 'name' in item else f'Generated Novel #{idx + 1}')
                except Exception:
                    title = f'Generated Novel #{idx + 1}'

                chunks = self._chunk_text(text, chunk_size)

                for chunk_idx, chunk in enumerate(chunks):
                    doc = {
                        "content_id": f"novel/{idx}-chunk{chunk_idx}",
                        "content": self._create_novel_content(title, chunk, chunk_idx, len(chunks)),
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
                            "content_available": bool(text and len(text) > 100)
                        }
                    }
                    warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} novel chunks from {len(items)} novels")
        return warbler_docs

    def _extract_pdf_text(self, pdf_data: Any, max_pages: int = 100) -> Optional[str]:
        """
        Extract text from PDF data (bytes, file path, PDF object, or file-like object)
        
        Args:
            pdf_data: PDF data in various formats (bytes, file path, PDF object, file-like)
            max_pages: Maximum number of pages to extract (default: 100)
        
        Returns:
            Extracted text or None if extraction fails
        """
        if not PDF_AVAILABLE:
            logger.debug("PDF extraction unavailable - pdfplumber not installed")
            return None
        
        try:
            # Handle pdfplumber.PDF object directly (HuggingFace datasets return this)
            if hasattr(pdf_data, 'pages') and hasattr(pdf_data, 'metadata'):
                logger.info("PDF data is already a pdfplumber.PDF object, extracting text...")
                text_parts = []
                total_pages = len(pdf_data.pages)
                logger.info(f"PDF has {total_pages} pages, extracting up to {max_pages} pages")
                
                try:
                    for page_num, page in enumerate(pdf_data.pages, 1):
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
                        
                        # Limit to max_pages to avoid memory issues
                        if page_num >= max_pages:
                            logger.info(f"Truncated PDF extraction at {page_num} pages (max: {max_pages})")
                            break
                    
                    extracted_text = "\n\n".join(text_parts) if text_parts else None
                    if extracted_text:
                        logger.info(f"Successfully extracted {len(extracted_text)} total characters from {len(text_parts)} pages")
                    else:
                        logger.warning("No text could be extracted from PDF object")
                    return extracted_text
                except Exception as e:
                    logger.warning(f"Error extracting from PDF object: {type(e).__name__}: {e}")
                    return None
            
            # Handle dict with 'bytes' key (common HuggingFace format)
            if isinstance(pdf_data, dict) and 'bytes' in pdf_data:
                logger.info(f"PDF data is dict with 'bytes' key, extracting {len(pdf_data['bytes'])} bytes")
                return self._extract_pdf_text(pdf_data['bytes'], max_pages)
            
            # Handle different PDF data types
            pdf_file = None
            if isinstance(pdf_data, bytes):
                logger.info(f"PDF data is bytes ({len(pdf_data)} bytes), creating BytesIO")
                pdf_file = io.BytesIO(pdf_data)
            elif isinstance(pdf_data, str) and os.path.exists(pdf_data):
                logger.info(f"PDF data is file path: {pdf_data}")
                pdf_file = pdf_data
            elif hasattr(pdf_data, 'read'):
                logger.info(f"PDF data is file-like object: {type(pdf_data)}")
                pdf_file = pdf_data
            else:
                logger.warning(f"Unknown PDF data type: {type(pdf_data)}, cannot extract")
                return None
            
            # Extract text from all pages
            text_parts = []
            with pdfplumber.open(pdf_file) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Opened PDF with {total_pages} pages, extracting up to {max_pages} pages")
                
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
                    
                    # Limit to max_pages to avoid memory issues
                    if page_num >= max_pages:
                        logger.info(f"Truncated PDF extraction at {page_num} pages (max: {max_pages})")
                        break
            
            extracted_text = "\n\n".join(text_parts) if text_parts else None
            if extracted_text:
                logger.info(f"Successfully extracted {len(extracted_text)} total characters from {len(text_parts)} pages")
            else:
                logger.warning("No text could be extracted from PDF")
            return extracted_text
            
        except Exception as e:
            logger.error(f"PDF extraction error: {type(e).__name__}: {e}")
            return None

    def _create_novel_placeholders(self, count: int) -> List[Dict[str, Any]]:
        """Create placeholder novel entries when dataset is unavailable"""
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
                    "content_available": False
                }
            }
            docs.append(doc)
        return docs

    def transform_manuals(self, dataset_name: str = "nlasso/anac-manuals-23") -> List[Dict[str, Any]]:
        """
        Transform nlasso/anac-manuals-23 dataset
        Format: Technical procedure and instruction manuals
        """
        logger.info(f"Loading {dataset_name}...")
        dataset = load_dataset(dataset_name)

        warbler_docs = []

        if isinstance(dataset, list):
            items = dataset
        elif hasattr(dataset, 'keys'):
            items = []
            for split in dataset.keys():
                items.extend(dataset[split])
        else:
            items = dataset

        for item in items:
            if isinstance(item, dict):
                doc = {
                    "content_id": f"manual/{item.get('id', hash(item.get('title', '')) % 10000)}",
                    "content": self._create_manual_content(item),
                    "metadata": {
                        "pack": "warbler-pack-manuals",
                        "source_dataset": dataset_name,
                        "title": item.get('title', '')[:150],
                        "sections": len(item.get('sections', [])),
                        "realm_type": "procedural",
                        "realm_label": "technical_manual",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.7,
                        "dialogue_type": "instructional_content",
                        "license": "MIT"
                    }
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} manual entries")
        return warbler_docs

    def transform_enterprise(self, dataset_name: str = "SustcZhangYX/ChatEnv") -> List[Dict[str, Any]]:
        """
        Transform SustcZhangYX/ChatEnv dataset
        Format: Software development chat conversations and collaborative coding scenarios
        
        Note: ChatEnv contains multi-agent software development conversations.
        """
        logger.info(f"Loading {dataset_name}...")
        items = []
        
        # Try multiple loading strategies
        try:
            # Strategy 1: Load without split specification (no trust_remote_code)
            dataset = load_dataset(dataset_name)
            # Try to access dataset directly
            if hasattr(dataset, '__getitem__'):
                # Check for common split names
                for split_name in ['train', 'test', 'validation', 'default']:
                    try:
                        if split_name in dataset:
                            items = list(dataset[split_name])
                            logger.info(f"Loaded {len(items)} items from '{split_name}' split")
                            break
                    except Exception as split_error:
                        logger.debug(f"Could not load split '{split_name}': {split_error}")
                        continue
                
                # If no split worked, try extracting
                if not items:
                    items = self._extract_dataset_items(dataset)
                    if items:
                        logger.info(f"Extracted {len(items)} items from dataset")
        except Exception as e:
            logger.warning(f"Failed to load {dataset_name}: {e}")
            # Dataset is broken, return empty list
            logger.info(f"Skipping {dataset_name} - dataset has loading issues")
            return []

        if not items:
            logger.warning(f"No items loaded from {dataset_name}")
            return []

        warbler_docs = []

        for idx, item in enumerate(items):
            if isinstance(item, dict) or hasattr(item, '__getitem__'):
                # ChatEnv typically has conversation/messages field with software dev chat
                messages = []
                conversation = None
                
                # Try to extract conversation data from various possible fields
                for field in ['conversation', 'messages', 'chat', 'dialogue']:
                    try:
                        if isinstance(item, dict):
                            if field in item and item[field]:
                                conversation = item[field]
                                break
                        elif hasattr(item, '__getitem__') and field in item:
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
                
                messages_text = "\n".join(
                    f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                    if isinstance(msg, dict) else str(msg)
                    for msg in messages
                ) if messages else "[No conversation data available]"
                
                # Extract task/scenario information
                task = item.get('task', item.get('scenario', 'Software development chat')) if isinstance(item, dict) else 'Software development chat'
                scenario = item.get('scenario', item.get('task', f'ChatEnv Scenario #{idx + 1}')) if isinstance(item, dict) else f'ChatEnv Scenario #{idx + 1}'
                
                doc = {
                    "content_id": f"chatenv/{idx}",
                    "content": self._create_enterprise_content({
                        'scenario': scenario,
                        'task': task,
                        'labels': [],
                        'messages_preview': messages_text[:500]
                    }),
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
                        "license": "MIT"
                    }
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} ChatEnv software development chat entries")
        return warbler_docs

    def transform_portuguese_education(self, dataset_name: str = "Solshine/Portuguese_Language_Education_Texts") -> List[Dict[str, Any]]:
        """
        Transform Solshine/Portuguese_Language_Education_Texts dataset
        Format: Portuguese language educational content (multilingual)
        """
        logger.info(f"Loading {dataset_name}...")
        try:
            # Try loading with split='train' first
            dataset = load_dataset(dataset_name, split='train')
            items = list(dataset)
            logger.info(f"Loaded {len(items)} items from 'train' split")
        except Exception as e:
            logger.warning(f"Failed to load with split='train': {e}")
            try:
                # Fallback: load without split specification
                dataset = load_dataset(dataset_name)
                items = []
                # Try to access dataset directly
                if hasattr(dataset, '__getitem__') and 'train' in dataset:
                    items = list(dataset['train'])
                    logger.info(f"Loaded {len(items)} items from dataset['train']")
                else:
                    items = self._extract_dataset_items(dataset)
                    logger.info(f"Extracted {len(items)} items from dataset")
            except Exception as e2:
                logger.warning(f"Failed to load {dataset_name}: {e2}")
                return []

        warbler_docs = []

        for idx, item in enumerate(items):
            # Skip non-dict items (like strings)
            if isinstance(item, str):
                logger.warning(f"Portuguese doc {idx + 1}: Item is a string, skipping")
                continue
            
            if isinstance(item, dict) or hasattr(item, '__getitem__'):
                # Safely get item keys for logging
                item_keys = []
                try:
                    if isinstance(item, dict):
                        item_keys = list(item.keys())
                    elif hasattr(item, 'keys') and callable(item.keys):
                        item_keys = list(item.keys())
                except Exception:
                    item_keys = []
                
                # Try multiple field names for content
                content = None
                for field in ['content', 'text', 'body', 'document', 'passage']:
                    try:
                        if isinstance(item, dict):
                            if field in item and item[field]:
                                content = item[field]
                                break
                        elif hasattr(item, '__getitem__'):
                            if field in item and item[field]:
                                content = item[field]
                                break
                    except (KeyError, TypeError):
                        continue
                
                # Try PDF extraction if no content found
                if not content and PDF_AVAILABLE:
                    for pdf_field in ['pdf', 'file', 'document']:
                        try:
                            pdf_data = None
                            if isinstance(item, dict):
                                if pdf_field in item and item[pdf_field]:
                                    pdf_data = item[pdf_field]
                            elif hasattr(item, '__getitem__'):
                                if pdf_field in item and item[pdf_field]:
                                    pdf_data = item[pdf_field]
                            
                            if pdf_data:
                                # HuggingFace datasets often store PDFs as dict with 'bytes' key
                                if isinstance(pdf_data, dict) and 'bytes' in pdf_data:
                                    pdf_bytes = pdf_data['bytes']
                                    logger.info(f"Portuguese doc {idx + 1}: Found PDF bytes ({len(pdf_bytes)} bytes), extracting...")
                                    content = self._extract_pdf_text(pdf_bytes)
                                elif isinstance(pdf_data, bytes):
                                    logger.info(f"Portuguese doc {idx + 1}: Found PDF bytes ({len(pdf_data)} bytes), extracting...")
                                    content = self._extract_pdf_text(pdf_data)
                                else:
                                    logger.info(f"Portuguese doc {idx + 1}: Found PDF data (type: {type(pdf_data)}), attempting extraction...")
                                    content = self._extract_pdf_text(pdf_data)
                                
                                if content:
                                    logger.info(f"Portuguese doc {idx + 1}: Successfully extracted {len(content)} chars from PDF")
                                    break
                                else:
                                    logger.warning(f"Portuguese doc {idx + 1}: PDF extraction returned no text")
                        except Exception as e:
                            logger.warning(f"Portuguese doc {idx + 1}: PDF extraction error: {type(e).__name__}: {e}")
                
                # If no content found, log warning and create informative placeholder
                if not content:
                    logger.warning(f"Portuguese doc {idx + 1}: No content found. Available fields: {item_keys}")
                    content = f"""[Conteúdo Indisponível]

Este documento (#{idx + 1}) faz parte do dataset Solshine/Portuguese_Language_Education_Texts.
O conteúdo original pode requerer extração especial.

Campos disponíveis: {', '.join(item_keys) if item_keys else 'Unknown'}

Esta entrada serve como placeholder para testes do sistema de recuperação."""
                
                # Generate unique content ID using index
                title = ''
                try:
                    if isinstance(item, dict):
                        title = item.get('title', item.get('name', ''))
                    elif hasattr(item, 'get'):
                        title = item.get('title', item.get('name', ''))
                    elif hasattr(item, '__getitem__'):
                        title = item['title'] if 'title' in item else (item['name'] if 'name' in item else '')
                except Exception:
                    title = ''
                
                content_id = f"portuguese/{idx}"
                
                # Create item dict for content creation - handle conversion safely
                item_with_content = {}
                try:
                    if isinstance(item, dict):
                        item_with_content = item.copy()
                    else:
                        # Manually create dict from item attributes
                        item_with_content = {}
                        for key in item_keys:
                            try:
                                item_with_content[key] = item[key]
                            except (KeyError, TypeError):
                                pass
                except Exception as e:
                    logger.warning(f"Portuguese doc {idx + 1}: Could not convert item to dict: {e}")
                    item_with_content = {}
                
                item_with_content['content'] = content
                
                # Safely get language
                language = 'pt'
                try:
                    if isinstance(item, dict):
                        language = item.get('language', 'pt')
                    elif hasattr(item, 'get'):
                        language = item.get('language', 'pt')
                    elif hasattr(item, '__getitem__') and 'language' in item:
                        language = item['language']
                except Exception:
                    language = 'pt'
                
                doc = {
                    "content_id": content_id,
                    "content": self._create_portuguese_content(item_with_content),
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
                        "content_available": bool(content and len(content) > 50)
                    }
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} Portuguese education entries")
        return warbler_docs

    def transform_edustories(self, dataset_name: str = "MU-NLPC/Edustories-en") -> List[Dict[str, Any]]:
        """
        Transform MU-NLPC/Edustories-en dataset
        Format: Educational case studies with structured teaching situations
        
        The dataset contains structured case studies from student teachers documenting
        classroom situations with: description (background), anamnesis (situation),
        solution (teacher intervention), and outcome (final state).
        """
        logger.info(f"Loading {dataset_name}...")
        try:
            dataset = load_dataset(dataset_name)
        except Exception as e:
            logger.warning(f"Failed to load {dataset_name}: {e}")
            return []

        warbler_docs = []

        # Try to access dataset directly first, then fall back to extraction
        items = []
        try:
            # Try accessing 'train' split directly
            if hasattr(dataset, '__getitem__') and 'train' in dataset:
                items = list(dataset['train'])
                logger.info(f"Loaded {len(items)} items from 'train' split")
            else:
                items = self._extract_dataset_items(dataset)
                logger.info(f"Extracted {len(items)} items from dataset")
        except Exception as e:
            logger.warning(f"Error accessing dataset: {e}")
            items = self._extract_dataset_items(dataset)

        for idx, item in enumerate(items):
            # Skip non-dict items
            if isinstance(item, str):
                logger.warning(f"Edustory {idx + 1}: Item is a string, skipping")
                continue
            
            if isinstance(item, dict) or hasattr(item, '__getitem__'):
                # Extract structured case study fields
                def safe_get(field_name: str, default: str = '') -> str:
                    """Safely extract field from item"""
                    try:
                        if isinstance(item, dict):
                            return item.get(field_name, default) or default
                        elif hasattr(item, '__getitem__'):
                            return item[field_name] if field_name in item else default
                    except (KeyError, TypeError):
                        return default
                    return default
                
                # Extract main structured fields
                description = safe_get('description', '')
                anamnesis = safe_get('anamnesis', '')
                solution = safe_get('solution', '')
                outcome = safe_get('outcome', '')
                
                # Skip if no content found in any of the main fields
                if not any([description, anamnesis, solution, outcome]):
                    logger.warning(f"Edustory {idx + 1}: No case study content found, skipping")
                    continue
                
                # Extract entry ID
                entry_id = safe_get('id', str(idx))
                
                # Extract student attributes
                student_age_year = safe_get('age, school year', '')
                student_hobbies = safe_get('hobbies', '')
                student_diagnoses = safe_get('diagnoses', '')
                student_disorders = safe_get('disorders', '')
                
                # Extract teacher attributes
                teacher_approbation = safe_get('approbation', '')
                teacher_practice_years = safe_get('practice_years', '')
                
                # Extract annotation fields
                problems_annotated = safe_get('problems_annotated', '')
                problems_possible = safe_get('problems_possible_annotated', '')
                solutions_annotated = safe_get('solutions_annotated', '')
                solutions_possible = safe_get('solutions_possible_annotated', '')
                implications_annotated = safe_get('implications_annotated', '')
                implications_possible = safe_get('implications_possible_annotated', '')
                
                # Extract annotator ID
                annotator_id = safe_get('annotator_id', '')
                
                doc = {
                    "content_id": f"edustory/{entry_id}",
                    "content": self._create_edustories_content(item),
                    "metadata": {
                        "pack": "warbler-pack-edustories",
                        "source_dataset": dataset_name,
                        "entry_id": str(entry_id),
                        "student_age_year": student_age_year,
                        "student_hobbies": student_hobbies,
                        "student_diagnoses": student_diagnoses,
                        "student_disorders": student_disorders,
                        "teacher_approbation": teacher_approbation,
                        "teacher_practice_years": teacher_practice_years,
                        "problems_annotated": problems_annotated,
                        "problems_possible_annotated": problems_possible,
                        "solutions_annotated": solutions_annotated,
                        "solutions_possible_annotated": solutions_possible,
                        "implications_annotated": implications_annotated,
                        "implications_possible_annotated": implications_possible,
                        "annotator_id": annotator_id,
                        "realm_type": "educational",
                        "realm_label": "educational_case_studies",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.7,
                        "dialogue_type": "teaching_case_study",
                        "license": "MIT"
                    }
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} educational case study entries")
        return warbler_docs

    def _create_npc_content(self, item: Dict[str, Any]) -> str:
        """Create content string for NPC dialogue"""
        return f"""Character: {item['Name']}
Biography: {item['Biography']}
Query: {item['Query']}
Response: {item['Response']}
Emotion: {item['Emotion']}

This represents a complete character interaction pattern for NPC training."""

    def _create_multi_char_content(self, item: Dict[str, Any]) -> str:
        """Create content string for multi-character dialogue with comprehensive error handling"""
        # Validate input
        if not isinstance(item, dict):
            return "[Invalid item format - not a dictionary]"
        
        # Safely get conversation and format it with bounds checking
        conversation = item.get('conversation', [])
        conversation_lines = []
        max_conversation_items = 1000  # Prevent memory issues with extremely large conversations
        
        if isinstance(conversation, list):
            # Limit conversation processing to prevent memory issues
            conversation_subset = conversation[:max_conversation_items]
            
            for msg_idx, msg in enumerate(conversation_subset):
                try:
                    # Handle None messages
                    if msg is None:
                        continue
                    
                    # Handle dict messages
                    if isinstance(msg, dict):
                        from_field = msg.get('from', 'Unknown')
                        message_field = msg.get('message', '')
                        
                        # Validate field types
                        if not isinstance(from_field, str):
                            from_field = str(from_field) if from_field is not None else 'Unknown'
                        if not isinstance(message_field, str):
                            message_field = str(message_field) if message_field is not None else ''
                        
                        # Truncate very long messages to prevent memory issues
                        if len(message_field) > 5000:
                            message_field = message_field[:5000] + "... [truncated]"
                        
                        conversation_lines.append(f"{from_field}: {message_field}")
                    
                    # Handle string messages
                    elif isinstance(msg, str):
                        # Truncate very long strings
                        if len(msg) > 5000:
                            msg = msg[:5000] + "... [truncated]"
                        conversation_lines.append(msg)
                    
                    # Handle other types
                    else:
                        conversation_lines.append(f"[Message {msg_idx + 1}: {type(msg).__name__}]")
                        
                except (RecursionError, MemoryError) as critical_err:
                    logger.warning(f"Critical error processing conversation message {msg_idx}: {critical_err}")
                    break
                except Exception as msg_err:
                    logger.debug(f"Error processing conversation message {msg_idx}: {msg_err}")
                    continue
            
            # Add note if conversation was truncated
            if len(conversation) > max_conversation_items:
                conversation_lines.append(f"\n[... {len(conversation) - max_conversation_items} more messages truncated]")
        
        conversation_text = "\n".join(conversation_lines) if conversation_lines else "[No conversation available]"
        
        # Safely get other fields with type validation
        setting = item.get('setting', '[No setting provided]')
        if not isinstance(setting, str):
            setting = str(setting) if setting is not None else '[No setting provided]'
        
        # Truncate very long settings
        if len(setting) > 2000:
            setting = setting[:2000] + "... [truncated]"
        
        characters = item.get('characters', [])
        if not isinstance(characters, list):
            characters = [] if characters is None else [characters]
        
        setting_after = item.get('setting after interaction', '[No setting after interaction provided]')
        if not isinstance(setting_after, str):
            setting_after = str(setting_after) if setting_after is not None else '[No setting after interaction provided]'
        
        # Truncate very long setting_after
        if len(setting_after) > 2000:
            setting_after = setting_after[:2000] + "... [truncated]"
        
        # Format characters safely with error handling
        characters_str = "[]"
        try:
            # Limit characters list size
            if len(characters) > 100:
                characters = characters[:100]
                characters_str = json.dumps(characters, indent=2, ensure_ascii=False) + "\n[... truncated]"
            else:
                characters_str = json.dumps(characters, indent=2, ensure_ascii=False) if characters else "[]"
        except (TypeError, ValueError, RecursionError) as json_err:
            logger.debug(f"Error serializing characters to JSON: {json_err}")
            try:
                characters_str = str(characters)[:500] if characters else "[]"
            except Exception:
                characters_str = "[Error formatting characters]"

        # Build final content with size limits
        try:
            content = f"""Setting: {setting}
Characters: {characters_str}
Conversation:
{conversation_text}

After Interaction: {setting_after}

This represents a multi-character narrative scenario for NPC interaction training."""
            
            # Final safety check on total content size
            if len(content) > 50000:
                content = content[:50000] + "\n\n[Content truncated due to size]"
            
            return content
        except Exception as final_err:
            logger.warning(f"Error building final content: {final_err}")
            return f"[Error creating multi-character content: {type(final_err).__name__}]"

    def _create_system_chat_content(self, system: str, human: str, ai: str) -> str:
        """Create content string for system chat"""
        return f"""System: {system}
Human: {human}
AI: {ai}

This represents an instruction-following pattern for NPC behavior training."""

    def _create_arxiv_content(self, item: Dict[str, Any]) -> str:
        """Create content string for arXiv paper"""
        return f"""Title: {item.get('title', 'Untitled')}
Authors: {item.get('authors', 'Unknown')}
Year: {item.get('year', 'Unknown')}
Categories: {item.get('categories', 'Unknown')}

Abstract:
{item.get('abstract', 'No abstract available')}

This scholarly work contributes to the knowledge base of academic research."""

    def _create_prompt_report_content(self, item: Dict[str, Any]) -> str:
        """Create content string for prompt report"""
        return f"""Title: {item.get('title', 'Untitled')}
Category: {item.get('category', 'Unknown')}

Content:
{item.get('text', 'No content available')}

This document contributes to the systematic study of prompting techniques."""

    def _create_novel_content(self, title: str, text_chunk: str, chunk_idx: int, total_chunks: int) -> str:
        """Create content string for novel chunk"""
        return f"""Novel: {title}
Part: {chunk_idx + 1} of {total_chunks}

{text_chunk}

This represents a narrative segment from a generated novel."""

    def _create_manual_content(self, item: Dict[str, Any]) -> str:
        """Create content string for technical manual"""
        sections = item.get('sections', [])
        sections_str = "\n".join(f"- {s}" for s in sections) if sections else "No sections listed"
        
        return f"""Manual: {item.get('title', 'Untitled')}

Sections:
{sections_str}

Content:
{item.get('content', 'No content available')}

This manual provides technical guidance and procedures."""

    def _create_enterprise_content(self, item: Dict[str, Any]) -> str:
        """Create content string for ChatEnv software development conversations"""
        labels = item.get('labels', [])
        labels_str = ", ".join(labels) if labels else "No labels specified"
        messages = item.get('messages_preview', '')
        
        content = f"""Scenario: {item.get('scenario', 'Unknown')}
Task: {item.get('task', 'Unknown')}
Labels: {labels_str}

This entry represents a software development collaboration scenario with multi-agent conversations."""
        
        if messages:
            content += f"\n\nDevelopment Chat:\n{messages}"
        
        return content

    def _create_portuguese_content(self, item: Dict[str, Any]) -> str:
        """Create content string for Portuguese education text"""
        return f"""Título: {item.get('title', 'Sem título')}
Língua: {item.get('language', 'pt')}

Conteúdo:
{item.get('content', 'Conteúdo não disponível')}

Este documento contribui para o ensino da língua portuguesa."""

    def _create_edustories_content(self, item: Dict[str, Any]) -> str:
        """Create content string for educational case studies with structured teaching situations"""
        
        # Helper function to safely get field values
        def safe_get(field_name: str, default: str = '') -> str:
            try:
                if isinstance(item, dict):
                    return item.get(field_name, default) or default
                elif hasattr(item, '__getitem__'):
                    return item[field_name] if field_name in item else default
            except (KeyError, TypeError):
                return default
            return default
        
        # Extract main structured fields
        description = safe_get('description', '[No background provided]')
        anamnesis = safe_get('anamnesis', '[No situation description provided]')
        solution = safe_get('solution', '[No intervention described]')
        outcome = safe_get('outcome', '[No outcome reported]')
        
        # Extract student profile
        student_age_year = safe_get('age, school year', '')
        student_hobbies = safe_get('hobbies', '')
        student_diagnoses = safe_get('diagnoses', '')
        student_disorders = safe_get('disorders', '')
        
        # Build student profile section
        student_profile_parts = []
        if student_age_year:
            student_profile_parts.append(f"Age/Year: {student_age_year}")
        if student_hobbies:
            student_profile_parts.append(f"Hobbies: {student_hobbies}")
        if student_diagnoses:
            student_profile_parts.append(f"Diagnoses: {student_diagnoses}")
        if student_disorders:
            student_profile_parts.append(f"Disorders: {student_disorders}")
        
        student_profile = "\n".join(student_profile_parts) if student_profile_parts else "[No student profile available]"
        
        # Extract annotation fields
        problems_annotated = safe_get('problems_annotated', '')
        solutions_annotated = safe_get('solutions_annotated', '')
        implications_annotated = safe_get('implications_annotated', '')
        
        # Build annotations section
        annotations_parts = []
        if problems_annotated:
            annotations_parts.append(f"Identified Problems: {problems_annotated}")
        if solutions_annotated:
            annotations_parts.append(f"Solution Categories: {solutions_annotated}")
        if implications_annotated:
            annotations_parts.append(f"Outcome Implications: {implications_annotated}")
        
        annotations = "\n".join(annotations_parts) if annotations_parts else ""
        
        # Build the complete content
        content_parts = [
            "=== Educational Case Study ===",
            "",
            "## Background",
            description,
            "",
            "## Situation",
            anamnesis,
            "",
            "## Teacher Intervention",
            solution,
            "",
            "## Outcome",
            outcome,
            "",
            "## Student Profile",
            student_profile
        ]
        
        if annotations:
            content_parts.extend([
                "",
                "## Annotations",
                annotations
            ])
        
        content_parts.extend([
            "",
            "This case study documents a real teaching situation from classroom practice,",
            "providing insights into educational interventions and their outcomes."
        ])
        
        return "\n".join(content_parts)

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks by word count"""
        if not text or chunk_size <= 0:
            return [text] if text else []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks if chunks else [text]

    def create_warbler_pack(self, docs: List[Dict[str, Any]], pack_name: str) -> str:
        """Create Warbler pack from transformed documents"""

        # Create pack directory
        pack_dir = PACKS_DIR / pack_name
        pack_dir.mkdir(exist_ok=True, parents=True)

        # Save documents as JSONL
        pack_file = pack_dir / f"{pack_name}.jsonl"

        with open(pack_file, 'w', encoding='utf-8') as f:
            for doc in docs:
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')

        # Create pack metadata
        metadata = {
            "name": pack_name,
            "version": "1.0.0",
            "description": f"Warbler pack generated from HuggingFace datasets",
            "created_at": datetime.now().isoformat(),
            "document_count": len(docs),
            "source": "HuggingFace",
            "content_types": list(set(doc['metadata']['dialogue_type'] for doc in docs))
        }

        metadata_file = pack_dir / "package.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            f.write('\n')

        logger.info(f"✓ Created Warbler pack: {pack_name} with {len(docs)} documents")
        return str(pack_dir)

    def save_ingestion_report(self, results: Dict[str, Any]) -> str:
        """Save detailed ingestion report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "total_documents": sum(len(docs) for docs in results.values()),
            "packs_created": len(results)
        }

        report_file = self.output_dir / f"ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write('\n')

        logger.info(f"✓ Saved ingestion report: {report_file}")
        return str(report_file)


@click.group()
def cli():
    """HuggingFace Warbler Pack Ingestion Tool"""
    pass


@cli.command()
@click.option('--datasets', '-d', multiple=True,
              type=click.Choice(['npc-dialogue', 'multi-character', 'system-chat', 'arxiv', 'prompt-report', 
                               'novels', 'manuals', 'enterprise', 'portuguese-edu', 'edustories', 'all']),
              default=['arxiv'], help='Datasets to ingest')
@click.option('--pack-prefix', '-p', default='warbler-pack-hf', help='Prefix for pack names')
@click.option('--arxiv-limit', type=int, default=None, help='Limit number of arXiv papers to ingest')
def ingest(datasets, pack_prefix, arxiv_limit):
    """Ingest HF datasets into Warbler packs"""

    ingestor = HFWarblerIngestor()
    results = {}

    if 'all' in datasets:
        datasets = ['arxiv', 'prompt-report', 'novels', 'manuals', 'enterprise', 'portuguese-edu',
                   'edustories', 'multi-character', 'system-chat']

    for dataset in datasets:
        click.echo(f"\n🔄 Processing {dataset}...")

        try:
            if dataset == 'npc-dialogue':
                docs = ingestor.transform_npc_dialogue()
                pack_name = f"{pack_prefix}-npc-dialogue"
            elif dataset == 'multi-character':
                docs = ingestor.transform_multi_character()
                pack_name = f"{pack_prefix}-multi-character"
            elif dataset == 'system-chat':
                docs = ingestor.transform_system_chat()
                pack_name = f"{pack_prefix}-system-chat"
            elif dataset == 'arxiv':
                docs = ingestor.transform_arxiv(limit=arxiv_limit)
                pack_name = f"{pack_prefix}-arxiv"
            elif dataset == 'prompt-report':
                docs = ingestor.transform_prompt_report()
                pack_name = f"{pack_prefix}-prompt-report"
            elif dataset == 'novels':
                docs = ingestor.transform_novels()
                pack_name = f"{pack_prefix}-novels"
            elif dataset == 'manuals':
                docs = ingestor.transform_manuals()
                pack_name = f"{pack_prefix}-manuals"
            elif dataset == 'enterprise':
                docs = ingestor.transform_enterprise()
                pack_name = f"{pack_prefix}-enterprise"
            elif dataset == 'portuguese-edu':
                docs = ingestor.transform_portuguese_education()
                pack_name = f"{pack_prefix}-portuguese-edu"
            elif dataset == 'edustories':
                docs = ingestor.transform_edustories()
                pack_name = f"{pack_prefix}-edustories"
            else:
                click.echo(f"❌ Unknown dataset: {dataset}")
                continue

            if docs:
                pack_path = ingestor.create_warbler_pack(docs, pack_name)
                results[dataset] = {
                    "documents": len(docs),
                    "pack_path": pack_path
                }
                click.echo(f"✓ {len(docs)} documents created")
            else:
                click.echo(f"⚠️  No documents generated for {dataset}")

        except Exception as e:
            click.echo(f"❌ Error processing {dataset}: {str(e)}")

    # Save report
    if results:
        report_file = ingestor.save_ingestion_report(results)

        click.echo(f"\n✅ Ingestion Complete!")
        click.echo(f"📊 Total Documents: {sum(r['documents'] for r in results.values())}")
        click.echo(f"📦 Packs Created: {len(results)}")
        click.echo(f"📄 Report: {report_file}")
    else:
        click.echo(f"\n⚠️  No packs were created")


@cli.command()
def list_available():
    """List available MIT-licensed datasets for ingestion"""
    click.echo("\n📋 Available MIT-Licensed Datasets:")
    click.echo("\n🔬 Primary Datasets (Recommended):")
    click.echo("  • arxiv                  - Scholarly papers (2.55M, use --arxiv-limit to control)")
    click.echo("  • prompt-report          - Prompt engineering docs (83 docs, 1.09K interactions)")
    click.echo("  • novels                 - Generated novels (20 novels, narrative text, PDF-based)")
    click.echo("  • manuals                - Technical manuals (52 manuals, procedural)")
    click.echo("  • enterprise             - ChatEnv software dev chat (collaborative coding scenarios)")
    click.echo("  • portuguese-edu         - Portuguese education texts (21 docs, multilingual)")
    click.echo("  • edustories             - Educational stories in English (MU-NLPC/Edustories-en)")
    click.echo("\n🔧 Legacy Datasets (Keep for compatibility):")
    click.echo("  • multi-character        - Multi-character conversations")
    click.echo("  • system-chat            - System prompt conversations")
    click.echo("\n📦 Special:")
    click.echo("  • all                    - All primary MIT-licensed datasets")
    click.echo("\n⚠️  Notes:")
    click.echo("  • amaydle/npc-dialogue has been REMOVED (unlicensed, copyrighted)")
    click.echo("  • enterprise now uses SustcZhangYX/ChatEnv (replaced AST-FRI/EnterpriseBench)")
    click.echo("  • novels dataset requires pdfplumber for full text extraction")


if __name__ == "__main__":
    cli()
