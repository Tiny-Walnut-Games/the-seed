"""
Integration Tests: STAT7.ID HTTP Authentication API

Tests the HTTP server at http://localhost:8000 with:
- Public endpoints: /api/auth/register, /api/auth/login, /api/auth/generate-qr
- Protected endpoints: /api/admin/audit-log, /api/admin/users
- Auth middleware and role-based access control
- Immutable audit logging

Run with: pytest tests/test_stat7_auth_http_endpoints.py -v

Prerequisites:
- Docker container with run_server.py running on port 8000
- Command: docker-compose up -d

TEST MODE (faster testing without registration flow):
- Set environment variable: STAT7_TEST_MODE=true
- Server will be pre-seeded with test accounts:
    - test-admin-001:  Full admin privileges
    - test-public-001: Read-only public access
    - test-demo-001:   Sandbox admin (simulation control)
"""

import pytest
import requests
import json
import time
import os
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

# Connection timeout (seconds)
TIMEOUT = 5

# Test credentials (pre-seeded when STAT7_TEST_MODE=true)
TEST_ADMIN_ID = "test-admin-001"
TEST_PUBLIC_ID = "test-public-001"
TEST_DEMO_ID = "test-demo-001"

# Helper functions

def make_request(method: str, endpoint: str, body: dict = None, headers: dict = None) -> tuple:
    """
    Make HTTP request and return (status_code, response_data).
    Returns (None, None) if connection fails.
    """
    url = f"{BASE_URL}{endpoint}"
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=req_headers, timeout=TIMEOUT)
        elif method == "POST":
            resp = requests.post(url, json=body or {}, headers=req_headers, timeout=TIMEOUT)
        else:
            return None, None
        
        try:
            data = resp.json()
        except:
            data = resp.text
        
        return resp.status_code, data
    except Exception as e:
        pytest.skip(f"Connection failed: {e}")
        return None, None


# ============================================================================
# PUBLIC ENDPOINTS (No auth required)
# ============================================================================

class TestPublicAuthEndpoints:
    """Test public authentication endpoints."""
    
    def test_generate_qr_returns_code(self):
        """POST /api/auth/generate-qr returns registration code."""
        status, data = make_request("POST", "/api/auth/generate-qr", {})
        
        assert status == 200, f"Expected 200, got {status}: {data}"
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        assert "code" in data, f"Missing 'code' in response: {data}"
        assert "qr_data" in data, f"Missing 'qr_data' in response: {data}"
        assert "expires_at" in data, f"Missing 'expires_at' in response: {data}"
    
    def test_generate_qr_code_format(self):
        """QR code format is valid (alphanumeric, 6+ chars)."""
        status, data = make_request("POST", "/api/auth/generate-qr", {})
        
        assert status == 200
        code = data.get("code")
        assert code, f"Empty code: {code}"
        assert len(code) >= 6, f"Code too short: {code}"
        assert code.replace("_", "").isalnum(), f"Code contains invalid chars: {code}"
    
    def test_register_with_valid_code(self):
        """POST /api/auth/register with valid code creates user."""
        # Step 1: Generate code
        qr_status, qr_data = make_request("POST", "/api/auth/generate-qr", {})
        assert qr_status == 200, f"Failed to generate QR: {qr_data}"
        code = qr_data["code"]
        
        # Step 2: Register
        timestamp = str(int(time.time() * 1000))
        reg_status, reg_data = make_request("POST", "/api/auth/register", {
            "registration_code": code,
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
        })
        
        assert reg_status == 201, f"Expected 201, got {reg_status}: {reg_data}"
        assert "stat7_id" in reg_data, f"Missing stat7_id: {reg_data}"
        assert "username" in reg_data, f"Missing username: {reg_data}"
        assert "role" in reg_data, f"Missing role: {reg_data}"
        assert reg_data["stat7_id"].startswith("stat7-"), f"Invalid STAT7.ID format: {reg_data['stat7_id']}"
    
    def test_register_rejects_invalid_code(self):
        """Registration fails with invalid code."""
        timestamp = str(int(time.time() * 1000))
        status, data = make_request("POST", "/api/auth/register", {
            "registration_code": "INVALID_CODE_12345",
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
        })
        
        assert status == 400, f"Expected 400, got {status}: {data}"
        assert "error" in data, f"Missing error message: {data}"
    
    def test_register_rejects_missing_fields(self):
        """Registration requires all fields."""
        status, data = make_request("POST", "/api/auth/register", {
            "registration_code": "CODE123",
            # Missing username and email
        })
        
        assert status == 400, f"Expected 400, got {status}: {data}"
        assert "Missing required fields" in data.get("error", ""), f"Wrong error: {data}"
    
    def test_login_creates_token(self):
        """POST /api/auth/login creates authentication token."""
        # Register a user first
        qr_status, qr_data = make_request("POST", "/api/auth/generate-qr", {})
        code = qr_data["code"]
        
        timestamp = str(int(time.time() * 1000))
        reg_status, reg_data = make_request("POST", "/api/auth/register", {
            "registration_code": code,
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
        })
        stat7_id = reg_data["stat7_id"]
        
        # Login
        login_status, login_data = make_request("POST", "/api/auth/login", {
            "stat7_id": stat7_id,
        })
        
        assert login_status == 200, f"Expected 200, got {login_status}: {login_data}"
        assert "token" in login_data, f"Missing token: {login_data}"
        assert login_data["token"].startswith("eyJ"), f"Invalid JWT format: {login_data['token']}"
    
    def test_login_rejects_nonexistent_id(self):
        """Login fails for non-existent STAT7.ID."""
        status, data = make_request("POST", "/api/auth/login", {
            "stat7_id": "stat7-nonexistent-fake-12345",
        })
        
        assert status == 401, f"Expected 401, got {status}: {data}"
        assert "error" in data, f"Missing error: {data}"


