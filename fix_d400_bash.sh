#!/bin/bash
cd warbler-cda-package

echo "Fixing D400 issues in warbler-cda-package..."

process_file() {
    local file=$1
    local -a line_nums=("${@:2}")
    
    if [ ! -f "$file" ]; then
        return
    fi
    
    for line_num in "${line_nums[@]}"; do
        sed -i "${line_num}s/\([^.?!:]\)\"\"\"$/\1.\"\"\"/" "$file"
        sed -i "${line_num}s/\([^.?!:]\)'''$/\1.'''/" "$file"
    done
}

# Fix app.py: lines 1, 215, 312, 339
process_file "app.py" 2 216 313 340

# Fix copy_and_transform.py: lines 2, 45, 80
process_file "copy_and_transform.py" 3 46 81

# Fix test_embedding_integration.py: lines 1, 12, 27, 58, 109, 138
process_file "test_embedding_integration.py" 2 13 28 59 110 139

# Fix test_fixes.py: lines 2, 15, 31
process_file "test_fixes.py" 3 16 32

# Fix tests/test_rag_e2e.py, tests/test_retrieval_api.py, tests/test_stat7_integration.py
process_file "tests/test_rag_e2e.py" 2
process_file "tests/test_retrieval_api.py" 2
process_file "tests/test_stat7_integration.py" 2

# Fix verify_pack_ingestion.py: lines 2, 19
process_file "verify_pack_ingestion.py" 3 20

# Fix warbler_cda/__init__.py and other warbler_cda files
process_file "warbler_cda/__init__.py" 2
process_file "warbler_cda/anchor_data_classes.py" 3
process_file "warbler_cda/anchor_memory_pool.py" 3
process_file "warbler_cda/api/__init__.py" 2
process_file "warbler_cda/conflict_detector.py" 2
process_file "warbler_cda/embeddings/__init__.py" 2
process_file "warbler_cda/embeddings/base_provider.py" 2
process_file "warbler_cda/embeddings/factory.py" 2
process_file "warbler_cda/embeddings/local_provider.py" 2
process_file "warbler_cda/embeddings/openai_provider.py" 2
process_file "warbler_cda/embeddings/sentence_transformer_provider.py" 2
process_file "warbler_cda/pack_loader.py" 2
process_file "warbler_cda/pack_sync.py" 2
process_file "warbler_cda/retrieval_api.py" 2
process_file "warbler_cda/semantic_anchors.py" 2
process_file "warbler_cda/stat7_entity.py" 3

echo "Fixing complete!"
