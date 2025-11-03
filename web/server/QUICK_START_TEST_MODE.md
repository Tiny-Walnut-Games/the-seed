# STAT7 Authentication Server - Quick Start (TEST MODE)

**WINDOWS POWERSHELL ONLY** — All commands below use PowerShell syntax. Do NOT use bash/WSL.

---

## ⚙ First, Install Prerequisites (One Time)

Open **PowerShell** and run:

```powershell
Set-Location "E:\Tiny_Walnut_Games\the-seed"
pip install -r requirements.txt
```

Done. Your Python environment now has all dependencies.

---

## 🚀 Start Server with Test Mode (30 seconds)

Open **NEW PowerShell tab** and run:

```powershell
Set-Location "E:\Tiny_Walnut_Games\the-seed"
$env:STAT7_TEST_MODE = "true"
python web/server/run_server.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
[AUTH] TEST MODE: Initializing test STAT7.IDs...
======================================================================
[TEST MODE ENABLED] Pre-seeded test STAT7.IDs for E2E testing
======================================================================
```

Leave this tab running. Proceed to testing in your original PowerShell tab.

---

## 📋 Test Credentials (Pre-Seeded)

| ID                | Use For                                     |
|-------------------|---------------------------------------------|
| `test-admin-001`  | Admin endpoints, audit-log, user management |
| `test-public-001` | Read-only testing, permission checks        |
| `test-demo-001`   | Sandbox testing, simulation control         |

All use token-based auth (no passwords).

---

## ✅ Quick Test (curl in PowerShell)

In your original PowerShell tab:

```powershell
# 1. Login and get token
$loginResponse = curl -s -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"stat7_id": "test-admin-001"}' | ConvertFrom-Json
$token = $loginResponse.token

# 2. Use token on protected endpoint
curl -X POST http://localhost:8000/api/admin/audit-log `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $token" `
  -d '{"limit": 5}'

# 3. Should return audit logs
```

---

## 🧪 Run E2E Tests

In your original PowerShell tab (server must still be running in the other tab):

```powershell
Set-Location "E:\Tiny_Walnut_Games\the-seed"

# Run admin permission tests
python -m pytest tests/test_stat7_auth_http_endpoints.py::TestTestModeAdminAccess -v

# Or run all test mode tests
python -m pytest tests/test_stat7_auth_http_endpoints.py -k TestTestMode -v
```

**All tests should PASS.**

---

## 🔍 Verify TEST MODE is Active

Check your server tab (the one running `python web/server/run_server.py`). You should see in the logs:

```
[AUTH] TEST MODE: Initializing test STAT7.IDs...
[TEST MODE ENABLED] Pre-seeded test STAT7.IDs for E2E testing
```

If you don't see this, `STAT7_TEST_MODE` was not set correctly. Stop the server (Ctrl+C), run the startup command again.

---

## 🚫 Disable TEST MODE (for later, not needed now)

When you want to run in production mode:

```powershell
Set-Location "E:\Tiny_Walnut_Games\the-seed"
$env:STAT7_TEST_MODE = "false"
python web/server/run_server.py
```

Or simply unset the variable and restart.

---

## 🐛 Troubleshooting

**Server won't start?**
- Check Python is installed: `python --version`
- Check dependencies: `pip list | findstr uvicorn`
- Check port 8000 isn't in use: Open Task Manager → find process on port 8000

**Tests fail/timeout?**
- Make sure server is still running in your other PowerShell tab
- Test connection manually: ```curl http://localhost:8000/api/health```

**403 Permission Denied on audit-log?**
- Use `test-admin-001`, not `test-demo-001` or `test-public-001`
- Run: `python -m pytest tests/test_stat7_auth_http_endpoints.py::TestTestModeAdminAccess -v -s`

**Tests say "permissions empty"?**
- This was a known bug. Make sure you have the LATEST code from this conversation.
- Run: `git status` to see your local changes
- If uncertain, show me your error output.

---

## 📚 Next Steps

1. ✅ Install prerequisites (Step 1)
2. ✅ Start server in PowerShell tab (Step 2)
3. ✅ Run quick curl test (Step 3)
4. ✅ Run E2E tests with pytest (Step 4)

Once all pass, you can access the MMO Orchestrator with authenticated endpoints.

---

**Key Point**: With TEST MODE enabled, you instantly login with pre-seeded credentials. No registration flow. No Docker needed. Just PowerShell + Python.
