#!/usr/bin/env python3
"""
STAT7 File Watcher
Automated file system monitoring for living project index.

Provides:
- Real-time file change detection
- Automatic index updates
- Event-driven reindexing
- Performance optimization
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, Set, Callable, Optional
import logging

# Try to import watchdog, make it optional
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    Observer = None
    FileSystemEventHandler = None
    FileModifiedEvent = None
    FileCreatedEvent = None
    FileDeletedEvent = None
    WATCHDOG_AVAILABLE = False

from stat7_file_index import STAT7FileIndex


class STAT7FileWatcher(FileSystemEventHandler):
    """
    File system event handler for STAT7 file indexing.

    Monitors file changes and triggers automatic index updates.
    """

    def __init__(self, file_index: STAT7FileIndex, debounce_seconds: float = 2.0):
        if not WATCHDOG_AVAILABLE:
            raise ImportError("watchdog package is required for file watching. Install with: pip install watchdog")

        self.file_index = file_index
        self.debounce_seconds = debounce_seconds

        # Debouncing
        self.pending_changes: Dict[str, float] = {}
        self.debounce_task: Optional[asyncio.Task] = None

        # Event callbacks
        self.on_file_changed: Optional[Callable] = None
        self.on_file_created: Optional[Callable] = None
        self.on_file_deleted: Optional[Callable] = None

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Performance tracking
        self.last_update_time = 0
        self.update_count = 0

    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._schedule_update(event.src_path, "modified")

    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._schedule_update(event.src_path, "created")

    def on_deleted(self, event):
        """Handle file deletion events"""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._schedule_update(event.src_path, "deleted")

    def _should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed"""
        path = Path(file_path)

        # Check extension
        if path.suffix.lower() not in self.file_index.include_extensions:
            return False

        # Check exclude patterns
        path_str = str(path)
        for pattern in self.file_index.exclude_patterns:
            if pattern in path_str:
                return False

        return True

    def _schedule_update(self, file_path: str, event_type: str):
        """Schedule file update with debouncing"""
        self.pending_changes[file_path] = time.time()

        # Cancel existing debounce task
        if self.debounce_task and not self.debounce_task.done():
            self.debounce_task.cancel()

        # Schedule new debounce task
        self.debounce_task = asyncio.create_task(self._debounced_update())

    async def _debounced_update(self):
        """Process pending changes after debounce period"""
        await asyncio.sleep(self.debounce_seconds)

        if not self.pending_changes:
            return

        # Process changes
        current_time = time.time()
        files_to_update = []

        for file_path, change_time in list(self.pending_changes.items()):
            if current_time - change_time >= self.debounce_seconds:
                files_to_update.append(file_path)
                del self.pending_changes[file_path]

        if files_to_update:
            await self._process_file_changes(files_to_update)

    async def _process_file_changes(self, file_paths: list):
        """Process batch of file changes"""
        try:
            update_start = time.time()

            for file_path in file_paths:
                path = Path(file_path)
                relative_path = str(path.relative_to(self.file_index.project_root))

                if path.exists():
                    # File was created or modified
                    entity = self.file_index.get_file_entity(relative_path)
                    if entity:
                        # Update existing entity
                        entity.update_from_file()
                        self.logger.info(f"Updated file entity: {relative_path}")
                        if self.on_file_changed:
                            self.on_file_changed(relative_path, entity)
                    else:
                        # Create new entity
                        from stat7_file_index import STAT7FileEntity
                        entity = STAT7FileEntity(file_path=path)
                        self.file_index.file_entities[entity.entity_id] = entity
                        self.file_index.path_to_entity_id[relative_path] = entity.entity_id
                        self.logger.info(f"Created file entity: {relative_path}")
                        if self.on_file_created:
                            self.on_file_created(relative_path, entity)
                else:
                    # File was deleted
                    if relative_path in self.file_index.path_to_entity_id:
                        entity_id = self.file_index.path_to_entity_id[relative_path]
                        del self.file_index.file_entities[entity_id]
                        del self.file_index.path_to_entity_id[relative_path]
                        self.logger.info(f"Deleted file entity: {relative_path}")
                        if self.on_file_deleted:
                            self.on_file_deleted(relative_path)

            # Rebuild relationships after batch update
            self.file_index._build_relationships()

            # Save updated index
            self.file_index.save_index()

            # Update performance tracking
            self.update_count += 1
            self.last_update_time = time.time()
            update_duration = time.time() - update_start

            self.logger.info(f"Processed {len(file_paths)} file changes in {update_duration:.3f}s")

        except Exception as e:
            self.logger.error(f"Error processing file changes: {e}")


