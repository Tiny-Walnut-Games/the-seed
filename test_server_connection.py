#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

try:
    # Test POST /api/auth/generate-qr
    response = requests.post(
        f"{BASE_URL}/api/auth/generate-qr",
        json={},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Headers: {dict(response.headers)}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()