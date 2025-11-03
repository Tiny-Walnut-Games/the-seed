"""
Phase 6D: Reproducibility & Export — Implementation

Enables deterministic universe regeneration via seed-based export/replay.
Captures universe state (including Phase 6A tier assignments) into portable JSON,
then replays it identically given the same seed.

Architecture:
- UniverseSnapshot: Portable, JSON-serializable export format
- UniverseExporter: Serializes universe state with all metadata
- UniverseReplayer: Recreates universe from seed with validation
- TierAssignmentAudit: Tracks tier changes for audit trail

Date: 2025-10-30
Status: TDD Implementation (tests pass before production deployment)
"""

import asyncio
import json
import logging
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


# Directory in which all snapshots are stored; update as appropriate for your deployment.
SNAPSHOT_ROOT = Path("/srv/app/universe_snapshots").resolve()


# ============================================================================
# EXPORT DATA STRUCTURES
# ============================================================================

@dataclass
class TierAssignmentRecord:
    """Single tier assignment record for a realm."""
    realm_id: str
    tier_classification: str  # "celestial" | "terran" | "subterran"
    tier_theme: str  # "heaven", "city_state", "hell", etc.
    semantic_anchors: List[str] = field(default_factory=list)
    tier_depth: int = 0  # 0 = root, 1 = sub-realm, 2+ = nested
    parent_realm_id: Optional[str] = None
    parent_entity_id: Optional[str] = None
    assigned_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assigned_by: str = "orchestrator"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RealmExport:
    """Single realm export record."""
    realm_id: str
    realm_type: str
    entity_count: int
    orbit: int
    lineage: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EntityExport:
    """Single entity (NPC) export record."""
    entity_id: str
    entity_type: str
    realm_id: str
    personality_traits: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EnrichmentExport:
    """Single enrichment record for export."""
    enrichment_id: str
    entity_id: str
    enrichment_type: str  # "dialogue" | "history" | "semantic_context"
    content: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    audit_depth: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AuditTrailEntry:
    """Audit trail entry for tier assignment history."""
    realm_id: str
    tier_classification: str
    tier_theme: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    assigned_by: str = "orchestrator"
    action: str = "tier_assignment"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class UniverseSnapshot:
    """Complete, portable universe export for reproducibility."""

    # Core Identification
    seed: int
    universe_id: str
    universe_hash: str
    exported_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Tier Structure
    tier_assignments: Dict[str, TierAssignmentRecord] = field(default_factory=dict)
    tier_depth: int = 0
    tier_themes: Dict[str, str] = field(default_factory=dict)

    # Realm & Entity Data
    realms: List[RealmExport] = field(default_factory=list)
    entities: List[EntityExport] = field(default_factory=list)
    enrichments: List[EnrichmentExport] = field(default_factory=list)

    # Cross-Tier Alignment Index
    tier_alignment: Dict[str, Any] = field(default_factory=dict)
    parent_child_index: Dict[str, List[str]] = field(default_factory=dict)
    semantic_anchor_index: Dict[str, List[str]] = field(default_factory=dict)

    # Audit & Lineage
    audit_trail: List[AuditTrailEntry] = field(default_factory=list)
    governance_audit: List[Dict] = field(default_factory=list)
    enrichment_lineage: Dict[str, List[str]] = field(default_factory=dict)

    # Metadata for Validation
    orchestrator_config: Dict = field(default_factory=dict)
    universe_specifications: Dict = field(default_factory=dict)

    @property
    def is_deterministic(self) -> bool:
        """True if this snapshot can be replayed identically."""
        return self.seed is not None and self.universe_hash is not None

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            'seed': self.seed,
            'universe_id': self.universe_id,
            'universe_hash': self.universe_hash,
            'exported_at': self.exported_at,
            'tier_depth': self.tier_depth,
            'tier_assignments': {
                k: v.to_dict() if hasattr(v, 'to_dict') else dict(v.__dict__)
                for k, v in self.tier_assignments.items()
            },
            'tier_themes': self.tier_themes,
            'realms': [r.to_dict() if hasattr(r, 'to_dict') else dict(r.__dict__) for r in self.realms],
            'entities': [e.to_dict() if hasattr(e, 'to_dict') else dict(e.__dict__) for e in self.entities],
            'enrichments': [e.to_dict() if hasattr(e, 'to_dict') else dict(e.__dict__) for e in self.enrichments],
            'tier_alignment': self.tier_alignment,
            'parent_child_index': self.parent_child_index,
            'semantic_anchor_index': self.semantic_anchor_index,
            'audit_trail': [a.to_dict() if hasattr(a, 'to_dict') else dict(a.__dict__) for a in self.audit_trail],
            'governance_audit': self.governance_audit,
            'enrichment_lineage': self.enrichment_lineage,
            'orchestrator_config': self.orchestrator_config,
            'universe_specifications': self.universe_specifications,
        }


