# STAT7.ID Quick Start (5 Minutes)

---

## What You Just Got

✅ **3 New Files** ready to deploy:

1. **`stat7_auth.py`** (366 lines)
   - User creation, registration codes, QR generation
   - Token management (no auto-expiry = permanent)
   - Immutable audit logging
   - Role-based permission system

2. **`auth_middleware.py`** (339 lines)
   - HTTP request interceptor
   - Token validation on every access
   - Permission checking
   - Integration-ready for FastAPI or Simple HTTP Server

3. **`stat7_auth.html`** (Frontend UI)
   - QR code display + registration
   - Login via STAT7.ID
   - Token display/copy
   - Mobile-friendly

---

## 30-Second Setup

### 1. Add Auth to Your Server
**File:** `web/server/run_server.py`

Replace the `do_GET` method:
```python
def do_GET(self):
    from auth_middleware import get_auth_middleware
    
    auth = get_auth_middleware()
    is_ok, user, msg = auth.simple_http_check(
        path=self.path,
        authorization_header=self.headers.get("Authorization", ""),
        ip_address=self.client_address[0] if self.client_address else ""
    )
    
    if not is_ok:
        self.send_response(401 if not user else 403)
        self.end_headers()
        return
    
    if self.path == '/':
        self.path = '/stat7_auth.html'
    return super().do_GET()
```

### 2. Rebuild Docker
```bash
docker-compose build --no-cache mmo-orchestrator
docker-compose up -d
```

### 3. That's It!
All hubs now require STAT7.ID login.

---

## How to Give Your Friend Access

### Step 1: You (Admin) - Create Friend Account
```python
# In Python or via API
from stat7_auth import get_auth_system

auth = get_auth_system()

# Get your admin STAT7.ID first (created on first login)
my_admin_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Create friend's account
friend = auth.admin_create_demo_user(
    admin_id=my_admin_id,
    username="sarah",
    email="sarah@example.com"
)

print(f"✅ Account created!")
print(f"   STAT7.ID: {friend.id}")
print(f"   Role: {friend.role}")
print(f"   Can: View all hubs, edit settings, start simulations")
```

### Step 2: Share Friend's STAT7.ID
Send to your friend:
```
Your STAT7.ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Visit: http://your-server:8000/stat7_auth.html
Click: Login tab
Paste: Your STAT7.ID above
Get: Token
Use: Authorization header on all hub requests
```

### Step 3: Friend Gets Token
```
1. Visit http://localhost:8000/stat7_auth.html
2. Click "Login" tab
3. Paste their STAT7.ID
4. Click "Get Token"
5. Copy the token
```

### Step 4: Friend Uses Token
```bash
# In browser console:
const token = "token-here";

fetch("http://localhost:8000/phase6c_dashboard.html", {
    headers: { "Authorization": `Bearer ${token}` }
});
```

Or in `curl`:
```bash
curl -H "Authorization: Bearer token-here" \
  http://localhost:8000/phase6c_dashboard.html
```

---

## Role Permissions

### Admin (You)
```
✅ View: Admin hubs + public dashboards
✅ Do: View audit logs, create demo users, manage system
❌ Cannot: Delete entities, stop simulations, modify policies
```

### DemoAdmin (Your Friend)
```
✅ View: Admin hubs + public dashboards
✅ Do: Edit settings, start simulations, replay events
❌ Cannot: Stop simulations, delete entities, create users
```

### Public
```
✅ View: Public dashboards only
✅ Do: Read entity state
❌ Cannot: Modify anything
```

---

## Key Features

| Feature | Benefit |
|---------|---------|
| **No CORS Wildcard** | Only STAT7.ID holders can access |
| **Permanent Tokens** | Friend doesn't re-authenticate constantly |
| **Immutable Audit Log** | All access recorded, cannot be deleted |
| **Scoped Admin** | You can't accidentally nuke production |
| **Role-Based** | Friend can't do dangerous things (kill simulations) |
| **Least Privilege** | Default is read-only for new users |

---

## Verify It Works

### 1. Unauthenticated Access (Should Fail)
```bash
curl http://localhost:8000/admin-entity-viewer.html
# Expected: 401 Unauthorized
```

### 2. With Token (Should Work)
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin-entity-viewer.html
# Expected: 200 OK + HTML
```

### 3. Check Audit Log
```bash
# As admin, get access history
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/admin/audit-log?limit=10
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **401 Unauthorized** | Missing token header. Add: `Authorization: Bearer {token}` |
| **403 Forbidden** | User role lacks permission. Check role in audit log. |
| **Token expired** | Tokens don't expire (permanent). If issue persists, login again. |
| **Audit log empty** | Log access to create entries (makes first request with token) |

---

## Files to Reference

- **Core**: `web/server/stat7_auth.py`
- **Integration**: `web/server/auth_middleware.py`
- **Frontend**: `web/stat7_auth.html`
- **Docs**: `docs/DEVELOPMENT/STAT7_ID_AUTH_INTEGRATION.md`

---

## Next: Advanced (Optional)

- **Store tokens in database** (instead of JSON)
- **Time-limited tokens** (revoke access after X days)
- **OAuth integration** (GitHub/Google login)
- **2FA** (TOTP/SMS)
- **Rate limiting** (per-user or per-role)
- **Geographic IP restrictions** (friend can only access from home)

---

## Questions?

Check the full integration guide:
```
docs/DEVELOPMENT/STAT7_ID_AUTH_INTEGRATION.md
```

Or review the code:
- `web/server/stat7_auth.py` — Read the docstrings
- `web/server/auth_middleware.py` — See permission checking logic
- `web/stat7_auth.html` — UI flows