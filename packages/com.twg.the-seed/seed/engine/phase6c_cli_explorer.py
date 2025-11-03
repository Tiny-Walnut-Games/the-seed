"""
Phase 6C: CLI Explorer for STAT7 Multiverse

A command-line interface for exploring realms, NPCs, players, and tier hierarchies
through the Phase 6B REST API and Universal Player Router.

Date: 2025-10-31 (Halloween)
Author: Tiny Walnut Games
"""

import click
import json
import requests
from typing import Optional, Dict, Any, List
from pathlib import Path
import sys

# Add paths for importing Phase 6 components
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "web" / "server"))

# Global player router and API client for testing injection
_PLAYER_ROUTER = None
_API_CLIENT = None


def set_player_router(router):
    """Inject player router for testing (global state for CLI context)."""
    global _PLAYER_ROUTER
    _PLAYER_ROUTER = router


def get_player_router():
    """Get current player router instance."""
    global _PLAYER_ROUTER
    if _PLAYER_ROUTER is None:
        # Lazy import to avoid circular dependencies
        from universal_player_router import UniversalPlayerRouter
        _PLAYER_ROUTER = UniversalPlayerRouter()
    return _PLAYER_ROUTER


def set_api_client(client):
    """Inject API client for testing (TestClient instance)."""
    global _API_CLIENT
    _API_CLIENT = client


def get_api_client():
    """Get current API client instance."""
    return _API_CLIENT


# ============================================================================
# API CLIENT HELPER
# ============================================================================

class Phase6BAPIClient:
    """Client for Phase 6B REST API requests."""
    
    def __init__(self, base_url: str = "http://localhost:8000", test_client=None):
        self.base_url = base_url.rstrip("/")
        self.test_client = test_client  # FastAPI TestClient for testing
    
    def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request to API endpoint."""
        try:
            if self.test_client:
                # Use injected TestClient (for tests)
                response = self.test_client.get(endpoint)
                response.raise_for_status()
                return response.json()
            else:
                # Use real HTTP requests
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.ConnectionError:
            click.echo("Error: Unable to connect to API. Is the server running?", err=True)
            sys.exit(1)
        except requests.exceptions.Timeout:
            click.echo("Error: API request timed out.", err=True)
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            click.echo(f"Error: API request failed: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            # Handle TestClient exceptions
            click.echo(f"Error: API request failed: {e}", err=True)
            sys.exit(1)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to API endpoint."""
        try:
            if self.test_client:
                # Use injected TestClient (for tests)
                response = self.test_client.post(endpoint, json=data)
                response.raise_for_status()
                return response.json()
            else:
                # Use real HTTP requests
                url = f"{self.base_url}{endpoint}"
                response = requests.post(url, json=data, timeout=5)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.ConnectionError:
            click.echo("Error: Unable to connect to API. Is the server running?", err=True)
            sys.exit(1)
        except requests.exceptions.Timeout:
            click.echo("Error: API request timed out.", err=True)
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            click.echo(f"Error: API request failed: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            # Handle TestClient exceptions
            click.echo(f"Error: API request failed: {e}", err=True)
            sys.exit(1)


# ============================================================================
# OUTPUT FORMATTERS
# ============================================================================

def output_json(data: Any):
    """Output data as formatted JSON."""
    click.echo(json.dumps(data, indent=2))


def output_text(title: str, data: Dict[str, Any]):
    """Output data as human-readable text."""
    click.echo(f"\n{title}")
    click.echo("=" * len(title))
    for key, value in data.items():
        click.echo(f"{key}: {value}")


# ============================================================================
# MAIN CLI GROUP
# ============================================================================

@click.group()
def cli():
    """STAT7 Multiverse Explorer CLI - Navigate realms, NPCs, and players."""
    pass


# ============================================================================
# REALMS COMMANDS
# ============================================================================

@cli.group()
def realms():
    """Manage and query realms."""
    pass


@realms.command("list")
@click.option("--tier", default=None, help="Filter by tier classification")
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "json"]))
@click.option("--api-url", default="http://localhost:8000", help="Phase 6B API base URL")
def realms_list(tier: Optional[str], output_format: str, api_url: str):
    """List all realms in the multiverse."""
    test_client = get_api_client()
    client = Phase6BAPIClient(api_url, test_client=test_client)
    
    # Query API
    endpoint = "/api/realms"
    if tier:
        endpoint += f"?tier={tier}"
    
    data = client.get(endpoint)
    
    if output_format == "json":
        output_json(data)
    else:
        click.echo("\n🌍 Realms in the Multiverse:")
        click.echo("=" * 40)
        
        realms_list = data.get("realms", [])
        for realm in realms_list:
            realm_id = realm.get("realm_id", "unknown")
            entity_count = realm.get("entity_count", 0)
            tier_info = realm.get("tier", "unknown")
            
            click.echo(f"\n  • {realm_id}")
            click.echo(f"    Tier: {tier_info}")
            click.echo(f"    Entities: {entity_count}")