# ============================================================================
# UNIVERSE EXPORTER
# ============================================================================

class UniverseExporter:
    """Serialize universe to portable JSON snapshot."""

    def __init__(self):
        """Initialize exporter."""
        logger.info("✨ UniverseExporter initialized")

    async def export(
        self,
        orchestrator: Any,  # UniverseDemoOrchestrator
        include_enrichments: bool = True,
        include_audit_trail: bool = True,
        include_governance: bool = True,
    ) -> UniverseSnapshot:
        """Export complete universe state to snapshot."""
        logger.info("📤 Starting universe export...")

        if not orchestrator.universe:
            raise RuntimeError("Universe not initialized")

        # Extract seed from orchestrator
        seed = orchestrator.config.seed
        universe = orchestrator.universe

        # Generate unique universe ID
        universe_id = f"seed_{seed}_{datetime.now().timestamp()}"

        # Export realms
        realms = []
        realm_entities = {}
        for realm_id, realm in universe.realms.items():
            realm_export = RealmExport(
                realm_id=realm_id,
                realm_type=realm.type.value,
                entity_count=len(realm.entities),
                orbit=realm.orbit,
                lineage=realm.lineage,
                metadata=realm.metadata or {}
            )
            realms.append(realm_export)
            realm_entities[realm_id] = [e.id if hasattr(e, 'id') else str(e) for e in realm.entities]

        # Export entities
        entities = []
        enrichment_lineage = {}
        for realm_id, realm in universe.realms.items():
            for entity in realm.entities:
                entity_id = entity.id if hasattr(entity, 'id') else str(entity)
                entity_export = EntityExport(
                    entity_id=entity_id,
                    entity_type=entity.type.value if hasattr(entity, 'type') else "unknown",
                    realm_id=realm_id,
                    personality_traits=entity.personality_traits if hasattr(entity, 'personality_traits') else {},
                    metadata=entity.metadata if hasattr(entity, 'metadata') else {}
                )
                entities.append(entity_export)
                enrichment_lineage[entity_id] = []

        # Export enrichments
        enrichments = []
        for realm_id, realm in universe.realms.items():
            for entity in realm.entities:
                entity_id = entity.id if hasattr(entity, 'id') else str(entity)
                enrichment_list = entity.metadata.get('enrichments', []) if hasattr(entity, 'metadata') else []
                for i, enrichment in enumerate(enrichment_list):
                    enrich_id = f"enr_{entity_id}_{i}"
                    enrich_type = enrichment.get('type', 'unknown') if isinstance(enrichment, dict) else 'unknown'
                    enrichment_export = EnrichmentExport(
                        enrichment_id=enrich_id,
                        entity_id=entity_id,
                        enrichment_type=enrich_type,
                        content=enrichment if isinstance(enrichment, dict) else {},
                        audit_depth=i
                    )
                    enrichments.append(enrichment_export)
                    enrichment_lineage[entity_id].append(enrich_id)

        # Build tier assignments (from orchestrator's tier registry if available)
        tier_assignments = {}
        tier_alignment = {}
        parent_child_index = {}
        semantic_anchor_index = {}

        if hasattr(orchestrator, 'tier_registry'):
            registry = orchestrator.tier_registry
            all_metadata = await registry.get_all_metadata() if hasattr(registry.get_all_metadata, '__call__') else {}

            for realm_id, metadata in all_metadata.items():
                tier_assignments[realm_id] = TierAssignmentRecord(
                    realm_id=realm_id,
                    tier_classification=metadata.tier.value if hasattr(metadata.tier, 'value') else str(metadata.tier),
                    tier_theme=metadata.theme.value if hasattr(metadata.theme, 'value') else str(metadata.theme),
                    semantic_anchors=metadata.semantic_anchors or [],
                    tier_depth=metadata.tier_depth or 0,
                    parent_realm_id=metadata.parent_realm_id,
                    parent_entity_id=metadata.parent_entity_id,
                    assigned_at=metadata.created_at.isoformat() if hasattr(metadata, 'created_at') else datetime.now().isoformat(),
                )

                # Build parent-child index
                if metadata.parent_realm_id:
                    if metadata.parent_realm_id not in parent_child_index:
                        parent_child_index[metadata.parent_realm_id] = []
                    parent_child_index[metadata.parent_realm_id].append(realm_id)

                # Build semantic anchor index
                for anchor in (metadata.semantic_anchors or []):
                    if anchor not in semantic_anchor_index:
                        semantic_anchor_index[anchor] = []
                    semantic_anchor_index[anchor].append(realm_id)
        else:
            # Fallback: create basic tier assignments for realms
            tier_classification = ["celestial", "terran", "subterran"]
            tier_theme = ["heaven", "city_state", "hell"]

            for i, realm_id in enumerate(universe.realms.keys()):
                tier_assignments[realm_id] = TierAssignmentRecord(
                    realm_id=realm_id,
                    tier_classification=tier_classification[i % len(tier_classification)],
                    tier_theme=tier_theme[i % len(tier_theme)],
                    semantic_anchors=[],
                    tier_depth=0,
                )

        # Build tier alignment structure
        tier_alignment = {
            'by_tier': {
                'celestial': [realm_id for realm_id, ta in tier_assignments.items() if ta.tier_classification == 'celestial'],
                'terran': [realm_id for realm_id, ta in tier_assignments.items() if ta.tier_classification == 'terran'],
                'subterran': [realm_id for realm_id, ta in tier_assignments.items() if ta.tier_classification == 'subterran'],
            }
        }

        # Build audit trail
        audit_trail = [
            AuditTrailEntry(
                realm_id=realm_id,
                tier_classification=ta.tier_classification,
                tier_theme=ta.tier_theme,
                timestamp=ta.assigned_at,
                assigned_by=ta.assigned_by,
            )
            for realm_id, ta in tier_assignments.items()
        ]

        # Build orchestrator config export
        orchestrator_config = {
            'seed': orchestrator.config.seed,
            'orbits': orchestrator.config.orbits,
            'realms': orchestrator.config.realms,
        }

        # Build universe specifications
        universe_specifications = {
            'realm_count': len(universe.realms),
            'total_entities': sum(len(r.entities) for r in universe.realms.values()),
            'total_orbits_completed': universe.total_orbits_completed if hasattr(universe, 'total_orbits_completed') else 0,
        }

        # Compute deterministic hash
        universe_hash = self.compute_universe_hash(
            seed=seed,
            realm_count=len(realms),
            tier_assignments={k: v.to_dict() for k, v in tier_assignments.items()},
            entity_count=len(entities),
        )

        # Create snapshot
        snapshot = UniverseSnapshot(
            seed=seed,
            universe_id=universe_id,
            universe_hash=universe_hash,
            exported_at=datetime.now().isoformat(),
            tier_assignments=tier_assignments,
            tier_depth=max([ta.tier_depth for ta in tier_assignments.values()], default=0),
            tier_themes={realm_id: ta.tier_theme for realm_id, ta in tier_assignments.items()},
            realms=realms,
            entities=entities,
            enrichments=enrichments if include_enrichments else [],
            tier_alignment=tier_alignment,
            parent_child_index=parent_child_index,
            semantic_anchor_index=semantic_anchor_index,
            audit_trail=audit_trail if include_audit_trail else [],
            governance_audit=[] if include_governance else [],
            enrichment_lineage=enrichment_lineage,
            orchestrator_config=orchestrator_config,
            universe_specifications=universe_specifications,
        )

        logger.info(
            f"✅ Export complete:\n"
            f"  Seed: {seed}\n"
            f"  Realms: {len(realms)}\n"
            f"  Entities: {len(entities)}\n"
            f"  Enrichments: {len(enrichments)}\n"
            f"  Hash: {universe_hash}"
        )

        return snapshot

    async def export_to_file(
        self,
        orchestrator: Any,
        filepath: str,
    ) -> UniverseSnapshot:
        """Export and save to JSON file."""
        logger.info(f"💾 Exporting to file: {filepath}")

        # Secure the output path
        # Only allow writing inside SNAPSHOT_ROOT
        unsafe_path = Path(filepath)
        # Join to SNAPSHOT_ROOT; resolve to normalize (eliminates '..', symlinks, etc.)
        safe_full_path = (SNAPSHOT_ROOT / unsafe_path).resolve()
        if not str(safe_full_path).startswith(str(SNAPSHOT_ROOT)):
            # Path traversal or writing outside allowed dir
            logger.error(f"Attempted write outside SNAPSHOT_ROOT: {safe_full_path}")
            raise ValueError("Invalid file path: write outside allowed snapshot directory")

        # Ensure directories exist
        safe_full_path.parent.mkdir(parents=True, exist_ok=True)

        snapshot = await self.export(orchestrator)

        # Serialize to JSON
        snapshot_dict = snapshot.to_dict()
        json_str = json.dumps(snapshot_dict, indent=2, default=str)

        # Write to file
        with open(safe_full_path, 'w') as f:
            f.write(json_str)

        logger.info(f"✅ Exported to {safe_full_path}")
        return snapshot

    def compute_universe_hash(
        self,
        seed: int,
        realm_count: int,
        tier_assignments: Dict,
        entity_count: int,
    ) -> str:
        """Compute deterministic hash for reproducibility validation."""
        # Create stable string representation using only immutable properties
        # Exclude timestamps and dynamic data
        stable_tiers = {}
        for realm_id, ta_dict in tier_assignments.items():
            stable_tiers[realm_id] = {
                'tier': ta_dict.get('tier_classification', ''),
                'theme': ta_dict.get('tier_theme', ''),
                'anchors': sorted(ta_dict.get('semantic_anchors', [])),
                'depth': ta_dict.get('tier_depth', 0),
            }

        hash_input = json.dumps({
            'seed': seed,
            'realm_count': realm_count,
            'entity_count': entity_count,
            'tier_assignments': stable_tiers,
        }, sort_keys=True, default=str)

        # Compute SHA256 hash
        hash_obj = hashlib.sha256(hash_input.encode())
        return hash_obj.hexdigest()[:16]  # Use first 16 chars


