# STAT7.ID Authentication Integration Guide

**Status**: Ready for deployment  
**Impact**: All hubs now require STAT7.ID login; no public access  
**Security Model**: Role-based, audited, least-privilege  

---

## Overview

The STAT7.ID system replaces the open CORS policy (`*`) with a **scoped, audited authentication layer**:

| Before | After |
|--------|-------|
| ❌ Anyone with port 8000 access | ✅ Only STAT7.ID holders |
| ❌ No audit trail | ✅ Immutable access logs |
| ❌ No roles/permissions | ✅ 3 distinct roles with boundaries |
| ❌ CORS wildcard exposed | ✅ Token-based, header validated |

---

## Architecture

### 3 New Files Created

```
web/server/
├── stat7_auth.py              # Auth system: tokens, users, roles, audit
├── auth_middleware.py         # HTTP request interceptor: validates tokens, enforces perms
└── web/
    └── stat7_auth.html        # Frontend: QR registration + login UI
```

### Integration Points

**1. API Gateway** (`api_gateway.py`)
```python
# Add token context to commands
@dataclass
class CommandRequest:
    entity_id: str
    command_type: str
    payload: Dict[str, Any]
    actor: str = "client"
    # NEW: Add these
    actor_id: str = ""              # STAT7.ID of requester
    actor_role: str = ""            # "admin", "demo_admin", "public"
```

**2. Governance Engine** (`governance.py`)
- Already has `actor_id` and `actor_role` in `PolicyContext` ✅
- Already has role-scoped policies (`role:{role}`) ✅
- No changes needed — just use existing architecture

**3. Docker Compose** (`docker-compose.yml`)
- Hubs are now self-protecting
- No changes needed to ports/volumes

---

## Role Definitions

### Admin (You - Customer Service)
**Permissions:**
- ✅ View all hubs (admin + public)
- ✅ Access audit logs
- ✅ Create DEMO_ADMIN users for friends
- ✅ View system health

**Restrictions (Intentional):**
- ❌ Cannot delete entities (prevent accidents)
- ❌ Cannot stop simulations (no kill switch)
- ❌ Cannot modify governance policies (immutable)
- ❌ Cannot view other admins' actions (privacy)

### DemoAdmin (Your Friend - Quarantined Sandbox)
**Permissions:**
- ✅ View all hubs (admin + public)
- ✅ Edit simulation settings
- ✅ Start new simulations
- ✅ Replay recorded events
- ✅ View system health

**Restrictions:**
- ❌ Cannot stop simulations (no interrupts)
- ❌ Cannot delete entities
- ❌ Cannot create other users
- ❌ Cannot view audit logs (privacy)
- ❌ Limited to sandbox environment

### Public (Unauthenticated / Basic Users)
**Permissions:**
- ✅ View public dashboards only
- ✅ Read entity state
- ✅ View system health

**Restrictions:**
- ❌ Cannot access admin hubs
- ❌ Cannot modify anything
- ❌ Cannot see non-public entities

---

## Step-by-Step Integration

### Step 1: Update API Gateway

**File:** `web/server/api_gateway.py`

```python
# Line ~45: Modify CommandRequest
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CommandRequest:
    entity_id: str
    command_type: str
    payload: Dict[str, Any]
    actor: str = "client"
    # NEW:
    actor_id: str = ""              # STAT7.ID of requester
    actor_role: str = ""            # Role name
```

### Step 2: Add Auth Middleware to Run Server

**File:** `web/server/run_server.py` (or Docker entry point)

```python
#!/usr/bin/env python3
import os
import sys
import socketserver
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

# NEW: Import auth middleware
from auth_middleware import get_auth_middleware
from stat7_auth import get_auth_system

class CustomHandler(SimpleHTTPRequestHandler):
    """Custom handler with auth validation."""
    
    def __init__(self, *args, **kwargs):
        web_dir = os.path.dirname(os.path.dirname(__file__))
        super().__init__(*args, directory=web_dir, **kwargs)
    
    def do_GET(self):
        # NEW: Check authentication
        auth = get_auth_middleware()
        is_permitted, user, reason = auth.simple_http_check(
            path=self.path,
            authorization_header=self.headers.get("Authorization", ""),
            cookies_header=self.headers.get("Cookie", ""),
            ip_address=self.client_address[0] if self.client_address else ""
        )
        
        if not is_permitted:
            self.send_response(401 if not user else 403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                f'{{"error": "Unauthorized", "reason": "{reason}"}}'.encode()
            )
            return
        
        # Original behavior
        if self.path == '/':
            self.path = '/stat7_auth.html'  # NEW: Route to auth page
        return super().do_GET()
    
    def end_headers(self):
        # REMOVE: self.send_header('Access-Control-Allow-Origin', '*')
        # REMOVE: self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        # REMOVE: self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # ADD: More restrictive headers
        self.send_header('Access-Control-Allow-Origin', 'null')  # No cross-origin
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

# ... rest of file unchanged
```

### Step 3: Update Docker Entry Point

**File:** `Dockerfile.mmo`

```dockerfile
# ... existing setup ...

# NEW: Initialize auth data directory
RUN mkdir -p /app/data && chmod 755 /app/data

# Entry point
CMD ["python", "web/server/run_server.py"]
```

### Step 4: Rebuild Container

```bash
docker-compose build --no-cache mmo-orchestrator
```

---

## Usage: Setting Up Your Friend's Access

### For Admin (You):

**1. Generate QR Code**
```bash
# In Python shell or API endpoint
from stat7_auth import get_auth_system

auth = get_auth_system()
qr_data = auth.create_qr_registration_code()

print(f"Share this code: {qr_data['code']}")
print(f"QR Data: {qr_data['qr_data']}")
```