@realms.command("show")
@click.option("--id", "realm_id", required=True, help="Realm ID to display")
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "json"]))
@click.option("--api-url", default="http://localhost:8000", help="Phase 6B API base URL")
def realms_show(realm_id: str, output_format: str, api_url: str):
    """Show detailed information about a specific realm."""
    test_client = get_api_client()
    client = Phase6BAPIClient(api_url, test_client=test_client)
    
    data = client.get(f"/api/realms/{realm_id}")
    
    if output_format == "json":
        output_json(data)
    else:
        click.echo(f"\n🏰 Realm: {realm_id}")
        click.echo("=" * 40)
        click.echo(f"Tier: {data.get('tier', 'unknown')}")
        click.echo(f"Theme: {data.get('theme', 'unknown')}")
        
        entities = data.get("entities", [])
        click.echo(f"\nEntities: {len(entities)}")
        for entity in entities[:5]:  # Show first 5
            click.echo(f"  • {entity.get('name', entity.get('id', 'Unknown'))}")
        
        if len(entities) > 5:
            click.echo(f"  ... and {len(entities) - 5} more")


# ============================================================================
# TIERS COMMANDS
# ============================================================================

@cli.group()
def tiers():
    """Query tier classification system."""
    pass


@tiers.command("list")
def tiers_list():
    """List all available tier classifications."""
    click.echo("\n📊 STAT7 Tier Classification System:")
    click.echo("=" * 40)
    click.echo("\n  • Celestial - Godly realms, divine planes")
    click.echo("  • Terran - Surface worlds, earthly domains")
    click.echo("  • Subterran - Underground, depths, underworld")
    click.echo("\nUse 'tiers show --tier <name>' to see realms in each tier.")


@tiers.command("show")
@click.option("--tier", required=True, help="Tier name to query")
@click.option("--api-url", default="http://localhost:8000", help="Phase 6B API base URL")
def tiers_show(tier: str, api_url: str):
    """Show realms in a specific tier."""
    test_client = get_api_client()
    client = Phase6BAPIClient(api_url, test_client=test_client)
    
    data = client.get(f"/api/tiers/{tier}")
    
    click.echo(f"\n🏔️ Tier: {tier.upper()}")
    click.echo("=" * 40)
    
    realms = data.get("realms", [])
    if realms:
        click.echo(f"Realms in this tier: {len(realms)}")
        for realm in realms:
            click.echo(f"  • {realm.get('realm_id', 'unknown')}")
    else:
        click.echo("No realms found in this tier.")


# ============================================================================
# NPCS COMMANDS
# ============================================================================

@cli.group()
def npcs():
    """Query and interact with NPCs."""
    pass


@npcs.command("list")
@click.option("--realm", default=None, help="Filter by realm")
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "json"]))
@click.option("--api-url", default="http://localhost:8000", help="Phase 6B API base URL")
def npcs_list(realm: Optional[str], output_format: str, api_url: str):
    """List all NPCs in the multiverse."""
    test_client = get_api_client()
    client = Phase6BAPIClient(api_url, test_client=test_client)
    
    endpoint = "/api/npcs"
    if realm:
        endpoint += f"?realm={realm}"
    
    data = client.get(endpoint)
    
    if output_format == "json":
        output_json(data)
    else:
        click.echo("\n👥 NPCs in the Multiverse:")
        click.echo("=" * 40)
        
        npcs_list = data.get("npcs", [])
        if npcs_list:
            for npc in npcs_list:
                npc_id = npc.get("npc_id", "unknown")
                npc_name = npc.get("name", "Unnamed")
                npc_realm = npc.get("realm", "unknown")
                click.echo(f"  • {npc_name} ({npc_id}) - Realm: {npc_realm}")
        else:
            click.echo("  No NPCs found.")


