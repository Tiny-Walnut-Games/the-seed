"""
Phase 6B: REST API Layer Tests

Tests the FastAPI server that exposes Phase 6A orchestrator and Phase 6-Alpha hierarchical realms.

Endpoints tested:
- GET /api/realms - List all realms with tier classification
- GET /api/realms/{realm_id} - Get specific realm details
- GET /api/realms/{realm_id}/tier - Get tier metadata
- GET /api/realms/by-tier/{tier} - Query realms by tier
- GET /api/realms/by-theme/{theme} - Query realms by theme
- POST /api/realms/{realm_id}/zoom - Create sub-realm via entity zoom
- GET /api/npcs - List all NPCs across all realms
- GET /api/npcs/{npc_id} - Get NPC details with personality
- GET /api/npcs/{npc_id}/context - Get dialogue context for NPC
- GET /api/universe/export - Export full universe metadata

Date: 2025-10-31 (Halloween)
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))

# We'll use httpx for async client testing with FastAPI
try:
    from httpx import AsyncClient
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    pytest.skip("httpx not available", allow_module_level=True)

from fastapi.testclient import TestClient


# ============================================================================
# TEST: API INITIALIZATION
# ============================================================================

class TestAPIInitialization:
    """Test that the REST API server initializes correctly."""
    
    def test_api_server_imports_successfully(self):
        """Verify the API module can be imported."""
        try:
            from phase6b_rest_api import app, Phase6BAPIServer
            assert app is not None
            assert Phase6BAPIServer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import phase6b_rest_api: {e}")
    
    def test_api_server_initializes_with_orchestrator(self):
        """Verify API server can be initialized with an orchestrator."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        
        api_server = Phase6BAPIServer(orchestrator)
        assert api_server.orchestrator is not None
        assert api_server.app is not None


# ============================================================================
# TEST: REALM ENDPOINTS
# ============================================================================