# ============================================================================
# PROTECTED ENDPOINTS (Auth required)
# ============================================================================

class TestProtectedAdminEndpoints:
    """Test protected admin endpoints."""
    
    def test_audit_log_requires_auth(self):
        """audit-log endpoint requires authentication."""
        status, data = make_request("POST", "/api/admin/audit-log", {"limit": 10})
        
        assert status == 401, f"Expected 401, got {status}: {data}"
        assert "error" in data, f"Missing error: {data}"
    
    def test_users_endpoint_requires_auth(self):
        """users endpoint requires authentication."""
        status, data = make_request("POST", "/api/admin/users", {
            "username": "newadmin",
            "email": "admin@example.com",
            "role": "admin",
        })
        
        assert status == 401, f"Expected 401, got {status}: {data}"
    
    def test_invalid_token_rejected(self):
        """Invalid token is rejected."""
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid"
        headers = {"Authorization": f"Bearer {fake_token}"}
        status, data = make_request("POST", "/api/admin/audit-log", {"limit": 10}, headers)
        
        assert status == 401, f"Expected 401 for invalid token, got {status}: {data}"


# ============================================================================
# SECURITY HEADERS
# ============================================================================

class TestSecurityHeaders:
    """Test security header presence."""
    
    def test_security_headers_present(self):
        """All responses include required security headers."""
        url = f"{BASE_URL}/api/auth/generate-qr"
        resp = requests.post(url, json={}, timeout=TIMEOUT)
        
        assert resp.headers.get("X-Content-Type-Options") == "nosniff", \
            f"Missing/invalid X-Content-Type-Options: {resp.headers}"
        assert resp.headers.get("X-Frame-Options") == "DENY", \
            f"Missing/invalid X-Frame-Options: {resp.headers}"
        assert "1" in resp.headers.get("X-XSS-Protection", ""), \
            f"Missing/invalid X-XSS-Protection: {resp.headers}"


# ============================================================================
# RESPONSE FORMATS
# ============================================================================

class TestResponseFormats:
    """Test response content-type and formatting."""
    
    def test_json_content_type(self):
        """All responses return JSON with correct Content-Type."""
        url = f"{BASE_URL}/api/auth/generate-qr"
        resp = requests.post(url, json={}, timeout=TIMEOUT)
        
        assert "application/json" in resp.headers.get("Content-Type", ""), \
            f"Invalid Content-Type: {resp.headers.get('Content-Type')}"


# ============================================================================
# ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test error response handling."""
    
    def test_error_doesnt_leak_sensitive_info(self):
        """Error messages don't expose sensitive information."""
        status, data = make_request("POST", "/api/auth/login", {"stat7_id": "fake"})
        
        error_str = json.dumps(data)
        # Should NOT contain SQL, file paths, or internal details
        bad_patterns = ["SELECT", "INSERT", "DROP", "/home", "/root", ".py", ".sql"]
        for pattern in bad_patterns:
            assert pattern not in error_str, f"Potential info leak in error: {error_str}"
    
    def test_unknown_endpoint_404(self):
        """Unknown endpoints return 404."""
        status, data = make_request("POST", "/api/unknown/endpoint", {})
        
        assert status == 404, f"Expected 404, got {status}: {data}"


# ============================================================================
# FULL WORKFLOW
# ============================================================================

class TestFullAuthWorkflow:
    """Test complete authentication workflow."""
    
    def test_register_and_login_flow(self):
        """Complete flow: generate QR → register → login."""
        # Step 1: Generate QR
        qr_status, qr_data = make_request("POST", "/api/auth/generate-qr", {})
        assert qr_status == 200, f"Generate QR failed: {qr_data}"
        code = qr_data["code"]
        
        # Step 2: Register
        timestamp = str(int(time.time() * 1000))
        reg_status, reg_data = make_request("POST", "/api/auth/register", {
            "registration_code": code,
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
        })
        assert reg_status == 201, f"Register failed: {reg_data}"
        stat7_id = reg_data["stat7_id"]
        
        # Step 3: Login
        login_status, login_data = make_request("POST", "/api/auth/login", {
            "stat7_id": stat7_id,
        })
        assert login_status == 200, f"Login failed: {login_data}"
        token = login_data["token"]
        
        # Step 4: Use token on protected endpoint (should fail with 403, not 401)
        headers = {"Authorization": f"Bearer {token}"}
        admin_status, admin_data = make_request("POST", "/api/admin/audit-log", {"limit": 10}, headers)
        
        # Public user should NOT have admin permission
        # Expect either 403 (Permission Denied) or error about insufficient permissions
        assert admin_status in [403, 401], \
            f"Expected 403/401 for non-admin user, got {admin_status}: {admin_data}"


