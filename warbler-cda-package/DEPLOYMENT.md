# Warbler CDA HuggingFace Deployment

This directory contains the Warbler CDA package prepared for HuggingFace deployment.

## Quick Start

### Local Testing

```bash
cd warbler-cda-package

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Run Gradio demo
python app.py
```

### Deploy to HuggingFace Space

#### Option 1: Manual Deployment

```bash
# Install HuggingFace CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Upload to Space
huggingface-cli upload YOUR_USERNAME/warbler-cda . --repo-type=space
```

#### Option 2: GitLab CI/CD (Automated)

1. Set up HuggingFace token in GitLab CI/CD variables:
   - Go to Settings > CI/CD > Variables
   - Add variable `HF_TOKEN` with your HuggingFace token
   - Add variable `HF_SPACE_NAME` with your Space name (e.g., `username/warbler-cda`)

2. Push to main branch or create a tag:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. The pipeline will automatically sync to HuggingFace!

## Package Structure

```none
warbler-cda-package/
├── warbler_cda/              # Main package
│   ├── __init__.py
│   ├── retrieval_api.py      # Core RAG API
│   ├── semantic_anchors.py   # Semantic memory
│   ├── fractalstat_rag_bridge.py   # FractalStat hybrid scoring
│   ├── embeddings/           # Embedding providers
│   ├── api/                  # FastAPI service
│   └── utils/                # Utilities
├── app.py                    # Gradio demo for HF Space
├── requirements.txt          # Dependencies
├── pyproject.toml            # Package metadata
├── README.md                 # Documentation
└── LICENSE                   # MIT License
```

## Features

- **Semantic Search**: Natural language document retrieval
- **FractalStat Addressing**: 7-dimensional multi-modal scoring
- **Hybrid Scoring**: Combines semantic + FractalStat for superior results
- **Production API**: FastAPI service with concurrent query support
- **CLI Tools**: Command-line interface for management
- **HF Integration**: Direct dataset ingestion

## Testing

```bash
# Run tests
pytest

# Run specific experiments
python -m warbler_cda.fractalstat_experiments
```

## Documentation

See [README.md](README.md) for full documentation.

## Support

- **Issues**: <https://gitlab.com/tiny-walnut-games/the-seed/-/issues>
- **Discussions**: <https://gitlab.com/tiny-walnut-games/the-seed/-/merge_requests>
