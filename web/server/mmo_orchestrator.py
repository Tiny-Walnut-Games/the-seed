"""
MMO Orchestrator: Multi-Game Simulation Backend

Wires together:
- MultiGameTickEngine: Coordinates multiple game instances
- Phase 6 Orchestrator: Procedural universe generation
- FastAPI Server: HTTP REST API + WebSocket
- Game Registry: Developers register their games into the multiverse

Architecture:
- Master control-tick synchronizes all registered games
- Each game runs local ticks independently
- Cross-game events routed via STAT7 addressing
- HTTP serves static files and REST API (/api/*)
- WebSocket broadcasts live game state to connected clients

This is the core MMO backend that makes "The Seed" a functional multiverse.
"""

import asyncio
import json
import time
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import websockets
import uuid
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, staticfiles, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add paths
current_dir = Path(__file__).parent
repo_root = current_dir.parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(repo_root / "packages" / "com.twg.the-seed" / "seed" / "engine"))

from tick_engine import TickEngine, ReactionRule
from multigame_tick_engine import (
    MultiGameTickEngine,
    RealmCoordinate,
    CrossGameEvent,
    GameInstanceState,
)

# Import authentication system
from stat7_auth import get_auth_system, PermissionType

# Import autonomous narrative loop
from warbler_autonomous_loop import WarblerAutonomousLoop

# Import event store and player services
from event_store import EventStore
from universal_player_router import UniversalPlayerRouter
from warbler_multiverse_bridge import WarblerMultiverseBridge
from warbler_query_service import WarblerQueryService

# Optional Phase 6 imports (graceful fallback)
try:
    from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
    PHASE6_AVAILABLE = True
except ImportError:
    PHASE6_AVAILABLE = False
    UniverseDemoOrchestrator = None
    OrchestratorConfig = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# GAME REGISTRATION & MANAGEMENT
# ============================================================================

