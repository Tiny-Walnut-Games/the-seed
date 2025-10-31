
#!/usr/bin/env python3
"""
STAT7 Admin API Server

Serves the admin entity viewer UI and provides REST API endpoints.
Also includes WebSocket support for real-time entity updates.

Usage:
    python admin_api_server.py

Then open: http://localhost:8000/admin-entity-viewer.html
"""

import json
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time
import math
import random

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# =====================================================================
# Sample Entity Data Generator
# =====================================================================

class EntityDataGenerator:
    """Generates sample entity data for the simulation."""

    PLAYER_TEMPLATES = [
        {"name": "AdventureSeeker", "level": 12, "class": "Warrior"},
        {"name": "MagicWeaver", "level": 15, "class": "Mage"},
        {"name": "ShadowHunter", "level": 10, "class": "Rogue"},
        {"name": "HolyGuard", "level": 14, "class": "Paladin"},
        {"name": "NaturesCaller", "level": 11, "class": "Druid"},
    ]

    NPC_TEMPLATES = [
        {"name": "Barkeep", "type": "vendor"},
        {"name": "Town Guard", "type": "guard"},
        {"name": "Merchant", "type": "vendor"},
        {"name": "Innkeeper", "type": "innkeeper"},
    ]

    REALMS = ["alpha", "void", "shadow"]

    @staticmethod
    def generate_entities(count: int = 10):
        """Generate sample entities with realistic data."""
        entities = []

        # Add players
        for i, template in enumerate(EntityDataGenerator.PLAYER_TEMPLATES[:count//2]):
            entity = {
                "id": f"player_{i}",
                "name": template["name"],
                "type": "player",
                "level": template["level"],
                "class": template["class"],
                "realm": random.choice(EntityDataGenerator.REALMS),
                "position": [
                    random.uniform(-100, 100),
                    random.uniform(0, 200),
                    random.uniform(-100, 100)
                ],
                "heading": random.uniform(0, 360),
                "health": random.randint(70, 100),
                "mana": random.randint(50, 100),
                "lastAction": random.choice(["walk", "cast_spell", "attack", "idle", "talk"]),
                "activeCommand": random.choice(["move_forward", "cast_fireball", "none"]),
                "lastUpdate": datetime.utcnow().isoformat() + "Z",
                "_version": random.randint(1, 100),
            }
            entities.append(entity)

        # Add NPCs
        for i, template in enumerate(EntityDataGenerator.NPC_TEMPLATES):
            entity = {
                "id": f"npc_{i}",
                "name": template["name"],
                "type": "npc",
                "npcType": template["type"],
                "realm": random.choice(EntityDataGenerator.REALMS),
                "position": [
                    random.uniform(-100, 100),
                    random.uniform(0, 50),
                    random.uniform(-100, 100)
                ],
                "heading": random.uniform(0, 360),
                "lastAction": "patrol",
                "lastUpdate": datetime.utcnow().isoformat() + "Z",
                "_version": random.randint(1, 50),
            }
            entities.append(entity)

        return entities


# =====================================================================
# HTTP Request Handler
# =====================================================================

class AdminAPIHandler(SimpleHTTPRequestHandler):
    """Handle HTTP requests for admin API."""

    # Sample entity database (in production, this would connect to real STAT7)
    entities_db = EntityDataGenerator.generate_entities(12)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # API Endpoints
        if path == '/api/entities':
            self.send_json(200, {
                "entities": self.entities_db,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "count": len(self.entities_db)
            })
            return

        elif path.startswith('/api/entities/'):
            entity_id = path.split('/')[-1]
            entity = next((e for e in self.entities_db if e['id'] == entity_id), None)
            if entity:
                self.send_json(200, {"entity": entity})
            else:
                self.send_json(404, {"error": "Entity not found"})
            return

        elif path == '/api/stats':
            stats = {
                "total_entities": len(self.entities_db),
                "players": len([e for e in self.entities_db if e['type'] == 'player']),
                "npcs": len([e for e in self.entities_db if e['type'] == 'npc']),
                "realms": list(set(e['realm'] for e in self.entities_db)),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self.send_json(200, stats)
            return

        elif path == '/admin-entity-viewer.html':
            # Serve the admin UI
            admin_path = Path(__file__).parent.parent / "admin-entity-viewer.html"
            if admin_path.exists():
                self.send_file(admin_path)
                return

        # Default: serve static files
        super().do_GET()

    def send_json(self, status_code: int, data: dict):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_file(self, file_path: Path):
        """Send file response."""
        try:
            content = file_path.read_bytes()
            self.send_response(200)

            # Determine content type
            if file_path.suffix == '.html':
                content_type = 'text/html'
            elif file_path.suffix == '.js':
                content_type = 'application/javascript'
            elif file_path.suffix == '.css':
                content_type = 'text/css'
            else:
                content_type = 'application/octet-stream'

            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_json(500, {"error": str(e)})

    def log_message(self, format, *args):
        """Suppress default logging."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {format % args}", file=sys.stderr)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


# =====================================================================
# Background Entity Updater
# =====================================================================

def simulate_entity_updates():
    """Background thread that simulates entity updates."""
    print("🎲 Starting entity simulation updates...", file=sys.stderr)

    while True:
        time.sleep(3)  # Update every 3 seconds

        # Simulate movement
        for entity in AdminAPIHandler.entities_db:
            if entity['type'] == 'player':
                # Players move around
                heading = entity.get('heading', 0)
                speed = random.uniform(0.5, 2.0)

                dx = math.cos(math.radians(heading)) * speed
                dz = math.sin(math.radians(heading)) * speed

                entity['position'][0] += dx
                entity['position'][2] += dz

                # Random actions
                entity['lastAction'] = random.choice(["walk", "idle", "cast_spell"])
                entity['health'] = max(0, entity['health'] + random.randint(-5, 5))

                # Random heading changes
                if random.random() < 0.3:
                    entity['heading'] = (entity['heading'] + random.uniform(-45, 45)) % 360

                entity['lastUpdate'] = datetime.utcnow().isoformat() + "Z"
                entity['_version'] += 1


# =====================================================================
# Main Server
# =====================================================================

def main():
    """Start the admin API server."""

    PORT = 8000
    ADDRESS = "0.0.0.0"

    # Start background update thread
    update_thread = threading.Thread(target=simulate_entity_updates, daemon=True)
    update_thread.start()

    # Create and run server
    server_address = (ADDRESS, PORT)
    httpd = HTTPServer(server_address, AdminAPIHandler)

    print("\n" + "="*70)
    print("🚀 STAT7 ADMIN API SERVER")
    print("="*70)
    print(f"✓ Listening on http://localhost:{PORT}")
    print(f"✓ Admin UI: http://localhost:{PORT}/admin-entity-viewer.html")
    print(f"✓ API: http://localhost:{PORT}/api/entities")
    print(f"✓ Entities: {len(AdminAPIHandler.entities_db)} simulated entities")
    print("="*70)
    print("\nPress Ctrl+C to stop\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...", file=sys.stderr)
        httpd.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