class TestRealmEndpoints:
    """Test realm query endpoints."""
    
    @pytest.fixture
    async def initialized_api(self):
        """Create initialized API server with demo universe."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        from phase6_hierarchical_realms import HierarchicalUniverseAdapter, TierClassification, TierTheme
        
        config = OrchestratorConfig(
            seed=42,
            orbits=2,
            realms=["overworld", "tavern"]
        )
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        # Initialize hierarchical adapter with tier classification
        api_server.hierarchical_adapter = HierarchicalUniverseAdapter(orchestrator.universe)
        tier_specs = {
            "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban"]),
            "overworld": (TierClassification.TERRAN, TierTheme.OVERWORLD, ["nature"]),
        }
        await api_server.hierarchical_adapter.initialize_with_tier_classification(tier_specs)
        
        return api_server
    
    @pytest.mark.asyncio
    async def test_list_realms_endpoint(self, initialized_api):
        """GET /api/realms - List all realms."""
        api = await initialized_api
        client = TestClient(api.app)
        response = client.get("/api/realms")
        
        assert response.status_code == 200
        data = response.json()
        assert "realms" in data
        assert len(data["realms"]) >= 2
        
        # Check realm structure
        realm = data["realms"][0]
        assert "realm_id" in realm
        assert "entity_count" in realm
        assert "lineage" in realm
    
    @pytest.mark.asyncio
    async def test_get_realm_by_id(self, initialized_api):
        """GET /api/realms/{realm_id} - Get specific realm."""
        api = await initialized_api
        client = TestClient(api.app)
        response = client.get("/api/realms/tavern")
        
        assert response.status_code == 200
        data = response.json()
        assert data["realm_id"] == "tavern"
        assert "entities" in data
        assert "lineage" in data
    
    @pytest.mark.asyncio
    async def test_get_realm_tier_metadata(self, initialized_api):
        """GET /api/realms/{realm_id}/tier - Get tier classification."""
        api = await initialized_api
        client = TestClient(api.app)
        response = client.get("/api/realms/tavern/tier")
        
        assert response.status_code == 200
        data = response.json()
        assert "tier" in data
        assert "theme" in data
        assert "semantic_anchors" in data


# ============================================================================
# TEST: TIER QUERY ENDPOINTS
# ============================================================================

class TestTierQueryEndpoints:
    """Test tier-based realm queries (Phase 6-Alpha integration)."""
    
    @pytest.fixture
    async def api_with_tiers(self):
        """Create API with tier-classified realms."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        from phase6_hierarchical_realms import HierarchicalUniverseAdapter, TierClassification, TierTheme
        
        config = OrchestratorConfig(
            seed=42,
            orbits=1,
            realms=["tavern", "overworld"]
        )
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        # Initialize hierarchical adapter and classify realms with tiers
        api_server.hierarchical_adapter = HierarchicalUniverseAdapter(orchestrator.universe)
        await api_server.hierarchical_adapter.initialize_with_tier_classification({
            "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban"]),
            "overworld": (TierClassification.TERRAN, TierTheme.OVERWORLD, ["nature"]),
        })
        
        return api_server
    
    @pytest.mark.asyncio
    async def test_query_realms_by_tier(self, api_with_tiers):
        """GET /api/realms/by-tier/{tier} - Query by tier."""
        api = await api_with_tiers
        client = TestClient(api.app)
        response = client.get("/api/realms/by-tier/terran")
        
        assert response.status_code == 200
        data = response.json()
        assert "realms" in data
        assert len(data["realms"]) >= 2
        
        for realm in data["realms"]:
            assert realm["tier"] == "terran"
    
    @pytest.mark.asyncio
    async def test_query_realms_by_theme(self, api_with_tiers):
        """GET /api/realms/by-theme/{theme} - Query by theme."""
        api = await api_with_tiers
        client = TestClient(api.app)
        response = client.get("/api/realms/by-theme/city_state")
        
        assert response.status_code == 200
        data = response.json()
        assert "realms" in data
        assert len(data["realms"]) >= 1
        
        realm = data["realms"][0]
        assert realm["theme"] == "city_state"


# ============================================================================
# TEST: SUB-REALM ZOOM ENDPOINTS
# ============================================================================

