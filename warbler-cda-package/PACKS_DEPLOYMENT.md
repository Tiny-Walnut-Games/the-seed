# Warbler Packs Deployment Guide

This guide explains how Warbler packs are loaded and deployed to HuggingFace Spaces.

## Overview

The Warbler CDA Space automatically discovers and ingests content packs at startup. Packs contain conversation templates, NPC dialogues, wisdom templates, and other domain-specific content for the RAG system.

## Pack Structure

```none
packs/
├── warbler-pack-core/              # Essential conversation templates
├── warbler-pack-faction-politics/  # Political dialogue templates
├── warbler-pack-wisdom-scrolls/    # Development wisdom generation
└── warbler-pack-hf-npc-dialogue/   # 1,900+ NPC dialogues from HuggingFace
```

## Deployment Process

### 1. Local Development

Copy packs from the main repository to warbler-cda-package:

```bash
cd warbler-cda-package
bash copy_packs.sh
```

This script copies all packs from:

```path
../packages/com.twg.the-seed/The Living Dev Agent/packs/
```

To:

```path
./packs/
```

### 2. Automatic Loading

When `app.py` starts, it:

1. **Initializes PackLoader**

   ```python
   pack_loader = PackLoader()
   ```

2. **Discovers documents from all packs**

   ```python
   pack_docs = pack_loader.discover_documents()
   ```

3. **Ingests documents into RetrievalAPI**

   ```python
   for doc in pack_docs:
       api.add_document(doc["id"], doc["content"], doc["metadata"])
   ```

4. **Falls back to sample documents** if packs not found
   - Ensures demo works even without packs
   - Provides example data for testing

### 3. HuggingFace Space Deployment

The `.gitlab-ci.yml` handles deployment:

```bash
hf upload-large-folder $SPACE_NAME . --repo-type=space --space-sdk=gradio
```

This uploads:

- All Python source code
- All packs in the `packs/` directory
- Configuration files

**Important**: The `packs/` directory must exist and contain pack data before deployment.

## Pack Loader Details

The `PackLoader` class (`warbler_cda/pack_loader.py`) handles:

### Pack Discovery

- Scans the `packs/` directory
- Identifies pack type (JSONL-based or structured)
- Discovers all documents

### Document Parsing

- **Structured Packs** (core, faction, wisdom): Load from `pack/templates.json`
- **JSONL Packs** (HF NPC dialogue): Parse line-by-line JSONL format

### Metadata Extraction

```python
{
    "pack": "pack-name",
    "type": "template|dialogue",
    "realm_type": "wisdom|faction|narrative",
    "realm_label": "pack-label",
    "lifecycle_stage": "emergence|peak",
    "activity_level": 0.7-0.8
}
```

## Adding New Packs

To add a new pack to the system:

### 1. Create Pack Structure

```bash
packs/
└── warbler-pack-mypack/
    ├── package.json
    ├── pack/
    │   └── templates.json  # OR
    └── mypack.jsonl        # JSONL format
```

### 2. Update Pack Loader (if needed)

If your pack format is different, add handling to `pack_loader.py`:

```python
def _load_pack(self, pack_dir: Path, pack_name: str):
    if "mypack" in pack_name:
        return self._load_my_format(pack_dir, pack_name)
    # ... existing logic
```

### 3. Register in copy_packs.sh

```bash
PACKS=(
    "warbler-pack-core"
    "warbler-pack-mypack"  # Add here
)
```

### 4. Deploy

Run copy script and deploy:

```bash
bash copy_packs.sh
# Commit and push to trigger CI/CD
```

## Document Format

Each loaded document follows this structure:

```python
{
    "id": "pack-name/document-id",
    "content": "Document text content...",
    "metadata": {
        "pack": "pack-name",
        "type": "template|dialogue",
        "realm_type": "wisdom|faction|narrative",
        "realm_label": "label",
        "lifecycle_stage": "emergence|peak|crystallization",
        "activity_level": 0.5-0.8
    }
}
```

## Monitoring

Check pack loading in Space logs:

```log
✓ Loaded 1915 documents from warbler-pack-hf-npc-dialogue
✓ Loaded 6 documents from warbler-pack-wisdom-scrolls
✓ Loaded 15 documents from warbler-pack-faction-politics
✓ Loaded 10 documents from warbler-pack-core
```

Or if packs not found:

```log
⚠️  No Warbler packs found. Using sample documents instead.
```

## Publishing to HuggingFace Hub

Each pack has a dataset card for publication:

- **README_HF_DATASET.md** - HuggingFace dataset card
- Contains metadata, attribution, and usage instructions

Publish to HuggingFace:

```bash
# Create repo on HuggingFace Hub (one per pack)
huggingface-cli repo create warbler-pack-core

# Push pack as dataset
cd packs/warbler-pack-core
huggingface-cli upload . tiny-walnut-games/warbler-pack-core --repo-type dataset
```

## Performance Considerations

### Load Time

- PackLoader loads all packs at startup
- Currently: ~1-2 seconds for all packs
- Packs are cached in memory for query performance

### Storage

- Core pack: ~50KB
- Faction politics pack: ~80KB
- Wisdom scrolls pack: ~60KB
- HF NPC dialogue: ~2MB
- **Total**: ~2.3MB

### Scaling

For larger deployments:

- Lazy-load individual packs on demand
- Implement pack caching layer
- Use database for large pack collections

## Troubleshooting

### Packs not loading

Check that `packs/` directory exists:

```bash
ls -la packs/
```

Verify pack structure:

```bash
ls -la packs/warbler-pack-core/
```

### Sample documents showing instead

If you see "No Warbler packs found", the `packs/` directory is empty. Run:

```bash
bash copy_packs.sh
```

### Pack loader errors

Check logs for parsing errors:

```log
Error loading JSONL pack: ...
Error parsing line 42 in warbler-pack-hf-npc-dialogue.jsonl: ...
```

Fix the source pack and re-run `copy_packs.sh`.

## Related Documentation

- [README.md](./README.md) - Main package documentation
- [DEPLOYMENT.md](./DEPLOYMENT.md) - General deployment guide
- [app.py](./app.py) - Application startup and pack initialization
- [warbler_cda/pack_loader.py](./warbler_cda/pack_loader.py) - Pack loading implementation

## License

All packs use MIT License. See individual pack LICENSE files for details.

Attribution: Warbler CDA - Tiny Walnut Games