class STAT7LivingIndex:
    """
    Living project index with automatic file monitoring.

    Combines STAT7FileIndex with STAT7FileWatcher for real-time updates.
    """

    def __init__(self, project_root: Path, watch: bool = True):
        self.project_root = Path(project_root)
        self.file_index = STAT7FileIndex(project_root)
        self.observer: Optional[Observer] = None
        self.watcher: Optional[STAT7FileWatcher] = None

        # Event tracking
        self.update_callbacks: Dict[str, Callable] = {}

        if watch:
            self.start_watching()

    def start_watching(self):
        """Start file system monitoring"""
        if not WATCHDOG_AVAILABLE:
            print("⚠️ File watching not available - install watchdog package: pip install watchdog")
            return

        if self.observer and self.observer.is_alive():
            return

        # Create watcher
        self.watcher = STAT7FileWatcher(self.file_index)
        self.watcher.on_file_changed = self._on_file_changed
        self.watcher.on_file_created = self._on_file_created
        self.watcher.on_file_deleted = self._on_file_deleted

        # Setup observer
        self.observer = Observer()
        self.observer.schedule(self.watcher, str(self.project_root), recursive=True)
        self.observer.start()

        print(f"🔍 Started watching {self.project_root} for file changes")

    def stop_watching(self):
        """Stop file system monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("⏹️ Stopped file watching")

    def _on_file_changed(self, file_path: str, entity):
        """Handle file change events"""
        for callback_id, callback in self.update_callbacks.items():
            try:
                callback("changed", file_path, entity)
            except Exception as e:
                print(f"Error in callback {callback_id}: {e}")

    def _on_file_created(self, file_path: str, entity):
        """Handle file creation events"""
        for callback_id, callback in self.update_callbacks.items():
            try:
                callback("created", file_path, entity)
            except Exception as e:
                print(f"Error in callback {callback_id}: {e}")

    def _on_file_deleted(self, file_path: str):
        """Handle file deletion events"""
        for callback_id, callback in self.update_callbacks.items():
            try:
                callback("deleted", file_path, None)
            except Exception as e:
                print(f"Error in callback {callback_id}: {e}")

    def add_update_callback(self, callback_id: str, callback: Callable):
        """Add callback for file update events"""
        self.update_callbacks[callback_id] = callback

    def remove_update_callback(self, callback_id: str):
        """Remove file update callback"""
        if callback_id in self.update_callbacks:
            del self.update_callbacks[callback_id]

    def force_reindex(self):
        """Force complete project reindex"""
        print("🔄 Starting complete project reindex...")
        results = self.file_index.scan_project(force_reindex=True)
        print(f"✅ Reindex complete: {results}")
        return results

    def get_index(self) -> STAT7FileIndex:
        """Get the underlying file index"""
        return self.file_index

    def get_status(self) -> Dict[str, any]:
        """Get living index status"""
        return {
            'watching': self.observer and self.observer.is_alive(),
            'project_root': str(self.project_root),
            'total_files': len(self.file_index.file_entities),
            'update_count': self.watcher.update_count if self.watcher else 0,
            'last_update': self.watcher.last_update_time if self.watcher else None,
            'pending_changes': len(self.watcher.pending_changes) if self.watcher else 0
        }


async def main():
    """Example usage of STAT7LivingIndex"""
    project_root = Path(".")

    # Create living index
    living_index = STAT7LivingIndex(project_root, watch=True)

    # Add callback for file changes
    def on_file_update(event_type: str, file_path: str, entity):
        print(f"📝 {event_type.upper()}: {file_path}")
        if entity:
            print(f"   STAT7: {entity.stat7.address}")
            print(f"   Intent: {entity.intent.primary_intent or 'No intent'}")

    living_index.add_update_callback("demo", on_file_update)

    # Initial scan
    living_index.force_reindex()

    # Keep running
    try:
        while True:
            await asyncio.sleep(10)
            status = living_index.get_status()
            print(f"📊 Status: {status['total_files']} files, {status['pending_changes']} pending changes")
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        living_index.stop_watching()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run example
    asyncio.run(main())
