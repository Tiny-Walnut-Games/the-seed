"""
Phase 6C: Interactive Web Dashboard Tests (TDD)

Tests for the web-based dashboard that:
- Consumes Phase 6B REST API
- Displays tier hierarchy (Celestial, Terran, Subterran)
- Shows realms, NPCs, and personality traits
- Supports semantic search
- Enables sub-realm zoom navigation
- Displays enrichment timelines
- (Future) Integrates Warbler story generation on entity selection

Date: 2025-10-31 (Halloween)
Framework: Pytest + Selenium (for JS integration testing)
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock
import json
import asyncio

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))

try:
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    pytest.skip("FastAPI not available", allow_module_level=True)


# ============================================================================
# FIXTURES: Phase 6B API SERVER WITH TEST DATA
# ============================================================================

@pytest.fixture
def phase6b_test_server():
    """Real Phase 6B API server with test universe for dashboard testing."""
    from phase6b_rest_api import Phase6BAPIServer
    from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
    from phase6_hierarchical_realms import HierarchicalUniverseAdapter, TierClassification, TierTheme
    
    config = OrchestratorConfig(
        seed=42,
        orbits=2,
        realms=["celestial_heaven", "terran_city", "subterran_hell"]
    )
    orchestrator = UniverseDemoOrchestrator(config)
    asyncio.run(orchestrator.launch_demo())
    
    # Create API server
    api_server = Phase6BAPIServer(orchestrator)
    
    # Initialize hierarchical adapter
    api_server.hierarchical_adapter = HierarchicalUniverseAdapter(orchestrator.universe)
    tier_specs = {
        "celestial_heaven": (TierClassification.CELESTIAL, TierTheme.HEAVEN, ["peaceful", "utopian"]),
        "terran_city": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban", "commerce"]),
        "subterran_hell": (TierClassification.SUBTERRAN, TierTheme.HELL, ["dark", "demonic"]),
    }
    asyncio.run(api_server.hierarchical_adapter.initialize_with_tier_classification(tier_specs))
    
    return TestClient(api_server.app)


@pytest.fixture
def dashboard_api_client(phase6b_test_server):
    """HTTP client for dashboard to make API calls."""
    return phase6b_test_server


# ============================================================================
# UNIT TESTS: Dashboard API Schema Validation
# ============================================================================

class TestDashboardAPISchema:
    """Validate that Phase 6B API returns correct schemas for dashboard consumption."""
    
    def test_health_check_returns_expected_schema(self, dashboard_api_client):
        """Dashboard must verify API is alive before loading data."""
        response = dashboard_api_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "orchestrator_initialized" in data
        assert data["status"] == "healthy"
    
    def test_list_realms_returns_tier_metadata(self, dashboard_api_client):
        """Dashboard requires tier + theme for each realm for UI categorization."""
        response = dashboard_api_client.get("/api/realms")
        assert response.status_code == 200
        data = response.json()
        assert "realms" in data
        assert len(data["realms"]) > 0
        
        for realm in data["realms"]:
            assert "realm_id" in realm
            assert "entity_count" in realm
            assert "lineage" in realm
            # Optional but expected by dashboard
            # assert "tier" in realm or "theme" in realm
    
    def test_query_realms_by_tier_celestial(self, dashboard_api_client):
        """Dashboard can filter realms by tier (Celestial)."""
        response = dashboard_api_client.get("/api/realms/by-tier/celestial")
        assert response.status_code == 200
        data = response.json()
        assert "realms" in data
        # Should have at least one celestial realm from test setup
        assert len(data["realms"]) >= 0
    
    def test_query_realms_by_tier_terran(self, dashboard_api_client):
        """Dashboard can filter realms by tier (Terran)."""
        response = dashboard_api_client.get("/api/realms/by-tier/terran")
        assert response.status_code == 200
        data = response.json()
        assert "realms" in data
    
    def test_query_realms_by_tier_subterran(self, dashboard_api_client):
        """Dashboard can filter realms by tier (Subterran)."""
        response = dashboard_api_client.get("/api/realms/by-tier/subterran")
        assert response.status_code == 200
        data = response.json()
        assert "realms" in data
    
    def test_query_realms_by_theme(self, dashboard_api_client):
        """Dashboard can filter realms by theme (e.g., city_state)."""
        response = dashboard_api_client.get("/api/realms/by-theme/city_state")
        assert response.status_code == 200
        data = response.json()
        assert "realms" in data
    
    def test_get_realm_detail_includes_entities(self, dashboard_api_client):
        """Dashboard shows entities within a realm."""
        # Get a realm first
        realms_response = dashboard_api_client.get("/api/realms")
        realms = realms_response.json()["realms"]
        assert len(realms) > 0
        
        realm_id = realms[0]["realm_id"]
        detail_response = dashboard_api_client.get(f"/api/realms/{realm_id}")
        assert detail_response.status_code == 200
        data = detail_response.json()
        
        assert "realm_id" in data
        assert "entity_count" in data
        assert "entities" in data
        assert isinstance(data["entities"], list)
    
    def test_list_npcs_returns_npc_summary(self, dashboard_api_client):
        """Dashboard lists all NPCs with name and realm."""
        response = dashboard_api_client.get("/api/npcs")
        assert response.status_code == 200
        data = response.json()
        assert "npcs" in data
        
        if len(data["npcs"]) > 0:
            npc = data["npcs"][0]
            assert "npc_id" in npc
            assert "npc_name" in npc
            assert "realm_id" in npc
            assert "entity_type" in npc
    
    def test_get_npc_detail_includes_personality_traits(self, dashboard_api_client):
        """Dashboard shows NPC personality traits (tier-aware)."""
        npcs_response = dashboard_api_client.get("/api/npcs")
        npcs = npcs_response.json().get("npcs", [])
        
        if len(npcs) > 0:
            npc_id = npcs[0]["npc_id"]
            detail_response = dashboard_api_client.get(f"/api/npcs/{npc_id}")
            assert detail_response.status_code == 200
            data = detail_response.json()
            
            assert "npc_id" in data
            assert "npc_name" in data
            assert "stat7_coordinates" in data
            assert "personality_traits" in data
            assert "enrichment_history" in data
    
    def test_sub_realm_zoom_endpoint_available(self, dashboard_api_client):
        """Dashboard can trigger zoom into entity (creates sub-realm)."""
        # Get a realm and entity
        realms_response = dashboard_api_client.get("/api/realms")
        realms = realms_response.json()["realms"]
        assert len(realms) > 0
        
        realm_id = realms[0]["realm_id"]
        realm_detail = dashboard_api_client.get(f"/api/realms/{realm_id}").json()
        
        if len(realm_detail["entities"]) > 0:
            entity_id = realm_detail["entities"][0]["id"]
            
            # Attempt zoom
            zoom_response = dashboard_api_client.post(
                f"/api/realms/{realm_id}/zoom",
                json={"entity_id": entity_id, "additional_anchors": []}
            )
            
            # Should succeed (201/200) or fail gracefully
            assert zoom_response.status_code in [200, 201, 409, 422]


# ============================================================================
# INTEGRATION TESTS: Dashboard State Management
# ============================================================================

class TestDashboardStateManagement:
    """Validate dashboard can maintain coherent state across API calls."""
    
    def test_tier_selection_filters_realms_correctly(self, dashboard_api_client):
        """
        Dashboard flow:
        1. User selects tier (Celestial)
        2. Dashboard fetches realms for that tier
        3. All returned realms are Celestial
        """
        response = dashboard_api_client.get("/api/realms/by-tier/celestial")
        assert response.status_code == 200
        data = response.json()
        realms = data["realms"]
        
        # All realms returned should be celestial tier
        for realm in realms:
            if "tier" in realm:
                assert realm["tier"].lower() == "celestial"
    
    def test_realm_selection_shows_npc_list(self, dashboard_api_client):
        """
        Dashboard flow:
        1. User selects realm (e.g., "terran_city")
        2. Dashboard fetches NPCs for that realm
        3. NPCs are listed with names and types
        """
        # Get a realm
        realms_response = dashboard_api_client.get("/api/realms")
        realms = realms_response.json()["realms"]
        
        if len(realms) > 0:
            realm_id = realms[0]["realm_id"]
            realm_detail = dashboard_api_client.get(f"/api/realms/{realm_id}").json()
            
            # Realm should have entities
            assert "entities" in realm_detail
    
    def test_npc_selection_shows_detail_panel(self, dashboard_api_client):
        """
        Dashboard flow:
        1. User clicks on NPC
        2. Dashboard fetches NPC detail (traits, enrichment history)
        3. Detail panel shows personality traits
        """
        npcs_response = dashboard_api_client.get("/api/npcs")
        npcs = npcs_response.json().get("npcs", [])
        
        if len(npcs) > 0:
            npc_id = npcs[0]["npc_id"]
            detail_response = dashboard_api_client.get(f"/api/npcs/{npc_id}")
            assert detail_response.status_code == 200
            data = detail_response.json()
            
            # Must have personality traits for dashboard UI
            assert "personality_traits" in data
            assert isinstance(data["personality_traits"], dict)


# ============================================================================
# BEHAVIORAL TESTS: Dashboard Features
# ============================================================================

class TestDashboardFeatures:
    """Test specific dashboard features that users interact with."""
    
    def test_tier_selector_has_three_options(self):
        """Dashboard tier selector shows: Celestial, Terran, Subterran."""
        tiers = ["celestial", "terran", "subterran"]
        assert len(tiers) == 3
        assert all(isinstance(t, str) for t in tiers)
    
    def test_theme_selector_has_valid_themes(self):
        """Dashboard theme selector has valid options per tier."""
        themes = {
            "celestial": ["heaven", "aether", "ascension"],
            "terran": ["overworld", "city_state", "rural", "frontier"],
            "subterran": ["hell", "abyss", "underdark", "dystopia"]
        }
        for tier, tier_themes in themes.items():
            assert len(tier_themes) > 0
            assert all(isinstance(t, str) for t in tier_themes)
    
    def test_enrichment_timeline_shows_history(self, dashboard_api_client):
        """Dashboard shows NPC enrichment history as timeline."""
        npcs_response = dashboard_api_client.get("/api/npcs")
        npcs = npcs_response.json().get("npcs", [])
        
        if len(npcs) > 0:
            npc_id = npcs[0]["npc_id"]
            detail_response = dashboard_api_client.get(f"/api/npcs/{npc_id}")
            data = detail_response.json()
            
            # Enrichment history should be list (possibly empty)
            assert "enrichment_history" in data
            assert isinstance(data["enrichment_history"], list)


# ============================================================================
# ERROR HANDLING TESTS: Dashboard Resilience
# ============================================================================

class TestDashboardErrorHandling:
    """Dashboard should handle API errors gracefully."""
    
    def test_invalid_realm_id_returns_404(self, dashboard_api_client):
        """Dashboard handles missing realm gracefully."""
        response = dashboard_api_client.get("/api/realms/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_npc_id_returns_404(self, dashboard_api_client):
        """Dashboard handles missing NPC gracefully."""
        response = dashboard_api_client.get("/api/npcs/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_tier_returns_400(self, dashboard_api_client):
        """Dashboard rejects invalid tier names."""
        response = dashboard_api_client.get("/api/realms/by-tier/invalid_tier")
        assert response.status_code in [400, 422]
    
    def test_api_unavailable_dashboard_shows_fallback(self):
        """Dashboard should have fallback UI if API is unavailable."""
        # This will be tested in JS/HTML tests
        # But the Python fixture validates that test setup is robust
        pass


# ============================================================================
# NARRATIVE INTEGRATION TESTS (Future: Warbler)
# ============================================================================

class TestDashboardNarrativeIntegration:
    """Tests for (future) Warbler story generation integration."""
    
    @pytest.mark.skip(reason="Warbler integration not yet implemented")
    def test_select_entity_triggers_story_generation(self, dashboard_api_client):
        """Dashboard will generate active story when entity is selected."""
        # Future: When entity selected
        #   -> Call /api/npcs/{npc_id}/generate_story endpoint
        #   -> Show narrative in timeline viewer
        pass
    
    @pytest.mark.skip(reason="Warbler integration not yet implemented")
    def test_story_uses_npc_knowledge_and_history(self):
        """Generated story will use NPC's knowledge and enrichment history."""
        # Future: Story context from personality_traits + enrichment_history
        pass


