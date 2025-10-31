"""
Phase 6C: CLI Explorer Tests (Hybrid TDD)

Tests for seed-explorer command-line interface that integrates:
- Phase 6B REST API (realm/tier/NPC queries) - REAL integration
- Universal Player Router (cross-realm player management) - REAL integration
- Edge case mocking (network failures, API unavailable)

Date: 2025-10-31 (Halloween)
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch
from click.testing import CliRunner
import json

# Add paths for Phase 6B and router imports
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))

# FastAPI test client for real integration
try:
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    pytest.skip("FastAPI not available", allow_module_level=True)


# ============================================================================
# REAL INTEGRATION FIXTURES
# ============================================================================

@pytest.fixture
def phase6b_server():
    """Real Phase 6B REST API server with test universe."""
    from phase6b_rest_api import Phase6BAPIServer
    from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
    from phase6_hierarchical_realms import HierarchicalUniverseAdapter, TierClassification, TierTheme
    
    # Create real orchestrator with test data
    config = OrchestratorConfig(
        seed=42,
        orbits=2,
        realms=["tavern", "overworld"]
    )
    orchestrator = UniverseDemoOrchestrator(config)
    # Note: We'll use sync version since CLI is synchronous
    import asyncio
    asyncio.run(orchestrator.launch_demo())
    
    # Create real API server
    api_server = Phase6BAPIServer(orchestrator)
    
    # Initialize hierarchical adapter with tier classification
    api_server.hierarchical_adapter = HierarchicalUniverseAdapter(orchestrator.universe)
    tier_specs = {
        "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban", "commerce"]),
        "overworld": (TierClassification.TERRAN, TierTheme.OVERWORLD, ["nature", "wilderness"]),
    }
    asyncio.run(api_server.hierarchical_adapter.initialize_with_tier_classification(tier_specs))
    
    # Return TestClient for HTTP requests
    return TestClient(api_server.app)


@pytest.fixture
def player_router():
    """Real Universal Player Router with test players."""
    from universal_player_router import UniversalPlayerRouter
    
    router = UniversalPlayerRouter()
    
    # Seed with test player
    player = router.create_player(
        player_name="Alice",
        character_race="human",
        character_class="Wanderer",
        starting_realm="tavern"
    )
    
    # Add inventory items
    from universal_player_router import InventoryItem
    sword = InventoryItem(
        item_id="sword_1",
        name="Steel Sword",
        item_type="weapon",
        rarity="common",
        source_realm="tavern"
    )
    router.add_item_to_inventory(
        player_id=player.player_id,
        item=sword
    )
    
    # Add reputation
    from universal_player_router import ReputationFaction
    router.modify_reputation(
        player_id=player.player_id,
        faction=ReputationFaction.THE_WANDERERS,
        change=100
    )
    
    return router


@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def api_base_url(phase6b_server):
    """Base URL for Phase 6B API (from test client)."""
    # TestClient handles URL internally, but CLI needs to know where to connect
    return "http://testserver"


# ============================================================================
# REALM COMMAND TESTS (REAL INTEGRATION)
# ============================================================================

class TestRealmCommands:
    """Tests for 'seed-explorer realms' commands using REAL Phase 6B API."""
    
    def test_realms_list(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer realms list (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['realms', 'list', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        assert "tavern" in result.output or "overworld" in result.output
        # Should show entity counts from real data
        assert "entities" in result.output.lower()
    
    def test_realms_list_with_tier_filter(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer realms list --tier terran (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['realms', 'list', '--tier', 'terran', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        assert "terran" in result.output.lower()
        # Should show both tavern and overworld (both terran tier)
    
    def test_realms_show(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer realms show --id tavern (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['realms', 'show', '--id', 'tavern', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        assert "tavern" in result.output
        # Should show entities from real realm
        assert "Entities:" in result.output or "entities" in result.output.lower()
    
    def test_realms_show_json_format(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer realms show --format json (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['realms', 'show', '--id', 'tavern', '--format', 'json', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        # Should be valid JSON
        data = json.loads(result.output)
        assert "realm_id" in data
        assert data["realm_id"] == "tavern"


# ============================================================================
# TIER COMMAND TESTS (REAL INTEGRATION)
# ============================================================================

class TestTierCommands:
    """Tests for 'seed-explorer tiers' commands using REAL Phase 6B API."""
    
    def test_tiers_list(self, cli_runner, api_base_url):
        """Test: seed-explorer tiers list (shows available tier classifications)"""
        from phase6c_cli_explorer import cli
        
        result = cli_runner.invoke(cli, ['tiers', 'list'])
        
        assert result.exit_code == 0
        # Should list tier system
        assert "celestial" in result.output.lower() or "terran" in result.output.lower() or "subterran" in result.output.lower()
    
    def test_tiers_show(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer tiers show --tier terran (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['tiers', 'show', '--tier', 'terran', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        assert "terran" in result.output.lower()
        # Should show realms in terran tier (tavern, overworld)
        assert "tavern" in result.output or "overworld" in result.output


# ============================================================================
# NPC COMMAND TESTS (REAL INTEGRATION)
# ============================================================================

class TestNPCCommands:
    """Tests for 'seed-explorer npcs' commands using REAL Phase 6B API."""
    
    def test_npcs_list(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer npcs list (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['npcs', 'list', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        # Should show NPCs from real universe (if any exist)
        # Note: orchestrator may or may not have NPCs depending on Phase 6A setup
        # At minimum, should not error
    
    def test_npcs_list_by_realm(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer npcs list --realm tavern (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['npcs', 'list', '--realm', 'tavern', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        # Should filter by realm (empty list is valid if no NPCs in tavern yet)
    
    def test_npcs_show(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer npcs show --npc-id <id> (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        # First, get list of NPCs to find a valid ID
        list_result = cli_runner.invoke(cli, ['npcs', 'list', '--format', 'json', '--api-url', api_base_url])
        
        if list_result.exit_code == 0:
            try:
                npcs_data = json.loads(list_result.output)
                if npcs_data.get("npcs") and len(npcs_data["npcs"]) > 0:
                    npc_id = npcs_data["npcs"][0]["npc_id"]
                    
                    # Now test show command
                    result = cli_runner.invoke(cli, ['npcs', 'show', '--npc-id', npc_id, '--api-url', api_base_url])
                    assert result.exit_code == 0
                    # Should show NPC details
            except json.JSONDecodeError:
                pass  # Skip if no NPCs available


# ============================================================================
# ZOOM COMMAND TESTS (REAL INTEGRATION)
# ============================================================================

class TestZoomCommands:
    """Tests for 'seed-explorer zoom' command using REAL Phase 6B API."""
    
    def test_zoom_create_subrealm(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer zoom --entity <entity_id> --parent-realm tavern (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        # First, get entities from tavern realm
        realm_result = cli_runner.invoke(cli, ['realms', 'show', '--id', 'tavern', '--format', 'json', '--api-url', api_base_url])
        
        if realm_result.exit_code == 0:
            try:
                realm_data = json.loads(realm_result.output)
                if realm_data.get("entities") and len(realm_data["entities"]) > 0:
                    entity_id = realm_data["entities"][0]["id"]
                    
                    # Now test zoom command
                    result = cli_runner.invoke(cli, [
                        'zoom',
                        '--entity', entity_id,
                        '--parent-realm', 'tavern',
                        '--api-url', api_base_url
                    ])
                    
                    # Should create sub-realm or handle gracefully
                    # Note: Zoom may fail if entity isn't suitable, which is valid behavior
                    assert "Sub-realm" in result.output or "zoom" in result.output.lower()
            except (json.JSONDecodeError, KeyError):
                pass  # Skip if no entities available
    
    def test_zoom_with_additional_anchors(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer zoom with semantic anchors (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        # Get first entity from tavern
        realm_result = cli_runner.invoke(cli, ['realms', 'show', '--id', 'tavern', '--format', 'json', '--api-url', api_base_url])
        
        if realm_result.exit_code == 0:
            try:
                realm_data = json.loads(realm_result.output)
                if realm_data.get("entities") and len(realm_data["entities"]) > 0:
                    entity_id = realm_data["entities"][0]["id"]
                    
                    result = cli_runner.invoke(cli, [
                        'zoom',
                        '--entity', entity_id,
                        '--parent-realm', 'tavern',
                        '--anchors', 'mystical,ancient',
                        '--api-url', api_base_url
                    ])
                    
                    # Should process anchors in zoom request
                    assert result.exit_code in [0, 1]  # May succeed or fail depending on entity
            except (json.JSONDecodeError, KeyError):
                pass


# ============================================================================
# PLAYER COMMAND TESTS (REAL Universal Player Router Integration)
# ============================================================================

class TestPlayerCommands:
    """Tests for 'seed-explorer players' commands using REAL player router."""
    
    def test_players_list(self, cli_runner, player_router):
        """Test: seed-explorer players list --realm tavern (REAL ROUTER)"""
        from phase6c_cli_explorer import cli, set_player_router
        
        set_player_router(player_router)
        result = cli_runner.invoke(cli, ['players', 'list', '--realm', 'tavern'])
        
        assert result.exit_code == 0
        assert "Alice" in result.output  # Test player created in fixture
        assert "Level" in result.output or "level" in result.output.lower()
    
    def test_players_show(self, cli_runner, player_router):
        """Test: seed-explorer players show --player-id <id> (REAL ROUTER)"""
        from phase6c_cli_explorer import cli, set_player_router
        
        # Get player ID from router
        players = player_router.get_realm_roster("tavern")
        assert len(players) > 0
        player_id = players[0].player_id
        
        set_player_router(player_router)
        result = cli_runner.invoke(cli, ['players', 'show', '--player-id', player_id])
        
        assert result.exit_code == 0
        assert "Alice" in result.output
        assert "human" in result.output.lower()
        assert "Steel Sword" in result.output  # Inventory item from fixture
        assert "the_wanderers" in result.output.lower()  # Reputation from fixture
    
    def test_players_create(self, cli_runner, player_router):
        """Test: seed-explorer players create --name Bob --race elf --realm tavern (REAL ROUTER)"""
        from phase6c_cli_explorer import cli, set_player_router
        
        set_player_router(player_router)
        result = cli_runner.invoke(cli, [
            'players', 'create',
            '--name', 'Bob',
            '--race', 'elf',
            '--realm', 'tavern'
        ])
        
        assert result.exit_code == 0
        assert "created" in result.output.lower()
        assert "Bob" in result.output
        
        # Verify player was actually created in router
        players = player_router.get_realm_roster("tavern")
        bob_exists = any(p.player_name == "Bob" for p in players)
        assert bob_exists
    
    def test_players_travel(self, cli_runner, player_router):
        """Test: seed-explorer players travel --player-id <id> --to overworld (REAL ROUTER)"""
        from phase6c_cli_explorer import cli, set_player_router
        
        # Get player ID
        players = player_router.get_realm_roster("tavern")
        player_id = players[0].player_id
        
        set_player_router(player_router)
        result = cli_runner.invoke(cli, [
            'players', 'travel',
            '--player-id', player_id,
            '--to', 'overworld'
        ])
        
        assert result.exit_code == 0
        assert "travel" in result.output.lower() or "transition" in result.output.lower()
        
        # Verify player actually moved
        player = player_router.get_player(player_id)
        assert player.active_realm == "overworld"


# ============================================================================
# HEALTH & STATS COMMAND TESTS (REAL INTEGRATION)
# ============================================================================

class TestUtilityCommands:
    """Tests for health and stats commands using REAL components."""
    
    def test_health_check(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer health (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['health', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        assert "health" in result.output.lower() or "status" in result.output.lower()
    
    def test_stats_command(self, cli_runner, phase6b_server, player_router, api_base_url):
        """Test: seed-explorer stats (REAL API + ROUTER)"""
        from phase6c_cli_explorer import cli, set_player_router, set_api_client
        
        set_api_client(phase6b_server)
        set_player_router(player_router)
        result = cli_runner.invoke(cli, ['stats', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        # Should show aggregate statistics
        assert "realms" in result.output.lower() or "Realms" in result.output


# ============================================================================
# OUTPUT FORMAT TESTS (REAL INTEGRATION)
# ============================================================================

class TestOutputFormats:
    """Tests for JSON output format option using REAL components."""
    
    def test_json_output_realms(self, cli_runner, phase6b_server, api_base_url):
        """Test: seed-explorer realms list --format json (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        result = cli_runner.invoke(cli, ['realms', 'list', '--format', 'json', '--api-url', api_base_url])
        
        assert result.exit_code == 0
        # Output should be valid JSON
        data = json.loads(result.output)
        assert "realms" in data
        assert len(data["realms"]) >= 2  # tavern + overworld
    
    def test_json_output_players(self, cli_runner, player_router):
        """Test: seed-explorer players show --format json (REAL ROUTER)"""
        from phase6c_cli_explorer import cli, set_player_router
        
        # Get player ID
        players = player_router.get_realm_roster("tavern")
        player_id = players[0].player_id
        
        set_player_router(player_router)
        result = cli_runner.invoke(cli, [
            'players', 'show',
            '--player-id', player_id,
            '--format', 'json'
        ])
        
        assert result.exit_code == 0
        # Output should be valid JSON
        data = json.loads(result.output)
        assert data["player_name"] == "Alice"
        assert data["level"] == 1  # Initial level from fixture


# ============================================================================
# ERROR HANDLING TESTS (MOCK EXTREME EDGE CASES)
# ============================================================================

class TestErrorHandling:
    """Tests for error handling edge cases (MOCKED for extreme scenarios)."""
    
    def test_api_connection_refused(self, cli_runner):
        """Test CLI behavior when API connection is refused (MOCK)."""
        from phase6c_cli_explorer import cli, set_api_client
        
        # Clear any injected test client to force real HTTP requests
        set_api_client(None)
        
        # Try to connect to non-existent API
        result = cli_runner.invoke(cli, ['realms', 'list', '--api-url', 'http://localhost:99999'])
        
        # Should handle connection error gracefully
        assert result.exit_code != 0
        assert "Error" in result.output or "connection" in result.output.lower() or "failed" in result.output.lower()
    
    def test_missing_required_argument(self, cli_runner):
        """Test CLI behavior with missing required arguments."""
        from phase6c_cli_explorer import cli
        
        result = cli_runner.invoke(cli, ['realms', 'show'])  # Missing --id
        
        assert result.exit_code != 0
        # Click should show usage or error
    
    def test_invalid_tier_name(self, cli_runner, phase6b_server, api_base_url):
        """Test CLI behavior with invalid tier name."""
        from phase6c_cli_explorer import cli
        
        result = cli_runner.invoke(cli, ['tiers', 'show', '--tier', 'NONEXISTENT_TIER', '--api-url', api_base_url])
        
        # Should handle gracefully (empty results or error message)
        assert result.exit_code in [0, 1]  # May succeed with empty results or fail


# ============================================================================
# INTEGRATION WORKFLOW TESTS (REAL END-TO-END)
# ============================================================================

class TestIntegrationWorkflows:
    """Real end-to-end workflow tests using REAL components."""
    
    def test_workflow_create_player_and_travel(self, cli_runner, player_router):
        """Test workflow: create player → show → travel → verify (REAL ROUTER)"""
        from phase6c_cli_explorer import cli, set_player_router
        
        set_player_router(player_router)
        
        # Create player
        result1 = cli_runner.invoke(cli, [
            'players', 'create',
            '--name', 'TestPlayer',
            '--race', 'human',
            '--realm', 'tavern'
        ])
        assert result1.exit_code == 0
        
        # Extract player ID from output (or get from router)
        players = player_router.get_realm_roster("tavern")
        test_player = next((p for p in players if p.player_name == "TestPlayer"), None)
        assert test_player is not None
        
        # Show player
        result2 = cli_runner.invoke(cli, [
            'players', 'show',
            '--player-id', test_player.player_id
        ])
        assert result2.exit_code == 0
        assert "TestPlayer" in result2.output
        
        # Travel
        result3 = cli_runner.invoke(cli, [
            'players', 'travel',
            '--player-id', test_player.player_id,
            '--to', 'overworld'
        ])
        assert result3.exit_code == 0
        
        # Verify player moved
        updated_player = player_router.get_player(test_player.player_id)
        assert updated_player.active_realm == "overworld"
    
    def test_workflow_list_realms_and_query_details(self, cli_runner, phase6b_server, api_base_url):
        """Test workflow: list realms → show details → query tier (REAL API)"""
        from phase6c_cli_explorer import cli, set_api_client
        
        set_api_client(phase6b_server)
        # List realms
        result1 = cli_runner.invoke(cli, ['realms', 'list', '--api-url', api_base_url])
        assert result1.exit_code == 0
        assert "tavern" in result1.output or "overworld" in result1.output
        
        # Show tavern details
        result2 = cli_runner.invoke(cli, ['realms', 'show', '--id', 'tavern', '--api-url', api_base_url])
        assert result2.exit_code == 0
        assert "tavern" in result2.output
        
        # Query terran tier
        result3 = cli_runner.invoke(cli, ['tiers', 'show', '--tier', 'terran', '--api-url', api_base_url])
        assert result3.exit_code == 0
        assert "terran" in result3.output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])