#!/usr/bin/env python3
"""
Ingest Warbler pack documents into EXP-09 API for testing
"""
import json
import requests
import time
from pathlib import Path

API_URL = 'http://localhost:8000'
PACKS_DIR = Path(__file__).parent.parent.parent / 'packs'

# Wait for API to be ready
time.sleep(2)

# Find all Warbler pack files
documents = []
for pack_dir in PACKS_DIR.iterdir():
    if pack_dir.is_dir() and 'warbler' in pack_dir.name:
        for file in pack_dir.rglob('*'):
            if file.is_file() and file.suffix in ['.json', '.md', '.yml', '.yaml', '.ts']:
                try:
                    doc_id = f"{pack_dir.name}/{file.relative_to(pack_dir)}"
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    documents.append({
                        'content_id': doc_id,
                        'content': content,
                        'metadata': {'pack': pack_dir.name, 'source_file': file.name}
                    })
                except Exception as e:
                    print(f"Error reading {file}: {e}")

# Ingest in batches
ingested = 0
for doc in documents:
    try:
        resp = requests.post(f'{API_URL}/ingest', json={'documents': [doc]})
        if resp.status_code == 200:
            print(f'OK {doc["content_id"]}')
            ingested += 1
        else:
            print(f'ERROR {doc["content_id"]}: {resp.status_code}')
    except Exception as e:
        print(f'ERROR {doc["content_id"]}: {e}')

print(f'\nTotal ingested: {ingested}/{len(documents)} documents')