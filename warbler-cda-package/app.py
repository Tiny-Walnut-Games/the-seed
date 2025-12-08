#!/usr/bin/env python3
"""
Gradio interface for Warbler CDA on HuggingFace Spaces.

Provides a web UI for the FractalStat RAG system with GPU acceleration.
"""

import gradio as gr
import time

# Import Warbler CDA components
from warbler_cda.retrieval_api import RetrievalAPI, RetrievalQuery, RetrievalMode
from warbler_cda.embeddings import EmbeddingProviderFactory
from warbler_cda.fractalstat_rag_bridge import FractalStatRAGBridge
from warbler_cda.semantic_anchors import SemanticAnchorGraph
from warbler_cda.pack_loader import PackLoader

# Initialize the system
print("🚀 Initializing Warbler CDA...")

# Create embedding provider (will use sentence-transformers with GPU if available)
embedding_provider = EmbeddingProviderFactory.get_default_provider()
print(f"✅ Embedding provider: {embedding_provider.get_provider_info()['provider_id']}")

# Create semantic anchors (required by RetrievalAPI)
semantic_anchors = SemanticAnchorGraph(embedding_provider=embedding_provider)
print("✅ Semantic anchors initialized")

# Create FractalStat bridge
fractalstat_bridge = FractalStatRAGBridge()
print("✅ FractalStat bridge initialized")

# Create RetrievalAPI with proper components
api = RetrievalAPI(
    semantic_anchors=semantic_anchors,
    embedding_provider=embedding_provider,
    fractalstat_bridge=fractalstat_bridge,
    config={"enable_fractalstat_hybrid": True}
)
print("✅ RetrievalAPI initialized")

# Load packs
print("📚 Loading Warbler packs...")
pack_loader = PackLoader()
documents = pack_loader.discover_documents()

# If no packs found, try to download them
if len(documents) == 0:
    print("⚠️ No packs found locally. Attempting to download from HuggingFace...")
    try:
        from warbler_cda.utils.hf_warbler_ingest import HFWarblerIngestor
        ingestor = HFWarblerIngestor(packs_dir=pack_loader.packs_dir, verbose=True)
        # Download a small demo dataset for deployment
        print("📦 Downloading warbler-pack-hf-prompt-report...")
        success = ingestor.ingest_dataset("prompt-report")
        if success:
            # Reload after download
            documents = pack_loader.discover_documents()
            print(f"✅ Downloaded {len(documents)} documents")
        else:
            print("❌ Failed to download dataset, using sample documents...")
            documents = []
    except Exception as e:
        print(f"⚠️ Could not download packs: {e}")
        print("Using sample documents instead...")
        documents = []

if len(documents) == 0:
    # Fallback to sample documents
    sample_docs = [
        {"id": "sample1", "content": "FractalStat is an 8-dimensional addressing system for intelligent retrieval.", "metadata": {}},
        {"id": "sample2", "content": "Semantic search finds documents by meaning, not just keywords.", "metadata": {}},
        {"id": "sample3", "content": "Bob the Skeptic validates results to prevent bias and hallucinations.", "metadata": {}},
    ]
    for doc in sample_docs:
        api.add_document(doc["id"], doc["content"], doc["metadata"])
    print(f"✅ Loaded {len(sample_docs)} sample documents")
else:
    print(f"✅ Found {len(documents)} documents")
    # Ingest documents
    for doc in documents:
        api.add_document(
            doc_id=doc["id"],
            content=doc["content"],
            metadata=doc.get("metadata", {})
        )

print(f"🎉 Warbler CDA ready with {api.get_context_store_size()} documents!")


