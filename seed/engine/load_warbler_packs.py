#!/usr/bin/env python3
"""
Load Warbler Pack Data into EXP-09 API Service

Ingests game wisdom, lore, and faction data into the STAT7-enabled RetrievalAPI
for end-to-end testing with real Warbler content.
"""

import json
import requests
import click
from pathlib import Path
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Warbler pack locations
PACKS_DIR = Path("E:/Tiny_Walnut_Games/the-seed/packs")
WARBLER_PACKS = [
    "warbler-pack-core",
    "warbler-pack-wisdom-scrolls",
    "warbler-pack-faction-politics",
    "warbler-pack-hf-npc-dialogue",
    "warbler-pack-hf-multi-character"
]


class WarblerPackLoader:
    """Load Warbler pack data into the API"""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip("/")
        self.session = requests.Session()
        self.loaded_count = 0
        self.error_count = 0

    def discover_documents(self, pack_name: str) -> List[Dict[str, Any]]:
        """Discover all documents in a pack"""
        pack_path = PACKS_DIR / pack_name
        documents = []

        if not pack_path.exists():
            logger.warning(f"Pack not found: {pack_path}")
            return []

        # Look for JSON, YAML, markdown, and JSONL files
        for pattern in ["**/*.json", "**/*.yaml", "**/*.yml", "**/*.md", "**/*.jsonl"]:
            for file_path in pack_path.glob(pattern):
                try:
                    doc = self._parse_document(file_path, pack_name)
                    if doc:
                        documents.append(doc)
                        logger.info(f"Discovered: {file_path.relative_to(PACKS_DIR)}")
                except Exception as e:
                    logger.error(f"Error parsing {file_path}: {e}")

        return documents

    def _parse_document(self, file_path: Path, pack_name: str) -> Dict[str, Any]:
        """Parse a document file"""
        try:
            if file_path.suffix in ['.json']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        content = json.dumps(content)
                    else:
                        content = json.dumps(content)
            elif file_path.suffix in ['.jsonl']:
                # JSONL files contain multiple JSON objects, one per line
                # We'll read the first few lines and combine them
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:5]  # First 5 lines
                    content = '\n'.join(line.strip() for line in lines if line.strip())
            elif file_path.suffix in ['.yaml', '.yml']:
                import yaml
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    content = json.dumps(content)
            elif file_path.suffix == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                return None

            # Infer realm from pack name
            if "wisdom" in pack_name:
                realm = "wisdom"
            elif "faction" in pack_name:
                realm = "faction"
            else:
                realm = "narrative"

            return {
                "content_id": f"{pack_name}/{file_path.stem}",
                "content": str(content)[:5000],  # Limit content size
                "metadata": {
                    "pack": pack_name,
                    "source_file": str(file_path.name),
                    "realm_type": realm,
                    "realm_label": pack_name.replace("warbler-pack-", ""),
                    "lifecycle_stage": "emergence",
                    "activity_level": 0.7
                }
            }
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return None

    def ingest_document(self, doc: Dict[str, Any]) -> bool:
        """Send document to API for ingestion"""
        try:
            # For now, we'll store in local context
            # The API service will need an /ingest endpoint
            logger.info(f"Ingesting: {doc['content_id']}")

            # Check if API has ingest endpoint
            response = self.session.post(
                f"{self.api_url}/ingest",
                json={"documents": [doc]},
                timeout=10
            )

            if response.status_code in [200, 201, 202]:
                self.loaded_count += 1
                logger.info(f"✓ Loaded: {doc['content_id']}")
                return True
            else:
                logger.warning(f"API returned {response.status_code}: {response.text[:200]}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to API. Is the service running?")
            return False
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            self.error_count += 1
            return False

    def load_all_packs(self) -> int:
        """Load all Warbler packs"""
        click.echo("\n" + "="*60)
        click.echo("Loading Warbler Pack Data into EXP-09 API")
        click.echo("="*60 + "\n")

        total_docs = 0
        for pack_name in WARBLER_PACKS:
            click.echo(f"\n📦 Processing: {pack_name}")
            click.echo("-" * 40)

            documents = self.discover_documents(pack_name)
            click.echo(f"Found {len(documents)} documents\n")

            for doc in documents:
                self.ingest_document(doc)
                total_docs += 1

        click.echo("\n" + "="*60)
        click.secho(f"✓ Load Complete: {self.loaded_count} docs ingested", fg="green")
        if self.error_count > 0:
            click.secho(f"✗ Errors: {self.error_count}", fg="yellow")
        click.echo("="*60 + "\n")

        return self.loaded_count


@click.group()
def cli():
    """Warbler Pack Loader for EXP-09"""
    pass


@cli.command()
@click.option("--api-url", default="http://localhost:8000", help="API service URL")
def load(api_url):
    """Load all Warbler packs into the API"""
    loader = WarblerPackLoader(api_url)

    # First, check if API is running
    try:
        response = loader.session.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            click.secho("✓ API service is running", fg="green")
        else:
            click.secho("✗ API service not responding correctly", fg="red")
            return
    except Exception as e:
        click.secho(f"✗ Cannot reach API at {api_url}: {e}", fg="red")
        click.echo("\nStart the service with: docker-compose up -d")
        return

    # Load the packs
    loaded = loader.load_all_packs()

    if loaded > 0:
        click.echo("\n📊 Next Steps:")
        click.echo("  1. Query the data with: python exp09_cli.py query --query-id q1 --semantic \"wisdom about courage\"")
        click.echo("  2. Test hybrid scoring: python exp09_cli.py query --query-id q1 --semantic \"...\" --hybrid")
        click.echo("  3. Check metrics: python exp09_cli.py metrics\n")


@cli.command()
@click.option("--api-url", default="http://localhost:8000", help="API service URL")
def discover(api_url):
    """Discover documents in Warbler packs (no loading)"""
    loader = WarblerPackLoader(api_url)

    click.echo("\n" + "="*60)
    click.echo("Discovering Warbler Pack Documents")
    click.echo("="*60 + "\n")

    total = 0
    for pack_name in WARBLER_PACKS:
        click.echo(f"\n📦 {pack_name}")
        click.echo("-" * 40)

        documents = loader.discover_documents(pack_name)
        total += len(documents)

        for doc in documents:
            click.echo(f"  • {doc['content_id']}")
            if "metadata" in doc:
                click.echo(f"    Realm: {doc['metadata'].get('realm_type', 'unknown')}")

    click.echo(f"\n📊 Total discovered: {total} documents\n")


if __name__ == "__main__":
    cli()
