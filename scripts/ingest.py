import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

INDEX_DIR = Path('.ai-index')
DATA_DIR = INDEX_DIR / 'data'
MANIFEST = INDEX_DIR / 'manifest.json'

# Treat these as text even without standard extensions (e.g., .log)
TEXT_LIKE_EXTS = {
    '.cs', '.js', '.ts', '.tsx', '.jsx', '.json', '.yml', '.yaml', '.xml', '.txt', '.md', '.ini', '.cfg', '.toml',
    '.py', '.sh', '.bat', '.ps1', '.csproj', '.sln', '.props', '.targets', '.glsl', '.hlsl', '.cginc', '.razor',
    '.html', '.css', '.scss', '.less', '.csv', '.tsv', '.proto', '.gradle', '.java', '.kt', '.dockerfile',
    '.log'
}

BINARY_EXTS = {
    '.dll', '.exe', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.zip', '.7z', '.rar', '.unitypackage',
    '.asset', '.prefab', '.psd', '.tga', '.dds', '.hdr', '.fbx', '.blend', '.mp3', '.mp4', '.wav', '.ogg',
}

MAX_SIZE = 20 * 1024 * 1024  # 20 MB safety cap
CHUNK_CHARS = 4000
CHUNK_OVERLAP = 400


def is_probably_text(path: Path) -> bool:
    ext = path.suffix.lower()
    if ext in BINARY_EXTS:
        return False
    if ext in TEXT_LIKE_EXTS or ext == '':
        return True
    # Try a heuristic: read a small header and check for NULL bytes
    try:
        with open(path, 'rb') as f:
            head = f.read(4096)
        if b'\x00' in head:
            return False
        return True
    except Exception:
        return False


def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def read_text_safely(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_SIZE:
            return None
        # Try UTF-8, fallback to latin-1 to avoid exceptions (we preserve bytes map)
        with open(path, 'rb') as f:
            data = f.read()
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('latin-1', errors='replace')
    except Exception as e:
        print(f"[ingest] Failed reading {path}: {e}", file=sys.stderr)
        return None


def chunk_text(s: str):
    if len(s) <= CHUNK_CHARS:
        return [s]
    chunks = []
    i = 0
    while i < len(s):
        chunk = s[i:i+CHUNK_CHARS]
        chunks.append(chunk)
        i += CHUNK_CHARS - CHUNK_OVERLAP
    return chunks


def load_manifest():
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_manifest(m):
    INDEX_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding='utf-8')


def normalize_path(p: str) -> str:
    return str(Path(p).resolve())


def process_paths(paths: list[str]):
    manifest = load_manifest()
    updated = 0
    removed = 0

    # Handle deletions for explicitly missing paths
    for p in list(paths):
        ap = Path(p)
        if not ap.exists():
            ap_str = normalize_path(p)
            if ap_str in manifest:
                # remove indexed data files
                old = manifest.pop(ap_str)
                for entry in old.get('chunks', []):
                    try:
                        Path(entry['data_file']).unlink(missing_ok=True)
                    except Exception:
                        pass
                removed += 1

    for p in paths:
        path = Path(p)
        if not path.exists() or not path.is_file():
            continue
        if not is_probably_text(path):
            continue
        text = read_text_safely(path)
        if text is None:
            continue
        b = text.encode('utf-8', errors='ignore')
        h = sha256_bytes(b)
        ap = normalize_path(p)
        prev = manifest.get(ap)
        if prev and prev.get('hash') == h:
            # unchanged
            continue
        # Write chunks to data dir
        chunks = []
        for i, ch in enumerate(chunk_text(text)):
            safe_name = re.sub(r'[^A-Za-z0-9_.-]+', '_', path.name)
            data_file = DATA_DIR / f"{h[:16]}_{i:04d}_{safe_name}.txt"
            data_file.write_text(ch, encoding='utf-8', errors='ignore')
            chunks.append({
                'index': i,
                'data_file': str(data_file.resolve()),
                'length': len(ch)
            })
        manifest[ap] = {
            'path': ap,
            'hash': h,
            'size': path.stat().st_size,
            'mtime': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            'chunks': chunks,
        }
        updated += 1

    save_manifest(manifest)
    print(f"[ingest] updated={updated} removed={removed} total_indexed={len(manifest)}")


def main():
    ap = argparse.ArgumentParser(description='Minimal local AI index ingester')
    ap.add_argument('--paths', nargs='+', help='Paths to upsert/delete in the index', required=True)
    args = ap.parse_args()

    process_paths(args.paths)


if __name__ == '__main__':
    main()
