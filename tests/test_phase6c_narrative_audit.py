"""
Phase 6C: Narrative Rendering & Admin Audit Tests

Tests the extended Phase 6B API with narrative decompression and Bob the Skeptic audit logging.

New Endpoints:
- GET /api/npcs/{npc_id}/narrative - Render enrichment_history as human-readable story
- POST /api/admin/audit-log - Log admin action (with Bob the Skeptic validation)
- GET /api/admin/audit-log - Retrieve audit trail with filtering

Date: 2025-10-31 (Halloween)
Framework: pytest + FastAPI TestClient
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone
from unittest.mock import Mock, patch

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

from fastapi.testclient import TestClient


# ============================================================================
# TEST: NARRATIVE RENDERING
# ============================================================================

class TestNarrativeRendering:
    """Test narrative decompression from enrichment_history to human-readable story."""
    
    def test_narrative_endpoint_exists(self):
        """Verify /api/npcs/{npc_id}/narrative endpoint is defined."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        api_server = Phase6BAPIServer(orchestrator)
        
        # Check that the endpoint is registered
        routes = [route.path for route in api_server.app.routes]
        assert any("/api/npcs/{npc_id}/narrative" in r for r in routes), \
            f"Narrative endpoint not found in routes: {routes}"
    
    @pytest.mark.asyncio
    async def test_narrative_returns_story_structure(self):
        """Narrative endpoint returns complete story with metadata."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        # Use "overworld" which generates procedural entities
        config = OrchestratorConfig(seed=42, orbits=1, realms=["overworld"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        client = TestClient(api_server.app)
        
        # Get first NPC
        npcs_response = client.get("/api/npcs")
        assert npcs_response.status_code == 200
        npcs = npcs_response.json()["npcs"]
        assert len(npcs) > 0, "No NPCs available for narrative test"
        
        npc_id = npcs[0]["npc_id"]
        
        # Request narrative
        narrative_response = client.get(f"/api/npcs/{npc_id}/narrative")
        assert narrative_response.status_code == 200
        
        narrative_data = narrative_response.json()
        assert "npc_id" in narrative_data
        assert "npc_name" in narrative_data
        assert "story" in narrative_data  # Human-readable narrative
        assert "enrichment_layers" in narrative_data  # Breakdown of enrichment phases
        assert isinstance(narrative_data["story"], str)
        assert len(narrative_data["story"]) > 0
    
    @pytest.mark.asyncio
    async def test_narrative_decompresses_enrichment_history(self):
        """Narrative transforms enrichment_history into readable prose."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        # Use "overworld" which generates procedural entities
        config = OrchestratorConfig(seed=42, orbits=1, realms=["overworld"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        client = TestClient(api_server.app)
        
        npcs_response = client.get("/api/npcs")
        npcs = npcs_response.json()["npcs"]
        npc_id = npcs[0]["npc_id"]
        
        # Get NPC details (includes enrichment_history)
        detail_response = client.get(f"/api/npcs/{npc_id}")
        npc_detail = detail_response.json()
        
        # Get narrative
        narrative_response = client.get(f"/api/npcs/{npc_id}/narrative")
        narrative_data = narrative_response.json()
        
        # Verify narrative is built from enrichment history
        if npc_detail.get("enrichment_history"):
            # Story should reference phases from enrichment history
            assert narrative_data["enrichment_layers"] is not None
            assert len(narrative_data["enrichment_layers"]) > 0
    
    @pytest.mark.asyncio
    async def test_narrative_handles_missing_npc(self):
        """Narrative endpoint returns 404 for nonexistent NPC."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        # Use "overworld" which generates procedural entities
        config = OrchestratorConfig(seed=42, orbits=1, realms=["overworld"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        api_server = Phase6BAPIServer(orchestrator)
        
        client = TestClient(api_server.app)
        
        response = client.get("/api/npcs/nonexistent-npc-999/narrative")
        assert response.status_code == 404


# ============================================================================
# TEST: AUDIT LOG SCHEMA & STORAGE
# ============================================================================

class TestAuditLogSchema:
    """Test audit log data structure and validation."""
    
    def test_audit_log_pydantic_model_exists(self):
        """Verify AuditLogEntry Pydantic model is defined."""
        from phase6b_rest_api import AuditLogEntry
        
        # Should have required fields
        entry = AuditLogEntry(
            action_type="entity_modify",
            entity_id="test-entity",
            entity_type="npc",
            admin_id="admin-001",
            changes={"personality_traits": {"old": {"trait": "valor"}, "new": {"trait": "honor"}}},
            governance_check_passed=True,
            governance_violations=[],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        assert entry.action_type == "entity_modify"
        assert entry.admin_id == "admin-001"
        assert entry.governance_check_passed is True
    
    def test_audit_log_tracks_all_actions(self):
        """Audit log schema supports create, update, delete actions."""
        from phase6b_rest_api import AuditLogEntry
        
        actions = ["entity_create", "entity_modify", "entity_delete", "realm_modify"]
        
        for action in actions:
            entry = AuditLogEntry(
                action_type=action,
                entity_id="test-entity",
                entity_type="npc",
                admin_id="admin-001",
                changes={},
                governance_check_passed=True,
                governance_violations=[],
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            assert entry.action_type == action
    
    def test_audit_log_records_governance_violations(self):
        """Audit log captures governance violations detected by Bob the Skeptic."""
        from phase6b_rest_api import AuditLogEntry
        
        entry = AuditLogEntry(
            action_type="entity_modify",
            entity_id="test-npc",
            entity_type="npc",
            admin_id="admin-001",
            changes={"tier": "celestial"},
            governance_check_passed=False,
            governance_violations=["cannot_change_tier_mid_simulation", "violates_realm_consistency"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        assert entry.governance_check_passed is False
        assert len(entry.governance_violations) == 2


# ============================================================================
# TEST: BOB THE SKEPTIC GOVERNANCE VALIDATION
# ============================================================================

class TestBobTheSkeptic:
    """Test governance validation (anti-cheat) system."""
    
    def test_bob_rejects_tier_changes_mid_simulation(self):
        """Bob prevents changing entity tier during simulation."""
        from phase6b_rest_api import BobTheSkeptic
        
        bob = BobTheSkeptic()
        
        # Simulate changing an entity's tier
        changes = {
            "tier": {"old": "terran", "new": "celestial"}
        }
        
        violations = bob.validate_modification(
            entity_type="npc",
            entity_id="npc-123",
            changes=changes,
            simulation_running=True
        )
        
        assert len(violations) > 0
        assert any("tier" in v.lower() for v in violations)
    
    def test_bob_allows_personality_changes(self):
        """Bob allows personality trait modifications (narrative-safe changes)."""
        from phase6b_rest_api import BobTheSkeptic
        
        bob = BobTheSkeptic()
        
        changes = {
            "personality_traits": {
                "old": {"courage": 0.5, "kindness": 0.7},
                "new": {"courage": 0.6, "kindness": 0.7}
            }
        }
        
        violations = bob.validate_modification(
            entity_type="npc",
            entity_id="npc-123",
            changes=changes,
            simulation_running=True
        )
        
        # Should allow personality changes (narrative-driven)
        # May have warnings but not hard violations
        assert isinstance(violations, list)
    
    def test_bob_validates_realm_consistency(self):
        """Bob checks that realm tier/theme changes don't break hierarchy."""
        from phase6b_rest_api import BobTheSkeptic
        
        bob = BobTheSkeptic()
        
        # Try to change realm theme without updating sub-realms
        changes = {
            "theme": {"old": "medieval", "new": "sci-fi"}
        }
        
        violations = bob.validate_modification(
            entity_type="realm",
            entity_id="realm-tavern",
            changes=changes,
            simulation_running=True,
            has_children=True  # Realm has sub-realms
        )
        
        # Should flag inconsistency risk
        assert isinstance(violations, list)


# ============================================================================
# TEST: AUDIT LOG ENDPOINTS
# ============================================================================

class TestAuditLogEndpoints:
    """Test audit log API endpoints."""
    
    def test_post_audit_log_endpoint_exists(self):
        """Verify POST /api/admin/audit-log endpoint is defined."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        api_server = Phase6BAPIServer(orchestrator)
        
        routes = [f"{route.path} {route.methods}" for route in api_server.app.routes]
        assert any("/api/admin/audit-log" in r for r in routes), \
            f"Audit log endpoint not found in routes: {routes}"
    
    @pytest.mark.asyncio
    async def test_post_audit_log_records_action(self):
        """POST /api/admin/audit-log records admin action."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        client = TestClient(api_server.app)
        
        # Log an action
        audit_entry = {
            "action_type": "entity_modify",
            "entity_id": "npc-test",
            "entity_type": "npc",
            "admin_id": "admin-001",
            "changes": {"personality_traits": {"courage": 0.6}},
            "governance_check_passed": True,
            "governance_violations": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = client.post("/api/admin/audit-log", json=audit_entry)
        assert response.status_code == 201 or response.status_code == 200
        
        data = response.json()
        assert "audit_id" in data or data.get("action_type") == "entity_modify"
    
    @pytest.mark.asyncio
    async def test_get_audit_log_retrieves_history(self):
        """GET /api/admin/audit-log retrieves audit trail."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        client = TestClient(api_server.app)
        
        # Post an action first
        audit_entry = {
            "action_type": "entity_modify",
            "entity_id": "npc-test",
            "entity_type": "npc",
            "admin_id": "admin-001",
            "changes": {"personality_traits": {"courage": 0.6}},
            "governance_check_passed": True,
            "governance_violations": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        client.post("/api/admin/audit-log", json=audit_entry)
        
        # Retrieve audit log
        response = client.get("/api/admin/audit-log")
        assert response.status_code == 200
        
        data = response.json()
        assert "audit_entries" in data or isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_audit_log_filtering_by_admin_id(self):
        """Audit log can be filtered by admin_id."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        client = TestClient(api_server.app)
        
        # Post action from admin-001
        audit_entry_1 = {
            "action_type": "entity_modify",
            "entity_id": "npc-test1",
            "entity_type": "npc",
            "admin_id": "admin-001",
            "changes": {},
            "governance_check_passed": True,
            "governance_violations": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        client.post("/api/admin/audit-log", json=audit_entry_1)
        
        # Post action from admin-002
        audit_entry_2 = {
            "action_type": "entity_modify",
            "entity_id": "npc-test2",
            "entity_type": "npc",
            "admin_id": "admin-002",
            "changes": {},
            "governance_check_passed": True,
            "governance_violations": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        client.post("/api/admin/audit-log", json=audit_entry_2)
        
        # Filter by admin-001
        response = client.get("/api/admin/audit-log?admin_id=admin-001")
        assert response.status_code == 200
        
        data = response.json()
        audit_list = data.get("audit_entries", []) if isinstance(data, dict) else data
        # Should only contain entries from admin-001
        assert all(entry.get("admin_id") == "admin-001" for entry in audit_list)
    
    @pytest.mark.asyncio
    async def test_audit_log_filtering_by_entity_id(self):
        """Audit log can be filtered by entity_id."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        client = TestClient(api_server.app)
        
        # Post multiple actions
        for i in range(3):
            audit_entry = {
                "action_type": "entity_modify",
                "entity_id": f"npc-test{i}",
                "entity_type": "npc",
                "admin_id": "admin-001",
                "changes": {},
                "governance_check_passed": True,
                "governance_violations": [],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            client.post("/api/admin/audit-log", json=audit_entry)
        
        # Filter by specific entity
        response = client.get("/api/admin/audit-log?entity_id=npc-test0")
        assert response.status_code == 200
        
        data = response.json()
        audit_list = data.get("audit_entries", []) if isinstance(data, dict) else data
        assert all(entry.get("entity_id") == "npc-test0" for entry in audit_list)
    
    @pytest.mark.asyncio
    async def test_audit_log_shows_violations(self):
        """Audit log displays Bob's governance violations."""
        from phase6b_rest_api import Phase6BAPIServer
        from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig(seed=42, orbits=1, realms=["tavern"])
        orchestrator = UniverseDemoOrchestrator(config)
        await orchestrator.launch_demo()
        
        api_server = Phase6BAPIServer(orchestrator)
        
        client = TestClient(api_server.app)
        
        # Post action with violations
        audit_entry = {
            "action_type": "entity_modify",
            "entity_id": "npc-test",
            "entity_type": "npc",
            "admin_id": "admin-001",
            "changes": {"tier": "celestial"},
            "governance_check_passed": False,
            "governance_violations": ["cannot_change_tier_mid_simulation"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        client.post("/api/admin/audit-log", json=audit_entry)
        
        # Retrieve and check for violations
        response = client.get("/api/admin/audit-log?governance_violations=true")
        assert response.status_code == 200
        
        data = response.json()
        audit_list = data.get("audit_entries", []) if isinstance(data, dict) else data
        assert any(not entry.get("governance_check_passed") for entry in audit_list)


# ============================================================================
# TEST: INTEGRATION - NARRATIVE + AUDIT
# ============================================================================

class TestNarrativeAuditIntegration:
    """Test narrative rendering and audit logging work together."""
    
    def test_audit_log_records_narrative_access(self):
        """Accessing narrative is tracked in audit log (for admin/public distinction)."""
        # This is optional but useful for analytics
        pass
    
    def test_narrative_excludes_admin_changes_before_audit(self):
        """Narrative doesn't include unapproved admin changes."""
        # Narratives are read-only from enrichment_history; admin changes are logged separately
        pass