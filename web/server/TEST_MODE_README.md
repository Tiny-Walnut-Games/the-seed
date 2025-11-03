# STAT7 Authentication Server - TEST MODE

## Overview

The STAT7 HTTP authentication server (`run_server.py`) supports a **TEST MODE** that pre-seeds the authentication system with test STAT7.IDs. This enables faster E2E testing without requiring the full registration flow for each test.

## Enabling Test Mode

### Via Environment Variable (PowerShell)

Set the `STAT7_TEST_MODE` environment variable when starting the server:

```powershell
# Enable test mode
Set-Location "E:\Tiny_Walnut_Games\the-seed"
$env:STAT7_TEST_MODE = "true"
python web/server/run_server.py
```

Valid values: `true`, `1`, `yes` (case-insensitive)

### In Code

Pass `enable_test_mode=True` when initializing the auth system:

```python
from stat7_auth import get_auth_system

auth_system = get_auth_system(enable_test_mode=True)
```

## Pre-Seeded Test Accounts

When TEST MODE is enabled, three test STAT7.IDs are automatically created:

| Account ID | Role | Permissions | Purpose |
|---|---|---|---|
| `test-admin-001` | `admin` | Full admin privileges | Test protected endpoints, audit-log access, user management |
| `test-public-001` | `public` | Read-only access | Test permission restrictions, non-admin flows |
| `test-demo-001` | `demo_admin` | Sandbox admin | Test restricted admin privileges (no audit/users) |

### Account Permissions

**test-admin-001 (Admin)**
- ✅ Access `/api/admin/audit-log` (read audit logs)
- ✅ Access `/api/admin/users` (create/manage users)
- ✅ Full visibility and control

**test-public-001 (Public)**
- ✅ Read-only access to dashboards
- ❌ Cannot access admin endpoints
- ❌ No audit-log or user management

**test-demo-001 (Demo Admin)**
- ✅ Sandbox-scoped admin privileges
- ✅ Can control simulations
- ❌ Cannot access audit-log
- ❌ Cannot manage users

## Using Test Mode with E2E Tests

### Playwright Tests

```typescript
const TEST_ADMIN_ID = 'test-admin-001';

// Login with test admin account
const loginResponse = await makeRequest('POST', '/api/auth/login', {
  stat7_id: TEST_ADMIN_ID,
});

const token = loginResponse.data.token;

// Access protected endpoint with token
const auditResponse = await makeRequest(
  'POST',
  '/api/admin/audit-log',
  { limit: 10 },
  { Authorization: `Bearer ${token}` }
);
```

### Pytest Tests

```python
TEST_ADMIN_ID = "test-admin-001"

# Login with test admin account
status, data = make_request("POST", "/api/auth/login", {
    "stat7_id": TEST_ADMIN_ID,
})

token = data["token"]

# Access protected endpoint with token
headers = {"Authorization": f"Bearer {token}"}
status, data = make_request("POST", "/api/admin/audit-log", {"limit": 5}, headers)
```

## Example: Complete Test Flow

### 1. Start server with TEST MODE (PowerShell)

```powershell
Set-Location "E:\Tiny_Walnut_Games\the-seed"
$env:STAT7_TEST_MODE = "true"
python web/server/run_server.py
```

Server output:
```
[AUTH] TEST MODE: Initializing test STAT7.IDs...
======================================================================
[TEST MODE ENABLED] Pre-seeded test STAT7.IDs for E2E testing
======================================================================

Test Accounts (use these for testing):
  ADMIN    : ID='test-admin-001'    (full admin privileges)
  PUBLIC   : ID='test-public-001'   (read-only access)
  DEMO ADM : ID='test-demo-001'     (sandbox admin, simulation control)

Example Test Flow:
  1. POST /api/auth/login { "stat7_id": "test-admin-001" }
  2. Use returned token in Authorization header: Bearer <token>
  3. Access protected endpoints: /api/admin/audit-log, /api/admin/users
======================================================================
```

### 2. Run tests (PowerShell - in NEW tab while server is running)

```powershell
Set-Location "E:\Tiny_Walnut_Games\the-seed"

# Run pytest integration tests
python -m pytest tests/test_stat7_auth_http_endpoints.py::TestTestModeAdminAccess -v

# Or run all TEST MODE tests
python -m pytest tests/test_stat7_auth_http_endpoints.py -k TestTestMode -v
```

