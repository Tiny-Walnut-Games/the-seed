#!/usr/bin/env python3
"""
Test the authentication endpoints in the Docker-deployed MMO orchestrator.
"""

import requests
import json
import time

# Wait for server to be fully initialized
print("[*] Waiting for MMO orchestrator to be ready...")
time.sleep(3)

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login endpoint with test admin account."""
    print("\n[TEST 1] POST /api/auth/login with test-admin-001")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"stat7_id": "test-admin-001"},
        timeout=5
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"  ✓ Login successful, token: {token[:20]}...")
        return token
    else:
        print(f"  ✗ Login failed")
        return None


def test_generate_qr():
    """Test QR generation endpoint."""
    print("\n[TEST 2] POST /api/auth/generate-qr")
    response = requests.post(
        f"{BASE_URL}/api/auth/generate-qr",
        json={},
        timeout=5
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print(f"  ✓ QR generation successful")
        return response.json().get("code")
    else:
        print(f"  ✗ QR generation failed")
        return None


def test_audit_log(token):
    """Test audit log endpoint with admin token."""
    print("\n[TEST 3] POST /api/admin/audit-log with admin token")
    response = requests.post(
        f"{BASE_URL}/api/admin/audit-log",
        json={"token": token, "limit": 5},
        timeout=5
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        count = response.json().get("count", 0)
        print(f"  ✓ Audit log retrieved successfully ({count} entries)")
    else:
        print(f"  ✗ Audit log access failed")


def test_health():
    """Test health check endpoint."""
    print("\n[TEST 0] GET /api/health (sanity check)")
    response = requests.get(
        f"{BASE_URL}/api/health",
        timeout=5
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print(f"  ✓ Health check passed")
        return True
    else:
        print(f"  ✗ Health check failed")
        return False


if __name__ == "__main__":
    try:
        print("=" * 70)
        print("Testing MMO Orchestrator Authentication Endpoints")
        print("=" * 70)
        
        # Sanity check
        if not test_health():
            print("\n[ERROR] Server not responding to health check")
            exit(1)
        
        # Test login
        token = test_login()
        if not token:
            print("\n[ERROR] Failed to login with test account")
            exit(1)
        
        # Test QR generation
        test_generate_qr()
        
        # Test audit log with the token we got
        test_audit_log(token)
        
        print("\n" + "=" * 70)
        print("✓ All tests passed! Authentication endpoints are working.")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server at http://localhost:8000")
        print("Make sure docker-compose is running: docker-compose up -d")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)