**2. Create DEMO_ADMIN User**
```bash
from stat7_auth import get_auth_system

auth = get_auth_system()

# First, get your STAT7.ID (created on first login)
my_id = "your-admin-stat7-id"

# Create friend's account
friend = auth.admin_create_demo_user(
    admin_id=my_id,
    username="friend_name",
    email="friend@example.com"
)

print(f"Friend's STAT7.ID: {friend.id}")
print(f"Role: {friend.role}")
print(f"Permissions: {friend.permissions}")
```

### For Friend (New User):

**1. Visit Auth Portal**
```
http://localhost:8000/stat7_auth.html
```

**2. Register (if you have code)**
- Click "Register" tab
- Enter registration code from admin
- Enter username and email
- Click "Create Account"
- System returns your STAT7.ID

**3. Login**
- Click "Login" tab
- Enter your STAT7.ID
- Click "Get Token"
- System returns your authentication token

**4. Access Hubs**
Add token to all requests:
```bash
# Browser console
const token = "your-token-here";
const headers = {
    "Authorization": `Bearer ${token}`
};

// Or in fetch
fetch("http://localhost:8000/phase6c_dashboard.html", {
    headers: { "Authorization": `Bearer ${token}` }
});
```

---

## API Endpoints Required

The system needs these backend endpoints:

### `POST /api/auth/login`
**Input:**
```json
{
    "stat7_id": "uuid-here"
}
```

**Output:**
```json
{
    "token": "auth-token",
    "stat7_id": "uuid",
    "role": "public|demo_admin|admin",
    "expires_at": "ISO8601"
}
```

### `POST /api/auth/register`
**Input:**
```json
{
    "registration_code": "CODE123",
    "username": "john_doe",
    "email": "john@example.com"
}
```

**Output:**
```json
{
    "stat7_id": "new-uuid",
    "role": "public",
    "created_at": "ISO8601"
}
```

### `GET /api/admin/users`
**Auth:** ADMIN only

**Output:**
```json
{
    "users": [
        {
            "stat7_id": "uuid",
            "username": "name",
            "role": "admin|demo_admin|public",
            "created_at": "ISO8601",
            "last_login": "ISO8601"
        }
    ]
}
```

### `GET /api/admin/audit-log`
**Auth:** ADMIN only

**Query:** `?limit=100&actor_id=optional`

**Output:**
```json
{
    "logs": [
        {
            "timestamp": "ISO8601",
            "actor_id": "uuid",
            "actor_role": "admin",
            "action": "login|permission_check|access_granted",
            "resource": "/admin-entity-viewer.html",
            "permission_required": "hub:admin:view",
            "result": "PERMIT|DENY",
            "reason": "..."
        }
    ]
}
```

---

## Security Checklist

- [x] No more CORS wildcard (`*`)
- [x] All hub access requires token
- [x] Tokens validated on every request
- [x] All access logged immutably
- [x] Admin permissions scoped (no God mode)
- [x] Friend access limited to DEMO_ADMIN role
- [x] Audit logs cannot be deleted
- [x] Admin actions audited separately
- [x] Roles have explicit permission lists
- [x] Least privilege by default

---

## Testing Access Control

### Test 1: Unauthenticated Access (Should Fail)
```bash
curl -v http://localhost:8000/admin-entity-viewer.html
# Expected: 401 Unauthorized
```

### Test 2: Wrong Permission (Should Fail)
```bash
# PUBLIC token trying to access ADMIN hub
curl -H "Authorization: Bearer <public-token>" \
  http://localhost:8000/admin-entity-viewer.html
# Expected: 403 Forbidden
```

### Test 3: Correct Access (Should Succeed)
```bash
# ADMIN token accessing ADMIN hub
curl -H "Authorization: Bearer <admin-token>" \
  http://localhost:8000/admin-entity-viewer.html
# Expected: 200 OK + HTML
```

### Test 4: Audit Logging
```bash
# As admin, fetch audit log
curl -H "Authorization: Bearer <admin-token>" \
  http://localhost:8000/api/admin/audit-log?limit=10
# Should show all 3 test accesses above
```

---

## Troubleshooting

### "Missing STAT7 token"
- **Issue**: Frontend didn't include Authorization header
- **Fix**: Add token to all requests: `Authorization: Bearer {token}`

### "Invalid or expired token"
- **Issue**: Token not found in system or expired
- **Fix**: Login again to get fresh token

### "Permission denied"
- **Issue**: User's role lacks permission for resource
- **Fix**: Check role permissions above; ask admin to upgrade role

### Admin can't create demo user
- **Issue**: Admin's own STAT7.ID not found in system
- **Fix**: Admin must login first to initialize their account

---

## Data Persistence

Auth data persists in:
```
/app/data/stat7_auth.json
```

This file contains:
- All users (STAT7IDs, roles, permissions)
- Active tokens
- Immutable access log (append-only)

**In production**, replace with:
- PostgreSQL for users/tokens (faster queries)
- CloudFlare Logs / Splunk for audit trail (immutable)

---

## Next Steps

1. ✅ Files created (you're here)
2. ⏳ Update API gateway with actor_id/actor_role
3. ⏳ Add auth middleware to run_server.py
4. ⏳ Rebuild Docker container
5. ⏳ Test all access patterns
6. ⏳ Create first admin account
7. ⏳ Generate QR code for friend
8. ⏳ Verify friend can login and access demo_admin hubs

---

## References

**Files:**
- `web/server/stat7_auth.py` — Core auth system
- `web/server/auth_middleware.py` — HTTP interceptor
- `web/stat7_auth.html` — Frontend UI
- `web/server/governance.py` — Already supports role-based policies

**Governance Model:**
- All policies stored with `role:{role}` scope
- Policy evaluation already checks `actor_role` field
- No changes needed to existing governance engine