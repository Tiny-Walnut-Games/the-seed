---
title: Warbler CDA FractalStat RAG
emoji: 🦜
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
short_description: RAG system with 8D FractalStat and 2.6M+ documents
tags:
  - rag
  - semantic-search
  - retrieval
  - fastapi
  - fractalstat
---

# Warbler CDA - Cognitive Development Architecture RAG System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://docker.com)

A **production-ready RAG (Retrieval-Augmented Generation) system** with **FractalStat multi-dimensional addressing** for intelligent document retrieval, semantic memory, and automatic data ingestion.

## 🌟 Features

### Core RAG System

- **Semantic Anchors**: Persistent memory with provenance tracking
- **Hierarchical Summarization**: Micro/macro distillation for efficient compression
- **Conflict Detection**: Automatic detection and resolution of contradictory information
- **Memory Pooling**: Performance-optimized object pooling for high-throughput scenarios

### FractalStat Multi-Dimensional Addressing

- **8-Dimensional Coordinates**: Realm, Lineage, Adjacency, Horizon, Luminosity, Polarity, Dimensionality, Alignment
- **Hybrid Scoring**: Combines semantic similarity with FractalStat resonance for superior retrieval
- **Entanglement Detection**: Identifies relationships across dimensional space
- **Validated System**: Comprehensive experiments (EXP-01 through EXP-10) validate uniqueness, efficiency, and narrative preservation

### Production-Ready API

- **FastAPI Service**: High-performance async API with concurrent query support
- **CLI Tools**: Command-line interface for queries, ingestion, and management
- **HuggingFace Integration**: Direct ingestion from HF datasets
- **Docker Support**: Containerized deployment ready

## 📚 Data Sources

The Warbler system is trained on carefully curated, MIT-licensed datasets from HuggingFace:

### Primary Datasets

- **arXiv Papers** (`nick007x/arxiv-papers`) - 2.5M+ scholarly papers covering scientific domains
- **Prompt Engineering Report** (`PromptSystematicReview/ThePromptReport`) - 83 comprehensive prompt documentation entries
- **Generated Novels** (`GOAT-AI/generated-novels`) - 20 narrative-rich novels for storytelling patterns
- **Technical Manuals** (`nlasso/anac-manuals-23`) - 52 procedural and operational documents
- **ChatEnv Enterprise** (`SustcZhangYX/ChatEnv`) - 112K+ software development conversations
- **Portuguese Education** (`Solshine/Portuguese_Language_Education_Texts`) - 21 multilingual educational texts
- **Educational Stories** (`MU-NLPC/Edustories-en`) - 1.5K+ case studies and learning narratives

### Original Warbler Packs

- `warbler-pack-core` - Core narrative and reasoning patterns
- `warbler-pack-wisdom-scrolls` - Philosophical and wisdom-based content
- `warbler-pack-faction-politics` - Political and faction dynamics

All datasets are provided under MIT or compatible licenses. For complete attribution, see the HuggingFace Hub pages listed above.

## 📦 Installation

### From Source (Current Method)

```bash
git clone https://github.com/tiny-walnut-games/the-seed.git
cd the-seed/warbler-cda-package
pip install -e .
```

### Optional Dependencies

```bash
# OpenAI embeddings integration
pip install openai

# Development tools
pip install pytest pytest-cov
```

## 🚀 Quick Start

### Option 1: Direct Python (Easiest)

```bash
cd warbler-cda-package

# Start the API with automatic pack loading
./run_api.ps1

# Or on Linux/Mac:
python start_server.py
```

The API automatically loads all Warbler packs on startup and serves them at **http://localhost:8000**

### Option 2: Docker Compose

```bash
cd warbler-cda-package
docker-compose up --build
```

### Option 3: Kubernetes

```bash
cd warbler-cda-package/k8s
./demo-docker-k8s.sh  # Full auto-deploy
```

## 📡 API Usage Examples

### Using the REST API

```bash
# Start the API first: ./run_api.ps1
# Then test with:

# Health check
curl http://localhost:8000/health

# Query the system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "test1",
    "semantic_query": "hello world",
    "max_results": 5
  }'

# Get metrics
curl http://localhost:8000/metrics
```

### Using Python Programmatically

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(f"API Status: {response.json()['status']}")

# Query
query_data = {
    "query_id": "python_test",
    "semantic_query": "rotation dynamics of Saturn's moons",
    "max_results": 5,
    "fractalstat_hybrid": True
}

results = requests.post("http://localhost:8000/query", json=query_data).json()
print(f"Found {len(results['results'])} results")

# Show top result
if results['results']:
    top_result = results['results'][0]
    print(f"Top score: {top_result['relevance_score']:.3f}")
    print(f"Content: {top_result['content'][:100]}...")
```

### FractalStat Hybrid Scoring

```python
from warbler_cda import FractalStatRAGBridge

# Enable FractalStat hybrid scoring
fractalstat_bridge = FractalStatRAGBridge()
api = RetrievalAPI(
    semantic_anchors=semantic_anchors,
    embedding_provider=embedding_provider,
    fractalstat_bridge=fractalstat_bridge,
    config={"enable_fractalstat_hybrid": True}
)

# Query with hybrid scoring
from warbler_cda import RetrievalQuery, RetrievalMode

query = RetrievalQuery(
    query_id="hybrid_query_1",
    mode=RetrievalMode.SEMANTIC_SIMILARITY,
    semantic_query="Find wisdom about resilience",
    fractalstat_hybrid=True,
    weight_semantic=0.6,
    weight_fractalstat=0.4
)