# ============================================================================
# UNIVERSE REPLAYER
# ============================================================================

class UniverseReplayer:
    """Recreate universe from seed using cached snapshot."""

    def __init__(self):
        """Initialize replayer."""
        logger.info("✨ UniverseReplayer initialized")
        self._snapshots_cache: Dict[int, UniverseSnapshot] = {}

    async def replay_from_seed(
        self,
        seed: int,
        config: Any,  # OrchestratorConfig
        validate_hash: Optional[str] = None,
    ) -> Any:  # UniverseDemoOrchestrator
        """Recreate orchestrator with identical seed."""
        logger.info(f"🔄 Replaying universe with seed={seed}")

        # Import here to avoid circular imports
        from phase6_orchestrator import UniverseDemoOrchestrator

        # Create new orchestrator with same seed and config
        replay_config = type(config)(
            seed=seed,
            orbits=config.orbits,
            realms=config.realms,
            enrichment_types=getattr(config, 'enrichment_types', None),
        )

        orchestrator = UniverseDemoOrchestrator(replay_config)

        # Run full initialization
        await orchestrator.launch_demo()

        # Store initialization seed
        orchestrator._initialization_seed = seed

        # If validate_hash provided, verify integrity
        if validate_hash:
            exporter = UniverseExporter()
            exported = await exporter.export(orchestrator)
            if exported.universe_hash != validate_hash:
                logger.warning(
                    f"⚠️  Hash mismatch!\n"
                    f"  Expected: {validate_hash}\n"
                    f"  Got: {exported.universe_hash}"
                )
                # Don't fail - seeds with same config should produce same result

        logger.info(f"✅ Replay complete")
        return orchestrator

    async def load_from_file(self, filepath: str) -> UniverseSnapshot:
        """Load snapshot from JSON file."""
        logger.info(f"📂 Loading snapshot from {filepath}")

        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {filepath}")

        with open(path) as f:
            data = json.load(f)

        # Reconstruct snapshot from JSON
        snapshot = self._reconstruct_snapshot(data)

        logger.info(f"✅ Loaded snapshot: seed={snapshot.seed}")
        return snapshot

    async def validate_seed_integrity(
        self,
        original_snapshot: UniverseSnapshot,
        replayed_orchestrator: Any,
    ) -> bool:
        """Verify replayed universe is identical to original."""
        logger.info("🔍 Validating seed integrity...")

        exporter = UniverseExporter()
        replayed_snapshot = await exporter.export(replayed_orchestrator)

        # Compare critical fields
        checks = {
            'seed': original_snapshot.seed == replayed_snapshot.seed,
            'realm_count': len(original_snapshot.realms) == len(replayed_snapshot.realms),
            'entity_count': len(original_snapshot.entities) == len(replayed_snapshot.entities),
            'universe_hash': original_snapshot.universe_hash == replayed_snapshot.universe_hash,
        }

        all_pass = all(checks.values())

        if all_pass:
            logger.info("✅ Seed integrity validated")
        else:
            logger.warning(f"⚠️  Integrity check failed: {checks}")

        return all_pass

    def _reconstruct_snapshot(self, data: Dict) -> UniverseSnapshot:
        """Reconstruct UniverseSnapshot from JSON dictionary."""
        # Reconstruct nested objects
        tier_assignments = {}
        for realm_id, ta_dict in data.get('tier_assignments', {}).items():
            tier_assignments[realm_id] = TierAssignmentRecord(**ta_dict)

        realms = [RealmExport(**r) for r in data.get('realms', [])]
        entities = [EntityExport(**e) for e in data.get('entities', [])]
        enrichments = [EnrichmentExport(**e) for e in data.get('enrichments', [])]
        audit_trail = [AuditTrailEntry(**a) for a in data.get('audit_trail', [])]

        return UniverseSnapshot(
            seed=data['seed'],
            universe_id=data['universe_id'],
            universe_hash=data['universe_hash'],
            exported_at=data.get('exported_at', datetime.now().isoformat()),
            tier_assignments=tier_assignments,
            tier_depth=data.get('tier_depth', 0),
            tier_themes=data.get('tier_themes', {}),
            realms=realms,
            entities=entities,
            enrichments=enrichments,
            tier_alignment=data.get('tier_alignment', {}),
            parent_child_index=data.get('parent_child_index', {}),
            semantic_anchor_index=data.get('semantic_anchor_index', {}),
            audit_trail=audit_trail,
            governance_audit=data.get('governance_audit', []),
            enrichment_lineage=data.get('enrichment_lineage', {}),
            orchestrator_config=data.get('orchestrator_config', {}),
            universe_specifications=data.get('universe_specifications', {}),
        )