### 3. Test with PowerShell (Invoke-WebRequest or curl)

**Option A: Using curl (Windows 10+)**

```powershell
# Login as test admin
$response = curl -s -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"stat7_id": "test-admin-001"}' | ConvertFrom-Json

$token = $response.token

# Use token to access protected endpoint
curl -X POST http://localhost:8000/api/admin/audit-log `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $token" `
  -d '{"limit": 10}'
```

**Option B: Using Invoke-WebRequest**

```powershell
# Login as test admin
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" `
  -Method POST `
  -Headers @{"Content-Type" = "application/json"} `
  -Body '{"stat7_id": "test-admin-001"}' | ConvertFrom-Json

$token = $response.token

# Use token to access protected endpoint
Invoke-WebRequest -Uri "http://localhost:8000/api/admin/audit-log" `
  -Method POST `
  -Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
  } `
  -Body '{"limit": 10}'
```

## What Happens Without TEST MODE

When `STAT7_TEST_MODE` is not set or disabled:

1. **No automatic test accounts** are created
2. Users must register via `/api/auth/register` first
3. Registration requires a valid registration code from `/api/auth/generate-qr`
4. Tests can still flow through: `generate-qr` → `register` → `login`

This is the **production mode** and ensures only registered users can authenticate.

## Data Persistence

- **With TEST MODE**: Test accounts are written to `/app/data/stat7_auth.json` on startup
- **Between restarts**: If the auth data file exists and contains test accounts, TEST MODE will skip re-initialization
- **To reset**: Delete `/app/data/stat7_auth.json` and restart the server

## Docker Compose Integration

To enable TEST MODE in Docker:

**Via docker-compose.yml**:
```yaml
environment:
  STAT7_TEST_MODE: "true"
```

**Via command line**:
```bash
STAT7_TEST_MODE=true docker-compose up -d
```

**Via docker-compose.override.yml**:
```yaml
version: '3.8'
services:
  mmo-orchestrator:
    environment:
      STAT7_TEST_MODE: "true"
```

## Security Considerations

⚠️ **TEST MODE is development-only** — Never enable in production:

- ✅ Safe for local testing and CI/CD pipelines
- ✅ Pre-seeded accounts are clearly marked as test accounts
- ❌ Do NOT expose test-mode-enabled server to the internet
- ❌ Do NOT use in production deployments

Test accounts have full permissions and bypass the normal registration flow.

## Troubleshooting

### Test accounts not available

**Symptoms**: Login with `test-admin-001` returns 401

**Solution**:
1. Check `STAT7_TEST_MODE` is set in your PowerShell: `$env:STAT7_TEST_MODE`
2. Stop the server (Ctrl+C in the terminal tab where it's running)
3. Restart with: `$env:STAT7_TEST_MODE = "true"; python web/server/run_server.py`
4. Check server output for `[AUTH] TEST MODE: Initializing test STAT7.IDs...`

### Tests timing out

**Symptoms**: pytest tests timeout trying to connect

**Solution**:
1. Verify server is running in your server tab (should show `Uvicorn running on http://0.0.0.0:8000`)
2. Test connection: `curl http://localhost:8000/api/health`
3. If no response, stop and restart the server (Ctrl+C, then run the startup command again)

### Permissions denied (403) on admin endpoints

**Symptoms**: Token valid but endpoint returns 403

**Check permission**: Use the correct test account:
- `test-admin-001` for audit-log and user management
- `test-demo-001` only for simulation control (no admin endpoints)
- `test-public-001` is read-only (no admin endpoints)

To verify which permissions your account has:
```powershell
python -m pytest tests/test_stat7_auth_http_endpoints.py::TestTestModeAdminAccess -v -s
```

## Test File References

- **Playwright E2E Tests**: `tests/e2e/stat7-auth-server.spec.ts` (tests marked `test.skip`)
- **Pytest Integration Tests**: `tests/test_stat7_auth_http_endpoints.py` (TestTestMode* classes)
- **Auth System**: `web/server/stat7_auth.py` (method `_initialize_test_users()`)
- **HTTP Server**: `web/server/run_server.py` (main entry point)