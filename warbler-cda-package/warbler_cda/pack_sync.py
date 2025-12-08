"""
Pack synchronization and update checking.

Verifies that local packs are up-to-date with upstream HuggingFace datasets.
Optionally re-ingests if packs are missing or outdated.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PackSync:
    """Manages pack synchronization with upstream sources."""

    PACK_MANIFEST = {
        "warbler-pack-hf-arxiv": {
            "source": "nick007x/arxiv-papers",
            "type": "huggingface",
            "description": "Scholarly papers",
        },
        "warbler-pack-hf-prompt-report": {
            "source": "PromptSystematicReview/ThePromptReport",
            "type": "huggingface",
            "description": "Prompt engineering documentation",
        },
        "warbler-pack-hf-novels": {
            "source": "GOAT-AI/generated-novels",
            "type": "huggingface",
            "description": "Generated novels",
        },
        "warbler-pack-hf-manuals": {
            "source": "nlasso/anac-manuals-23",
            "type": "huggingface",
            "description": "Technical manuals",
        },
        "warbler-pack-hf-enterprise": {
            "source": "AST-FRI/EnterpriseBench",
            "type": "huggingface",
            "description": "Enterprise benchmarks",
        },
        "warbler-pack-hf-portuguese-edu": {
            "source": "Solshine/Portuguese_Language_Education_Texts",
            "type": "huggingface",
            "description": "Portuguese education texts",
        },
    }

    def __init__(self, packs_dir: Path = None):
        """Initialize the pack synchronizer."""
        if packs_dir is None:
            packs_dir = Path(__file__).parent.parent / "packs"
        self.packs_dir = Path(packs_dir)
        self.metadata_file = self.packs_dir / ".pack_metadata.json"

    def verify_packs(self) -> Dict[str, Any]:
        """Verify all packs exist and are accessible."""
        status = {"verified": [], "missing": [], "timestamp": datetime.now().isoformat()}

        for pack_name in self.PACK_MANIFEST:
            pack_dir = self.packs_dir / pack_name
            pack_file = pack_dir / f"{pack_name}.jsonl"

            if pack_dir.exists() and pack_file.exists():
                try:
                    with open(pack_file, "r", encoding="utf-8") as f:
                        line_count = sum(1 for _ in f)
                    status["verified"].append(
                        {"pack": pack_name, "documents": line_count, "path": str(pack_dir)}
                    )
                    logger.info("✓ %s: %d documents", pack_name, line_count)
                except OSError as e:
                    logger.warning("⚠️  %s exists but unable to read: %s", pack_name, e)
                    status["missing"].append(pack_name)
            else:
                status["missing"].append(pack_name)
                logger.warning("⚠️  %s not found", pack_name)

        return status

    def save_metadata(self, status: Dict[str, Any]) -> None:
        """Save pack verification metadata."""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2)
            logger.debug("Saved pack metadata to %s", self.metadata_file)
        except OSError as e:
            logger.warning("Could not save pack metadata: %s", e)

    def get_sync_status(self) -> str:
        """Return human-readable pack sync status."""
        status = self.verify_packs()
        verified_count = len(status["verified"])
        missing_count = len(status["missing"])

        if missing_count == 0:
            return f"✓ All {verified_count} packs verified and ready"
        else:
            return (
                f"⚠️  {verified_count} packs verified, {missing_count} "
                f"missing (run ingest to rebuild)"
            )

    def suggest_reingest(self) -> Optional[str]:
        """Return reingest command if packs are missing."""
        status = self.verify_packs()
        if status["missing"]:
            return "python -m warbler_cda.utils.hf_warbler_ingest ingest --datasets all"
        return None
