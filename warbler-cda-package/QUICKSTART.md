# Warbler CDA - Quick Start Guide

## 🚀 Quick Start (3 options)

### 📝 Home may not be available on path immediately

```bash
# set home path for environment
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
# start the terminal
source ~/.bashrc
```

### Option 1: Local Python (Recommended for Development)

```bash
cd warbler-cda-package
./setup.sh
python app.py
```

Open <http://localhost:7860>

### Option 2: Docker

```bash
cd warbler-cda-package
docker-compose up warbler-cda-demo
```

Open <http://localhost:7860>

### Option 3: HuggingFace Space (Recommended for Sharing)

1. Create a HuggingFace Space at <https://huggingface.co/new-space>
2. Choose "Gradio" as SDK
3. Upload the `warbler-cda-package/` contents
4. Your Space will be live at `https://huggingface.co/spaces/YOUR_USERNAME/warbler-cda`

## 📚 Usage Examples

### Example 1: Basic Query

```python
from warbler_cda import RetrievalAPI, EmbeddingProviderFactory

# Initialize
embedding_provider = EmbeddingProviderFactory.get_default_provider()
api = RetrievalAPI(embedding_provider=embedding_provider)

# Add document
api.add_document(
    doc_id="wisdom_1",
    content="Courage is not the absence of fear, but acting despite it.",
    metadata={"realm_type": "wisdom", "realm_label": "virtue"}
)

# Query
results = api.query_semantic_anchors("What is courage?", max_results=5)
for result in results:
    print(f"{result.relevance_score:.3f} - {result.content}")
```

### Example 2: FractalStat Hybrid Scoring

```python
from warbler_cda import FractalStatRAGBridge, RetrievalQuery, RetrievalMode

# Enable FractalStat
fractalstat_bridge = FractalStatRAGBridge()
api = RetrievalAPI(
    embedding_provider=embedding_provider,
    fractalstat_bridge=fractalstat_bridge,
    config={"enable_fractalstat_hybrid": True}
)

# Query with hybrid scoring
query = RetrievalQuery(
    query_id="hybrid_1",
    mode=RetrievalMode.SEMANTIC_SIMILARITY,
    semantic_query="wisdom about resilience",
    fractalstat_hybrid=True,
    weight_semantic=0.6,
    weight_fractalstat=0.4
)

assembly = api.retrieve_context(query)
print(f"Quality: {assembly.assembly_quality:.3f}")
print(f"Results: {len(assembly.results)}")
```

### Example 3: API Service

```bash
# Start the API
uvicorn warbler_cda.api.service:app --host 0.0.0.0 --port 8000

# In another terminal, use the CLI
warbler-cli query --query-id q1 --semantic "wisdom about courage" --hybrid

# Or use curl
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "test1",
    "semantic_query": "wisdom about courage",
    "fractalstat_hybrid": true
  }'
```

## 🔧 Configuration

### Embedding Providers

```python
# Local TF-IDF (default, no API key needed)
from warbler_cda import EmbeddingProviderFactory
provider = EmbeddingProviderFactory.create_provider("local")

# OpenAI (requires API key)
provider = EmbeddingProviderFactory.create_provider(
    "openai",
    config={"api_key": "your-api-key", "model": "text-embedding-ada-002"}
)
```

### FractalStat Configuration

```python
# Custom FractalStat weights
api = RetrievalAPI(
    fractalstat_bridge=fractalstat_bridge,
    config={
        "enable_fractalstat_hybrid": True,
        "default_weight_semantic": 0.7,  # 70% semantic
        "default_weight_fractalstat": 0.3       # 30% FractalStat
    }
)
```

## 📊 Running Experiments

```python
from warbler_cda import run_all_experiments

# Run FractalStat validation experiments
results = run_all_experiments(
    exp01_samples=1000,
    exp01_iterations=10,
    exp02_queries=1000,
    exp03_samples=1000
)

print(f"EXP-01 (Uniqueness): {results['EXP-01']['success']}")
print(f"EXP-02 (Efficiency): {results['EXP-02']['success']}")
print(f"EXP-03 (Necessity): {results['EXP-03']['success']}")
```

## 🐛 Troubleshooting

### Import Errors

If you see import errors, make sure the package is installed:

```bash
pip install -e .
```

### Missing Dependencies

Install all dependencies:

```bash
pip install -r requirements.txt
```

### Gradio Not Starting

Check if port 7860 is available:

```bash
lsof -i :7860  # Linux/Mac
netstat -ano | findstr :7860  # Windows
```

## 📖 More Information

- Full documentation: [README.md](README.md)
- Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Package manifest: [PACKAGE_MANIFEST.md](PACKAGE_MANIFEST.md)
