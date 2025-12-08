"""Load Warbler pack data into the RetrievalAPI."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class PackLoader:
    """Load Warbler pack data into the system."""

    def __init__(self, packs_dir: Path = None):
        """Initialize the pack loader."""
        if packs_dir is None:
            packs_dir = Path(__file__).parent.parent / "packs"

        self.packs_dir = Path(packs_dir)
        self.documents = []

    def discover_documents(self) -> List[Dict[str, Any]]:
        """Discover all documents across all packs."""
        if not self.packs_dir.exists():
            logger.warning(f"Packs directory not found: {self.packs_dir}")
            return []

        documents = []

        for pack_dir in sorted(self.packs_dir.iterdir()):
            if not pack_dir.is_dir():
                continue

            pack_name = pack_dir.name
            logger.info(f"Loading pack: {pack_name}")

            pack_docs = self._load_pack(pack_dir, pack_name)
            documents.extend(pack_docs)
            logger.info(f"✓ Loaded {len(pack_docs)} documents from {pack_name}")

        self.documents = documents
        return documents

    def _load_pack(self, pack_dir: Path, pack_name: str) -> List[Dict[str, Any]]:
        """Load documents from a specific pack."""
        documents = []

        jsonl_file = pack_dir / f"{pack_name}.jsonl"

        # Validate this is actually a Warbler pack before loading
        if self._is_valid_warbler_pack(pack_dir, pack_name, jsonl_file):
            docs = self._load_jsonl_pack(pack_dir, pack_name)
            documents.extend(docs)
        else:
            # Fall back to structured pack format
            docs = self._load_structured_pack(pack_dir, pack_name)
            documents.extend(docs)

        return documents

    def _is_valid_warbler_pack(self, pack_dir: Path, pack_name: str, jsonl_file: Path) -> bool:
        """Validate that a directory is a valid Warbler pack.

        A valid Warbler pack must have:
        1. Either:
           - A JSONL file matching the pack name (single-file pack), OR
           - Chunk files matching the pattern (chunked pack)
           - OR structured templates that can be converted to JSONL
        2. AND either:
           - A package.json metadata file, OR
           - The pack name starts with 'warbler-pack-hf-' (HuggingFace packs)
        """
        # Check for package.json metadata first
        package_json = pack_dir / "package.json"
        has_valid_metadata = False
        is_chunked = False

        if package_json.exists():
            try:
                with open(package_json, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    # Validate it has required fields
                    if "name" in metadata and "version" in metadata:
                        has_valid_metadata = True
                        is_chunked = metadata.get("chunked", False)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Invalid package.json in {pack_dir}: {e}")

        # Allow HuggingFace packs even without package.json (for backward compatibility)
        if pack_name.startswith("warbler-pack-hf-"):
            has_valid_metadata = True

        if not has_valid_metadata:
            return False

        # Check for appropriate JSONL files based on chunked status
        if is_chunked:
            # For chunked packs, look for chunk files
            chunk_files = list(pack_dir.glob(f"{pack_name}-chunk-*.jsonl"))
            if chunk_files:
                logger.debug(f"Found {len(chunk_files)} chunk files for {pack_name}")
                return True
            else:
                logger.warning(f"Chunked pack {pack_name} has no chunk files")
                return False
        else:
            # For single-file packs, check if JSONL file exists
            if jsonl_file.exists():
                return True
            # Check for structured pack templates that can be converted
            templates_file = pack_dir / "pack" / "templates.json"
            if templates_file.exists():
                logger.debug(f"Single-file pack {pack_name} missing JSONL, but templates.json exists")
                return True
            logger.warning(f"Single-file pack {pack_name} missing JSONL file: {jsonl_file}")
            return False

    def _load_jsonl_pack(self, pack_dir: Path, pack_name: str) -> List[Dict[str, Any]]:
        """Load JSONL-based pack (supports both single-file and chunked packs)."""
        documents = []

        # Check if this is a chunked pack by reading package.json
        package_json = pack_dir / "package.json"
        is_chunked = False

        if package_json.exists():
            try:
                with open(package_json, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    is_chunked = metadata.get("chunked", False)
            except (json.JSONDecodeError, IOError) as err:
                logger.warning(f"Could not read package.json for {pack_name}: {err}")

        if is_chunked:
            # Load chunked pack
            logger.info(f"Loading chunked pack: {pack_name}")

            # Find all chunk files matching the pattern
            # Pattern is like "warbler-pack-hf-arxiv-chunk-*.jsonl"
            # We need to find files like "warbler-pack-hf-arxiv-chunk-001.jsonl", etc.
            chunk_files = sorted(pack_dir.glob(f"{pack_name}-chunk-*.jsonl"))

            if not chunk_files:
                logger.warning(f"No chunk files found for chunked pack {pack_name}")
                return documents

            logger.info(f"Found {len(chunk_files)} chunk files for {pack_name}")

            # Load each chunk file in order
            for chunk_file in chunk_files:
                logger.debug(f"Loading chunk: {chunk_file.name}")
                chunk_docs = self._load_jsonl_file(chunk_file, pack_name)
                documents.extend(chunk_docs)

            logger.info(f"Loaded {len(documents)} total documents from {len(chunk_files)} chunks")
        else:
            # Load single-file pack (backward compatibility)
            jsonl_file = pack_dir / f"{pack_name}.jsonl"
            if not jsonl_file.exists():
                logger.warning(f"JSONL file not found: {jsonl_file}")
                return documents

            documents = self._load_jsonl_file(jsonl_file, pack_name)

        return documents

    def _load_jsonl_file(self, jsonl_file: Path, pack_name: str) -> List[Dict[str, Any]]:
        """Load a single JSONL file with robust error handling."""
        documents = []
        error_count = 0
        max_errors_to_log = 5

        try:
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)
                        doc = self._format_document(
                            entry, pack_name, f"{jsonl_file.stem}_line_{line_num}"
                        )
                        documents.append(doc)
                    except json.JSONDecodeError as e:
                        error_count += 1
                        # Only log first few errors to avoid spam
                        if error_count <= max_errors_to_log:
                            logger.warning(
                                f"Error parsing line {line_num} in {jsonl_file.name}: {e}"
                            )
                        # Continue processing other lines instead of failing
                        continue

            if error_count > 0:
                logger.info(
                    f"Loaded {len(documents)} documents from {jsonl_file.name} "
                    f"({error_count} lines skipped due to errors)"
                )
        except Exception as e:
            logger.error(f"Error loading JSONL file {jsonl_file}: {e}")

        return documents

    def _load_structured_pack(self, pack_dir: Path, pack_name: str) -> List[Dict[str, Any]]:
        """Load structured pack with templates."""
        documents = []

        templates_file = pack_dir / "pack" / "templates.json"
        if not templates_file.exists():
            logger.debug(f"No templates.json found in {pack_dir}")
            return documents

        try:
            with open(templates_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            templates = data if isinstance(data, list) else data.get("templates", [])

            for template in templates:
                doc = {
                    "id": f"{pack_name}/{template.get('id', 'unknown')}",
                    "content": template.get("content", json.dumps(template)),
                    "metadata": {
                        "pack": pack_name,
                        "type": "template",
                        "template_id": template.get("id"),
                        "realm_type": self._infer_realm(pack_name),
                        "realm_label": pack_name.replace("warbler-pack-", ""),
                        "lifecycle_stage": "peak",
                        "activity_level": 0.8,
                    },
                }
                documents.append(doc)
            
            self._generate_jsonl_from_templates(pack_dir, pack_name, documents)
        except Exception as e:
            logger.error(f"Error loading templates from {pack_name}: {e}")

        return documents

    def _generate_jsonl_from_templates(
        self, pack_dir: Path, pack_name: str, documents: List[Dict[str, Any]]
    ) -> None:
        """Generate JSONL file from templates for future loads."""
        try:
            jsonl_file = pack_dir / f"{pack_name}.jsonl"
            if jsonl_file.exists():
                return
            
            with open(jsonl_file, "w", encoding="utf-8") as f:
                for doc in documents:
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
            
            logger.info(f"Generated JSONL file for {pack_name}: {jsonl_file.name}")
        except Exception as e:
            logger.debug(f"Could not generate JSONL for {pack_name}: {e}")

    def _format_document(
        self, entry: Dict[str, Any], pack_name: str, doc_id: str
    ) -> Dict[str, Any]:
        """Format a pack entry into a document."""
        content = entry.get("content") or entry.get("text") or json.dumps(entry)

        return {
            "id": f"{pack_name}/{doc_id}",
            "content": str(content),
            "metadata": {
                "pack": pack_name,
                "type": entry.get("type", "dialogue"),
                "realm_type": self._infer_realm(pack_name),
                "realm_label": pack_name.replace("warbler-pack-", ""),
                "lifecycle_stage": "emergence",
                "activity_level": 0.7,
                **{k: v for k, v in entry.items() if k not in ["content", "text"]},
            },
        }

    def _infer_realm(self, pack_name: str) -> str:
        """Infer realm type from pack name."""
        if "wisdom" in pack_name:
            return "wisdom"
        elif "faction" in pack_name or "politics" in pack_name:
            return "faction"
        elif "dialogue" in pack_name or "npc" in pack_name:
            return "narrative"
        else:
            return "narrative"