@npcs.command("show")
@click.option("--npc-id", required=True, help="NPC ID to display")
@click.option("--api-url", default="http://localhost:8000", help="Phase 6B API base URL")
def npcs_show(npc_id: str, api_url: str):
    """Show detailed information about a specific NPC."""
    test_client = get_api_client()
    client = Phase6BAPIClient(api_url, test_client=test_client)
    
    data = client.get(f"/api/npcs/{npc_id}")
    
    click.echo(f"\n🧙 NPC: {data.get('name', 'Unknown')}")
    click.echo("=" * 40)
    click.echo(f"ID: {npc_id}")
    click.echo(f"Realm: {data.get('realm', 'unknown')}")
    click.echo(f"Type: {data.get('type', 'unknown')}")
    
    if "dialogue" in data:
        click.echo(f"\nDialogue: {data['dialogue'][:100]}...")


# ============================================================================
# ZOOM COMMANDS
# ============================================================================

@cli.command("zoom")
@click.option("--entity", required=True, help="Entity ID to zoom into")
@click.option("--parent-realm", required=True, help="Parent realm containing entity")
@click.option("--anchors", default=None, help="Comma-separated semantic anchors")
@click.option("--api-url", default="http://localhost:8000", help="Phase 6B API base URL")
def zoom(entity: str, parent_realm: str, anchors: Optional[str], api_url: str):
    """Zoom into an entity to create a sub-realm."""
    test_client = get_api_client()
    client = Phase6BAPIClient(api_url, test_client=test_client)
    
    payload = {
        "entity_id": entity,
        "parent_realm_id": parent_realm
    }
    
    if anchors:
        payload["semantic_anchors"] = [a.strip() for a in anchors.split(",")]
    
    data = client.post("/api/zoom", payload)
    
    click.echo(f"\n🔍 Zoom Operation Complete")
    click.echo("=" * 40)
    click.echo(f"Sub-realm created: {data.get('subrealm_id', 'unknown')}")
    click.echo(f"Parent entity: {entity}")
    click.echo(f"Parent realm: {parent_realm}")
    
    if anchors:
        click.echo(f"Semantic anchors: {anchors}")


# ============================================================================
# PLAYERS COMMANDS
# ============================================================================

@cli.group()
def players():
    """Manage player characters."""
    pass


@players.command("list")
@click.option("--realm", required=True, help="Realm to query players")
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "json"]))
def players_list(realm: str, output_format: str):
    """List players in a specific realm."""
    router = get_player_router()
    players_in_realm = router.get_realm_roster(realm)
    
    if output_format == "json":
        data = {
            "realm": realm,
            "players": [
                {
                    "player_id": p.player_id,
                    "player_name": p.player_name,
                    "level": p.level,
                    "character_race": p.character_race,
                    "character_class": p.character_class
                }
                for p in players_in_realm
            ]
        }
        output_json(data)
    else:
        click.echo(f"\n🎮 Players in {realm}:")
        click.echo("=" * 40)
        
        if players_in_realm:
            for player in players_in_realm:
                click.echo(f"  • {player.player_name} (Level {player.level})")
                click.echo(f"    Race: {player.character_race}, Class: {player.character_class}")
        else:
            click.echo("  No players in this realm.")


