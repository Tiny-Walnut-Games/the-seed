# HuggingFace Warbler Pack Ingestion Guide

## 🎯 Overview

This guide shows developers how to import HuggingFace datasets into Warbler packs for NPC intelligence training via the magma layer self-training system.

## 📋 Prerequisites

### Required Dependencies
```bash
pip install datasets transformers
```

### Directory Structure
```
E:/Tiny_Walnut_Games/the-seed/
├── packs/                    # Warbler pack output directory
├── seed/engine/
│   ├── hf_warbler_ingest.py  # Ingestion script
│   └── load_warbler_packs.py  # Pack loader (updated)
└── results/hf_ingest/         # Ingestion reports
```

## 🚀 Quick Start

### 1. List Available Datasets
```bash
cd E:\Tiny_Walnut_Games\the-seed\seed\engine
python hf_warbler_ingest.py list-available
```

**Available Datasets:**
- `npc-dialogue` - Character profiles + dialog (1.9K entries)
- `multi-character` - Multi-character conversations (10K+ entries)
- `system-chat` - System prompt conversations (7K entries)
- `all` - All datasets above

### 2. Ingest a Dataset
```bash
# Single dataset
python hf_warbler_ingest.py ingest --datasets npc-dialogue

# Multiple datasets
python hf_warbler_ingest.py ingest --datasets npc-dialogue multi-character

# All datasets
python hf_warbler_ingest.py ingest --datasets all
```

### 3. Load into API Service
```bash
# Start API service
python -m uvicorn exp09_api_service:app --host 0.0.0.0 --port 8000

# Load packs (in new terminal)
python load_warbler_packs.py load
```

### 4. Test the Data
```bash
# Test semantic search
python exp09_cli.py query --query-id "test_npc" --semantic "bounty hunter character"

# Test hybrid scoring
python exp09_cli.py query --query-id "test_hybrid" --semantic "character background" --hybrid
```

## 📊 Dataset Details

### NPC Dialogue (`amaydle/npc-dialogue`)
- **Size**: 1,915 entries
- **Format**: Name, Biography, Query, Response, Emotion
- **Use Case**: Character personality training
- **Example**: Bounty hunters, clerics, vampires, werewolves

### Multi-Character (`agentlans/multi-character-dialogue`)
- **Size**: 10,000+ entries
- **Format**: Setting, Characters, Conversation, Post-interaction
- **Use Case**: Multi-NPC interaction training
- **Example**: Concert halls, fantasy scenarios, group dynamics

### System Chat (`abacusai/SystemChat`)
- **Size**: 7,000+ entries
- **Format**: System prompt + Human + AI responses
- **Use Case**: Instruction following training
- **Example**: Religious advisors, technical support, ethical guides

## 🔧 Advanced Usage

### Custom Pack Names
```bash
python hf_warbler_ingest.py ingest --datasets npc-dialogue --pack-prefix my-custom-pack
```

### Processing Specific Splits
```python
# In hf_warbler_ingest.py, modify dataset loading:
dataset = load_dataset("amaydle/npc-dialogue", split="train")  # or "test"
```

### Custom Content Transformation
Edit the `_create_*_content()` methods in `HFWarblerIngestor` class to customize how HF data is transformed into Warbler format.

## 📁 Output Structure

### Generated Pack Structure
```
packs/warbler-pack-hf-npc-dialogue/
├── package.json                    # Pack metadata
└── warbler-pack-hf-npc-dialogue.jsonl  # Warbler documents (JSONL)
```

### Document Format (JSONL)
```json
{
  "content_id": "npc-dialogue/arcturus-bounty-hunter",
  "content": "Character: Arcturus the Bounty Hunter\nBiography: ...",
  "metadata": {
    "pack": "warbler-pack-hf-npc-dialogue",
    "source_dataset": "amaydle/npc-dialogue",
    "character_name": "Arcturus the Bounty Hunter",
    "realm_type": "character",
    "dialogue_type": "character_interaction"
  }
}
```

## 🧪 Testing Results

### Successful Test Query
```bash
python exp09_cli.py query --query-id "test_bounty" --semantic "bounty hunter dangerous missions"
```

**Expected Output:**
```
Results: 1
Execution Time: 1.2ms
Semantic Similarity: 1.000
Narrative Analysis:
  Coherence Score: 0.899
  Narrative Threads: 1
```

## 🔍 Troubleshooting

### Dataset Not Found
```bash
# Check dataset exists on HuggingFace
python -c "from datasets import load_dataset; load_dataset('amaydle/npc-dialogue')"
```

### JSONL Not Loading
Ensure `load_warbler_packs.py` includes JSONL support:
```python
for pattern in ["**/*.json", "**/*.yaml", "**/*.yml", "**/*.md", "**/*.jsonl"]:
```

### API Service Issues
```bash
# Check API health
python exp09_cli.py health

# Check metrics
python exp09_cli.py metrics --json-output
```

## 📈 Integration with Magma Layer

The ingested HF data feeds directly into Warbler's self-training loop:

1. **Content → Clusters**: HF documents are grouped into semantic clusters
2. **Clusters → Melt Layer**: Compressed into molten glyphs
3. **Glyphs → Evaporation**: Distilled into mist lines (proto-thoughts)
4. **Mist → Warbler**: Used for NPC dialog generation

### Example Flow
```
HF NPC Dialogue → Character Cluster → Melt Layer → Evaporation → Warbler Output
```

## 🎮 Use Cases for Developers

### 1. Character Training
```python
# Load character-specific data
python hf_warbler_ingest.py ingest --datasets npc-dialogue

# Query character backgrounds
python exp09_cli.py query --query-id "character_bg" --semantic "paladin holy warrior"
```

### 2. Multi-NPC Scenarios
```python
# Load multi-character data
python hf_warbler_ingest.py ingest --datasets multi-character

# Test group interactions
python exp09_cli.py query --query-id "group_scene" --semantic "concert hall musicians"
```

### 3. Instruction Following
```python
# Load system chat data
python hf_warbler_ingest.py ingest --datasets system-chat

# Test instruction compliance
python exp09_cli.py query --query-id "instruction_test" --semantic "religious advice guidance"
```

## 📚 Next Steps

1. **Custom Datasets**: Create domain-specific datasets for your game
2. **Fine-tuning**: Use ingested data to fine-tune NPC models
3. **Real-time Training**: Set up continuous data ingestion pipelines
4. **Performance Monitoring**: Track magma layer processing efficiency

## 🔗 References

- [HuggingFace Datasets](https://huggingface.co/datasets)
- [Warbler Pack System](../testing/TESTING-ZERO-TO-BOB.md)
- [Magma Layer Documentation](../engine/melt_layer.py)
- [API Service Documentation](../engine/exp09_api_service.py)

---

**Last Updated**: 2025-10-21
**Status**: Production Ready ✅
**Tested Datasets**: npc-dialogue, multi-character, system-chat