assembly = api.retrieve_context(query)
print(f"Found {len(assembly.results)} results with quality {assembly.assembly_quality:.3f}")
```

### Running the API Service

```bash
# Start the FastAPI service
uvicorn warbler_cda.api.service:app --host 0.0.0.0 --port 8000

# Or use the CLI
warbler-api --port 8000
```

### Using the CLI

```bash
# Query the API
warbler-cli query --query-id q1 --semantic "wisdom about courage" --max-results 10

# Enable hybrid scoring
warbler-cli query --query-id q2 --semantic "narrative patterns" --hybrid

# Bulk concurrent queries
warbler-cli bulk --num-queries 10 --concurrency 5 --hybrid

# Check metrics
warbler-cli metrics
```

## 📊 FractalStat Experiments

The system includes validated experiments demonstrating:

- **EXP-01**: Address uniqueness (0% collision rate across 10K+ entities)
- **EXP-02**: Retrieval efficiency (sub-millisecond at 100K scale)
- **EXP-03**: Dimension necessity (all 7 dimensions required)
- **EXP-10**: Narrative preservation under concurrent load

```python
from warbler_cda import run_all_experiments

# Run validation experiments
results = run_all_experiments(
    exp01_samples=1000,
    exp01_iterations=10,
    exp02_queries=1000,
    exp03_samples=1000
)

print(f"EXP-01 Success: {results['EXP-01']['success']}")
print(f"EXP-02 Success: {results['EXP-02']['success']}")
print(f"EXP-03 Success: {results['EXP-03']['success']}")
```

## 🎯 Use Cases

### 1. Intelligent Document Retrieval

```python
# Add documents from various sources
for doc in documents:
    api.add_document(
        doc_id=doc["id"],
        content=doc["text"],
        metadata={
            "realm_type": "knowledge",
            "realm_label": "technical_docs",
            "lifecycle_stage": "emergence"
        }
    )

# Retrieve with context awareness
results = api.query_semantic_anchors("How to optimize performance?")
```

### 2. Narrative Coherence Analysis

```python
from warbler_cda import ConflictDetector

conflict_detector = ConflictDetector(embedding_provider=embedding_provider)

# Process statements
statements = [
    {"id": "s1", "text": "The system is fast"},
    {"id": "s2", "text": "The system is slow"}
]

report = conflict_detector.process_statements(statements)
print(f"Conflicts detected: {report['conflict_summary']}")
```

### 3. HuggingFace Dataset Ingestion

```python
from warbler_cda.utils import HFWarblerIngestor

ingestor = HFWarblerIngestor()

# Transform HF dataset to Warbler format
docs = ingestor.transform_npc_dialogue("amaydle/npc-dialogue")

# Create pack
pack_path = ingestor.create_warbler_pack(docs, "warbler-pack-npc-dialogue")
```

## 🏗️ Architecture

```none
warbler_cda/
├── retrieval_api.py          # Main RAG API
├── semantic_anchors.py        # Semantic memory system
├── anchor_data_classes.py     # Core data structures
├── anchor_memory_pool.py      # Performance optimization
├── summarization_ladder.py    # Hierarchical compression
├── conflict_detector.py       # Conflict detection
├── castle_graph.py            # Concept extraction
├── melt_layer.py              # Memory consolidation
├── evaporation.py             # Content distillation
├── fractalstat_rag_bridge.py        # FractalStat hybrid scoring
├── fractalstat_entity.py            # FractalStat entity system
├── fractalstat_experiments.py       # Validation experiments
├── embeddings/                # Embedding providers
│   ├── base_provider.py
│   ├── local_provider.py
│   ├── openai_provider.py
│   └── factory.py
├── api/                       # Production API
│   ├── service.py             # FastAPI service
│   └── cli.py                 # CLI interface
└── utils/                     # Utilities
    ├── load_warbler_packs.py
    └── hf_warbler_ingest.py
```

## 🔬 Technical Details

### FractalStat Dimensions

1. **Realm**: Domain classification (type + label)
2. **Lineage**: Generation/version number
3. **Adjacency**: Graph connectivity (0.0-1.0)
4. **Horizon**: Lifecycle stage (logline, outline, scene, panel)
5. **Luminosity**: Clarity/activity level (0.0-1.0)
6. **Polarity**: Resonance/tension (0.0-1.0)
7. **Dimensionality**: Complexity/thread count (1-7)

### Hybrid Scoring Formula

```math
hybrid_score = (weight_semantic × semantic_similarity) + (weight_fractalstat × fractalstat_resonance)
```

Where:

- `semantic_similarity`: Cosine similarity of embeddings
- `fractalstat_resonance`: Multi-dimensional alignment score
- Default weights: 60% semantic, 40% FractalStat

## 📚 Documentation

- [API Reference](docs/api.md)
- [FractalStat Guide](docs/fractalstat.md)
- [Experiments](docs/experiments.md)
- [Deployment](docs/deployment.md)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built on research from The Seed project
- FractalStat addressing system inspired by multi-dimensional data structures
- Semantic anchoring based on cognitive architecture principles

## 📞 Contact

- **Project**: [The Seed](https://github.com/tiny-walnut-games/the-seed)
- **Issues**: [GitHub Issues](https://github.com/tiny-walnut-games/the-seed/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tiny-walnut-games/the-seed/discussions)

---

### **Made with ❤️ by Tiny Walnut Games**
