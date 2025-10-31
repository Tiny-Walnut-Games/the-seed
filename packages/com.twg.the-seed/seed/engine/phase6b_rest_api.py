"""
Phase 6B: REST API Layer

FastAPI server that exposes Phase 6A orchestrator and Phase 6-Alpha hierarchical realms
via REST endpoints for university demonstration and production use.

Architecture:
- Wraps UniverseDemoOrchestrator (Phase 6A)
- Exposes HierarchicalUniverseAdapter (Phase 6-Alpha)
- Provides Phase 2-4 bridge data (NPCs, semantic contexts, dialogue state)
- Supports reproducible universe export

Date: 2025-10-31 (Halloween)
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json

try:
    from fastapi import FastAPI, HTTPException, Path as PathParam, Body
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: FastAPI not available. Install with: pip install fastapi uvicorn")

# Import Phase 6A orchestrator
from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig, DemoUniverseMetadata

# Import Phase 6-Alpha hierarchical realms
from phase6_hierarchical_realms import (
    TierClassification, TierTheme, RealmTierMetadata,
    HierarchicalUniverseAdapter
)

# Import Phase 5 structures
from phase5_bigbang import Universe, RealmData, Entity

# Import Phase 5→2-4 bridge
from phase5_to_phase2_bridge import Phase5Phase2Phase3Phase4Bridge


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ============================================================================
# PYDANTIC REQUEST/RESPONSE MODELS
# ============================================================================

class ZoomRequest(BaseModel):
    """Request to create a sub-realm via entity zoom."""
    entity_id: str
    additional_anchors: List[str] = []


class RealmSummary(BaseModel):
    """Realm summary for list responses."""
    realm_id: str
    entity_count: int
    lineage: int
    tier: Optional[str] = None
    theme: Optional[str] = None


class RealmDetail(BaseModel):
    """Detailed realm information."""
    realm_id: str
    entity_count: int
    lineage: int
    entities: List[Dict[str, Any]]
    tier: Optional[str] = None
    theme: Optional[str] = None
    semantic_anchors: List[str] = []


class TierMetadata(BaseModel):
    """Tier classification metadata."""
    realm_id: str
    tier: str
    theme: str
    semantic_anchors: List[str]
    tier_depth: int
    parent_realm_id: Optional[str] = None
    parent_entity_id: Optional[str] = None


class NPCSummary(BaseModel):
    """NPC summary for list responses."""
    npc_id: str
    npc_name: str
    realm_id: str
    entity_type: str


class NPCDetail(BaseModel):
    """Detailed NPC information."""
    npc_id: str
    npc_name: str
    realm_id: str
    entity_type: str
    stat7_coordinates: Dict[str, int]
    personality_traits: Dict[str, Any]
    enrichment_history: List[Dict[str, Any]]


class DialogueContext(BaseModel):
    """Dialogue context for Phase 4 integration."""
    npc_id: str
    realm_id: str
    location_type: str
    time_of_day: str
    npc_mood: str
    narrative_phase: str
    dialogue_turn: int
    enrichment_depth: int


class SubRealmCreated(BaseModel):
    """Response after creating sub-realm."""
    sub_realm_id: str
    parent_realm_id: str
    entity_id: str
    tier: str
    theme: str
    tier_depth: int
    semantic_anchors: List[str]


class UniverseExport(BaseModel):
    """Full universe export for reproducibility."""
    seed: int
    total_orbits_completed: int
    total_entities: int
    initialization_time_ms: float
    realms: Dict[str, Any]
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    orchestrator_initialized: bool


# ============================================================================
# PHASE 6B API SERVER
# ============================================================================

class Phase6BAPIServer:
    """
    FastAPI REST API server for Phase 6B.
    
    Wraps Phase 6A orchestrator and Phase 6-Alpha hierarchical realms
    to provide HTTP endpoints for realm queries, NPC queries, dialogue context,
    and universe export.
    """
    
    def __init__(self, orchestrator: UniverseDemoOrchestrator):
        """
        Initialize API server with an orchestrator.
        
        Args:
            orchestrator: Initialized UniverseDemoOrchestrator
        """
        self.orchestrator = orchestrator
        self.app = FastAPI(
            title="Phase 6B - The Seed Multiverse API",
            description="REST API for The Seed multiverse simulation system",
            version="6B-Alpha",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Hierarchical universe adapter (Phase 6-Alpha)
        self.hierarchical_adapter: Optional[HierarchicalUniverseAdapter] = None
        
        # Initialize routes
        self._setup_routes()
        
        logger.info("🌐 Phase 6B API Server initialized")
    
    def _setup_routes(self):
        """Register all API routes."""
        
        # Health check
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "orchestrator_initialized": self.orchestrator.universe is not None
            }
        
        # ====================================================================
        # REALM ENDPOINTS
        # ====================================================================
        
        @self.app.get("/api/realms", response_model=Dict[str, List[RealmSummary]])
        async def list_realms():
            """List all realms with tier classification."""
            if not self.orchestrator.universe:
                raise HTTPException(status_code=503, detail="Universe not initialized")
            
            realms = []
            for realm_id, realm_data in self.orchestrator.universe.realms.items():
                realm_summary = {
                    "realm_id": realm_id,
                    "entity_count": len(realm_data.entities),
                    "lineage": realm_data.lineage,
                }
                
                # Add tier info if available
                if self.hierarchical_adapter:
                    try:
                        tier_meta = await self.hierarchical_adapter.tier_registry.get_realm_tier(realm_id)
                        if tier_meta:
                            realm_summary["tier"] = tier_meta.tier.value
                            realm_summary["theme"] = tier_meta.theme.value
                    except:
                        pass
                
                realms.append(realm_summary)
            
            return {"realms": realms}
        
        @self.app.get("/api/realms/{realm_id}", response_model=RealmDetail)
        async def get_realm(realm_id: str = PathParam(..., description="Realm ID")):
            """Get detailed realm information."""
            if not self.orchestrator.universe:
                raise HTTPException(status_code=503, detail="Universe not initialized")
            
            realm_data = self.orchestrator.universe.realms.get(realm_id)
            if not realm_data:
                raise HTTPException(status_code=404, detail={"error": f"Realm '{realm_id}' not found"})
            
            realm_detail = {
                "realm_id": realm_id,
                "entity_count": len(realm_data.entities),
                "lineage": realm_data.lineage,
                "entities": [self._entity_to_dict(e) for e in realm_data.entities],
            }
            
            # Add tier info if available
            if self.hierarchical_adapter:
                try:
                    tier_meta = await self.hierarchical_adapter.tier_registry.get_metadata(realm_id)
                    if tier_meta:
                        realm_detail["tier"] = tier_meta.tier.value
                        realm_detail["theme"] = tier_meta.theme.value
                        realm_detail["semantic_anchors"] = tier_meta.semantic_anchors
                except:
                    pass
            
            return realm_detail
        
        @self.app.get("/api/realms/{realm_id}/tier", response_model=TierMetadata)
        async def get_realm_tier(realm_id: str = PathParam(..., description="Realm ID")):
            """Get tier classification metadata for a realm."""
            if not self.hierarchical_adapter:
                raise HTTPException(status_code=503, detail="Hierarchical adapter not initialized")
            
            tier_meta = await self.hierarchical_adapter.tier_registry.get_metadata(realm_id)
            if not tier_meta:
                raise HTTPException(status_code=404, detail={"error": f"Tier metadata for realm '{realm_id}' not found"})
            
            return tier_meta.to_dict()
        
        # ====================================================================
        # TIER QUERY ENDPOINTS
        # ====================================================================
        
        @self.app.get("/api/realms/by-tier/{tier}", response_model=Dict[str, List[RealmSummary]])
        async def query_realms_by_tier(tier: str = PathParam(..., description="Tier classification")):
            """Query realms by tier (celestial, terran, subterran)."""
            if not self.hierarchical_adapter:
                raise HTTPException(status_code=503, detail="Hierarchical adapter not initialized")
            
            try:
                tier_enum = TierClassification(tier.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail={"error": f"Invalid tier: {tier}"})
            
            # Get realm IDs by tier, then fetch metadata for each
            realm_ids = await self.hierarchical_adapter.tier_registry.get_realms_by_tier(tier_enum)
            
            realms = []
            for realm_id in realm_ids:
                realm_data = self.orchestrator.universe.realms.get(realm_id)
                tier_meta = await self.hierarchical_adapter.tier_registry.get_metadata(realm_id)
                if realm_data and tier_meta:
                    realms.append({
                        "realm_id": realm_id,
                        "entity_count": len(realm_data.entities),
                        "lineage": realm_data.lineage,
                        "tier": tier_meta.tier.value,
                        "theme": tier_meta.theme.value,
                    })
            
            return {"realms": realms}
        
        @self.app.get("/api/realms/by-theme/{theme}", response_model=Dict[str, List[RealmSummary]])
        async def query_realms_by_theme(theme: str = PathParam(..., description="Tier theme")):
            """Query realms by theme (heaven, city_state, hell, etc)."""
            if not self.hierarchical_adapter:
                raise HTTPException(status_code=503, detail="Hierarchical adapter not initialized")
            
            try:
                theme_enum = TierTheme(theme.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail={"error": f"Invalid theme: {theme}"})
            
            # Get realm IDs by theme, then fetch metadata for each
            realm_ids = await self.hierarchical_adapter.tier_registry.get_realms_by_theme(theme_enum)
            
            realms = []
            for realm_id in realm_ids:
                realm_data = self.orchestrator.universe.realms.get(realm_id)
                tier_meta = await self.hierarchical_adapter.tier_registry.get_metadata(realm_id)
                if realm_data and tier_meta:
                    realms.append({
                        "realm_id": realm_id,
                        "entity_count": len(realm_data.entities),
                        "lineage": realm_data.lineage,
                        "tier": tier_meta.tier.value,
                        "theme": tier_meta.theme.value,
                    })
            
            return {"realms": realms}
        
        # ====================================================================
        # SUB-REALM ZOOM ENDPOINT
        # ====================================================================
        
        @self.app.post("/api/realms/{realm_id}/zoom", response_model=SubRealmCreated)
        async def create_sub_realm(
            realm_id: str = PathParam(..., description="Parent realm ID"),
            request: ZoomRequest = Body(...)
        ):
            """Create a sub-realm by zooming into an entity."""
            if not self.hierarchical_adapter:
                raise HTTPException(status_code=503, detail="Hierarchical adapter not initialized")
            
            # Verify realm exists
            realm_data = self.orchestrator.universe.realms.get(realm_id)
            if not realm_data:
                raise HTTPException(status_code=404, detail={"error": f"Realm '{realm_id}' not found"})
            
            # Verify entity exists
            entity = next((e for e in realm_data.entities if e.id == request.entity_id), None)
            if not entity:
                raise HTTPException(status_code=404, detail={"error": f"Entity '{request.entity_id}' not found in realm '{realm_id}'"})
            
            # Create sub-realm via zoom
            sub_realm_meta = await self.hierarchical_adapter.create_sub_realm(
                parent_realm_id=realm_id,
                entity_id=request.entity_id,
                additional_anchors=request.additional_anchors
            )
            
            return {
                "sub_realm_id": sub_realm_meta.realm_id,
                "parent_realm_id": sub_realm_meta.parent_realm_id,
                "entity_id": sub_realm_meta.parent_entity_id,
                "tier": sub_realm_meta.tier.value,
                "theme": sub_realm_meta.theme.value,
                "tier_depth": sub_realm_meta.tier_depth,
                "semantic_anchors": sub_realm_meta.semantic_anchors,
            }
        
        # ====================================================================
        # NPC ENDPOINTS
        # ====================================================================
        
        @self.app.get("/api/npcs", response_model=Dict[str, List[NPCSummary]])
        async def list_npcs():
            """List all NPCs across all realms."""
            if not self.orchestrator.bridge:
                raise HTTPException(status_code=503, detail="Bridge not initialized")
            
            npcs = []
            for npc_id, npc_reg in self.orchestrator.bridge.phase2_adapter.npc_registry.items():
                npcs.append({
                    "npc_id": npc_reg.npc_id,
                    "npc_name": npc_reg.npc_name,
                    "realm_id": npc_reg.realm_id,
                    "entity_type": npc_reg.entity_type,
                })
            
            return {"npcs": npcs}
        
        @self.app.get("/api/npcs/{npc_id}", response_model=NPCDetail)
        async def get_npc(npc_id: str = PathParam(..., description="NPC ID")):
            """Get detailed NPC information with personality traits."""
            if not self.orchestrator.bridge:
                raise HTTPException(status_code=503, detail="Bridge not initialized")
            
            npc_reg = self.orchestrator.bridge.phase2_adapter.get_npc_registration(npc_id)
            if not npc_reg:
                raise HTTPException(status_code=404, detail={"error": f"NPC '{npc_id}' not found"})
            
            return {
                "npc_id": npc_reg.npc_id,
                "npc_name": npc_reg.npc_name,
                "realm_id": npc_reg.realm_id,
                "entity_type": npc_reg.entity_type,
                "stat7_coordinates": npc_reg.stat7_coordinates,
                "personality_traits": npc_reg.personality_traits,
                "enrichment_history": npc_reg.enrichment_history,
            }
        
        @self.app.get("/api/npcs/{npc_id}/context", response_model=DialogueContext)
        async def get_npc_context(npc_id: str = PathParam(..., description="NPC ID")):
            """Get dialogue context for an NPC (Phase 4 integration)."""
            if not self.orchestrator.bridge:
                raise HTTPException(status_code=503, detail="Bridge not initialized")
            
            npc_reg = self.orchestrator.bridge.phase2_adapter.get_npc_registration(npc_id)
            if not npc_reg:
                raise HTTPException(status_code=404, detail={"error": f"NPC '{npc_id}' not found"})
            
            # Get dialogue context from Phase 4 adapter
            context = self.orchestrator.bridge.phase4_adapter.get_dialogue_context(
                entity_id=npc_id,
                realm_id=npc_reg.realm_id,
                current_orbit=self.orchestrator.universe.current_orbit
            )
            
            return {
                "npc_id": npc_id,
                "realm_id": npc_reg.realm_id,
                "location_type": context.get("location_type", "unknown"),
                "time_of_day": context.get("time_of_day", "unknown"),
                "npc_mood": context.get("npc_mood", "neutral"),
                "narrative_phase": context.get("narrative_phase", "introduction"),
                "dialogue_turn": context.get("dialogue_turn", 0),
                "enrichment_depth": context.get("enrichment_depth", 0),
            }
        
        # ====================================================================
        # UNIVERSE EXPORT ENDPOINT
        # ====================================================================
        
        @self.app.get("/api/universe/export", response_model=UniverseExport)
        async def export_universe():
            """Export full universe metadata for reproducibility."""
            if not self.orchestrator.universe:
                raise HTTPException(status_code=503, detail="Universe not initialized")
            
            universe_export = self.orchestrator.get_universe_export()
            metadata = self.orchestrator.get_demo_metadata()
            
            return {
                "seed": self.orchestrator.config.seed,
                "total_orbits_completed": metadata.total_orbits_completed,
                "total_entities": metadata.total_entities,
                "initialization_time_ms": metadata.initialization_time_ms,
                "realms": universe_export.get("realms", {}),
                "metadata": {
                    "universe_initialized_at": metadata.universe_initialized_at,
                    "realm_entity_counts": metadata.realm_entity_counts,
                },
            }
    
    def _entity_to_dict(self, entity: Entity) -> Dict[str, Any]:
        """Convert Entity to dictionary."""
        return {
            "id": entity.id,
            "type": entity.type,
            "position": entity.position,
            "stat7": entity.stat7.to_dict() if entity.stat7 else {},
            "metadata": entity.metadata,
            "enrichment_count": entity.enrichment_count,
        }


# ============================================================================
# FASTAPI APP INSTANCE (for direct ASGI usage)
# ============================================================================

# Default app instance (can be initialized later)
app = FastAPI(
    title="Phase 6B - The Seed Multiverse API",
    description="REST API for The Seed multiverse simulation system",
    version="6B-Alpha",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/health")
async def default_health():
    """Default health check before server initialization."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "orchestrator_initialized": False
    }


