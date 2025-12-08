# Warbler CDA Test Suite

Comprehensive test suite for the Warbler CDA (Cognitive Development Architecture) RAG system with GPU-accelerated embeddings and FractalStat hybrid scoring.

## Test Organization

### Test Files

1. **test_embedding_providers.py** - Embedding provider tests
   - `TestEmbeddingProviderFactory` - Factory pattern tests
   - `TestLocalEmbeddingProvider` - Local TF-IDF provider tests
   - `TestSentenceTransformerProvider` - GPU-accelerated SentenceTransformer provider tests
   - `TestEmbeddingProviderInterface` - Interface contract validation

2. **test_retrieval_api.py** - Retrieval API tests
   - `TestRetrievalAPIContextStore` - Document store operations
   - `TestRetrievalQueryExecution` - Query execution and filtering
   - `TestRetrievalModes` - Different retrieval modes (semantic, temporal, composite)
   - `TestRetrievalHybridScoring` - FractalStat hybrid scoring
   - `TestRetrievalMetrics` - Metrics and caching

3. **test_fractalstat_integration.py** - FractalStat integration tests
   - `TestFractalStatCoordinateComputation` - FractalStat coordinate computation from embeddings
   - `TestFractalStatHybridScoring` - Hybrid semantic + FractalStat scoring
   - `TestFractalStatDocumentEnrichment` - Document enrichment with FractalStat data
   - `TestFractalStatQueryAddressing` - Multi-dimensional query addressing
   - `TestFractalStatDimensions` - FractalStat dimensional space properties

4. **test_rag_e2e.py** - End-to-end RAG integration
   - `TestEndToEndRAG` - Complete RAG pipeline validation
   - 10 comprehensive end-to-end tests covering the full system

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Embedding provider tests
pytest tests/test_embedding_providers.py -v

# Retrieval API tests
pytest tests/test_retrieval_api.py -v

# FractalStat integration tests
pytest tests/test_fractalstat_integration.py -v

# End-to-end tests
pytest tests/test_rag_e2e.py -v -s
```

### Run Tests by Marker

```bash
# Embedding tests
pytest tests/ -m embedding -v

# Retrieval tests
pytest tests/ -m retrieval -v

# FractalStat tests
pytest tests/ -m fractalstat -v

# End-to-end tests
pytest tests/ -m e2e -v -s

# Exclude slow tests
pytest tests/ -m "not slow" -v
```

### Run with Coverage

```bash
pytest tests/ --cov=warbler_cda --cov-report=html -v
```

### Run Specific Test

```bash
pytest tests/test_embedding_providers.py::TestSentenceTransformerProvider::test_semantic_search -v
```

## Test Coverage

The test suite covers:

- ✅ Embedding provider creation and configuration
- ✅ Single text and batch embedding generation
- ✅ Embedding similarity and cosine distance calculations
- ✅ Semantic search across embedding collections
- ✅ Document ingestion into context store
- ✅ Semantic similarity retrieval
- ✅ Temporal sequence retrieval
- ✅ Query result filtering by confidence threshold
- ✅ FractalStat coordinate computation from embeddings
- ✅ FractalStat resonance calculation between documents and queries
- ✅ Hybrid semantic + FractalStat scoring
- ✅ Document enrichment with embeddings and FractalStat data
- ✅ Query result caching and metrics tracking
- ✅ End-to-end RAG pipeline execution

## Dependencies

- **Core**: pytest, warbler-cda
- **Optional**: sentence-transformers (for GPU-accelerated embeddings)

## Expected Test Results

### With SentenceTransformer Installed
All tests pass, including:
- GPU acceleration tests (falls back to CPU if CUDA unavailable)
- FractalStat coordinate computation tests
- Hybrid scoring tests

### Without SentenceTransformer
Tests gracefully skip SentenceTransformer-specific tests and fall back to local TF-IDF provider.

## Writing New Tests

When adding new tests, follow this pattern:

```python
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from warbler_cda import RetrievalAPI, RetrievalQuery, RetrievalMode

class TestMyFeature:
    """Test description."""
    
    def setup_method(self):
        """Setup for each test."""
        self.api = RetrievalAPI()
    
    def test_my_feature(self):
        """Test my feature."""
        # Arrange
        self.api.add_document("doc_1", "test")
        
        # Act
        result = self.api.retrieve_context(query)
        
        # Assert
        assert result is not None
```

## CI/CD Integration

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Warbler CDA Tests
  run: pytest tests/ --cov=warbler_cda --cov-report=xml
```

## Performance Considerations

- Embedding generation tests are fastest with local TF-IDF provider
- SentenceTransformer tests are slower but more accurate
- First SentenceTransformer test loads the model (cache warmup)
- Subsequent tests benefit from model caching

## Troubleshooting

### ImportError: No module named 'sentence_transformers'

Install the optional dependency:
```bash
pip install sentence-transformers
```

### Tests hang on first SentenceTransformer test

The model is being downloaded. This is normal on first run. Progress can be monitored.

### CUDA out of memory errors

The system automatically falls back to CPU. Tests will still pass but run slower.

### Test file not found

Ensure you're running pytest from the warbler-cda-package directory:
```bash
cd warbler-cda-package
pytest tests/ -v
```
