# Game Registration Guide - The Seed MMO

Welcome to **The Seed** - a multiverse simulation framework where developers can register their games to appear in a shared, interconnected space.

## Quick Start

### 1. Launch the MMO Server

```bash
cd E:/Tiny_Walnut_Games/the-seed
python web/launchers/launch_mmo_simulation.py
```

This starts:
- **MMO Orchestrator** (ws://localhost:8765) - Backend coordination
- **Web Server** (http://localhost:8000) - Dashboards & visualization
- **Browser** opens to Admin Dashboard

### 2. Register Your Game

Connect to the WebSocket API and register your game:

```python
import asyncio
import websockets
import json

async def register_game():
    async with websockets.connect('ws://localhost:8765') as ws:
        # Send registration request
        registration = {
            "action": "register_game",
            "game_id": "my_first_game",
            "realm_id": "My Game World",
            "developer_name": "Your Name",
            "description": "My awesome game in The Seed multiverse",
            "realm_type": "custom_realm",
            "adjacency": "cluster_main",
            "resonance": "adventure",
            "density": 0
        }
        
        await ws.send(json.dumps(registration))
        response = await ws.recv()
        print(json.loads(response))

asyncio.run(register_game())
```

### 3. Send Cross-Game Events

Once registered, publish events that other games can receive:

```python
event = {
    "action": "publish_event",
    "source_game_id": "my_first_game",
    "target_game_id": None,  # None = broadcast to all
    "event_type": "player_action",
    "data": {
        "player_id": "hero_123",
        "action": "defeated_boss",
        "loot": ["sword", "gold_100"]
    }
}

await ws.send(json.dumps(event))
```

### 4. Listen for Events

Receive events from other games:

```python
async def listen_for_events():
    async with websockets.connect('ws://localhost:8765') as ws:
        async for message in ws:
            event = json.loads(message)
            
            if event.get("event_type") == "cross_game_event":
                print(f"Event from {event['source_game_id']}: {event['event_type_detail']}")
                print(f"Data: {event['data']}")
```

## Architecture

### Control-Tick Synchronization

The MMO backend uses a **control-tick architecture** to coordinate multiple games:

```
Master Control-Tick (every N local ticks)
    ├─ Game 1: Local ticks complete
    ├─ Game 2: Local ticks complete
    └─ All games synchronized
    
    ↓ Propagate cross-game events
    
    ├─ Game 1 receives event from Game 2
    └─ Game 2 receives event from Game 1
```

**Key concepts:**
- **Control-Tick**: Master synchronization point (default: every 10 local ticks)
- **Local Tick**: Independent game loop (default: 100ms)
- **Cross-Game Event**: Message routed via STAT7 addressing
- **Realm Coordinate**: STAT7 address for your game's location

### STAT7 Addressing

Each registered game gets a **STAT7 coordinate** for routing:

```
stat7://realm_id/realm_type/adjacency/resonance/density
```

Examples:
- `stat7://My Game World/custom_realm/cluster_main/adventure/0`
- `stat7://Tavern/custom_realm/cluster_main/social/0`
- `stat7://Forest/custom_realm/cluster_main/wilderness/0`

## WebSocket API Reference

### Available Actions

| Action | Purpose | Returns |
|--------|---------|---------|
| `register_game` | Register game instance | `{"status": "registered", "game_id": "...", "realm_coordinate": "..."}` |
| `list_games` | Get all registered games | `{"event_type": "game_list", "games": [...]}` |
| `publish_event` | Send cross-game event | Event ID |
| `universe_state` | Get MMO metadata | `{"event_type": "universe_state", "metadata": {...}}` |

### Example: Full Workflow

```python
import asyncio
import websockets
import json
import uuid

async def full_mmo_workflow():
    async with websockets.connect('ws://localhost:8765') as ws:
        
        # 1. Register game
        print("[1] Registering game...")
        reg_msg = {
            "action": "register_game",
            "game_id": f"game_{uuid.uuid4().hex[:8]}",
            "realm_id": "The Enchanted Tower",
            "developer_name": "Dev Team",
            "description": "A tower filled with magical puzzles",
            "realm_type": "dungeon",
            "adjacency": "cluster_magic",
            "resonance": "mystery",
            "density": 0
        }
        await ws.send(json.dumps(reg_msg))
        response = await ws.recv()
        print(json.loads(response))
        game_id = reg_msg["game_id"]
        
        # 2. List all games
        print("\n[2] Listing all games...")
        await ws.send(json.dumps({"action": "list_games"}))
        response = await ws.recv()
        games = json.loads(response)
        print(f"Total games: {len(games['games'])}")
        
        # 3. Publish an event
        print("\n[3] Publishing cross-game event...")
        event_msg = {
            "action": "publish_event",
            "source_game_id": game_id,
            "target_game_id": None,  # Broadcast
            "event_type": "treasure_discovered",
            "data": {
                "location": "Tower Floor 3",
                "treasure": "Ancient Staff of Power",
                "difficulty": "hard"
            }
        }
        await ws.send(json.dumps(event_msg))
        print("Event published!")
        
        # 4. Listen for events
        print("\n[4] Listening for events (10 seconds)...")
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < 10:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=1)
                event = json.loads(response)
                if "event_type" in event and event["event_type"] != "control_tick_complete":
                    print(f"  <- {event.get('event_type')}: {event.get('data', {})}")
            except asyncio.TimeoutError:
                pass

asyncio.run(full_mmo_workflow())
```

## Multi-Realm Example

Create a multi-game experience where players can travel between realms:

```python
# Game 1: Tavern
tavern = {
    "action": "register_game",
    "game_id": "tavern_main",
    "realm_id": "The Golden Dragon Tavern",
    "developer_name": "Social Team",
    "description": "Gathering place for adventurers",
    "realm_type": "social",
    "adjacency": "hub",
    "resonance": "social",
}

# Game 2: Dungeon
dungeon = {
    "action": "register_game",
    "game_id": "dungeon_1",
    "realm_id": "Dark Caverns",
    "developer_name": "Adventure Team",
    "description": "Dangerous underground labyrinth",
    "realm_type": "dungeon",
    "adjacency": "quest_zone",
    "resonance": "danger",
}

# Game 3: Marketplace
marketplace = {
    "action": "register_game",
    "game_id": "marketplace_center",
    "realm_id": "Grand Marketplace",
    "developer_name": "Economy Team",
    "description": "Trading hub with vendors",
    "realm_type": "commerce",
    "adjacency": "hub",
    "resonance": "economy",
}

# When players finish dungeon, publish event
dungeon_victory = {
    "action": "publish_event",
    "source_game_id": "dungeon_1",
    "target_game_id": "tavern_main",
    "event_type": "player_completed_quest",
    "data": {
        "player": "hero_123",
        "quest": "defeat_dragon",
        "reward": "legendary_sword"
    }
}

# Tavern NPCs react to the victory announcement
```

## Performance Characteristics

- **Control-Tick Latency**: <5ms per tick (default)
- **Cross-Game Event Routing**: <50ms end-to-end
- **Supported Games**: 2-100 concurrent game instances
- **Players per Realm**: Depends on individual game implementation
- **Event Buffer Size**: 5000 recent events (for new client broadcast)

## Troubleshooting

### WebSocket Connection Refused
- Ensure MMO Orchestrator is running: `python web/launchers/launch_mmo_simulation.py`
- Check port 8765 is not in use: `netstat -an | findstr :8765`

### Game Registration Fails
- Ensure game_id is unique (no two games with same ID)
- Verify all required fields are present in registration message

### Cross-Game Events Not Received
- Make sure target_game_id is registered
- Check that events are within the 5000 event buffer size
- Verify WebSocket connection is still active

## Next Steps

1. **Implement Game State Sync**: Send periodic heartbeats with game state
2. **Add Player Transitions**: Let players move between realms
3. **Implement Shared Resources**: Create cross-realm economies
4. **Multi-Developer Collaboration**: Build interconnected game experiences

## API Reference

See `docs/Shared/API/` for detailed API documentation.

---

**The Seed** enables collaborative multiverse creation. Register your game and become part of the interconnected experience!