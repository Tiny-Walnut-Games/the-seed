#!/usr/bin/env python3
"""
Massive Warbler Pack Ingestion for Bob Stress Testing

Ingests large-scale datasets to reach 1M+ conversations for realistic
city simulation stress testing of Bob the Skeptic.
"""

import json
import os
import click
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import asyncio
import aiohttp
import time
import random

try:
    from datasets import load_dataset, DatasetDict, Dataset
    from transformers import AutoTokenizer
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("pip install datasets transformers aiohttp")
    exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Warbler pack locations
BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[4] if len(BASE_DIR.parents) > 4 else BASE_DIR
PACKS_DIR = REPO_ROOT / 'packs'
OUTPUT_DIR = BASE_DIR / 'results' / 'massive_ingest'

class MassiveWarblerIngestor:
    """High-volume dataset ingestion for stress testing"""

    def __init__(self, tokenizer_name: str = "microsoft/DialoGPT-medium"):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.target_documents = 1000000  # 1M target
        self.batch_size = 10000  # Process in batches

    def generate_synthetic_npc_dialogue(self, count: int = 100000) -> List[Dict[str, Any]]:
        """Generate synthetic NPC dialogue for volume testing"""

        logger.info(f"🔄 Generating {count:,} synthetic NPC dialogues...")

        # Templates for synthetic content
        npc_names = [
            "Elena", "Marcus", "Sofia", "James", "Aria", "Kai", "Luna", "Orion",
            "Zara", "Finn", "Maya", "Leo", "Iris", "Rex", "Nova", "Echo",
            "Phoenix", "Atlas", "Celeste", "Dante", "Ember", "Frost", "Gaia", "Haven"
        ]

        locations = [
            "Crystal Spire", "Shadow Market", "Sun Temple", "Moon Harbor",
            "Star Forge", "Dream Weavers", "Time Keepers", "Memory Palace",
            "Echo Gardens", "Quantum Core", "Neon Streets", "Sky Docks"
        ]

        professions = [
            "merchant", "guard", "scholar", "artisan", "healer", "explorer",
            "diplomat", "engineer", "mystic", "hunter", "storyteller", "architect"
        ]

        emotions = [
            "joyful", "melancholy", "determined", "conflicted", "hopeful",
            "anxious", "peaceful", "restless", "curious", "wary", "excited",
            "thoughtful", "impatient", "grateful", "skeptical", "inspired"
        ]

        topics = [
            "trade negotiations", "ancient artifacts", "family matters", "city politics",
            "magical research", "travel plans", "personal relationships", "community events",
            "mysterious occurrences", "daily routines", "future aspirations", "past experiences"
        ]

        warbler_docs = []

        for i in range(count):
            npc = random.choice(npc_names)
            location = random.choice(locations)
            profession = random.choice(professions)
            emotion = random.choice(emotions)
            topic = random.choice(topics)

            # Generate varied content
            content_templates = [
                f"{npc} the {profession} discusses {topic} with {emotion} enthusiasm at {location}.",
                f"During a {emotion} moment at {location}, {npc} shares thoughts about {topic}.",
                f"{npc} works as a {profession} in {location}, feeling {emotion} about {topic}.",
                f"A {emotion} {npc} from {location} engages in conversation about {topic}.",
                f"The {profession} {npc} appears {emotion} while discussing {topic} in {location}."
            ]

            content = random.choice(content_templates)

            # Add variation and depth
            if random.random() < 0.3:
                content += f" This interaction reveals deeper character motivations and personal history."
            if random.random() < 0.2:
                content += f" The conversation touches on broader themes affecting the entire community."

            doc = {
                "content_id": f"synthetic-npc-{i:06d}",
                "content": content,
                "metadata": {
                    "pack": "warbler-pack-massive-synthetic",
                    "source_dataset": "synthetic_generation",
                    "character_name": npc,
                    "character_profession": profession,
                    "location": location,
                    "emotion": emotion,
                    "topic": topic,
                    "realm_type": "character",
                    "realm_label": "synthetic_npc_dialogue",
                    "lifecycle_stage": "emergence",
                    "activity_level": random.uniform(0.5, 1.0),
                    "dialogue_type": "synthetic_character_interaction",
                    "generation_timestamp": datetime.now().isoformat()
                }
            }
            warbler_docs.append(doc)

            # Progress reporting
            if (i + 1) % 10000 == 0:
                logger.info(f"  Generated {i + 1:,}/{count:,} synthetic dialogues...")

        logger.info(f"✓ Generated {len(warbler_docs):,} synthetic NPC dialogues")
        return warbler_docs

    def augment_existing_datasets(self) -> List[Dict[str, Any]]:
        """Load and augment existing datasets with variations"""

        logger.info("🔄 Loading and augmenting existing datasets...")

        augmented_docs = []

        # Try to load existing datasets
        datasets_to_try = [
            "amaydle/npc-dialogue",
            "agentlans/multi-character-dialogue",
            "abacusai/SystemChat",
            "daily_dialog",
            "empathetic_dialogues",
            "blended_skill_talk"
        ]

        for dataset_name in datasets_to_try:
            try:
                logger.info(f"  Loading {dataset_name}...")
                dataset = load_dataset(dataset_name)

                for split in dataset.keys():
                    for i, item in enumerate(dataset[split]):
                        # Create multiple variations per item
                        for variation in range(3):  # 3 variations per original
                            doc = self._create_augmented_doc(item, dataset_name, split, i, variation)
                            augmented_docs.append(doc)

                            # Limit to prevent memory issues
                            if len(augmented_docs) >= 200000:
                                break

                        if len(augmented_docs) >= 200000:
                            break

                    if len(augmented_docs) >= 200000:
                        break

                logger.info(f"  ✓ Augmented {len(augmented_docs):,} documents from {dataset_name}")
                break  # Only use first successful dataset

            except Exception as e:
                logger.warning(f"  ⚠️ Could not load {dataset_name}: {e}")
                continue

        return augmented_docs

    def _create_augmented_doc(self, item: Dict[str, Any], dataset_name: str, split: str, index: int, variation: int) -> Dict[str, Any]:
        """Create augmented document from dataset item"""

        # Extract content based on dataset structure
        content = ""
        metadata = {
            "pack": "warbler-pack-massive-augmented",
            "source_dataset": dataset_name,
            "original_split": split,
            "original_index": index,
            "variation": variation,
            "realm_type": "narrative",
            "realm_label": "augmented_dialogue",
            "lifecycle_stage": "emergence",
            "activity_level": random.uniform(0.6, 1.0),
            "dialogue_type": "augmented_interaction"
        }

        # Handle different dataset structures
        if dataset_name == "amaydle/npc-dialogue":
            content = f"Character: {item.get('Name', 'Unknown')}\n"
            content += f"Biography: {item.get('Biography', '')}\n"
            content += f"Query: {item.get('Query', '')}\n"
            content += f"Response: {item.get('Response', '')}\n"
            content += f"Emotion: {item.get('Emotion', '')}"

            metadata.update({
                "character_name": item.get('Name', 'Unknown'),
                "emotion": item.get('Emotion', 'unknown'),
                "dialogue_type": "npc_character_interaction"
            })

        elif "conversation" in str(item):
            # Handle conversation-based datasets
            if isinstance(item.get('conversation'), list):
                conversation_text = "\n".join([
                    f"{msg.get('from', 'unknown')}: {msg.get('message', msg.get('value', ''))}"
                    for msg in item['conversation']
                ])
                content = conversation_text
                metadata["dialogue_type"] = "multi_character_conversation"
            else:
                content = str(item)

        else:
            # Generic handling
            content = json.dumps(item, ensure_ascii=False)
            metadata["dialogue_type"] = "generic_content"

        # Add variation-specific modifications
        if variation == 1:
            content = f"Alternative perspective: {content}"
            metadata["variation_type"] = "alternative_perspective"
        elif variation == 2:
            content = f"Extended context: {content}\nAdditional details and background information."
            metadata["variation_type"] = "extended_context"
        else:
            metadata["variation_type"] = "original"

        return {
            "content_id": f"augmented-{dataset_name.replace('/', '-')}-{split}-{index:06d}-var{variation}",
            "content": content,
            "metadata": metadata
        }

    def create_massive_pack(self, docs: List[Dict[str, Any]], pack_name: str) -> str:
        """Create a massive Warbler pack with chunked files"""

        logger.info(f"📦 Creating massive pack: {pack_name} with {len(docs):,} documents")

        # Create pack directory
        pack_dir = PACKS_DIR / pack_name
        pack_dir.mkdir(exist_ok=True, parents=True)

        # Split into multiple files for manageability
        chunk_size = 50000  # 50K docs per file
        chunk_files = []

        for i in range(0, len(docs), chunk_size):
            chunk_docs = docs[i:i + chunk_size]
            chunk_file = pack_dir / f"{pack_name}_part_{i//chunk_size + 1:03d}.jsonl"
            chunk_files.append(chunk_file)

            logger.info(f"  Writing chunk {i//chunk_size + 1} with {len(chunk_docs):,} documents...")

            with open(chunk_file, 'w', encoding='utf-8') as f:
                for doc in chunk_docs:
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')

        # Create pack metadata
        metadata = {
            "name": pack_name,
            "version": "1.0.0",
            "description": f"Massive Warbler pack for Bob stress testing ({len(docs):,} documents)",
            "created_at": datetime.now().isoformat(),
            "document_count": len(docs),
            "chunk_count": len(chunk_files),
            "chunk_files": [f.name for f in chunk_files],
            "source": "Massive Ingestion Pipeline",
            "content_types": list(set(doc['metadata']['dialogue_type'] for doc in docs)),
            "target_use": "Bob Skeptic stress testing and city simulation"
        }

        metadata_file = pack_dir / "package.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Created massive pack: {pack_name}")
        logger.info(f"   Documents: {len(docs):,}")
        logger.info(f"   Chunks: {len(chunk_files)}")
        logger.info(f"   Location: {pack_dir}")

        return str(pack_dir)

    def save_ingestion_report(self, results: Dict[str, Any]) -> str:
        """Save detailed massive ingestion report"""

        total_docs = sum(result['document_count'] for result in results.values())

        report = {
            "timestamp": datetime.now().isoformat(),
            "ingestion_type": "massive_scale",
            "target_documents": self.target_documents,
            "results": results,
            "total_documents": total_docs,
            "packs_created": len(results),
            "completion_percentage": (total_docs / self.target_documents) * 100,
            "estimated_city_simulation_capacity": f"{total_docs // 1000}K NPCs with {total_docs // 100} conversations each"
        }

        report_file = self.output_dir / f"massive_ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Saved massive ingestion report: {report_file}")
        return str(report_file)


