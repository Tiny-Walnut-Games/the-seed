#!/usr/bin/env python3
"""
HuggingFace Warbler Pack Ingestion Pipeline.

Imports HF datasets and transforms them into Warbler-compatible packs
for NPC intelligence training via the magma layer self-training system.
"""

import logging
from pathlib import Path
from typing import List, Optional

import click

from .transformers import (
    NPCDialogueTransformer,
    MultiCharacterTransformer,
    SystemChatTransformer,
    ArxivTransformer,
    PromptReportTransformer,
    NovelsTransformer,
    ManualsTransformer,
    EnterpriseTransformer,
    PortugueseEducationTransformer,
    EdustoriesTransformer,
    WarblerPackBuilder,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
PACKS_DIR = BASE_DIR.parents[1] / "packs"


@click.group()
def cli():
    """HuggingFace Warbler Pack Ingestion Tool."""
    pass


@cli.command()
@click.option(
    "--datasets",
    "-d",
    multiple=True,
    type=click.Choice(
        [
            "npc-dialogue",
            "multi-character",
            "system-chat",
            "arxiv",
            "prompt-report",
            "novels",
            "manuals",
            "enterprise",
            "portuguese-edu",
            "edustories",
            "all",
        ]
    ),
    default=["arxiv"],
    help="Datasets to ingest",
)
@click.option("--pack-prefix", "-p", default="warbler-pack-hf", help="Prefix for pack names")
@click.option(
    "--arxiv-limit", type=int, default=None, help="Limit number of arXiv papers to ingest (HARD LIMIT: 250,000 for 1GB storage compliance)"
)
@click.option(
    "--max-docs-per-chunk",
    type=int,
    default=50000,
    help="Maximum documents per chunk file (default: 50000). Use 0 for no chunking.",
)
@click.option(
    "--max-pdf-pages",
    type=int,
    default=None,
    help="Maximum PDF pages to extract (default: None for unlimited)",
)
def ingest(datasets, pack_prefix, arxiv_limit, max_docs_per_chunk, max_pdf_pages):
    """Ingest HF datasets into Warbler packs."""
    PACKS_DIR.mkdir(exist_ok=True, parents=True)
    builder = WarblerPackBuilder(PACKS_DIR)
    results = {}

    if "all" in datasets:
        datasets = [
            "arxiv",
            "prompt-report",
            "novels",
            "manuals",
            "enterprise",
            "portuguese-edu",
            "edustories",
        ]

    if max_docs_per_chunk > 0:
        click.echo(f"[PACK] Chunking enabled: {max_docs_per_chunk} documents per chunk")
    else:
        click.echo("[PACK] Chunking disabled: single file per pack")

    if max_pdf_pages is not None:
        click.echo(f"[PDF] PDF extraction limit: {max_pdf_pages} pages")
    else:
        click.echo("[PDF] PDF extraction: unlimited pages")

    click.echo()

    for dataset in datasets:
        click.echo(f"\n[*] Processing {dataset}...")

        try:
            docs = None
            pack_name = None

            if dataset == "npc-dialogue":
                transformer = NPCDialogueTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-npc-dialogue"
            elif dataset == "multi-character":
                transformer = MultiCharacterTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-multi-character"
            elif dataset == "system-chat":
                transformer = SystemChatTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-system-chat"
            elif dataset == "arxiv":
                transformer = ArxivTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform(limit=arxiv_limit)
                pack_name = f"{pack_prefix}-arxiv"
            elif dataset == "prompt-report":
                transformer = PromptReportTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-prompt-report"
            elif dataset == "novels":
                transformer = NovelsTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-novels"
            elif dataset == "manuals":
                transformer = ManualsTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-manuals"
            elif dataset == "enterprise":
                transformer = EnterpriseTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-enterprise"
            elif dataset == "portuguese-edu":
                transformer = PortugueseEducationTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-portuguese-edu"
            elif dataset == "edustories":
                transformer = EdustoriesTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-edustories"
            else:
                click.echo(f"[ERROR] Unknown dataset: {dataset}")
                continue

            if docs:
                chunk_size = max_docs_per_chunk if max_docs_per_chunk > 0 else float("inf")
                pack_path = builder.create_pack(docs, pack_name, max_docs_per_chunk=chunk_size)
                results[dataset] = {"documents": len(docs), "pack_path": pack_path}
                click.echo(f"[OK] {dataset}: {len(docs)} documents -> {pack_path}")

        except Exception as e:
            click.echo(f"[ERROR] Error processing {dataset}: {str(e)}")

    if results:
        report_file = builder.save_report(results)

        click.echo("\n[SUCCESS] Ingestion Complete!")
        click.echo(f"[STATS] Total Documents: {sum(r['documents'] for r in results.values())}")
        click.echo(f"[STATS] Packs Created: {len(results)}")
        click.echo(f"[STATS] Report saved to: {report_file}")
    else:
        click.echo("\n[WARNING] No datasets processed successfully")


class HFWarblerIngestor:
    """Runtime ingestion class for downloading datasets at app launch."""
    def __init__(self, packs_dir: Path = None, verbose: bool = True):
        """Initialize the ingestor."""
        if packs_dir is None:
            packs_dir = PACKS_DIR
        self.packs_dir = Path(packs_dir)
        self.verbose = verbose
        self.builder = WarblerPackBuilder(self.packs_dir)

    def ingest_dataset(self, dataset_name: str, pack_prefix: str = "warbler-pack-hf",
                      arxiv_limit: Optional[int] = None, max_docs_per_chunk: int = 50000,
                      max_pdf_pages: Optional[int] = None) -> bool:
        """Ingest a specific dataset.

        Args:
            dataset_name: Name of dataset to ingest
            pack_prefix: Prefix for pack names
            arxiv_limit: Limit for arXiv papers
            max_docs_per_chunk: Chunking configuration
            max_pdf_pages: PDF extraction limit

        Returns:
            True if ingestion successful, False otherwise
        """
        try:
            if self.verbose:
                print(f"📦 Processing {dataset_name}...")

            docs = None
            pack_name = None

            if dataset_name == "npc-dialogue":
                transformer = NPCDialogueTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-npc-dialogue"
            elif dataset_name == "multi-character":
                transformer = MultiCharacterTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-multi-character"
            elif dataset_name == "system-chat":
                transformer = SystemChatTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-system-chat"
            elif dataset_name == "arxiv":
                transformer = ArxivTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform(limit=arxiv_limit)
                pack_name = f"{pack_prefix}-arxiv"
            elif dataset_name == "prompt-report":
                transformer = PromptReportTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-prompt-report"
            elif dataset_name == "novels":
                transformer = NovelsTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-novels"
            elif dataset_name == "manuals":
                transformer = ManualsTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-manuals"
            elif dataset_name == "enterprise":
                transformer = EnterpriseTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-enterprise"
            elif dataset_name == "portuguese-edu":
                transformer = PortugueseEducationTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-portuguese-edu"
            elif dataset_name == "edustories":
                transformer = EdustoriesTransformer(max_pdf_pages=max_pdf_pages)
                docs = transformer.transform()
                pack_name = f"{pack_prefix}-edustories"
            else:
                if self.verbose:
                    print(f"❌ Unknown dataset: {dataset_name}")
                return False

            if docs:
                chunk_size = max_docs_per_chunk if max_docs_per_chunk > 0 else float("inf")
                pack_path = self.builder.create_pack(docs, pack_name, max_docs_per_chunk=chunk_size)

                if self.verbose:
                    print(f"✅ {dataset_name}: {len(docs)} documents -> {pack_path}")
                return True
            else:
                if self.verbose:
                    print(f"⚠️ No documents found for {dataset_name}")
                return False

        except Exception as e:
            if self.verbose:
                print(f"❌ Error processing {dataset_name}: {e}")
            return False


if __name__ == "__main__":
    cli()
