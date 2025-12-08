# Dataset Migration Guide: Removing Contaminated Data

## 🚨 Critical Issue

The `amaydle/npc-dialogue` dataset has been **REMOVED** from this project due to:
- **No license** specified
- **References to copyrighted material**
- **Legal risk** to the project

## ✅ New MIT-Licensed Datasets

We've replaced the contaminated dataset with 6 high-quality MIT-licensed alternatives:

### 1. **nick007x/arxiv-papers** (2.55M papers)
- Massive scholarly corpus
- Perfect for testing Warbler's retrieval depth
- Technical domain coverage

### 2. **PromptSystematicReview/ThePromptReport** (83 docs)
- Focused on prompt engineering
- Great for AI-related discourse
- Systematic review methodology

### 3. **GOAT-AI/generated-novels** (20 novels)
- Long-form narrative structure
- Stress-tests creative/literary retrieval
- Character and plot development

### 4. **Solshine/Portuguese_Language_Education_Texts** (21 docs)
- Educational content in Portuguese
- Multilingual retrieval testing
- Cross-language capabilities

### 5. **nlasso/anac-manuals-23** (52 manuals)
- Technical procedural documentation
- "Find the right section" retrieval
- Structured content

### 6. **AST-FRI/EnterpriseBench** (283 entries)
- Enterprise-style benchmarks
- Business/organizational scenarios
- Real-world document types

## 🔄 Migration Steps

### Step 1: Remove Old Packs

```bash
# Remove any packs created from contaminated data
rm -rf packs/warbler-pack-*npc-dialogue*
rm -rf packs/warbler-pack-hf-npc-dialogue
```

### Step 2: Ingest New Datasets

```bash
# Start small - validate pipeline
python packages/com.twg.the-seed/seed/engine/hf_warbler_ingest.py ingest -d prompt-report
python packages/com.twg.the-seed/seed/engine/hf_warbler_ingest.py ingest -d manuals

# Scale up - add volume
python packages/com.twg.the-seed/seed/engine/hf_warbler_ingest.py ingest -d arxiv --arxiv-limit 10000

# Diversify - narrative and multilingual
python packages/com.twg.the-seed/seed/engine/hf_warbler_ingest.py ingest -d novels
python packages/com.twg.the-seed/seed/engine/hf_warbler_ingest.py ingest -d portuguese-edu

# Benchmark - enterprise content
python packages/com.twg.the-seed/seed/engine/hf_warbler_ingest.py ingest -d enterprise

# Or ingest all at once
python packages/com.twg.the-seed/seed/engine/hf_warbler_ingest.py ingest -d all --arxiv-limit 50000
```

### Step 3: Verify Ingestion

```bash
# Check what's available
python packages/com.twg.the-seed/seed/engine/hf_warbler_ingest.py list-available

# Verify packs were created
ls -lh packs/warbler-pack-*

# Check pack metadata
cat packs/warbler-pack-hf-arxiv/package.json
```

### Step 4: Update Warbler Configuration

Update any Warbler configuration files to point to the new packs:

```python
# Old (REMOVE)
pack_paths = ["packs/warbler-pack-npc-dialogue"]

# New (USE THESE)
pack_paths = [
    "packs/warbler-pack-hf-arxiv",
    "packs/warbler-pack-hf-prompt-report",
    "packs/warbler-pack-hf-manuals",
    "packs/warbler-pack-hf-novels",
    "packs/warbler-pack-hf-enterprise",
    "packs/warbler-pack-hf-portuguese-edu"
]
```

## 📊 Recommended Ingestion Strategy

Based on the issue description:

1. **Start small**: Load `prompt-report` or `manuals` to validate pipeline
2. **Scale up**: Add `arxiv` for volume stress-tests (start with 10K, increase as needed)
3. **Diversify**: Mix in `novels` for narrative retrieval and `portuguese-edu` for multilingual
4. **Benchmark**: Use `enterprise` to measure retrieval accuracy in structured domains

## 🎯 Expected Outcomes

### Before (Contaminated)
- ❌ 1,915 unlicensed NPC dialogue entries
- ❌ Legal risk from copyrighted material
- ❌ Limited domain coverage

### After (Clean)
- ✅ 2.55M+ MIT-licensed documents available
- ✅ Zero legal risk
- ✅ Diverse domains: scholarly, technical, narrative, business, multilingual
- ✅ Better stress-testing capabilities
- ✅ More realistic retrieval scenarios

## 🔍 Verification Checklist

- [ ] Old `amaydle/npc-dialogue` references removed from code
- [ ] Old packs deleted from `packs/` directory
- [ ] New MIT-licensed datasets ingested
- [ ] Pack metadata shows "license": "MIT"
- [ ] Warbler configuration updated
- [ ] Tests pass with new data sources
- [ ] Documentation updated

## 📝 Notes

- All new datasets are **MIT-licensed** - safe for commercial use
- arXiv dataset is massive (2.55M) - use `--arxiv-limit` to control size
- Novels are chunked automatically for better retrieval
- Portuguese texts enable multilingual testing
- Enterprise and manuals provide structured, real-world content

## 🆘 Troubleshooting

### Dataset Download Issues

```bash
# If HuggingFace downloads fail, try:
export HF_DATASETS_CACHE="/path/to/large/disk"
pip install --upgrade datasets transformers
```

### Memory Issues with Large Datasets

```bash
# Use streaming for very large datasets
# Or limit the number of documents:
python ... ingest -d arxiv --arxiv-limit 1000
```

### Pack Creation Errors

```bash
# Ensure packs directory exists
mkdir -p packs

# Check permissions
chmod -R u+w packs/
```

## 📚 Additional Resources

- [HuggingFace Datasets Documentation](https://huggingface.co/docs/datasets)
- [MIT License Details](https://opensource.org/licenses/MIT)
- [Warbler Pack Format Specification](./HF-WARBLER-INGESTION-GUIDE.md)