# ============================================================================
# MAIN ENTRY POINT (FOR TESTING)
# ============================================================================

async def launch_api_server(
    seed: int = 42,
    orbits: int = 2,
    realms: List[str] = None,
    port: int = 8000
) -> Phase6BAPIServer:
    """
    Launch the Phase 6B API server with a demo universe.
    
    Args:
        seed: Random seed for reproducibility
        orbits: Number of enrichment cycles
        realms: List of realm IDs to generate
        port: HTTP port (not used in async mode, for reference only)
    
    Returns:
        Initialized Phase6BAPIServer instance
    """
    if realms is None:
        realms = ["overworld", "tavern"]
    
    logger.info(f"🚀 Launching Phase 6B API Server (seed={seed}, orbits={orbits})")
    
    # Step 1: Initialize orchestrator
    config = OrchestratorConfig(seed=seed, orbits=orbits, realms=realms)
    orchestrator = UniverseDemoOrchestrator(config)
    await orchestrator.launch_demo()
    
    # Step 2: Create API server
    api_server = Phase6BAPIServer(orchestrator)
    
    # Step 3: Initialize hierarchical adapter (Phase 6-Alpha)
    api_server.hierarchical_adapter = HierarchicalUniverseAdapter(orchestrator.universe)
    
    # Classify realms with default tiers
    tier_specs = {
        "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban", "social"]),
        "overworld": (TierClassification.TERRAN, TierTheme.OVERWORLD, ["nature", "outdoor"]),
    }
    await api_server.hierarchical_adapter.initialize_with_tier_classification(tier_specs)
    
    logger.info(f"✅ Phase 6B API Server ready on port {port}")
    logger.info(f"   📍 Realms: {len(orchestrator.universe.realms)}")
    logger.info(f"   📍 Entities: {orchestrator.get_demo_metadata().total_entities}")
    logger.info(f"   📍 Orbits: {orchestrator.universe.current_orbit}")
    
    return api_server


if __name__ == "__main__":
    import asyncio
    
    print("=" * 70)
    print("PHASE 6B REST API - QUICK TEST")
    print("=" * 70)
    print("Date: 2025-10-31 (Halloween)")
    print()
    
    async def main():
        api_server = await launch_api_server(seed=42, orbits=2, realms=["tavern", "overworld"])
        
        print()
        print("API Server initialized successfully!")
        print(f"Universe: {len(api_server.orchestrator.universe.realms)} realms")
        print(f"Total entities: {api_server.orchestrator.get_demo_metadata().total_entities}")
        print()
        print("To start the server, run:")
        print("  uvicorn phase6b_rest_api:app --reload --port 8000")
        print()
        print("API Documentation will be available at:")
        print("  http://localhost:8000/docs")
    
    asyncio.run(main())