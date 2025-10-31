# STAT7 File Index System

A living, automatically updated project index with intent tracking and STAT7 coordinate integration.

## Overview

The STAT7 File Index System solves the problem of keeping track of project files and their purpose by:

- **Automatic Scanning**: Continuously monitors your project for file changes
- **Intent Extraction**: Reads intent comments and documentation from source code
- **STAT7 Integration**: Assigns 7-dimensional coordinates to each file
- **Relationship Tracking**: Maps import dependencies and file relationships
- **Living Updates**: Real-time updates as files change
- **Visualization**: Web interface for exploring your project structure

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies (should already be installed)
pip install watchdog flask flask-cors

# Optional: for better file watching
pip install watchdog
```

### 2. Basic Usage

```bash
# Scan and index your project
python stat7_index.py scan

# Start live file watching
python stat7_index.py watch

# Search files by intent
python stat7_index.py search "database connection"

# Show project statistics
python stat7_index.py stats

# Get detailed file information
python stat7_index.py info src/main.py
```

### 3. Web Visualization

```bash
# Start the web server
python web/stat7_index_server.py

# Open browser to http://localhost:5000
```

## File Intent Tagging

Add intent comments to your files to improve indexing:

```python
# INTENT: Core application entry point
# PURPOSE: Initialize and start the main application
# DEPENDENCIES: config.py, database.py, logger.py
# STAT7_COORD: realm=faculty, lineage=0, adjacency=high, horizon=genesis

def main():
    """Main application entry point"""
    pass
```

Supported intent tags:
- `INTENT`: Primary purpose of the file
- `PURPOSE`: Detailed description of what the file does
- `DEPENDENCIES`: Comma-separated list of dependencies
- `STAT7_COORD`: Manual STAT7 coordinate hints

## STAT7 Coordinate System

Each file gets a 7-dimensional STAT7 address:

```
STAT7-R-LLL-AA-H-LL-P-D
```

Where:
- **R**ealm: Domain category (faculty, pattern, companion, etc.)
- **L**ineage: Directory depth from project root
- **A**djacency: Semantic similarity to other files (0-100)
- **H**orizon: Development lifecycle stage
- **L**uminosity: Activity/importance level (0-100)
- **P**olarity: Technical vs creative nature
- **D**imensionality: Complexity and detail level (1-7)

## API Endpoints

The web server provides these REST API endpoints:

- `GET /api/project/stats` - Project statistics
- `GET /api/project/files` - All files with basic info
- `GET /api/search?q=query` - Search files by intent
- `GET /api/file/<path>` - Detailed file information
- `GET /api/stat7/realms` - Files by STAT7 realm
- `GET /api/stat7/horizons` - Files by STAT7 horizon
- `GET /api/relationships` - File relationship graph data
- `POST /api/scan` - Trigger project reindex

## File Categories

Files are automatically categorized:

- **code**: Source code files (.py, .js, .ts, .cs, etc.)
- **config**: Configuration files (.json, .yaml, .toml, etc.)
- **documentation**: Documentation (.md, .rst, .txt)
- **test**: Test files (test_*, *.test.*, *.spec.*)
- **asset**: Media files (.png, .jpg, .mp3, etc.)
- **build**: Build artifacts (.exe, .dll, .so, etc.)
- **temp**: Temporary files (.tmp, .bak, etc.)
- **meta**: Metadata and index files

## STAT7 Realms

Files are mapped to STAT7 realms based on category:

- **faculty**: Code files (technical knowledge)
- **pattern**: Configuration and meta files (structural patterns)
- **companion**: Documentation (supporting content)
- **achievement**: Test files (validation and proof)
- **sponsor_ring**: Assets (valuable resources)
- **void**: Temporary and build files (transient)

## Integration with Development Workflow

### Before Committing

1. Add intent comments to new files
2. Run `python stat7_index.py scan` to update index
3. Check `python stat7_index.py stats` for project overview
4. Use web interface to explore file relationships

### During Development

1. Run `python stat7_index.py watch` for live updates
2. Use `python stat7_index.py search "feature"` to find related files
3. Check file details with `python stat7_index.py info path/to/file`

### Code Reviews

1. Use web interface to visualize file relationships
2. Check that files have appropriate intent comments
3. Verify STAT7 coordinates make sense for file purpose
4. Look for orphaned files or missing dependencies

## Advanced Usage

### Custom File Watching

```python
from stat7_file_watcher import STAT7LivingIndex
from pathlib import Path

# Create living index
living_index = STAT7LivingIndex(Path("."), watch=True)

# Add custom callback
def on_file_change(event_type, file_path, entity):
    print(f"File {event_type}: {file_path}")
    if entity:
        print(f"STAT7: {entity.stat7.address}")

living_index.add_update_callback("custom", on_file_change)

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    living_index.stop_watching()
```

### Programmatic Search

```python
from stat7_file_index import STAT7FileIndex
from pathlib import Path

# Create index
index = STAT7FileIndex(Path("."))
index.scan_project()

# Search by intent
results = index.search_by_intent("database connection")
for entity in results:
    print(f"{entity.file_path}: {entity.intent.primary_intent}")

# Search by STAT7 coordinates
from stat7_entity import Realm, Polarity
results = index.search_by_stat7_coordinates(realm=Realm.FACULTY, polarity=Polarity.LOGIC)
```

## Configuration

### Exclude Patterns

The system automatically excludes these patterns:
- `__pycache__`, `.git`, `.vs`, `.idea`, `node_modules`
- `bin`, `obj`, `Temp`, `Library`, `Logs`

### Include Extensions

Only these file extensions are indexed:
- Code: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.cs`, `.java`, `.cpp`, `.c`, `.h`
- Docs: `.md`, `.rst`, `.txt`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`
- Web: `.html`, `.css`, `.scss`, `.less`, `.vue`, `.svelte`

## Troubleshooting

### Common Issues

1. **"watchdog not available"**
   - Install with: `pip install watchdog`

2. **"Flask not available"**
   - Install with: `pip install flask flask-cors`

3. **"STAT7 modules not found"**
   - Make sure you're running from project root
   - Check that `packages/com.twg.the-seed/seed/engine/` exists

4. **Large projects take time to scan**
   - First scan is always slower
   - Subsequent scans are incremental
   - Use `--force` flag only when needed

### Performance Tips

1. Exclude large directories from scanning
2. Use appropriate file extension filters
3. Run scans on schedule rather than continuously for large projects
4. Consider using SSD storage for better file watching performance

## Integration with IDE

### VS Code

Add these tasks to `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "STAT7: Scan Project",
            "type": "shell",
            "command": "python stat7_index.py scan",
            "group": "build"
        },
        {
            "label": "STAT7: Watch Files",
            "type": "shell",
            "command": "python stat7_index.py watch",
            "group": "build"
        }
    ]
}
```

### JetBrains Rider

Create external tools in Settings → Tools → External Tools:

1. **STAT7 Scan**
   - Program: `python`
   - Arguments: `stat7_index.py scan`
   - Working directory: `$ProjectFileDir$`

2. **STAT7 Watch**
   - Program: `python`
   - Arguments: `stat7_index.py watch`
   - Working directory: `$ProjectFileDir$`

## Contributing

The STAT7 File Index System is designed to be extensible:

1. **New File Types**: Add support for new languages in `stat7_file_index.py`
2. **Intent Patterns**: Add new intent extraction patterns
3. **STAT7 Dimensions**: Modify coordinate computation logic
4. **Visualization**: Enhance web interface with new views

## License

This system is part of The Seed project and follows the same licensing terms.

---

*For more information, see the main project documentation or check the SWEEP.md file for development commands.*
