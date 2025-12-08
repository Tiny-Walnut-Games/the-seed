---
title: Warbler CDA - FractalStat RAG System
emoji: 🦜
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

## Warbler CDA - Cognitive Development Architecture

A production-ready RAG system with **FractalStat 8D multi-dimensional addressing** for intelligent document retrieval.

## 🚀 Quick Start

This Space runs a FastAPI service on port 7860.

### Query the API

```bash
curl -X POST https://YOUR-USERNAME-warbler-cda.hf.space/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "test1",
    "semantic_query": "hello world",
    "max_results": 5
  }'
```

### API Endpoints

- `GET /health` - Health check
- `POST /query` - Semantic query with optional FractalStat hybrid scoring
- `GET /metrics` - System metrics
- `GET /docs` - Interactive API documentation

## 🌟 Features

- **Semantic Retrieval**: Find documents by meaning, not just keywords
- **FractalStat 8D Addressing**: Multi-dimensional intelligence for superior ranking
- **Bob the Skeptic**: Automatic bias detection and validation
- **Narrative Coherence**: Analyzes result quality and threading
- **10k+ Documents**: Pre-indexed arXiv papers, education, fiction, and more

## 📊 Performance

- **Avg Response Time**: 9-28s (depending on query complexity)
- **Avg Relevance**: 0.88
- **Narrative Coherence**: 75-83%
- **Coverage**: 84% test coverage with 587 passing tests

## 🔗 Links

- [Full Documentation](https://gitlab.com/tiny-walnut-games/the-seed/-/tree/main/warbler-cda-package)
- [Source Code](https://gitlab.com/tiny-walnut-games/the-seed)
- [Performance Report](https://gitlab.com/tiny-walnut-games/the-seed/-/blob/main/warbler-cda-package/WARBLER_CDA_PERFORMANCE_REPORT.md)