class GameRegistration:
    """Registration metadata for a game instance."""
    
    def __init__(self, 
                 game_id: str,
                 realm_id: str,
                 developer_name: str,
                 description: str,
                 tick_engine: TickEngine,
                 realm_coord: RealmCoordinate):
        self.game_id = game_id
        self.realm_id = realm_id
        self.developer_name = developer_name
        self.description = description
        self.tick_engine = tick_engine
        self.realm_coord = realm_coord
        self.registered_at = datetime.now(timezone.utc).isoformat()
        self.stats = {
            "events_sent": 0,
            "events_received": 0,
            "last_heartbeat": None,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize registration to dictionary."""
        return {
            "game_id": self.game_id,
            "realm_id": self.realm_id,
            "developer_name": self.developer_name,
            "description": self.description,
            "registered_at": self.registered_at,
            "realm_coordinate": {
                "realm_id": self.realm_coord.realm_id,
                "realm_type": self.realm_coord.realm_type,
                "adjacency": self.realm_coord.adjacency,
                "resonance": self.realm_coord.resonance,
                "density": self.realm_coord.density,
            },
            "stats": self.stats,
        }


# ============================================================================
# MMO ORCHESTRATOR
# ============================================================================

class MMOOrchestrator:
    """
    Main MMO backend orchestrator.
    
    Responsibilities:
    1. Game registration and lifecycle management
    2. Control-tick synchronization via MultiGameTickEngine
    3. Cross-game event routing and broadcasting
    4. WebSocket client communication
    5. Universe state management
    """
    
    def __init__(self,
                 ws_host: str = "localhost",
                 ws_port: int = 8765,
                 control_tick_interval_ticks: int = 10,
                 local_tick_interval_ms: int = 100):
        """Initialize MMO orchestrator."""
        
        self.ws_host = ws_host
        self.ws_port = ws_port
        self.is_running = False
        
        # Game orchestration
        self.orchestrator = MultiGameTickEngine(
            control_tick_interval_ticks=control_tick_interval_ticks,
            local_tick_interval_ms=local_tick_interval_ms
        )
        
        # Game registry (game_id -> GameRegistration)
        self.game_registry: Dict[str, GameRegistration] = {}
        
        # WebSocket clients
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Event buffer for new clients
        self.event_buffer: List[Dict[str, Any]] = []
        self.max_buffer_size = 5000
        
        # Universe metadata
        self.universe_metadata: Dict[str, Any] = {
            "mmo_version": "1.0",
            "started_at": None,
            "total_games_registered": 0,
            "total_control_ticks": 0,
            "total_cross_game_events": 0,
        }
        
        # Phase 6 orchestrator (optional)
        self.phase6_orchestrator: Optional[UniverseDemoOrchestrator] = None
        
        # Warbler Autonomous Loop (continuous narrative generation)
        self.warbler_autonomous_loop: Optional[WarblerAutonomousLoop] = None
        
        logger.info("✅ MMO Orchestrator initialized")
    
    # ========================================================================
    # GAME REGISTRATION API
    # ========================================================================
    
    def register_game(self,
                      game_id: str,
                      realm_id: str,
                      developer_name: str,
                      description: str,
                      realm_type: str = "custom_realm",
                      adjacency: str = "cluster_main",
                      resonance: str = "default",
                      density: int = 0) -> Dict[str, Any]:
        """
        Register a new game instance in the multiverse.
        
        Args:
            game_id: Unique game identifier
            realm_id: Realm name (displayed to players)
            developer_name: Developer attribution
            description: Game description
            realm_type: Type of realm ("custom_realm", "sol_system", etc.)
            adjacency: Region/cluster grouping
            resonance: Narrative context
            density: Instance multiplicity (0=main, 1+=instances)
        
        Returns:
            Registration response with STAT7 coordinate
        """
        if game_id in self.game_registry:
            raise ValueError(f"Game {game_id} already registered")
        
        # Create realm coordinate
        realm_coord = RealmCoordinate(
            realm_id=realm_id,
            realm_type=realm_type,
            adjacency=adjacency,
            resonance=resonance,
            density=density,
        )
        
        # Create tick engine for this game
        tick_engine = TickEngine(tick_interval_ms=100)
        
        # Register with orchestrator
        self.orchestrator.register_game(game_id, tick_engine, realm_coord)
        
        # Create registration record
        registration = GameRegistration(
            game_id=game_id,
            realm_id=realm_id,
            developer_name=developer_name,
            description=description,
            tick_engine=tick_engine,
            realm_coord=realm_coord,
        )
        
        self.game_registry[game_id] = registration
        self.universe_metadata["total_games_registered"] += 1
        
        logger.info(f"🎮 Registered game: {game_id} (realm: {realm_id})")
        
        # Broadcast registration event
        self._broadcast_event({
            "event_type": "game_registered",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "game_id": game_id,
            "realm_id": realm_id,
            "developer_name": developer_name,
            "stat7_uri": realm_coord.to_stat7_key(),
        })
        
        return {
            "status": "registered",
            "game_id": game_id,
            "realm_coordinate": realm_coord.to_stat7_key(),
            "ws_endpoint": f"ws://{self.ws_host}:{self.ws_port}",
        }
    
    def list_registered_games(self) -> List[Dict[str, Any]]:
        """Get list of all registered games."""
        return [reg.to_dict() for reg in self.game_registry.values()]
    
    def unregister_game(self, game_id: str) -> Dict[str, Any]:
        """Unregister a game from the multiverse."""
        if game_id not in self.game_registry:
            raise ValueError(f"Game {game_id} not found")
        
        self.orchestrator.unregister_game(game_id)
        del self.game_registry[game_id]
        
        logger.info(f"🗑️  Unregistered game: {game_id}")
        
        # Broadcast unregistration event
        self._broadcast_event({
            "event_type": "game_unregistered",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "game_id": game_id,
        })
        
        return {"status": "unregistered", "game_id": game_id}
    
    # ========================================================================
    # CROSS-GAME EVENT ROUTING
    # ========================================================================
    
    def publish_cross_game_event(self,
                                 source_game_id: str,
                                 target_game_id: Optional[str],
                                 event_type: str,
                                 data: Dict[str, Any]) -> str:
        """
        Publish event from one game to another (or broadcast to all).
        
        Args:
            source_game_id: Originating game
            target_game_id: Destination game (None = broadcast)
            event_type: Type of event
            data: Event payload
        
        Returns:
            Event ID
        """
        if source_game_id not in self.game_registry:
            raise ValueError(f"Source game {source_game_id} not registered")
        
        event_id = str(uuid.uuid4())
        source_realm = self.game_registry[source_game_id].realm_coord
        target_realm = None
        
        if target_game_id:
            if target_game_id not in self.game_registry:
                raise ValueError(f"Target game {target_game_id} not registered")
            target_realm = self.game_registry[target_game_id].realm_coord
        
        # Create cross-game event
        event = CrossGameEvent(
            event_id=event_id,
            source_realm=source_realm,
            target_realm=target_realm,
            event_type=event_type,
            data=data,
            control_tick_id=self.orchestrator.control_tick_count,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )
        
        self.orchestrator.cross_game_events.append(event)
        self.universe_metadata["total_cross_game_events"] += 1
        
        # Update stats
        self.game_registry[source_game_id].stats["events_sent"] += 1
        if target_game_id:
            self.game_registry[target_game_id].stats["events_received"] += 1
        
        logger.info(f"📡 Cross-game event: {source_game_id} → {target_game_id or 'broadcast'}")
        
        # Broadcast to all connected clients
        self._broadcast_event({
            "event_type": "cross_game_event",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": event_id,
            "source_game_id": source_game_id,
            "target_game_id": target_game_id,
            "event_type_detail": event_type,
            "data": data,
        })
        
        return event_id
    
    # ========================================================================
    # AUTONOMOUS NARRATIVE LOOP MANAGEMENT
    # ========================================================================
    
    def initialize_autonomous_narrative(self, event_store, warbler_query_service):
        """Initialize the Warbler autonomous narrative loop."""
        self.warbler_autonomous_loop = WarblerAutonomousLoop(
            event_store=event_store,
            warbler_query_service=warbler_query_service,
            tick_interval_ticks=1  # Run every tick
        )
        logger.info("🧬 Warbler Autonomous Loop initialized - narrative generation enabled")
    
    # ========================================================================
    # ORCHESTRATION EXECUTION
    # ========================================================================
    
    async def execute_control_tick(self) -> Dict[str, Any]:
        """Execute one control-tick synchronization cycle."""
        start_time = time.time()
        
        metrics = self.orchestrator.execute_control_tick()
        current_tick = self.orchestrator.control_tick_count
        
        # Run autonomous narrative generation for each realm
        autonomous_stats = {}
        if self.warbler_autonomous_loop:
            for game_id, registration in self.game_registry.items():
                realm_id = registration.realm_id
                try:
                    result = await self.warbler_autonomous_loop.execute_autonomous_tick(
                        realm_id=realm_id,
                        current_tick=current_tick
                    )
                    autonomous_stats[realm_id] = result
                    
                    # If events were generated, broadcast them to clients
                    if result.get("events_generated", 0) > 0:
                        for event in result.get("events", []):
                            self._broadcast_event({
                                "event_type": "autonomous_narrative_event",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "realm_id": realm_id,
                                "event": event,
                            })
                except Exception as e:
                    logger.warning(f"Error in autonomous narrative for {realm_id}: {e}")
                    autonomous_stats[realm_id] = {"status": "error", "error": str(e)}
        
        elapsed_ms = (time.time() - start_time) * 1000
        self.universe_metadata["total_control_ticks"] += 1
        
        # Update last heartbeat for all games
        for game_id, registration in self.game_registry.items():
            registration.stats["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        
        # Broadcast control-tick completion
        self._broadcast_event({
            "event_type": "control_tick_complete",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "control_tick_id": self.orchestrator.control_tick_count,
            "games_synced": len(self.game_registry),
            "autonomous_narratives": len([s for s in autonomous_stats.values() if s.get("status") == "success"]),
            "elapsed_ms": elapsed_ms,
        })
        
        return {
            "control_tick_id": metrics.get("control_tick_id"),
            "games_synced": len(self.game_registry),
            "autonomous_stats": autonomous_stats,
            "elapsed_ms": elapsed_ms,
        }
    
    async def run_orchestration_loop(self, max_ticks: Optional[int] = None):
        """
        Main orchestration loop.
        
        Continuously executes control-ticks, syncing all registered games.
        """
        logger.info("🚀 Starting MMO orchestration loop...")
        self.universe_metadata["started_at"] = datetime.now(timezone.utc).isoformat()
        self.is_running = True
        
        tick_count = 0
        
        try:
            while self.is_running:
                if max_ticks and tick_count >= max_ticks:
                    break
                
                await self.execute_control_tick()
                tick_count += 1
                
                # Yield to allow WebSocket handling
                await asyncio.sleep(0.1)
        
        except KeyboardInterrupt:
            logger.info("⏹️  Orchestration loop interrupted")
        finally:
            self.is_running = False
            logger.info(f"✅ Orchestration loop completed ({tick_count} ticks)")
    
    # ========================================================================
    # WEBSOCKET SERVER
    # ========================================================================
    
    async def register_client(self, websocket):
        """Register new WebSocket client."""
        client_id = str(uuid.uuid4())[:8]
        self.clients[client_id] = websocket
        
        # Accept the WebSocket connection first
        await websocket.accept()
        logger.info(f"➕ Client connected: {client_id}")
        
        # Send event buffer to new client (FastAPI WebSocket uses send_json)
        for event in self.event_buffer[-100:]:  # Last 100 events
            try:
                await websocket.send_json(event)
            except:
                pass
        
        return client_id
    
    async def unregister_client(self, client_id: str):
        """Unregister disconnected WebSocket client."""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"➖ Client disconnected: {client_id}")
    
    def _broadcast_event(self, event: Dict[str, Any]):
        """Queue event for broadcast to all connected clients."""
        self.event_buffer.append(event)
        if len(self.event_buffer) > self.max_buffer_size:
            self.event_buffer = self.event_buffer[-self.max_buffer_size:]
    
    async def broadcast_to_clients(self):
        """Broadcast queued events to all connected clients."""
        disconnected = set()
        
        for event in self.event_buffer[-10:]:  # Recent events
            for client_id, websocket in list(self.clients.items()):
                try:
                    # FastAPI WebSocket uses send_json
                    await websocket.send_json(event)
                except Exception:
                    disconnected.add(client_id)
        
        for client_id in disconnected:
            await self.unregister_client(client_id)
    
    async def start_websocket_server(self):
        """Start WebSocket server for client communication."""
        
        async def handle_client(websocket, path):
            client_id = await self.register_client(websocket)
            try:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        
                        # Route based on command
                        if data.get("action") == "list_games":
                            games = self.list_registered_games()
                            await websocket.send(json.dumps({
                                "event_type": "game_list",
                                "games": games,
                            }))
                        elif data.get("action") == "universe_state":
                            await websocket.send(json.dumps({
                                "event_type": "universe_state",
                                "metadata": self.universe_metadata,
                            }))
                    except json.JSONDecodeError:
                        pass
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                await self.unregister_client(client_id)
        
        logger.info(f"[WS] Starting WebSocket server on ws://{self.ws_host}:{self.ws_port}")
        async with websockets.serve(handle_client, self.ws_host, self.ws_port):
            # Run until explicitly stopped
            while self.is_running:
                await asyncio.sleep(0.1)
    
    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    
    async def initialize_phase6_universe(self) -> Optional[Dict[str, Any]]:
        """Initialize Phase 6 procedural universe if available."""
        if not PHASE6_AVAILABLE:
            logger.warning("Phase 6 Orchestrator not available, skipping universe generation")
            return None
        
        try:
            logger.info("🌌 Initializing Phase 6 procedural universe...")
            config = OrchestratorConfig(seed=42, orbits=2)
            self.phase6_orchestrator = UniverseDemoOrchestrator(config)
            
            # metadata = await self.phase6_orchestrator.launch_demo()
            # logger.info(f"✅ Phase 6 universe initialized: {metadata.realm_entity_counts}")
            # return metadata
        except Exception as e:
            logger.error(f"❌ Phase 6 initialization failed: {e}")
            return None
    
    async def initialize_demo_games(self):
        """Initialize some demo games for testing."""
        logger.info("🎮 Initializing demo games...")
        
        # Demo game 1: Tavern
        self.register_game(
            game_id="demo_tavern",
            realm_id="The Golden Dragon Tavern",
            developer_name="The Seed Framework",
            description="A welcoming tavern where adventurers gather to share stories",
            realm_type="custom_realm",
            adjacency="cluster_main",
            resonance="social",
            density=0
        )
        
        # Demo game 2: Forest
        self.register_game(
            game_id="demo_forest",
            realm_id="Whisperwood Forest",
            developer_name="The Seed Framework",
            description="A mystical forest teeming with magical creatures",
            realm_type="custom_realm",
            adjacency="cluster_main",
            resonance="wilderness",
            density=0
        )
        
        logger.info(f"✅ Demo games initialized ({len(self.game_registry)} total)")
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    async def start_background_tasks(self, demo_mode: bool = True, max_ticks: Optional[int] = None):
        """Start background orchestration tasks (orchestration + broadcast loops)."""
        
        # Initialize universe
        # await self.initialize_phase6_universe()
        
        # Initialize demo games
        if demo_mode:
            await self.initialize_demo_games()
        
        # Start orchestration loop
        orch_task = asyncio.create_task(self.run_orchestration_loop(max_ticks))
        
        # Broadcast loop
        async def broadcast_loop():
            while self.is_running:
                await self.broadcast_to_clients()
                await asyncio.sleep(0.1)
        
        bc_task = asyncio.create_task(broadcast_loop())
        
        logger.info("=" * 70)
        logger.info("🎮 THE SEED - MMO ORCHESTRATOR")
        logger.info("=" * 70)
        logger.info("✅ MMO Orchestrator started!")
        logger.info(f"   HTTP API: http://localhost:8000/api")
        logger.info(f"   WebSocket: ws://localhost:8000/ws")
        logger.info(f"   Games: {len(self.game_registry)} registered")
        logger.info("=" * 70)
        
        self.is_running = True
        return orch_task, bc_task


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Global orchestrator instance
_orchestrator: Optional[MMOOrchestrator] = None
_background_tasks: Optional[tuple] = None
_auth_system: Optional[Any] = None


# ============================================================================
# LIFESPAN EVENTS & APP CREATION
# ============================================================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global _orchestrator, _background_tasks, _auth_system
    
    # Startup
    logger.info("Starting MMO Orchestrator...")
    
    # Initialize authentication system (with TEST MODE if enabled)
    test_mode_enabled = os.environ.get("STAT7_TEST_MODE", "").lower() in ("true", "1", "yes")
    _auth_system = get_auth_system(enable_test_mode=test_mode_enabled)
    
    # Log test mode status
    if test_mode_enabled:
        logger.info("=" * 70)
        logger.info("🔐 TEST MODE ENABLED - Pre-seeded test accounts available:")
        logger.info("=" * 70)
        logger.info("  ADMIN    : ID='test-admin-001'    (full admin privileges)")
        logger.info("  PUBLIC   : ID='test-public-001'   (read-only access)")
        logger.info("  DEMO ADM : ID='test-demo-001'     (sandbox admin, simulation control)")
        logger.info("=" * 70)
    
    # Initialize event store for narrative persistence
    store_dir = Path(__file__).parent.parent / "event_store_data"
    event_store = EventStore(str(store_dir))
    logger.info(f"📝 Event store initialized at {store_dir}")
    
    # Initialize player router for cross-realm player management
    player_router = UniversalPlayerRouter()
    logger.info("👥 Universal player router initialized")
    
    # Initialize warbler bridge for dialogue context
    warbler_bridge = WarblerMultiverseBridge(player_router)
    logger.info("🌉 Warbler multiverse bridge initialized")
    
    # Initialize warbler query service for NPC responses
    warbler_query_service = WarblerQueryService(
        player_router=player_router,
        warbler_bridge=warbler_bridge,
        enable_cache=True
    )
    logger.info("🧙 Warbler query service initialized")
    
    # Use 0.0.0.0 for Docker compatibility (binds to all interfaces)
    _orchestrator = MMOOrchestrator(ws_host="0.0.0.0", ws_port=8000)
    
    # Initialize autonomous narrative loop with dependencies
    _orchestrator.initialize_autonomous_narrative(event_store, warbler_query_service)
    logger.info("🧬 Autonomous narrative loop integrated with orchestrator")
    
    orch_task, bc_task = await _orchestrator.start_background_tasks(demo_mode=True)
    _background_tasks = (orch_task, bc_task)
    
    yield
    
    # Shutdown
    if _orchestrator:
        _orchestrator.is_running = False
        logger.info("⏹️  Orchestrator shutting down...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="The Seed MMO Orchestrator",
    description="Multi-game orchestration backend for the multiverse",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from web directory
web_dir = Path(__file__).parent.parent
app.mount("/static", staticfiles.StaticFiles(directory=web_dir), name="static")


# ============================================================================
# HTTP REST API ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    if _orchestrator is None:
        return JSONResponse({"status": "initializing"}, status_code=503)
    
    return {
        "status": "healthy",
        "orchestrator": "running" if _orchestrator.is_running else "stopped",
        "games": len(_orchestrator.game_registry),
        "clients": len(_orchestrator.clients),
        "events_buffered": len(_orchestrator.event_buffer),
    }


@app.get("/api/realms")
async def get_realms():
    """Get all registered game realms."""
    if _orchestrator is None:
        return JSONResponse({"realms": []})
    
    realms = []
    for game_id, registration in _orchestrator.game_registry.items():
        realms.append({
            "game_id": game_id,
            "realm_id": registration.realm_id,
            "developer_name": registration.developer_name,
            "description": registration.description,
            "registered_at": registration.registered_at,
            "realm_coordinate": {
                "realm_id": registration.realm_coord.realm_id,
                "realm_type": registration.realm_coord.realm_type,
                "adjacency": registration.realm_coord.adjacency,
                "resonance": registration.realm_coord.resonance,
                "density": registration.realm_coord.density,
            },
            "stats": registration.stats,
        })
    
    return {"realms": realms}


@app.get("/api/npcs")
async def get_npcs():
    """Get NPC data (placeholder for future integration)."""
    return {
        "npcs": [],
        "total": 0,
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    if _orchestrator is None:
        return {"stats": {}}
    
    return {
        "stats": _orchestrator.universe_metadata,
        "games": len(_orchestrator.game_registry),
        "clients": len(_orchestrator.clients),
        "events": len(_orchestrator.event_buffer),
    }


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login")
async def login_endpoint(request: Request):
    """POST /api/auth/login — Get token from STAT7.ID."""
    if _auth_system is None:
        return JSONResponse({"error": "Authentication system not initialized"}, status_code=503)
    
    try:
        body = await request.json()
        stat7_id = body.get("stat7_id")
        
        if not stat7_id:
            return JSONResponse({"error": "Missing stat7_id"}, status_code=400)
        
        token = _auth_system.get_token_for_id(stat7_id)
        
        if not token:
            return JSONResponse(
                {"error": "STAT7.ID not found or no active token", "reason": "LOGIN_FAILED"},
                status_code=401
            )
        
        return {
            "token": token,
            "stat7_id": stat7_id,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/auth/register")
async def register_endpoint(request: Request):
    """POST /api/auth/register — Create new STAT7.ID via registration code."""
    if _auth_system is None:
        return JSONResponse({"error": "Authentication system not initialized"}, status_code=503)
    
    try:
        body = await request.json()
        registration_code = body.get("registration_code")
        username = body.get("username")
        email = body.get("email")
        
        if not all([registration_code, username, email]):
            return JSONResponse({"error": "Missing required fields"}, status_code=400)
        
        user = _auth_system.register_user_with_code(
            registration_code=registration_code,
            username=username,
            email=email,
            desired_role="public"  # Default role for self-registration
        )
        
        if not user:
            return JSONResponse(
                {"error": "Registration failed", "reason": "INVALID_CODE_OR_CONFLICT"},
                status_code=400
            )
        
        return JSONResponse({
            "stat7_id": user.id,
            "username": user.username,
            "role": user.role,
            "status": "success"
        }, status_code=201)
    
    except Exception as e:
        logger.error(f"Register error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/auth/generate-qr")
async def generate_qr_endpoint(request: Request):
    """POST /api/auth/generate-qr — Admin generates QR for friend."""
    if _auth_system is None:
        return JSONResponse({"error": "Authentication system not initialized"}, status_code=503)
    
    try:
        qr_data = _auth_system.create_qr_registration_code()
        
        return {
            "code": qr_data["code"],
            "qr_data": qr_data["qr_data"],
            "expires_at": qr_data["expires_at"],
            "instructions": qr_data["instructions"]
        }
    
    except Exception as e:
        logger.error(f"Generate QR error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/admin/audit-log")
async def audit_log_endpoint(request: Request):
    """POST /api/admin/audit-log — Get audit logs (admin only)."""
    if _auth_system is None:
        return JSONResponse({"error": "Authentication system not initialized"}, status_code=503)
    
    try:
        body = await request.json()
        token = body.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
        limit = body.get("limit", 10)
        
        # Validate token and check permission
        user = _auth_system.validate_token(token) if token else None
        
        if not user or not user.has_permission(PermissionType.ADMIN_AUDIT_READ):
            return JSONResponse({"error": "Permission denied"}, status_code=403)
        
        logs = _auth_system.get_audit_logs(limit=limit)
        
        return {
            "logs": [log.to_dict() for log in logs],
            "count": len(logs)
        }
    
    except Exception as e:
        logger.error(f"Audit log error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/admin/users")
async def admin_users_endpoint(request: Request):
    """POST /api/admin/users — Create demo user (admin only)."""
    if _auth_system is None:
        return JSONResponse({"error": "Authentication system not initialized"}, status_code=503)
    
    try:
        body = await request.json()
        token = body.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
        username = body.get("username")
        email = body.get("email")
        desired_role = body.get("role", "demo_admin")
        
        if not all([username, email]):
            return JSONResponse({"error": "Missing required fields"}, status_code=400)
        
        # Validate token and check permission
        user = _auth_system.validate_token(token) if token else None
        
        if not user or not user.has_permission(PermissionType.ADMIN_USER_MANAGE):
            return JSONResponse({"error": "Permission denied"}, status_code=403)
        
        new_user = _auth_system.admin_create_demo_user(
            admin_id=user.id,
            username=username,
            email=email,
            desired_role=desired_role
        )
        
        if not new_user:
            return JSONResponse({"error": "Failed to create user"}, status_code=400)
        
        return JSONResponse({
            "stat7_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        }, status_code=201)
    
    except Exception as e:
        logger.error(f"Admin users error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for game registration and events."""
    if _orchestrator is None:
        await websocket.close(code=4000, reason="Orchestrator not initialized")
        return
    
    client_id = await _orchestrator.register_client(websocket)
    
    try:
        # Handle incoming messages
        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                
                # Route based on action
                if data.get("action") == "list_games":
                    games = _orchestrator.list_registered_games()
                    await websocket.send_json({
                        "event_type": "game_list",
                        "games": games,
                    })
                elif data.get("action") == "universe_state":
                    await websocket.send_json({
                        "event_type": "universe_state",
                        "metadata": _orchestrator.universe_metadata,
                    })
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await _orchestrator.unregister_client(client_id)


# ============================================================================
# STATIC FILE SERVING
# ============================================================================

@app.get("/")
async def serve_root():
    """Serve root - redirect to dashboard."""
    return FileResponse(web_dir / "phase6c_dashboard.html")


@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files."""
    file_path_obj = web_dir / file_path
    
    # Security: prevent directory traversal
    if not file_path_obj.resolve().is_relative_to(web_dir.resolve()):
        return JSONResponse({"error": "Not found"}, status_code=404)
    
    # Check if file exists
    if file_path_obj.is_file():
        return FileResponse(file_path_obj)
    
    return JSONResponse({"error": "Not found"}, status_code=404)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="The Seed MMO Orchestrator")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port")
    parser.add_argument("--ticks", type=int, default=None, help="Max control-ticks")
    parser.add_argument("--demo", action="store_true", default=True, help="Initialize demo games")
    parser.add_argument("--no-demo", dest="demo", action="store_false", help="Disable demo games")
    
    args = parser.parse_args()
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
    )