# ============================================================================
# TEST MODE: Pre-seeded test credentials (when STAT7_TEST_MODE=true)
# ============================================================================
# These tests use pre-seeded test accounts for faster E2E testing
# Only run if STAT7_TEST_MODE environment variable is set to true

class TestTestModeAdminAccess:
    """Test protected endpoints using pre-seeded admin account."""
    
    def test_admin_login_and_access_audit_log(self):
        """Admin can login and access audit-log endpoint."""
        # Login as admin
        login_status, login_data = make_request("POST", "/api/auth/login", {
            "stat7_id": TEST_ADMIN_ID,
        })
        
        # Skip if test account not available
        if login_status == 401:
            pytest.skip("Test admin account not available (STAT7_TEST_MODE not enabled?)")
        
        assert login_status == 200, f"Admin login failed: {login_data}"
        assert "token" in login_data, f"No token in response: {login_data}"
        token = login_data["token"]
        
        # Access audit-log with admin token
        headers = {"Authorization": f"Bearer {token}"}
        audit_status, audit_data = make_request("POST", "/api/admin/audit-log", {"limit": 5}, headers)
        
        assert audit_status == 200, f"Audit-log access failed: {audit_data}"
        assert "logs" in audit_data, f"No 'logs' in response: {audit_data}"
        assert "count" in audit_data, f"No 'count' in response: {audit_data}"
        assert isinstance(audit_data["logs"], list), f"'logs' is not a list: {type(audit_data['logs'])}"
    
    def test_admin_can_create_users(self):
        """Admin can create new users via /api/admin/users."""
        # Login as admin
        login_status, login_data = make_request("POST", "/api/auth/login", {
            "stat7_id": TEST_ADMIN_ID,
        })
        
        if login_status == 401:
            pytest.skip("Test admin account not available")
        
        assert login_status == 200
        token = login_data["token"]
        
        # Create a new user
        timestamp = str(int(time.time() * 1000))
        headers = {"Authorization": f"Bearer {token}"}
        create_status, create_data = make_request("POST", "/api/admin/users", {
            "username": f"e2e_admin_test_{timestamp}",
            "email": f"e2e_admin_{timestamp}@test.local",
            "role": "demo_admin",
        }, headers)
        
        assert create_status == 201, f"User creation failed: {create_data}"
        assert "stat7_id" in create_data, f"No 'stat7_id' in response: {create_data}"
        assert "username" in create_data, f"No 'username' in response: {create_data}"
        assert create_data["role"] == "demo_admin", f"Wrong role: {create_data.get('role')}"


class TestTestModePublicAccess:
    """Test permission restrictions using pre-seeded public account."""
    
    def test_public_user_cannot_access_admin_endpoints(self):
        """Public user cannot access admin-only endpoints."""
        # Login as public user
        login_status, login_data = make_request("POST", "/api/auth/login", {
            "stat7_id": TEST_PUBLIC_ID,
        })
        
        if login_status == 401:
            pytest.skip("Test public account not available")
        
        assert login_status == 200
        token = login_data["token"]
        
        # Try to access audit-log (should fail with 403)
        headers = {"Authorization": f"Bearer {token}"}
        audit_status, audit_data = make_request("POST", "/api/admin/audit-log", {"limit": 5}, headers)
        
        assert audit_status == 403, \
            f"Expected 403 (Permission Denied), got {audit_status}: {audit_data}"
        assert "error" in audit_data, f"No 'error' in response: {audit_data}"


class TestTestModeDemoAdminAccess:
    """Test sandboxed demo-admin permissions."""
    
    def test_demo_admin_restricted_permissions(self):
        """Demo admin cannot access audit-log or create users."""
        # Login as demo admin
        login_status, login_data = make_request("POST", "/api/auth/login", {
            "stat7_id": TEST_DEMO_ID,
        })
        
        if login_status == 401:
            pytest.skip("Test demo admin account not available")
        
        assert login_status == 200
        token = login_data["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Demo admin should NOT be able to access audit-log
        audit_status, audit_data = make_request("POST", "/api/admin/audit-log", {"limit": 5}, headers)
        assert audit_status == 403, \
            f"Demo admin should not access audit-log, got {audit_status}: {audit_data}"
        
        # Demo admin should NOT be able to create users
        timestamp = str(int(time.time() * 1000))
        user_status, user_data = make_request("POST", "/api/admin/users", {
            "username": f"demo_test_{timestamp}",
            "email": f"demo_{timestamp}@test.local",
        }, headers)
        assert user_status == 403, \
            f"Demo admin should not create users, got {user_status}: {user_data}"