def query_warbler(query_text: str, max_results: int = 5, use_hybrid: bool = True) -> str:
    """Query the Warbler CDA system."""
    if not query_text.strip():
        return "Please enter a query."
    
    start_time = time.time()
    
    # Create query
    query = RetrievalQuery(
        query_id=f"gradio_{int(time.time())}",
        mode=RetrievalMode.SEMANTIC_SIMILARITY,
        semantic_query=query_text,
        max_results=max_results,
        fractalstat_hybrid=use_hybrid
    )
    
    # Execute query
    assembly = api.retrieve_context(query)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Format results
    output = f"## Query Results\n\n"
    output += f"**Query:** {query_text}\n\n"
    output += f"**Found:** {len(assembly.results)} results in {elapsed_ms:.0f}ms\n\n"
    output += f"**Quality Score:** {assembly.assembly_quality:.3f}\n\n"
    
    if assembly.results:
        output += "### Top Results\n\n"
        for i, result in enumerate(assembly.results[:max_results], 1):
            output += f"**{i}. Score: {result.relevance_score:.3f}**\n\n"
            output += f"{result.content[:300]}...\n\n"
            if use_hybrid:
                output += f"- Semantic: {result.semantic_similarity:.3f}\n"
                output += f"- FractalStat: {result.fractalstat_resonance:.3f}\n\n"
            output += "---\n\n"
    else:
        output += "No results found.\n"
    
    return output


def get_system_stats() -> str:
    """Get system statistics."""
    metrics = api.get_retrieval_metrics()
    
    output = "## System Statistics\n\n"
    output += f"**Total Documents:** {api.get_context_store_size():,}\n\n"
    output += f"**Total Queries:** {metrics['retrieval_metrics']['total_queries']}\n\n"
    output += f"**Cache Hit Rate:** {metrics['cache_performance']['hit_rate']:.1%}\n\n"
    output += f"**Avg Quality:** {metrics['system_health']['average_quality']:.3f}\n\n"
    
    return output


# Create Gradio interface
with gr.Blocks(title="Warbler CDA - FractalStat RAG") as demo:
    gr.Markdown("""
    # 🦜 Warbler CDA - FractalStat RAG System
    
    Semantic retrieval with 8D FractalStat multi-dimensional addressing.
    
    **Features:**
    - 2.6M+ documents from arXiv, education, fiction, and more
    - Hybrid semantic + FractalStat scoring
    - Bob the Skeptic bias detection
    - Narrative coherence analysis
    """)
    
    with gr.Tab("Query"):
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Query",
                    placeholder="Enter your search query...",
                    lines=2
                )
                max_results = gr.Slider(
                    minimum=1,
                    maximum=20,
                    value=5,
                    step=1,
                    label="Max Results"
                )
                use_hybrid = gr.Checkbox(
                    label="Enable FractalStat Hybrid Scoring",
                    value=True
                )
                query_btn = gr.Button("Search", variant="primary")
            
            with gr.Column():
                results_output = gr.Markdown(label="Results")
        
        query_btn.click(  # pylint: disable=E1101
            fn=query_warbler,
            inputs=[query_input, max_results, use_hybrid],
            outputs=results_output
        )
        
        gr.Examples(
            examples=[
                ["hello world", 5, True],
                ["rotation dynamics of Saturn's moons", 5, True],
                ["anything about machine learning", 10, False],
            ],
            inputs=[query_input, max_results, use_hybrid]
        )
    
    with gr.Tab("System Stats"):
        stats_output = gr.Markdown()
        stats_btn = gr.Button("Refresh Stats")
        stats_btn.click(fn=get_system_stats, outputs=stats_output)  # pylint: disable=E1101
        demo.load(fn=get_system_stats, outputs=stats_output)  # pylint: disable=E1101
    
    with gr.Tab("About"):
        gr.Markdown("""
        ## About Warbler CDA
        
        Warbler CDA is a production-ready RAG system featuring:
        
        - **8D FractalStat Addressing**: Multi-dimensional intelligence for superior retrieval
        - **Semantic Anchors**: Persistent memory with provenance tracking
        - **Bob the Skeptic**: Automatic bias detection and validation
        - **Narrative Coherence**: Quality analysis beyond simple similarity
        
        ### Performance
        
        - 84% test coverage with 587 passing tests
        - 9-28s query response time
        - 0.88 average relevance score
        - 75-83% narrative coherence
        
        ### Links
        
        - [Source Code](https://gitlab.com/tiny-walnut-games/the-seed)
        - [Documentation](https://gitlab.com/tiny-walnut-games/the-seed/-/tree/main/warbler-cda-package)
        - [Performance Report](https://gitlab.com/tiny-walnut-games/the-seed/-/blob/main/warbler-cda-package/WARBLER_CDA_PERFORMANCE_REPORT.md)
        """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
