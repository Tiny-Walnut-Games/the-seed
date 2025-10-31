#!/usr/bin/env python3
"""
STAT7 File Index System
Living project index with intent tracking and automatic updates.

This system extends STAT7 to provide:
- File indexing with intent metadata
- Automatic scanning and updates
- STAT7 coordinate assignment for files
- Intent extraction from comments and code
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import hashlib
import re
from typing import Dict, List, Optional, Any, Set, Tuple

# Import existing STAT7 system
from stat7_entity import STAT7Entity, STAT7Coordinates, Realm, Horizon, Polarity


class FileCategory(Enum):
    """File categorization for STAT7 indexing"""
    CODE = "code"                    # Source code files
    CONFIG = "config"                # Configuration files
    DOCUMENTATION = "documentation"  # Docs, READMEs
    TEST = "test"                    # Test files
    ASSET = "asset"                  # Media, resources
    BUILD = "build"                  # Build artifacts
    TEMP = "temp"                    # Temporary files
    META = "meta"                    # Metadata, indexes


@dataclass
class FileIntent:
    """Extracted intent and metadata from file content"""
    primary_intent: str = ""
    purpose: str = ""
    dependencies: List[str] = field(default_factory=list)
    stat7_coord_hint: Optional[str] = None
    complexity_score: float = 0.0
    narrative_context: str = ""
    author_notes: str = ""


@dataclass
class FileMetrics:
    """File metrics for STAT7 coordinate computation"""
    line_count: int = 0
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    comment_ratio: float = 0.0
    last_modified: datetime = field(default_factory=datetime.utcnow)
    file_size_bytes: int = 0


class STAT7FileEntity(STAT7Entity):
    """
    STAT7 entity for project files with intent tracking.

    Extends STAT7Entity to provide:
    - File-specific coordinate computation
    - Intent extraction from source code
    - Dependency tracking
    - Automatic metadata updates
    """

    # File-specific fields
    file_path: Path = field(default_factory=lambda: Path(""))
    file_category: FileCategory = FileCategory.CODE
    file_extension: str = ""
    file_encoding: str = "utf-8"

    # Intent and analysis
    intent: FileIntent = field(default_factory=FileIntent)
    metrics: FileMetrics = field(default_factory=FileMetrics)

    # Content analysis
    extracted_tags: Set[str] = field(default_factory=set)
    semantic_hash: str = ""
    content_fingerprint: str = ""

    # Relationships
    imports_files: List[str] = field(default_factory=list)
    imported_by_files: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize file-specific properties"""
        if not self.file_path:
            raise ValueError("file_path is required for STAT7FileEntity")

        self.entity_type = "file"
        self.file_extension = self.file_path.suffix.lower()
        self.file_category = self._determine_category()

        # Initialize STAT7 coordinates
        if self.stat7 is None:
            self.stat7 = self._compute_stat7_coordinates()

        self._record_event("file_indexed", f"File {self.file_path} indexed in STAT7")

    def _determine_category(self) -> FileCategory:
        """Determine file category from path and extension"""
        path_str = str(self.file_path).lower()
        ext = self.file_extension

        # Configuration files
        if ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']:
            return FileCategory.CONFIG

        # Documentation
        if ext in ['.md', '.rst', '.txt'] or 'doc' in path_str or 'readme' in path_str:
            return FileCategory.DOCUMENTATION

        # Tests
        if 'test' in path_str or ext in ['.test.js', '.spec.ts']:
            return FileCategory.TEST

        # Assets
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.mp3', '.wav', '.mp4']:
            return FileCategory.ASSET

        # Build artifacts
        if 'build' in path_str or 'dist' in path_str or ext in ['.exe', '.dll', '.so']:
            return FileCategory.BUILD

        # Temporary
        if 'temp' in path_str or 'tmp' in path_str or ext in ['.tmp', '.bak']:
            return FileCategory.TEMP

        # Meta files
        if 'meta' in path_str or ext in ['.meta', '.index']:
            return FileCategory.META

        # Default to code
        return FileCategory.CODE

    def _compute_stat7_coordinates(self) -> STAT7Coordinates:
        """
        Compute STAT7 coordinates based on file properties and intent.

        Coordinate mapping:
        - Realm: Based on file category and purpose
        - Lineage: Directory depth from project root
        - Adjacency: Semantic similarity to other files
        - Horizon: Development lifecycle stage
        - Luminosity: Activity/importance level
        - Polarity: Technical vs creative nature
        - Dimensionality: Complexity and detail level
        """
        # Compute lineage (directory depth)
        lineage = len(self.file_path.parts) - 1

        # Determine realm from category and intent
        realm = self._compute_realm()

        # Compute adjacency based on file relationships
        adjacency = self._compute_adjacency_score()

        # Determine horizon from file state
        horizon = self._compute_horizon()

        # Compute luminosity (activity/importance)
        luminosity = self._compute_luminosity()

        # Determine polarity (technical vs creative)
        polarity = self._compute_polarity()

        # Compute dimensionality (complexity)
        dimensionality = self._compute_dimensionality()

        return STAT7Coordinates(
            realm=realm,
            lineage=lineage,
            adjacency=adjacency,
            horizon=horizon,
            luminosity=luminosity,
            polarity=polarity,
            dimensionality=dimensionality
        )

    def _compute_realm(self) -> Realm:
        """Map file category to STAT7 realm"""
        category_realm_map = {
            FileCategory.CODE: Realm.FACULTY,
            FileCategory.CONFIG: Realm.PATTERN,
            FileCategory.DOCUMENTATION: Realm.COMPANION,
            FileCategory.TEST: Realm.ACHIEVEMENT,
            FileCategory.ASSET: Realm.SPONSOR_RING,
            FileCategory.BUILD: Realm.VOID,
            FileCategory.TEMP: Realm.VOID,
            FileCategory.META: Realm.PATTERN
        }
        return category_realm_map.get(self.file_category, Realm.FACULTY)

    def _compute_adjacency_score(self) -> float:
        """Compute adjacency score based on dependencies and relationships"""
        base_score = 50.0  # Neutral starting point

        # More dependencies = higher adjacency
        dependency_bonus = min(len(self.imports_files) * 5, 30.0)

        # More importers = higher adjacency
        importer_bonus = min(len(self.imported_by_files) * 3, 20.0)

        # Related files increase adjacency
        related_bonus = min(len(self.related_files) * 2, 15.0)

        return min(base_score + dependency_bonus + importer_bonus + related_bonus, 100.0)

    def _compute_horizon(self) -> Horizon:
        """Determine lifecycle horizon from file state"""
        if self.file_category in [FileCategory.TEMP, FileCategory.BUILD]:
            return Horizon.DECAY
        elif self.file_category == FileCategory.META:
            return Horizon.CRYSTALLIZATION
        elif self.intent.primary_intent and "prototype" in self.intent.primary_intent.lower():
            return Horizon.GENESIS
        elif self.intent.primary_intent and "production" in self.intent.primary_intent.lower():
            return Horizon.PEAK
        else:
            return Horizon.EMERGENCE

    def _compute_luminosity(self) -> float:
        """Compute luminosity based on activity and importance"""
        base_luminosity = 50.0

        # Core files get higher luminosity
        if any(core in str(self.file_path).lower() for core in ['engine', 'core', 'main']):
            base_luminosity += 20.0

        # Recently modified files are more luminous
        days_since_modified = (datetime.utcnow() - self.metrics.last_modified).days
        recency_bonus = max(0, 30 - days_since_modified)
        base_luminosity += recency_bonus

        # Complex files get higher luminosity
        complexity_bonus = min(self.metrics.line_count / 100, 20.0)
        base_luminosity += complexity_bonus

        return min(base_luminosity, 100.0)

    def _compute_polarity(self) -> Polarity:
        """Determine polarity from file nature"""
        path_str = str(self.file_path).lower()

        # Technical polarity
        if any(tech in path_str for tech in ['engine', 'system', 'core', 'algorithm']):
            return Polarity.LOGIC

        # Creative polarity
        if any(creative in path_str for creative in ['ui', 'art', 'design', 'creative']):
            return Polarity.CREATIVITY

        # Order polarity
        if any(order in path_str for order in ['config', 'structure', 'organization']):
            return Polarity.ORDER

        # Achievement polarity for tests
        if self.file_category == FileCategory.TEST:
            return Polarity.ACHIEVEMENT

        # Community polarity for docs
        if self.file_category == FileCategory.DOCUMENTATION:
            return Polarity.COMMUNITY

        # Default to technical
        return Polarity.TECHNICAL

    def _compute_dimensionality(self) -> int:
        """Compute dimensionality from complexity metrics"""
        base_dimension = 1

        # Add dimensions for complexity
        if self.metrics.line_count > 100:
            base_dimension += 1
        if self.metrics.function_count > 10:
            base_dimension += 1
        if self.metrics.class_count > 5:
            base_dimension += 1
        if len(self.imports_files) > 5:
            base_dimension += 1
        if self.intent.complexity_score > 0.7:
            base_dimension += 1

        return min(base_dimension, 7)  # Cap at 7 dimensions

    def extract_intent_from_content(self, content: str) -> FileIntent:
        """
        Extract intent and metadata from file content.

        Looks for:
        - INTENT comments
        - PURPOSE statements
        - DEPENDENCIES lists
        - STAT7_COORD hints
        - Function/class documentation
        """
        intent = FileIntent()

        # Extract intent comments
        intent_patterns = [
            r'#\s*INTENT:\s*(.+)',
            r'//\s*INTENT:\s*(.+)',
            r'/\*\s*INTENT:\s*(.+?)\*/',
            r'"""INTENT:\s*(.+?)"""',
            r"'''INTENT:\s*(.+?)'''"
        ]

        for pattern in intent_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                intent.primary_intent = matches[0].strip()
                break

        # Extract purpose
        purpose_patterns = [
            r'#\s*PURPOSE:\s*(.+)',
            r'//\s*PURPOSE:\s*(.+)',
            r'/\*\s*PURPOSE:\s*(.+?)\*/',
            r'"""PURPOSE:\s*(.+?)"""',
            r"'''PURPOSE:\s*(.+?)'''"
        ]

        for pattern in purpose_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                intent.purpose = matches[0].strip()
                break

        # Extract dependencies
        dep_patterns = [
            r'#\s*DEPENDENCIES:\s*(.+)',
            r'//\s*DEPENDENCIES:\s*(.+)',
            r'/\*\s*DEPENDENCIES:\s*(.+?)\*/',
            r'"""DEPENDENCIES:\s*(.+?)"""',
            r"'''DEPENDENCIES:\s*(.+?)'''"
        ]

        for pattern in dep_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                dep_text = matches[0].strip()
                # Split by commas and clean up
                intent.dependencies = [dep.strip() for dep in dep_text.split(',') if dep.strip()]

        # Extract STAT7 coordinate hints
        stat7_patterns = [
            r'#\s*STAT7_COORD:\s*(.+)',
            r'//\s*STAT7_COORD:\s*(.+)',
            r'/\*\s*STAT7_COORD:\s*(.+?)\*/',
            r'"""STAT7_COORD:\s*(.+?)"""',
            r"'''STAT7_COORD:\s*(.+?)'''"
        ]

        for pattern in stat7_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                intent.stat7_coord_hint = matches[0].strip()
                break

        # Extract narrative context from docstrings
        docstring_patterns = [
            r'"""([^"]+)"""',
            r"'''([^']+)'''",
            r'/\*\*([^*]+)\*/'
        ]

        narrative_parts = []
        for pattern in docstring_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            narrative_parts.extend([match.strip() for match in matches if len(match.strip()) > 20])

        intent.narrative_context = ' '.join(narrative_parts[:3])  # First 3 meaningful docstrings

        # Compute complexity score
        intent.complexity_score = self._compute_complexity_score(content)

        return intent

    def _compute_complexity_score(self, content: str) -> float:
        """Compute complexity score from content analysis"""
        score = 0.0

        # Line count contribution
        lines = content.split('\n')
        line_score = min(len(lines) / 1000, 0.3)  # Max 0.3 from line count
        score += line_score

        # Function/class count
        func_matches = len(re.findall(r'def\s+\w+|function\s+\w+|class\s+\w+', content))
        func_score = min(func_matches / 50, 0.2)  # Max 0.2 from functions
        score += func_score

        # Import complexity
        import_matches = len(re.findall(r'import\s+|from\s+.*import|#include', content))
        import_score = min(import_matches / 20, 0.2)  # Max 0.2 from imports
        score += import_score

        # Control flow complexity
        control_matches = len(re.findall(r'if\s+|for\s+|while\s+|switch\s+|try\s+', content))
        control_score = min(control_matches / 100, 0.2)  # Max 0.2 from control flow
        score += control_score

        # Comment density (more comments = more complex intent)
        comment_matches = len(re.findall(r'#.*|//.*|/\*.*?\*/', content, re.DOTALL))
        comment_ratio = comment_matches / max(len(lines), 1)
        comment_score = min(comment_ratio, 0.1)  # Max 0.1 from comments
        score += comment_score

        return min(score, 1.0)

    def analyze_file_metrics(self, content: str) -> FileMetrics:
        """Analyze file content and compute metrics"""
        metrics = FileMetrics()

        # Basic metrics
        metrics.line_count = len(content.split('\n'))
        metrics.file_size_bytes = len(content.encode(self.file_encoding))

        # Get file modification time
        if self.file_path.exists():
            metrics.last_modified = datetime.fromtimestamp(self.file_path.stat().st_mtime)

        # Language-specific analysis
        if self.file_extension in ['.py', '.pyx']:
            metrics.function_count = len(re.findall(r'def\s+\w+', content))
            metrics.class_count = len(re.findall(r'class\s+\w+', content))
            metrics.import_count = len(re.findall(r'import\s+|from\s+.*import', content))

        elif self.file_extension in ['.js', '.ts', '.jsx', '.tsx']:
            metrics.function_count = len(re.findall(r'function\s+\w+|const\s+\w+\s*=|=>', content))
            metrics.class_count = len(re.findall(r'class\s+\w+', content))
            metrics.import_count = len(re.findall(r'import\s+.*from|require\(', content))

        elif self.file_extension in ['.cs']:
            metrics.function_count = len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', content))
            metrics.class_count = len(re.findall(r'class\s+\w+', content))
            metrics.import_count = len(re.findall(r'using\s+', content))

        # Compute comment ratio
        comment_lines = len(re.findall(r'#.*|//.*|/\*.*?\*/', content, re.MULTILINE))
        metrics.comment_ratio = comment_lines / max(metrics.line_count, 1)

        return metrics

    def to_collectible_card_data(self) -> Dict[str, Any]:
        """Convert file entity to collectible card display format"""
        return {
            'title': self.file_path.name,
            'subtitle': str(self.file_path.parent),
            'fluff_text': self.intent.purpose or f"File in {self.file_category.value} category",
            'icon_url': f"/icons/{self.file_extension[1:] or 'file'}.png",
            'rarity': self._compute_rarity(),
            'key_stats': {
                'Lines': self.metrics.line_count,
                'Functions': self.metrics.function_count,
                'Dependencies': len(self.imports_files),
                'Complexity': f"{self.intent.complexity_score:.2f}"
            },
            'properties': {
                'file_path': str(self.file_path),
                'file_category': self.file_category.value,
                'stat7_address': self.stat7.address,
                'last_modified': self.metrics.last_modified.isoformat(),
                'intent': self.intent.primary_intent,
                'tags': list(self.extracted_tags)
            }
        }

    def _compute_rarity(self) -> str:
        """Compute rarity based on file importance and complexity"""
        if self.file_category == FileCategory.CODE and self.metrics.line_count > 500:
            return "Legendary"
        elif self.file_category == FileCategory.CODE and self.metrics.line_count > 200:
            return "Epic"
        elif self.intent.complexity_score > 0.8:
            return "Rare"
        elif self.metrics.function_count > 20:
            return "Uncommon"
        else:
            return "Common"

    def validate_hybrid_encoding(self) -> Tuple[bool, str]:
        """Validate that STAT7 coordinates correctly encode file properties"""
        try:
            # Check realm matches category
            expected_realm = self._compute_realm()
            if self.stat7.realm != expected_realm:
                return False, f"Realm mismatch: expected {expected_realm.value}, got {self.stat7.realm.value}"

            # Check lineage matches directory depth
            expected_lineage = len(self.file_path.parts) - 1
            if self.stat7.lineage != expected_lineage:
                return False, f"Lineage mismatch: expected {expected_lineage}, got {self.stat7.lineage}"

            # Check adjacency is in valid range
            if not (0 <= self.stat7.adjacency <= 100):
                return False, f"Adjacency out of range: {self.stat7.adjacency}"

            # Check luminosity is in valid range
            if not (0 <= self.stat7.luminosity <= 100):
                return False, f"Luminosity out of range: {self.stat7.luminosity}"

            return True, ""

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def update_from_file(self):
        """Update entity data from current file state"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # Read file content
        try:
            with open(self.file_path, 'r', encoding=self.file_encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(self.file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    self.file_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Could not decode file {self.file_path}")

        # Update metrics
        self.metrics = self.analyze_file_metrics(content)

        # Update intent
        self.intent = self.extract_intent_from_content(content)

        # Update content fingerprint
        self.content_fingerprint = hashlib.sha256(content.encode()).hexdigest()

        # Update semantic hash (based on structure, not content)
        structure_hash = self._compute_structure_hash(content)
        self.semantic_hash = hashlib.sha256(structure_hash.encode()).hexdigest()

        # Recompute STAT7 coordinates
        self.stat7 = self._compute_stat7_coordinates()

        # Record update event
        self._record_event("file_updated", f"File {self.file_path} updated and re-indexed")

    def _compute_structure_hash(self, content: str) -> str:
        """Compute hash based on code structure, not exact content"""
        # Normalize content by removing string literals and comments
        normalized = re.sub(r'""".*?"""', '""""""', content, flags=re.DOTALL)
        normalized = re.sub(r"'''.*?'''", "''''''", normalized, flags=re.DOTALL)
        normalized = re.sub(r'//.*', '', normalized)
        normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
        normalized = re.sub(r'#.*', '', normalized)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def add_file_relationship(self, other_file_path: str, relationship_type: str = "related"):
        """Add relationship to another file"""
        if relationship_type == "imports":
            if other_file_path not in self.imports_files:
                self.imports_files.append(other_file_path)
        elif relationship_type == "imported_by":
            if other_file_path not in self.imported_by_files:
                self.imported_by_files.append(other_file_path)
        elif relationship_type == "related":
            if other_file_path not in self.related_files:
                self.related_files.append(other_file_path)

        self._record_event("relationship_added", f"Added {relationship_type} relationship to {other_file_path}")

    def get_file_summary(self) -> Dict[str, Any]:
        """Get comprehensive file summary"""
        return {
            'file_info': {
                'path': str(self.file_path),
                'name': self.file_path.name,
                'extension': self.file_extension,
                'category': self.file_category.value,
                'size_bytes': self.metrics.file_size_bytes,
                'last_modified': self.metrics.last_modified.isoformat()
            },
            'stat7_coordinates': self.stat7.to_dict(),
            'intent': {
                'primary': self.intent.primary_intent,
                'purpose': self.intent.purpose,
                'dependencies': self.intent.dependencies,
                'complexity_score': self.intent.complexity_score,
                'narrative_context': self.intent.narrative_context[:200] + "..." if len(self.intent.narrative_context) > 200 else self.intent.narrative_context
            },
            'metrics': {
                'line_count': self.metrics.line_count,
                'function_count': self.metrics.function_count,
                'class_count': self.metrics.class_count,
                'import_count': self.metrics.import_count,
                'comment_ratio': f"{self.metrics.comment_ratio:.2f}"
            },
            'relationships': {
                'imports': self.imports_files,
                'imported_by': self.imported_by_files,
                'related': self.related_files
            },
            'tags': list(self.extracted_tags),
            'entity_id': self.entity_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }


class STAT7FileIndex:
    """
    Living project index with automatic updates and STAT7 integration.

    Provides:
    - Automatic file scanning and indexing
    - Intent extraction and metadata analysis
    - STAT7 coordinate assignment
    - Relationship tracking
    - Real-time updates
    """

    def __init__(self, project_root: Path, index_file: Optional[Path] = None):
        self.project_root = Path(project_root)
        self.index_file = index_file or self.project_root / ".stat7_index.json"

        # File entity storage
        self.file_entities: Dict[str, STAT7FileEntity] = {}
        self.path_to_entity_id: Dict[str, str] = {}

        # Configuration
        self.exclude_patterns = {
            '__pycache__', '.git', '.vs', '.idea', 'node_modules',
            'bin', 'obj', 'Temp', 'Library', 'Logs'
        }

        self.include_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.cs', '.java', '.cpp', '.c', '.h',
            '.md', '.rst', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini',
            '.html', '.css', '.scss', '.less', '.vue', '.svelte'
        }

        # Load existing index if available
        self.load_index()

    def scan_project(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Scan entire project and update index.

        Args:
            force_reindex: If True, reindex all files even if unchanged

        Returns:
            Scan results with statistics
        """
        scan_start = datetime.utcnow()
        results = {
            'scanned': 0,
            'updated': 0,
            'added': 0,
            'removed': 0,
            'errors': [],
            'start_time': scan_start.isoformat()
        }

        # Get all files to scan
        files_to_scan = self._get_project_files()

        # Check for removed files
        existing_paths = set(self.path_to_entity_id.keys())
        scanned_paths = set(str(f.relative_to(self.project_root)) for f in files_to_scan)
        removed_paths = existing_paths - scanned_paths

        for removed_path in removed_paths:
            entity_id = self.path_to_entity_id[removed_path]
            del self.file_entities[entity_id]
            del self.path_to_entity_id[removed_path]
            results['removed'] += 1

        # Scan current files
        for file_path in files_to_scan:
            try:
                relative_path = str(file_path.relative_to(self.project_root))
                entity_id = self.path_to_entity_id.get(relative_path)

                if entity_id:
                    # Existing file
                    entity = self.file_entities[entity_id]
                    if force_reindex or self._should_reindex(entity, file_path):
                        entity.update_from_file()
                        results['updated'] += 1
                else:
                    # New file
                    entity = STAT7FileEntity(file_path=file_path)
                    self.file_entities[entity.entity_id] = entity
                    self.path_to_entity_id[relative_path] = entity.entity_id
                    results['added'] += 1

                results['scanned'] += 1

            except Exception as e:
                error_msg = f"Error scanning {file_path}: {str(e)}"
                results['errors'].append(error_msg)

        # Build relationships after all files are indexed
        self._build_relationships()

        # Save updated index
        self.save_index()

        results['end_time'] = datetime.utcnow().isoformat()
        results['duration_seconds'] = (datetime.utcnow() - scan_start).total_seconds()
        results['total_files'] = len(self.file_entities)

        return results

    def _get_project_files(self) -> List[Path]:
        """Get all files that should be indexed"""
        files = []

        for file_path in self.project_root.rglob('*'):
            # Skip directories
            if not file_path.is_file():
                continue

            # Skip excluded patterns
            if any(pattern in str(file_path) for pattern in self.exclude_patterns):
                continue

            # Check extension
            if file_path.suffix.lower() not in self.include_extensions:
                continue

            files.append(file_path)

        return files

    def _should_reindex(self, entity: STAT7FileEntity, file_path: Path) -> bool:
        """Check if file needs reindexing"""
        if not file_path.exists():
            return False

        # Check modification time
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        if file_mtime > entity.last_activity:
            return True

        # Check file size
        current_size = file_path.stat().st_size
        if current_size != entity.metrics.file_size_bytes:
            return True

        return False

    def _build_relationships(self):
        """Build import/dependency relationships between files"""
        # Clear existing relationships
        for entity in self.file_entities.values():
            entity.imports_files.clear()
            entity.imported_by_files.clear()

        # Build import relationships
        for entity in self.file_entities.values():
            if entity.file_category != FileCategory.CODE:
                continue

            try:
                with open(entity.file_path, 'r', encoding=entity.file_encoding) as f:
                    content = f.read()

                # Extract imports based on file type
                imports = self._extract_imports(content, entity.file_extension)

                for import_path in imports:
                    # Try to resolve import to actual file
                    resolved_path = self._resolve_import_path(import_path, entity.file_path)
                    if resolved_path:
                        relative_import = str(resolved_path.relative_to(self.project_root))
                        if relative_import in self.path_to_entity_id:
                            entity.add_file_relationship(relative_import, "imports")
                            import_entity_id = self.path_to_entity_id[relative_import]
                            import_entity = self.file_entities[import_entity_id]
                            import_entity.add_file_relationship(str(entity.file_path.relative_to(self.project_root)), "imported_by")

            except Exception as e:
                # Log error but continue
                continue

    def _extract_imports(self, content: str, extension: str) -> List[str]:
        """Extract import statements from file content"""
        imports = []

        if extension in ['.py', '.pyx']:
            # Python imports
            import_patterns = [
                r'from\s+([^\s]+)\s+import',
                r'import\s+([^\s,]+)'
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.extend(matches)

        elif extension in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript imports
            import_patterns = [
                r'import.*from\s+["\']([^"\']+)["\']',
                r'require\(["\']([^"\']+)["\']\)'
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.extend(matches)

        elif extension in ['.cs']:
            # C# using statements
            matches = re.findall(r'using\s+([^;]+);', content)
            imports.extend(matches)

        return imports

    def _resolve_import_path(self, import_path: str, source_file: Path) -> Optional[Path]:
        """Resolve import path to actual file path"""
        # Remove relative path components
        import_path = import_path.replace('.', '/').replace('\\', '/')

        # Try different extensions
        for ext in ['.py', '.js', '.ts', '.cs']:
            potential_path = self.project_root / f"{import_path}{ext}"
            if potential_path.exists():
                return potential_path

            # Try as module with __init__
            init_path = self.project_root / import_path / f"__init__{ext}"
            if init_path.exists():
                return init_path

        return None

    def get_file_entity(self, file_path: str) -> Optional[STAT7FileEntity]:
        """Get file entity by path"""
        relative_path = str(Path(file_path).relative_to(self.project_root))
        entity_id = self.path_to_entity_id.get(relative_path)
        return self.file_entities.get(entity_id) if entity_id else None

    def search_by_intent(self, query: str) -> List[STAT7FileEntity]:
        """Search files by intent content"""
        query_lower = query.lower()
        results = []

        for entity in self.file_entities.values():
            if (query_lower in entity.intent.primary_intent.lower() or
                query_lower in entity.intent.purpose.lower() or
                query_lower in entity.intent.narrative_context.lower()):
                results.append(entity)

        return sorted(results, key=lambda e: e.stat7.luminosity, reverse=True)

    def search_by_stat7_coordinates(self, realm: Optional[Realm] = None,
                                   horizon: Optional[Horizon] = None,
                                   polarity: Optional[Polarity] = None) -> List[STAT7FileEntity]:
        """Search files by STAT7 coordinates"""
        results = []

        for entity in self.file_entities.values():
            if realm and entity.stat7.realm != realm:
                continue
            if horizon and entity.stat7.horizon != horizon:
                continue
            if polarity and entity.stat7.polarity != polarity:
                continue

            results.append(entity)

        return results

    def get_project_statistics(self) -> Dict[str, Any]:
        """Get comprehensive project statistics"""
        stats = {
            'total_files': len(self.file_entities),
            'by_category': {},
            'by_realm': {},
            'by_horizon': {},
            'by_polarity': {},
            'complexity_distribution': {'low': 0, 'medium': 0, 'high': 0},
            'size_distribution': {'small': 0, 'medium': 0, 'large': 0},
            'most_connected': [],
            'recently_modified': []
        }

        for entity in self.file_entities.values():
            # Category stats
            category = entity.file_category.value
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

            # Realm stats
            realm = entity.stat7.realm.value
            stats['by_realm'][realm] = stats['by_realm'].get(realm, 0) + 1

            # Horizon stats
            horizon = entity.stat7.horizon.value
            stats['by_horizon'][horizon] = stats['by_horizon'].get(horizon, 0) + 1

            # Polarity stats
            polarity = entity.stat7.polarity.value
            stats['by_polarity'][polarity] = stats['by_polarity'].get(polarity, 0) + 1

            # Complexity distribution
            if entity.intent.complexity_score < 0.3:
                stats['complexity_distribution']['low'] += 1
            elif entity.intent.complexity_score < 0.7:
                stats['complexity_distribution']['medium'] += 1
            else:
                stats['complexity_distribution']['high'] += 1

            # Size distribution
            if entity.metrics.line_count < 50:
                stats['size_distribution']['small'] += 1
            elif entity.metrics.line_count < 200:
                stats['size_distribution']['medium'] += 1
            else:
                stats['size_distribution']['large'] += 1

        # Most connected files
        stats['most_connected'] = sorted(
            self.file_entities.values(),
            key=lambda e: len(e.imports_files) + len(e.imported_by_files),
            reverse=True
        )[:10]

        # Recently modified
        stats['recently_modified'] = sorted(
            self.file_entities.values(),
            key=lambda e: e.metrics.last_modified,
            reverse=True
        )[:10]

        return stats

    def save_index(self):
        """Save index to file"""
        index_data = {
            'version': '1.0.0',
            'created_at': datetime.utcnow().isoformat(),
            'project_root': str(self.project_root),
            'file_entities': {
                entity_id: entity.to_dict()
                for entity_id, entity in self.file_entities.items()
            },
            'path_to_entity_id': self.path_to_entity_id
        }

        with open(self.index_file, 'w') as f:
            json.dump(index_data, f, indent=2, default=str)

    def load_index(self):
        """Load index from file"""
        if not self.index_file.exists():
            return

        try:
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)

            # Recreate entities (simplified - would need proper deserialization)
            for entity_id, entity_data in index_data.get('file_entities', {}).items():
                # This is a simplified version - full implementation would need
                # proper STAT7Entity deserialization
                pass

            self.path_to_entity_id = index_data.get('path_to_entity_id', {})

        except Exception as e:
            print(f"Error loading index: {e}")
            # Start fresh if index is corrupted
            self.file_entities.clear()
            self.path_to_entity_id.clear()


if __name__ == "__main__":
    # Example usage
    project_root = Path(".")
    index = STAT7FileIndex(project_root)

    # Scan project
    results = index.scan_project()
    print(f"Scan results: {results}")

    # Get statistics
    stats = index.get_project_statistics()
    print(f"Project statistics: {stats}")