class TestSubRealmZoomEndpoints:
    """Test sub-realm creation via zoom (Phase 6-Alpha integration)."""
    
    @pytest.fixture
    async def api_ready_for_zoom(self):
        """Create API with realms ready for zoom navigation."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        from phase6_hierarchical_realms import HierarchicalUniverseAdapter, TierClassification, TierTheme
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        # Initialize hierarchical adapter and classify realms
        api_server.hierarchical_adapter = HierarchicalUniverseAdapter(orchestrator.universe)
        await api_server.hierarchical_adapter.initialize_with_tier_classification({
            "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban"]),
        })
        
        return api_server
    
    @pytest.mark.asyncio
    async def test_create_sub_realm_via_zoom(self, api_ready_for_zoom):
        """POST /api/realms/{realm_id}/zoom - Create sub-realm."""
        api = await api_ready_for_zoom
        client = TestClient(api.app)
        
        # Get first entity from tavern
        realm_response = client.get("/api/realms/tavern")
        entities = realm_response.json()["entities"]
        
        if len(entities) > 0:
            entity_id = entities[0]["id"]
            
            zoom_request = {
                "entity_id": entity_id,
                "additional_anchors": ["interior", "close_up"]
            }
            
            response = client.post("/api/realms/tavern/zoom", json=zoom_request)
            assert response.status_code == 200
            
            data = response.json()
            assert "sub_realm_id" in data
            assert data["parent_realm_id"] == "tavern"
            assert data["entity_id"] == entity_id
            assert data["tier_depth"] == 1


# ============================================================================
# TEST: NPC ENDPOINTS
# ============================================================================

class TestNPCEndpoints:
    """Test NPC query endpoints (Phase 2 bridge integration)."""
    
    @pytest.fixture
    async def api_with_npcs(self):
        """Create API with NPCs registered."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(
            seed=42,
            orbits=2,
            realms=["overworld"]
        )
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        return api_server
    
    @pytest.mark.asyncio
    async def test_list_all_npcs(self, api_with_npcs):
        """GET /api/npcs - List all NPCs."""
        api = await api_with_npcs
        client = TestClient(api.app)
        response = client.get("/api/npcs")
        
        assert response.status_code == 200
        data = response.json()
        assert "npcs" in data
        assert len(data["npcs"]) >= 0
        
        if len(data["npcs"]) > 0:
            npc = data["npcs"][0]
            assert "npc_id" in npc
            assert "npc_name" in npc
            assert "realm_id" in npc
    
    @pytest.mark.asyncio
    async def test_get_npc_details(self, api_with_npcs):
        """GET /api/npcs/{npc_id} - Get NPC details with personality."""
        api = await api_with_npcs
        client = TestClient(api.app)
        
        # First get list of NPCs
        list_response = client.get("/api/npcs")
        npcs = list_response.json()["npcs"]
        
        if len(npcs) > 0:
            npc_id = npcs[0]["npc_id"]
            
            response = client.get(f"/api/npcs/{npc_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["npc_id"] == npc_id
            assert "personality_traits" in data
            assert "enrichment_history" in data
    
    @pytest.mark.asyncio
    async def test_get_npc_dialogue_context(self, api_with_npcs):
        """GET /api/npcs/{npc_id}/context - Get dialogue context."""
        api = await api_with_npcs
        client = TestClient(api.app)
        
        list_response = client.get("/api/npcs")
        npcs = list_response.json()["npcs"]
        
        if len(npcs) > 0:
            npc_id = npcs[0]["npc_id"]
            
            response = client.get(f"/api/npcs/{npc_id}/context")
            assert response.status_code == 200
            
            data = response.json()
            assert "location_type" in data
            assert "npc_mood" in data
            assert "narrative_phase" in data
            assert "dialogue_turn" in data


# ============================================================================
# TEST: UNIVERSE EXPORT ENDPOINT
# ============================================================================

class TestUniverseExportEndpoint:
    """Test universe export for reproducibility."""
    
    @pytest.mark.asyncio
    async def test_export_universe(self):
        """GET /api/universe/export - Export full universe."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        client = TestClient(api_server.app)
        
        response = client.get("/api/universe/export")
        assert response.status_code == 200
        
        data = response.json()
        assert "seed" in data
        assert data["seed"] == 42
        assert "total_orbits_completed" in data
        assert "realms" in data
        assert "metadata" in data


# ============================================================================
# TEST: ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test API error handling."""
    
    @pytest.mark.asyncio
    async def test_realm_not_found(self):
        """Verify 404 for non-existent realm."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        client = TestClient(api_server.app)
        
        response = client.get("/api/realms/nonexistent_realm")
        assert response.status_code == 404
        json_response = response.json()
        assert "detail" in json_response
        assert "error" in json_response["detail"]
    
    @pytest.mark.asyncio
    async def test_npc_not_found(self):
        """Verify 404 for non-existent NPC."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        client = TestClient(api_server.app)
        
        response = client.get("/api/npcs/nonexistent_npc")
        assert response.status_code == 404
        json_response = response.json()
        assert "detail" in json_response
        assert "error" in json_response["detail"]


# ============================================================================
# TEST: HEALTH CHECK
# ============================================================================

class TestHealthCheck:
    """Test API health check endpoint."""
    
    def test_health_endpoint(self):
        """GET /health - Health check."""
        from phase6b_rest_api import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 6B REST API - TEST SUITE")
    print("=" * 70)
    print("Date: 2025-10-31 (Halloween)")
    print("Test Count: 18 tests across 7 test classes")
    print()
    print("Run with: pytest tests/test_phase6b_rest_api.py -v")
    print("=" * 70)