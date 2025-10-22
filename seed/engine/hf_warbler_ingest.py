#!/usr/bin/env python3
"""
HuggingFace Warbler Pack Ingestion Pipeline

Imports HF datasets and transforms them into Warbler-compatible packs
for NPC intelligence training via the magma layer self-training system.
"""

import json
import os
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Warbler pack locations
PACKS_DIR = Path("E:/Tiny_Walnut_Games/the-seed/packs")
OUTPUT_DIR = Path("E:/Tiny_Walnut_Games/the-seed/seed/engine/results/hf_ingest")

class HFWarblerIngestor:
    """Transform HF datasets into Warbler packs"""

    def __init__(self, tokenizer_name: str = "microsoft/DialoGPT-medium"):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)

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
        dataset = load_dataset(dataset_name)

        warbler_docs = []

        for item in dataset['train']:
            # Create Warbler-compatible document
            doc = {
                "content_id": f"multi-char/{hash(item['setting']) % 10000}",
                "content": self._create_multi_char_content(item),
                "metadata": {
                    "pack": "warbler-pack-multi-character",
                    "source_dataset": dataset_name,
                    "setting": item['setting'][:150] + "..." if len(item['setting']) > 150 else item['setting'],
                    "character_count": len(item['characters']),
                    "conversation_length": len(item['conversation']),
                    "realm_type": "narrative",
                    "realm_label": "multi_character_dialogue",
                    "lifecycle_stage": "emergence",
                    "activity_level": 0.7,
                    "dialogue_type": "multi_character_interaction"
                }
            }
            warbler_docs.append(doc)

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
                        "dialogue_type": "instruction_following"
                    }
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} system chat entries")
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
        """Create content string for multi-character dialogue"""
        conversation_text = "\n".join([f"{msg['from']}: {msg['message']}" for msg in item['conversation']])

        return f"""Setting: {item['setting']}
Characters: {json.dumps(item['characters'], indent=2)}
Conversation:
{conversation_text}

After Interaction: {item['setting after interaction']}

This represents a multi-character narrative scenario for NPC interaction training."""

    def _create_system_chat_content(self, system: str, human: str, ai: str) -> str:
        """Create content string for system chat"""
        return f"""System: {system}
Human: {human}
AI: {ai}

This represents an instruction-following pattern for NPC behavior training."""

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

        logger.info(f"✓ Saved ingestion report: {report_file}")
        return str(report_file)


@click.group()
def cli():
    """HuggingFace Warbler Pack Ingestion Tool"""
    pass


@cli.command()
@click.option('--datasets', '-d', multiple=True,
              type=click.Choice(['npc-dialogue', 'multi-character', 'system-chat', 'all']),
              default=['npc-dialogue'], help='Datasets to ingest')
@click.option('--pack-prefix', '-p', default='warbler-pack-hf', help='Prefix for pack names')
def ingest(datasets, pack_prefix):
    """Ingest HF datasets into Warbler packs"""

    ingestor = HFWarblerIngestor()
    results = {}

    if 'all' in datasets:
        datasets = ['npc-dialogue', 'multi-character', 'system-chat']

    for dataset in datasets:
        click.echo(f"\n🔄 Processing {dataset}...")

        if dataset == 'npc-dialogue':
            docs = ingestor.transform_npc_dialogue()
            pack_name = f"{pack_prefix}-npc-dialogue"
        elif dataset == 'multi-character':
            docs = ingestor.transform_multi_character()
            pack_name = f"{pack_prefix}-multi-character"
        elif dataset == 'system-chat':
            docs = ingestor.transform_system_chat()
            pack_name = f"{pack_prefix}-system-chat"
        else:
            click.echo(f"❌ Unknown dataset: {dataset}")
            continue

        pack_path = ingestor.create_warbler_pack(docs, pack_name)
        results[dataset] = {
            "documents": len(docs),
            "pack_path": pack_path
        }

    # Save report
    report_file = ingestor.save_ingestion_report(results)

    click.echo(f"\n✅ Ingestion Complete!")
    click.echo(f"📊 Total Documents: {sum(r['documents'] for r in results.values())}")
    click.echo(f"📦 Packs Created: {len(results)}")
    click.echo(f"📄 Report: {report_file}")


@cli.command()
def list_available():
    """List available datasets for ingestion"""
    click.echo("\n📋 Available Datasets:")
    click.echo("  • npc-dialogue     - Character profiles + dialog (1.9K entries)")
    click.echo("  • multi-character  - Multi-character conversations (10K+ entries)")
    click.echo("  • system-chat      - System prompt conversations (7K entries)")
    click.echo("  • all              - All datasets above")


if __name__ == "__main__":
    cli()
