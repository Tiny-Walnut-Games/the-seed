#!/usr/bin/env python3
"""
STAT7 HTTP Server with Authentication & Authorization

Features:
- Static file serving via SimpleHTTPRequestHandler
- JSON API endpoints for authentication (/api/auth/*, /api/admin/*)
- Auth middleware intercepts all requests
- Immutable audit logging for all access
- Role-based permission enforcement
- TEST MODE: Pre-seeded test STAT7.IDs for E2E testing (via STAT7_TEST_MODE env var)

Environment Variables:
- STAT7_TEST_MODE=true/1/yes  : Enable test mode with pre-seeded test accounts
                                  (test-admin-001, test-public-001, test-demo-001)
"""

import os
import sys
import json
import socketserver
import traceback
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

# Import auth system
sys.path.insert(0, os.path.dirname(__file__))
from stat7_auth import get_auth_system, PermissionType
from auth_middleware import get_auth_middleware


class AuthenticatedHandler(SimpleHTTPRequestHandler):
    """HTTP handler with STAT7.ID authentication."""
    
    def __init__(self, *args, **kwargs):
        web_dir = os.path.dirname(os.path.dirname(__file__))
        super().__init__(*args, directory=web_dir, **kwargs)
    
    def end_headers(self):
        """Send security headers (no CORS wildcard)."""
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        super().end_headers()
    
    def _send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _get_body(self) -> dict:
        """Read and parse JSON request body."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            return json.loads(body) if body else {}
        except Exception as e:
            return {"error": str(e)}
    
    def _check_auth(self, required_permission: str = None) -> tuple:
        """
        Check authentication for current request.
        
        Returns:
            (is_allowed: bool, user: STAT7ID or None, reason: str)
        """
        middleware = get_auth_middleware()
        auth_header = self.headers.get('Authorization', '')
        cookies_header = self.headers.get('Cookie', '')
        
        is_ok, user, reason = middleware.simple_http_check(
            path=self.path,
            authorization_header=auth_header,
            cookies_header=cookies_header,
            ip_address=self.client_address[0] if self.client_address else ""
        )
        
        return is_ok, user, reason
    
    def do_OPTIONS(self):
        """Handle CORS preflight (allow all)."""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests with auth enforcement."""
        # Redirect root to stat7_auth.html
        if self.path == '/':
            self.path = '/stat7_auth.html'
        
        # Check if auth is required
        middleware = get_auth_middleware()
        if self.path not in middleware.public_paths:
            # Protected path - require auth
            is_ok, user, reason = self._check_auth()
            if not is_ok:
                self._send_json({"error": reason}, 401 if not user else 403)
                return
        
        return super().do_GET()
    
    def do_POST(self):
        """Handle POST requests (API endpoints)."""
        # =====================================================================
        # PUBLIC ENDPOINTS (no auth required)
        # =====================================================================
        
        if self.path == '/api/auth/login':
            return self._handle_login()
        
        if self.path == '/api/auth/register':
            return self._handle_register()
        
        if self.path == '/api/auth/generate-qr':
            return self._handle_generate_qr()
        
        # =====================================================================
        # PROTECTED ENDPOINTS (auth required)
        # =====================================================================
        
        is_ok, user, reason = self._check_auth()
        if not is_ok:
            self._send_json({"error": reason}, 401 if not user else 403)
            return
        
        # Admin endpoints
        if self.path == '/api/admin/audit-log':
            return self._handle_audit_log(user)
        
        if self.path == '/api/admin/users':
            return self._handle_admin_users(user)
        
        # Query endpoints (narration, entity info, etc.)
        if self.path == '/api/query/entity-narration':
            return self._handle_entity_narration(user)
        
        # Unknown endpoint
        self._send_json({"error": "Not found"}, 404)
    
    def _handle_login(self):
        """POST /api/auth/login — Get token from STAT7.ID."""
        try:
            body = self._get_body()
            stat7_id = body.get('stat7_id')
            
            if not stat7_id:
                self._send_json({"error": "Missing stat7_id"}, 400)
                return
            
            auth = get_auth_system()
            token = auth.get_token_for_id(stat7_id)
            
            if not token:
                self._send_json(
                    {"error": "STAT7.ID not found or no active token", "reason": "LOGIN_FAILED"},
                    401
                )
                return
            
            self._send_json({
                "token": token,
                "stat7_id": stat7_id,
                "status": "success"
            }, 200)
        
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    
    def _handle_register(self):
        """POST /api/auth/register — Create new STAT7.ID via registration code."""
        try:
            body = self._get_body()
            registration_code = body.get('registration_code')
            username = body.get('username')
            email = body.get('email')
            
            if not all([registration_code, username, email]):
                self._send_json({"error": "Missing required fields"}, 400)
                return
            
            auth = get_auth_system()
            user = auth.register_user_with_code(
                registration_code=registration_code,
                username=username,
                email=email,
                desired_role="public"  # Default role for self-registration
            )
            
            if not user:
                self._send_json(
                    {"error": "Registration failed", "reason": "INVALID_CODE_OR_CONFLICT"},
                    400
                )
                return
            
            self._send_json({
                "stat7_id": user.id,
                "username": user.username,
                "role": user.role,
                "status": "success"
            }, 201)
        
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    
    def _handle_generate_qr(self):
        """POST /api/auth/generate-qr — Admin generates QR for friend."""
        try:
            body = self._get_body()
            admin_token = body.get('token')  # Optional; can use Authorization header
            
            auth = get_auth_system()
            qr_data = auth.create_qr_registration_code()
            
            self._send_json({
                "code": qr_data["code"],
                "qr_data": qr_data["qr_data"],
                "expires_at": qr_data["expires_at"],
                "instructions": qr_data["instructions"]
            }, 200)
        
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    
    def _handle_audit_log(self, user):
        """POST /api/admin/audit-log — Get audit logs (admin only)."""
        try:
            # Check permission
            if not user or "admin:audit:read" not in user.permissions:
                self._send_json({"error": "Permission denied"}, 403)
                return
            
            body = self._get_body()
            limit = body.get('limit', 10)
            
            auth = get_auth_system()
            logs = auth.get_audit_logs(limit=limit)
            
            self._send_json({
                "logs": [log.to_dict() for log in logs],
                "count": len(logs)
            }, 200)
        
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    
    def _handle_admin_users(self, user):
        """POST /api/admin/users — Create demo user (admin only)."""
        try:
            # Check permission
            if not user or "admin:user:manage" not in user.permissions:
                self._send_json({"error": "Permission denied"}, 403)
                return
            
            body = self._get_body()
            username = body.get('username')
            email = body.get('email')
            desired_role = body.get('role', 'demo_admin')
            
            if not all([username, email]):
                self._send_json({"error": "Missing required fields"}, 400)
                return
            
            auth = get_auth_system()
            new_user = auth.admin_create_demo_user(
                admin_id=user.id,
                username=username,
                email=email,
                desired_role=desired_role
            )
            
            if not new_user:
                self._send_json({"error": "Failed to create user"}, 400)
                return
            
            self._send_json({
                "stat7_id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role
            }, 201)
        
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    
    def _handle_entity_narration(self, user):
        """POST /api/query/entity-narration — Get Warbler narration for an entity."""
        try:
            body = self._get_body()
            entity_id = body.get('entity_id')
            entity_type = body.get('entity_type', 'unknown')
            realm = body.get('realm', 'void')
            coordinates = body.get('coordinates', {})
            
            if not entity_id:
                self._send_json({"error": "Missing entity_id"}, 400)
                return
            
            # Try to load WarblerQueryService if available
            try:
                # Import the service from the web server directory
                import sys
                server_dir = os.path.dirname(__file__)
                if server_dir not in sys.path:
                    sys.path.insert(0, server_dir)
                
                from warbler_query_service import WarblerQueryService
                from event_store import EventStore
                from universal_player_router import UniversalPlayerRouter
                from warbler_multiverse_bridge import WarblerMultiverseBridge
                
                # Initialize services (or use cached versions if possible)
                event_store = EventStore("web/event_store_data")
                player_router = UniversalPlayerRouter()
                warbler_bridge = WarblerMultiverseBridge(player_router)
                warbler_service = WarblerQueryService(player_router, warbler_bridge)
                
                # Query Warbler for narration
                narration = warbler_service.query_entity_narration(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    realm=realm,
                    coordinates=coordinates
                )
                
                self._send_json({
                    "entity_id": entity_id,
                    "narration": narration,
                    "source": "warbler",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, 200)
                
            except ImportError as e:
                # Fallback: generate placeholder narration
                placeholder_narration = self._generate_placeholder_narration(
                    entity_id, entity_type, realm
                )
                self._send_json({
                    "entity_id": entity_id,
                    "narration": placeholder_narration,
                    "source": "placeholder",
                    "warning": f"Warbler not available: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, 200)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._send_json({"error": str(e)}, 500)
    
    def _generate_placeholder_narration(self, entity_id: str, entity_type: str, realm: str) -> str:
        """Generate placeholder narration for an entity."""
        narratives = {
            'data': f"A fragment of data from the {entity_id} convergence, holding patterns of meaning from the data realm.",
            'narrative': f"The tale of {entity_id} echoes through the narrative realm, weaving threads of story and consequence.",
            'system': f"In the system realm, {entity_id} manifests as a structural node, bearing weight and connection.",
            'faculty': f"{entity_id} resonates with faculty—cognition, judgment, and scholarly insight dwelling within.",
            'event': f"The event {entity_id} erupted in time, leaving ripples of causality and transformation.",
            'pattern': f"Within patterns, {entity_id} traces itself as a recurring motif, a signature of deeper order.",
            'void': f"{entity_id} drifts in the void—uncharted, undefined, brimming with potential.",
        }
        
        base_narrative = narratives.get(realm, f"An entity named {entity_id} exists in unknown realms.")
        type_suffix = {
            'node': " It stands as a junction point.",
            'nexus': " It serves as a meeting place of forces.",
            'beacon': " It shines with purpose and clarity.",
            'echo': " It reverberates with echoes of creation.",
            'probe': " It searches and questions the fabric of existence.",
        }
        
        suffix = type_suffix.get(entity_type, " Its nature remains mysterious.")
        return base_narrative + suffix


def find_free_port(start_port=8000):
    """Find a free port starting from start_port."""
    import socket
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None


if __name__ == '__main__':
    # Check for test mode
    test_mode_enabled = os.environ.get("STAT7_TEST_MODE", "").lower() in ("true", "1", "yes")
    
    # Initialize auth system (with test mode if enabled)
    auth_system = get_auth_system(enable_test_mode=test_mode_enabled)
    
    port = find_free_port()
    if not port:
        print("ERROR: Could not find free port")
        sys.exit(1)
    
    print(f"[STAT7] Starting authenticated HTTP server on port {port}")
    print(f"[INFO] Auth portal: http://localhost:{port}/stat7_auth.html")
    print(f"[INFO] API Gateway: http://localhost:{port}/api/")
    
    if test_mode_enabled:
        print("\n" + "="*70)
        print("[TEST MODE ENABLED] Pre-seeded test STAT7.IDs for E2E testing")
        print("="*70)
        print("\nTest Accounts (use these for testing):")
        print("  ADMIN    : ID='test-admin-001'    (full admin privileges)")
        print("  PUBLIC   : ID='test-public-001'   (read-only access)")
        print("  DEMO ADM : ID='test-demo-001'     (sandbox admin, simulation control)")
        print("\nExample Test Flow:")
        print("  1. POST /api/auth/login { \"stat7_id\": \"test-admin-001\" }")
        print("  2. Use returned token in Authorization header: Bearer <token>")
        print("  3. Access protected endpoints: /api/admin/audit-log, /api/admin/users")
        print("="*70 + "\n")
    
    try:
        with socketserver.TCPServer(("127.0.0.1", port), AuthenticatedHandler) as httpd:
            print(f"[OK] Server running on port {port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)