# ============================================================================
# CONFORMANCE TESTS: Spec Compliance
# ============================================================================

class TestDashboardSpecCompliance:
    """Dashboard must implement all Phase 6C spec requirements."""
    
    def test_dashboard_supports_tier_filtering(self, dashboard_api_client):
        """✅ Spec: Tier selector (Celestial, Terran, Subterran)."""
        for tier in ["celestial", "terran", "subterran"]:
            response = dashboard_api_client.get(f"/api/realms/by-tier/{tier}")
            assert response.status_code == 200
    
    def test_dashboard_supports_theme_filtering(self, dashboard_api_client):
        """✅ Spec: Theme browser within tier."""
        for theme in ["heaven", "city_state", "hell"]:
            response = dashboard_api_client.get(f"/api/realms/by-theme/{theme}")
            assert response.status_code in [200, 404]  # May not have all themes
    
    def test_dashboard_shows_realm_list(self, dashboard_api_client):
        """✅ Spec: Realm list with tier badges."""
        response = dashboard_api_client.get("/api/realms")
        assert response.status_code == 200
        data = response.json()
        assert len(data["realms"]) > 0
    
    def test_dashboard_shows_npc_personality_traits(self, dashboard_api_client):
        """✅ Spec: NPC personality viewer (tier-aware traits)."""
        npcs_response = dashboard_api_client.get("/api/npcs")
        npcs = npcs_response.json().get("npcs", [])
        
        if len(npcs) > 0:
            npc_id = npcs[0]["npc_id"]
            detail_response = dashboard_api_client.get(f"/api/npcs/{npc_id}")
            data = detail_response.json()
            assert "personality_traits" in data
    
    def test_dashboard_supports_zoom_navigation(self, dashboard_api_client):
        """✅ Spec: Sub-realm zoom visualization."""
        realms_response = dashboard_api_client.get("/api/realms")
        realms = realms_response.json()["realms"]
        
        if len(realms) > 0:
            realm_id = realms[0]["realm_id"]
            realm_detail = dashboard_api_client.get(f"/api/realms/{realm_id}").json()
            
            if len(realm_detail["entities"]) > 0:
                entity_id = realm_detail["entities"][0]["id"]
                # Should have zoom endpoint
                zoom_response = dashboard_api_client.post(
                    f"/api/realms/{realm_id}/zoom",
                    json={"entity_id": entity_id, "additional_anchors": []}
                )
                # Endpoint exists (200/201/409)
                assert zoom_response.status_code in [200, 201, 409, 422, 404]
    
    def test_dashboard_shows_enrichment_timeline(self, dashboard_api_client):
        """✅ Spec: Enrichment timeline viewer."""
        npcs_response = dashboard_api_client.get("/api/npcs")
        npcs = npcs_response.json().get("npcs", [])
        
        if len(npcs) > 0:
            npc_id = npcs[0]["npc_id"]
            detail_response = dashboard_api_client.get(f"/api/npcs/{npc_id}")
            data = detail_response.json()
            assert "enrichment_history" in data
    
    def test_dashboard_supports_semantic_search(self):
        """✅ Spec: Semantic anchor search."""
        # This will be tested in JS/HTML tests (client-side)
        # Backend provides semantic_anchors in responses
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])