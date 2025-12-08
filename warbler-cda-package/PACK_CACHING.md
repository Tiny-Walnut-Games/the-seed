# Warbler Pack Caching Strategy

## Overview

The app now implements intelligent pack caching to avoid unnecessary re-ingestion of large datasets. This minimizes GitLab storage requirements and allows fast session startup.

## How It Works

### First Run (Session Start)

1. **PackManager** initializes and checks for cached metadata
2. **Health check** verifies if documents are already in the context store
3. **Ingestion** occurs only if:
   - No cache metadata exists
   - Pack count changed
   - Health check fails (documents missing)
4. **Cache** is saved with timestamp and document count

### Subsequent Runs

- Reuses cached documents without re-ingestion
- Quick health check ensures documents are still valid
- Fallback to sample docs if packs unavailable

## Environment Variables

Control pack ingestion behavior with these variables:

### `WARBLER_INGEST_PACKS` (default: `true`)

Enable/disable automatic pack ingestion.

```bash
export WARBLER_INGEST_PACKS=false
```

### `WARBLER_SAMPLE_ONLY` (default: `false`)

Load only sample documents (for CI/CD verification).

```bash
export WARBLER_SAMPLE_ONLY=true
```

Best for:

- PyPI package CI/CD pipelines
- Quick verification that ingestion works
- Minimal startup time in restricted environments

### `WARBLER_SKIP_PACK_CACHE` (default: `false`)

Force reingest even if cache exists.

```bash
export WARBLER_SKIP_PACK_CACHE=true
```

Best for:

- Testing pack ingestion pipeline
- Updating stale cache
- Debugging

## Cache Location

Default cache stored at:

```path
~/.warbler_cda/cache/pack_metadata.json
```

Metadata includes:

```json
{
  "ingested_at": 1699564800,
  "pack_count": 7,
  "doc_count": 12345,
  "status": "healthy"
}
```

## CI/CD Optimization

### For GitLab CI (Minimal PyPI Package)

```yaml
test:
  script:
    - export WARBLER_SAMPLE_ONLY=true
    - pip install .
    - python -m pytest tests/
```

Benefits:

- ✅ No large pack files in repository
- ✅ Fast CI runs (5 samples vs 2.5M docs)
- ✅ Verifies ingestion code works
- ✅ Full packs load on first user session

### For Local Development

Keep full packs in working directory:

```bash
cd warbler-cda-package
python -m warbler_cda.utils.hf_warbler_ingest ingest -d all
python app.py
```

First run ingests all packs. Subsequent runs use cache.

### For Gradio Space/Cloud Deployment

Set environment at deployment:

```bash
WARBLER_INGEST_PACKS=true
```

Packs ingest once per session, then cached in instance memory.

## Files Affected

- `app.py` - Main Gradio app with PackManager
- `warbler_cda/utils/load_warbler_packs.py` - Pack discovery (already handles caching)
- No changes needed to pack ingestion scripts

## Performance Impact

### Memory

- **With packs**: ~500MB (2.5M arxiv docs + others)
- **With samples**: ~1MB (5 test documents)

### Startup Time

- **First run**: ~30-60 seconds (ingest packs)
- **Cached run**: ~2-5 seconds (health check only)
- **Sample only**: <1 second

## Troubleshooting

### Packs not loading?

1. Check `WARBLER_INGEST_PACKS=true` (default)
2. Verify packs exist: `ls -la packs/`
3. Force reingest: `export WARBLER_SKIP_PACK_CACHE=true`

### Cache corrupted?

```bash
rm -rf ~/.warbler_cda/cache/pack_metadata.json
```

Will reingest on next run.

### Need sample docs only?

```bash
export WARBLER_SAMPLE_ONLY=true
python app.py
```

## Future Improvements

- [ ] Detect pack updates via file hash instead of just count
- [ ] Selective pack loading (choose which datasets to cache)
- [ ] Metrics dashboard showing cache hit/miss rates
- [ ] Automatic cache expiration after N days
