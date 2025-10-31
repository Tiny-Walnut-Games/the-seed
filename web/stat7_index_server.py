#!/usr/bin/env python3
"""
STAT7 Project Index Web Server
Flask API server for project index visualization.

Provides REST API endpoints for:
- Project statistics
- File search
- File details
- Real-time updates via WebSocket
"""

import sys
from pathlib import Path
import json
import asyncio
import threading
import time

# Try to import Flask dependencies
try:
    from flask import Flask, jsonify, request, render_template_string
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    Flask = None
    jsonify = None
    request = None
    render_template_string = None
    CORS = None
    FLASK_AVAILABLE = False

# Add seed engine to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

try:
    from stat7_file_index import STAT7FileIndex
    from stat7_file_watcher import STAT7LivingIndex
    STAT7_AVAILABLE = True
except ImportError:
    STAT7FileIndex = None
    STAT7LivingIndex = None
    STAT7_AVAILABLE = False


app = Flask(__name__)
CORS(app)

# Global living index instance
living_index = None
index_lock = threading.Lock()


def get_living_index():
    """Get or create living index instance"""
    global living_index
    with index_lock:
        if living_index is None:
            project_root = Path(__file__).parent.parent
            living_index = STAT7LivingIndex(project_root, watch=True)
            # Initial scan
            living_index.force_reindex()
        return living_index


@app.route('/')
def index():
    """Serve the main visualization page"""
    with open('stat7_project_index.html', 'r') as f:
        return f.read()


@app.route('/api/project/stats')
def project_stats():
    """Get project statistics"""
    try:
        index = get_living_index().get_index()
        stats = index.get_project_statistics()

        # Calculate additional statistics
        files_with_intent = sum(1 for f in index.file_entities.values()
                              if f.intent and f.intent.primary_intent)

        avg_complexity = sum(f.intent.complexity_score for f in index.file_entities.values()) / max(len(index.file_entities), 1)

        stats['files_with_intent'] = files_with_intent
        stats['avg_complexity'] = avg_complexity

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/files')
def list_files():
    """Get all files with basic info"""
    try:
        index = get_living_index().get_index()
        files = []

        for entity in index.file_entities.values():
            files.append({
                'entity_id': entity.entity_id,
                'file_path': str(entity.file_path.relative_to(index.project_root)),
                'file_category': entity.file_category.value,
                'stat7': entity.stat7.to_dict(),
                'intent': {
                    'primary_intent': entity.intent.primary_intent,
                    'purpose': entity.intent.purpose,
                    'complexity_score': entity.intent.complexity_score
                },
                'metrics': {
                    'line_count': entity.metrics.line_count,
                    'function_count': entity.metrics.function_count,
                    'class_count': entity.metrics.class_count
                },
                'imports_files': entity.imports_files,
                'imported_by_files': entity.imported_by_files
            })

        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search')
def search_files():
    """Search files by intent or content"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400

        index = get_living_index().get_index()
        results = index.search_by_intent(query)

        search_results = []
        for entity in results:
            search_results.append({
                'entity_id': entity.entity_id,
                'file_path': str(entity.file_path.relative_to(index.project_root)),
                'file_category': entity.file_category.value,
                'stat7': entity.stat7.to_dict(),
                'intent': {
                    'primary_intent': entity.intent.primary_intent,
                    'purpose': entity.intent.purpose,
                    'complexity_score': entity.intent.complexity_score
                },
                'metrics': {
                    'line_count': entity.metrics.line_count,
                    'function_count': entity.metrics.function_count
                },
                'relevance_score': entity.stat7.luminosity  # Use luminosity as relevance
            })

        return jsonify({'results': search_results, 'query': query, 'count': len(search_results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/<path:file_path>')
def get_file_details(file_path):
    """Get detailed information about a specific file"""
    try:
        index = get_living_index().get_index()
        entity = index.get_file_entity(file_path)

        if not entity:
            return jsonify({'error': 'File not found'}), 404

        return jsonify(entity.get_file_summary())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stat7/realms')
def get_stat7_realms():
    """Get available STAT7 realms with file counts"""
    try:
        index = get_living_index().get_index()
        realm_counts = {}

        for entity in index.file_entities.values():
            realm = entity.stat7.realm.value
            realm_counts[realm] = realm_counts.get(realm, 0) + 1

        return jsonify(realm_counts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stat7/horizons')
def get_stat7_horizons():
    """Get available STAT7 horizons with file counts"""
    try:
        index = get_living_index().get_index()
        horizon_counts = {}

        for entity in index.file_entities.values():
            horizon = entity.stat7.horizon.value
            horizon_counts[horizon] = horizon_counts.get(horizon, 0) + 1

        return jsonify(horizon_counts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/relationships')
def get_file_relationships():
    """Get file relationship graph data"""
    try:
        index = get_living_index().get_index()
        nodes = []
        edges = []

        # Create nodes
        for entity in index.file_entities.values():
            nodes.append({
                'id': entity.entity_id,
                'label': entity.file_path.name,
                'path': str(entity.file_path.relative_to(index.project_root)),
                'category': entity.file_category.value,
                'realm': entity.stat7.realm.value,
                'complexity': entity.intent.complexity_score,
                'size': max(5, min(30, entity.metrics.line_count / 10))  # Node size based on lines
            })

        # Create edges (relationships)
        for entity in index.file_entities.values():
            for imported_file in entity.imports_files:
                if imported_file in index.path_to_entity_id:
                    target_id = index.path_to_entity_id[imported_file]
                    edges.append({
                        'from': entity.entity_id,
                        'to': target_id,
                        'type': 'imports'
                    })

        return jsonify({'nodes': nodes, 'edges': edges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Trigger a project reindex"""
    try:
        force = request.json.get('force', False) if request.is_json else False
        index = get_living_index().get_index()
        results = index.scan_project(force_reindex=force)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def get_server_status():
    """Get server and index status"""
    try:
        li = get_living_index()
        status = li.get_status()
        status['server_time'] = time.time()
        status['api_version'] = '1.0.0'
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Main entry point"""
    import argparse

    if not FLASK_AVAILABLE:
        print("❌ Flask is required. Install with: pip install flask flask-cors")
        sys.exit(1)

    if not STAT7_AVAILABLE:
        print("❌ STAT7 modules not found. Make sure you're running from the project root.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='STAT7 Project Index Web Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    print(f"🚀 Starting STAT7 Project Index Server")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Debug: {args.debug}")
    print(f"   Web UI: http://{args.host}:{args.port}")
    print(f"   API: http://{args.host}:{args.port}/api/")

    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        if living_index:
            living_index.stop_watching()


if __name__ == '__main__':
    main()