@players.command("show")
@click.option("--player-id", required=True, help="Player ID to display")
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "json"]))
def players_show(player_id: str, output_format: str):
    """Show detailed information about a specific player."""
    router = get_player_router()
    player = router.get_player(player_id)
    
    if player is None:
        click.echo(f"Error: Player '{player_id}' not found.", err=True)
        sys.exit(1)
    
    if output_format == "json":
        data = {
            "player_id": player.player_id,
            "player_name": player.player_name,
            "level": player.level,
            "experience": player.experience,
            "character_race": player.character_race,
            "character_class": player.character_class,
            "active_realm": player.active_realm,
            "inventory": [
                {
                    "item_id": item.item_id,
                    "name": item.name,
                    "type": item.item_type,
                    "rarity": item.rarity
                }
                for item in player.inventory
            ],
            "reputation": {
                rep.faction.name.lower(): rep.score 
                for rep in player.reputation
            }
        }
        output_json(data)
    else:
        click.echo(f"\n⚔️ Player: {player.player_name}")
        click.echo("=" * 40)
        click.echo(f"Level: {player.level} | XP: {player.experience}")
        click.echo(f"Race: {player.character_race} | Class: {player.character_class}")
        click.echo(f"Current Realm: {player.active_realm}")
        
        click.echo(f"\n📦 Inventory ({len(player.inventory)} items):")
        for item in player.inventory[:5]:
            click.echo(f"  • {item.name} ({item.rarity} {item.item_type})")
        
        click.echo(f"\n🏆 Reputation:")
        for rep in player.reputation:
            click.echo(f"  • {rep.faction.name.lower()}: {rep.score}")


@players.command("create")
@click.option("--name", required=True, help="Player name")
@click.option("--race", required=True, help="Character race")
@click.option("--class", "char_class", default="Wanderer", help="Character class")
@click.option("--realm", required=True, help="Starting realm")
def players_create(name: str, race: str, char_class: str, realm: str):
    """Create a new player character."""
    router = get_player_router()
    
    player = router.create_player(
        player_name=name,
        character_race=race,
        character_class=char_class,
        starting_realm=realm
    )
    
    click.echo(f"\n✨ Player Created!")
    click.echo("=" * 40)
    click.echo(f"Name: {player.player_name}")
    click.echo(f"Race: {player.character_race}")
    click.echo(f"Class: {player.character_class}")
    click.echo(f"Starting Realm: {player.active_realm}")
    click.echo(f"Player ID: {player.player_id}")


@players.command("travel")
@click.option("--player-id", required=True, help="Player ID")
@click.option("--to", "destination", required=True, help="Destination realm")
def players_travel(player_id: str, destination: str):
    """Travel player to a different realm."""
    router = get_player_router()
    
    player = router.get_player(player_id)
    if player is None:
        click.echo(f"Error: Player '{player_id}' not found.", err=True)
        sys.exit(1)
    
    previous_realm = player.active_realm
    success, message = router.transition_player(player_id, previous_realm, destination)
    
    if not success:
        click.echo(f"Error: {message}", err=True)
        sys.exit(1)
    
    click.echo(f"\n🚀 Travel Complete!")
    click.echo("=" * 40)
    click.echo(f"Player: {player.player_name}")
    click.echo(f"From: {previous_realm}")
    click.echo(f"To: {destination}")


# ============================================================================
# UTILITY COMMANDS
# ============================================================================

@cli.command("health")
@click.option("--api-url", default="http://localhost:8000", help="Phase 6B API base URL")
def health(api_url: str):
    """Check health status of Phase 6B API."""
    test_client = get_api_client()
    client = Phase6BAPIClient(api_url, test_client=test_client)
    
    data = client.get("/api/health")
    
    click.echo("\n💚 API Health Check")
    click.echo("=" * 40)
    click.echo(f"Status: {data.get('status', 'unknown')}")
    click.echo(f"Version: {data.get('version', 'unknown')}")


@cli.command("stats")
@click.option("--api-url", default="http://localhost:8000", help="Phase 6B API base URL")
def stats(api_url: str):
    """Display aggregate statistics."""
    test_client = get_api_client()
    client = Phase6BAPIClient(api_url, test_client=test_client)
    router = get_player_router()
    
    # Get realm stats from API
    realms_data = client.get("/api/realms")
    realms = realms_data.get("realms", [])
    
    # Get player stats from router
    all_players = []
    for realm in realms:
        realm_id = realm.get("realm_id")
        if realm_id:
            all_players.extend(router.get_realm_roster(realm_id))
    
    click.echo("\n📊 Multiverse Statistics")
    click.echo("=" * 40)
    click.echo(f"Total Realms: {len(realms)}")
    click.echo(f"Total Players: {len(all_players)}")
    
    # Entity count
    total_entities = sum(r.get("entity_count", 0) for r in realms)
    click.echo(f"Total Entities: {total_entities}")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    cli()