@click.group()
def cli():
    """Massive Warbler Pack Ingestion Tool for Bob Stress Testing"""
    pass


@cli.command()
@click.option('--synthetic-count', '-s', type=int, default=100000, help='Number of synthetic documents to generate')
@click.option('--augment', '-a', is_flag=True, help='Augment existing datasets')
@click.option('--pack-prefix', '-p', default='warbler-pack-massive', help='Prefix for pack names')
@click.option('--target', '-t', type=int, default=1000000, help='Target total documents')
def ingest(synthetic_count, augment, pack_prefix, target):
    """Ingest massive datasets for Bob stress testing"""

    ingestor = MassiveWarblerIngestor()
    ingestor.target_documents = target
    results = {}

    # Generate synthetic data
    if synthetic_count > 0:
        click.echo(f"\n🔄 Generating {synthetic_count:,} synthetic documents...")
        synthetic_docs = ingestor.generate_synthetic_npc_dialogue(synthetic_count)

        pack_name = f"{pack_prefix}-synthetic"
        pack_path = ingestor.create_massive_pack(synthetic_docs, pack_name)
        results["synthetic"] = {
            "document_count": len(synthetic_docs),
            "pack_path": pack_path
        }

    # Augment existing datasets
    if augment:
        click.echo(f"\n🔄 Augmenting existing datasets...")
        augmented_docs = ingestor.augment_existing_datasets()

        if augmented_docs:
            pack_name = f"{pack_prefix}-augmented"
            pack_path = ingestor.create_massive_pack(augmented_docs, pack_name)
            results["augmented"] = {
                "document_count": len(augmented_docs),
                "pack_path": pack_path
            }

    # Save report
    report_file = ingestor.save_ingestion_report(results)

    total_docs = sum(result['document_count'] for result in results.values())
    completion_pct = (total_docs / target) * 100

    click.echo(f"\n✅ Massive Ingestion Complete!")
    click.echo(f"📊 Target Documents: {target:,}")
    click.echo(f"📊 Actual Documents: {total_docs:,}")
    click.echo(f"📊 Completion: {completion_pct:.1f}%")
    click.echo(f"📦 Packs Created: {len(results)}")
    click.echo(f"📄 Report: {report_file}")

    if completion_pct >= 100:
        click.echo(f"\n🎉 Ready for Bob stress testing at city simulation scale!")
    else:
        click.echo(f"\n⚠️ Below target. Run again with more synthetic data to reach {target:,} documents.")


@cli.command()
def status():
    """Check current massive ingestion status"""

    packs_dir = PACKS_DIR
    massive_packs = [d for d in packs_dir.iterdir() if d.is_dir() and 'massive' in d.name]

    click.echo(f"\n📊 Massive Warbler Pack Status")
    click.echo("=" * 50)

    total_docs = 0
    for pack_dir in massive_packs:
        metadata_file = pack_dir / "package.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)

            doc_count = metadata.get('document_count', 0)
            total_docs += doc_count

            click.echo(f"📦 {pack_dir.name}")
            click.echo(f"   Documents: {doc_count:,}")
            click.echo(f"   Chunks: {metadata.get('chunk_count', 'N/A')}")
            click.echo(f"   Created: {metadata.get('created_at', 'Unknown')}")
            click.echo()

    click.echo(f"📊 Total Massive Documents: {total_docs:,}")
    click.echo(f"🎯 Target (1M): {(total_docs / 1000000) * 100:.1f}%")

    if total_docs >= 1000000:
        click.echo("✅ Ready for city-scale Bob stress testing!")
    else:
        remaining = 1000000 - total_docs
        click.echo(f"⚠️ Need {remaining:,} more documents for 1M target")


if __name__ == "__main__":
    cli()
