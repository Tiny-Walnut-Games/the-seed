#!/usr/bin/env python3
"""
STAT7 Project Index CLI
Command-line interface for the living project index.

Usage:
    python stat7_index.py scan          # Scan and index project
    python stat7_index.py watch         # Start file watcher
    python stat7_index.py search <query> # Search by intent
    python stat7_index.py stats         # Show project statistics
    python stat7_index.py info <file>   # Show file information
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add seed engine to path
sys.path.insert(0, str(Path(__file__) / "packages" / "com.twg.the-seed" / "seed" / "engine"))

from stat7_file_index import STAT7FileIndex, FileCategory, Realm, Horizon, Polarity
from stat7_file_watcher import STAT7LivingIndex


def scan_project(project_root: Path, force: bool = False):
    """Scan and index project files"""
    print(f"🔍 Scanning project: {project_root}")

    index = STAT7FileIndex(project_root)
    results = index.scan_project(force_reindex=force)

    print(f"✅ Scan completed:")
    print(f"   Files scanned: {results['scanned']}")
    print(f"   Files added: {results['added']}")
    print(f"   Files updated: {results['updated']}")
    print(f"   Files removed: {results['removed']}")
    print(f"   Errors: {len(results['errors'])}")
    print(f"   Duration: {results['duration_seconds']:.2f}s")

    if results['errors']:
        print("\n❌ Errors:")
        for error in results['errors']:
            print(f"   {error}")

    return index


def watch_project(project_root: Path):
    """Start file watcher for live updates"""
    print(f"👁️ Starting file watcher for: {project_root}")
    print("Press Ctrl+C to stop...")

    living_index = STAT7LivingIndex(project_root, watch=True)

    # Add change callback
    def on_change(event_type: str, file_path: str, entity):
        icon = {"created": "➕", "changed": "📝", "deleted": "🗑️"}.get(event_type, "📄")
        print(f"{icon} {event_type}: {file_path}")
        if entity:
            print(f"   STAT7: {entity.stat7.address}")
            if entity.intent.primary_intent:
                print(f"   Intent: {entity.intent.primary_intent}")

    living_index.add_update_callback("cli", on_change)

    # Initial scan
    living_index.force_reindex()

    # Keep running
    try:
        while True:
            asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping file watcher...")
        living_index.stop_watching()


def search_project(project_root: Path, query: str):
    """Search files by intent"""
    index = STAT7FileIndex(project_root)

    # Load existing index or scan if needed
    if not index.file_entities:
        print("📂 No index found, scanning project...")
        index.scan_project()

    results = index.search_by_intent(query)

    print(f"🔍 Search results for '{query}':")
    if not results:
        print("   No matches found")
        return

    for entity in results[:10]:  # Show top 10
        print(f"\n📄 {entity.file_path}")
        print(f"   STAT7: {entity.stat7.address}")
        print(f"   Category: {entity.file_category.value}")
        print(f"   Intent: {entity.intent.primary_intent or 'No intent'}")
        if entity.intent.purpose:
            print(f"   Purpose: {entity.intent.purpose[:100]}...")
        print(f"   Complexity: {entity.intent.complexity_score:.2f}")


def show_statistics(project_root: Path):
    """Show project statistics"""
    index = STAT7FileIndex(project_root)

    # Load existing index or scan if needed
    if not index.file_entities:
        print("📂 No index found, scanning project...")
        index.scan_project()

    stats = index.get_project_statistics()

    print(f"📊 Project Statistics for {project_root.name}")
    print("=" * 50)

    print(f"\n📁 Overview:")
    print(f"   Total files: {stats['total_files']}")

    print(f"\n📂 By Category:")
    for category, count in stats['by_category'].items():
        print(f"   {category}: {count}")

    print(f"\n🌌 By STAT7 Realm:")
    for realm, count in stats['by_realm'].items():
        print(f"   {realm}: {count}")

    print(f"\n🌅 By Horizon:")
    for horizon, count in stats['by_horizon'].items():
        print(f"   {horizon}: {count}")

    print(f"\n⚡ By Polarity:")
    for polarity, count in stats['by_polarity'].items():
        print(f"   {polarity}: {count}")

    print(f"\n🧠 Complexity Distribution:")
    print(f"   Low: {stats['complexity_distribution']['low']}")
    print(f"   Medium: {stats['complexity_distribution']['medium']}")
    print(f"   High: {stats['complexity_distribution']['high']}")

    print(f"\n📏 Size Distribution:")
    print(f"   Small (<50 lines): {stats['size_distribution']['small']}")
    print(f"   Medium (50-200 lines): {stats['size_distribution']['medium']}")
    print(f"   Large (>200 lines): {stats['size_distribution']['large']}")

    if stats['most_connected']:
        print(f"\n🔗 Most Connected Files:")
        for i, entity in enumerate(stats['most_connected'][:5], 1):
            connections = len(entity.imports_files) + len(entity.imported_by_files)
            print(f"   {i}. {entity.file_path.name} ({connections} connections)")

    if stats['recently_modified']:
        print(f"\n🕒 Recently Modified:")
        for i, entity in enumerate(stats['recently_modified'][:5], 1):
            print(f"   {i}. {entity.file_path.name} ({entity.metrics.last_modified.strftime('%Y-%m-%d %H:%M')})")


def show_file_info(project_root: Path, file_path: str):
    """Show detailed information about a specific file"""
    index = STAT7FileIndex(project_root)

    # Load existing index or scan if needed
    if not index.file_entities:
        print("📂 No index found, scanning project...")
        index.scan_project()

    entity = index.get_file_entity(file_path)
    if not entity:
        print(f"❌ File not found in index: {file_path}")
        return

    summary = entity.get_file_summary()

    print(f"📄 File Information: {entity.file_path}")
    print("=" * 60)

    print(f"\n📋 Basic Info:")
    print(f"   Path: {summary['file_info']['path']}")
    print(f"   Category: {summary['file_info']['category']}")
    print(f"   Size: {summary['file_info']['size_bytes']} bytes")
    print(f"   Lines: {summary['metrics']['line_count']}")
    print(f"   Last Modified: {summary['file_info']['last_modified']}")

    print(f"\n🌌 STAT7 Coordinates:")
    coords = summary['stat7_coordinates']
    print(f"   Address: {coords['address']}")
    print(f"   Realm: {coords['realm']}")
    print(f"   Lineage: {coords['lineage']}")
    print(f"   Adjacency: {coords['adjacency']}")
    print(f"   Horizon: {coords['horizon']}")
    print(f"   Luminosity: {coords['luminosity']}")
    print(f"   Polarity: {coords['polarity']}")
    print(f"   Dimensionality: {coords['dimensionality']}")

    print(f"\n🎯 Intent & Purpose:")
    intent = summary['intent']
    print(f"   Primary Intent: {intent['primary'] or 'Not specified'}")
    print(f"   Purpose: {intent['purpose'] or 'Not specified'}")
    print(f"   Complexity Score: {intent['complexity_score']:.2f}")
    if intent['dependencies']:
        print(f"   Dependencies: {', '.join(intent['dependencies'])}")

    print(f"\n📊 Code Metrics:")
    metrics = summary['metrics']
    print(f"   Functions: {metrics['function_count']}")
    print(f"   Classes: {metrics['class_count']}")
    print(f"   Imports: {metrics['import_count']}")
    print(f"   Comment Ratio: {metrics['comment_ratio']}")

    print(f"\n🔗 Relationships:")
    relationships = summary['relationships']
    if relationships['imports']:
        print(f"   Imports: {len(relationships['imports'])} files")
        for imp in relationships['imports'][:5]:
            print(f"     - {imp}")
    if relationships['imported_by']:
        print(f"   Imported By: {len(relationships['imported_by'])} files")
        for imp_by in relationships['imported_by'][:5]:
            print(f"     - {imp_by}")
    if relationships['related']:
        print(f"   Related: {len(relationships['related'])} files")

    print(f"\n🏷️ Tags:")
    if summary['tags']:
        for tag in summary['tags']:
            print(f"   - {tag}")
    else:
        print("   No tags found")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="STAT7 Project Index CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python stat7_index.py scan --force
    python stat7_index.py watch
    python stat7_index.py search "database connection"
    python stat7_index.py stats
    python stat7_index.py info src/main.py
        """
    )

    parser.add_argument(
        "command",
        choices=["scan", "watch", "search", "stats", "info"],
        help="Command to execute"
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query for search command or file path for info command"
    )

    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force complete reindex for scan command"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"❌ Project root does not exist: {project_root}")
        sys.exit(1)

    try:
        if args.command == "scan":
            scan_project(project_root, args.force)

        elif args.command == "watch":
            watch_project(project_root)

        elif args.command == "search":
            if not args.query:
                print("❌ Search command requires a query")
                sys.exit(1)
            search_project(project_root, args.query)

        elif args.command == "stats":
            show_statistics(project_root)

        elif args.command == "info":
            if not args.query:
                print("❌ Info command requires a file path")
                sys.exit(1)
            show_file_info(project_root, args.query)

    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
