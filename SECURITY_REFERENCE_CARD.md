# 🔐 Security Reference Card

**Quick Reference for Phase 6B REST API Security Implementation**

---

## 🚀 Quick Start Commands

```bash
# Install
pip install -r requirements-security-api.txt

# Test
pytest tests/test_phase6b_rest_api_security.py -v

# Generate JWT secret
openssl rand -hex 32 > jwt_secret.txt

# Start API
python run_stat7.py

# Get token (separate terminal)
curl -X POST "http://localhost:8000/api/auth/token" \
  -d "username=admin&password=admin"

# Use token
curl -X POST "http://localhost:8000/api/endpoint" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔑 Authentication Flow

```
1. POST /api/auth/token
   ├─ Input: username, password
   └─ Output: JWT token
        ↓
2. Store token
   └─ Valid for 24 hours
        ↓
3. Use token in requests
   ├─ Header: Authorization: Bearer TOKEN
   └─ All requests now authenticated
        ↓
4. Token expires?
   └─ Get new token from /api/auth/token
```

---

## 📝 Decorator Pattern

```python
# Require authentication + specific role
@app.post("/api/endpoint")
@RBACMiddleware.require_role([ROLE_ADMIN])
async def endpoint(
    param: str = Query(...),
    current_user: Dict = Depends(BearerAuth.get_current_user),
):
    # param is user input - VALIDATE IT
    safe_param = InputValidator.validate_realm_id(param)
    
    # Log the action
    AuditLogger.log_action(
        current_user["user_id"],
        "action_name",
        safe_param,
        "initiated"
    )
    
    # Do something
    result = await do_something(safe_param)
    
    # Log success
    AuditLogger.log_action(
        current_user["user_id"],
        "action_name",
        safe_param,
        "success"
    )
    
    return result
```

---

## ✅ Input Validators

```python
from security_validators import InputValidator

# Validate file paths (prevent ../.. traversal)
path = InputValidator.validate_filepath("snapshot.json")
# ✅ ACCEPTED: "snapshot.json", "archive/snapshot.json"
# ❌ BLOCKED: "../etc/passwd", "../../config", "$HOME/.ssh"

# Validate realm IDs
realm = InputValidator.validate_realm_id("realm_123")
# ✅ ACCEPTED: alphanumeric, underscore, hyphen

# Validate NPC IDs
npc = InputValidator.validate_npc_id("npc-warbler_001")
# ✅ ACCEPTED: alphanumeric, underscore, hyphen

# Validate seeds (0 to 2^31-1)
seed = InputValidator.validate_seed(12345)
# ✅ ACCEPTED: 0 to 2147483647

# Validate hashes (hex format)
hash_val = InputValidator.validate_hash("abc123def456")
# ✅ ACCEPTED: hex characters only
```

---

## 🛡️ 7 Security Layers

```
┌──────────────────────────────────────┐
│ 1. Network Layer (HTTPS/TLS)         │  ← Enable in production
├──────────────────────────────────────┤
│ 2. CORS + Trusted Host Middleware    │  ← Already added
├──────────────────────────────────────┤
│ 3. Authentication (JWT Bearer Token) │  ← Validates token
├──────────────────────────────────────┤
│ 4. Authorization (RBAC)              │  ← Checks role
├──────────────────────────────────────┤
│ 5. Input Validation                  │  ← Sanitizes input
├──────────────────────────────────────┤
│ 6. Business Logic                    │  ← Your code
├──────────────────────────────────────┤
│ 7. Audit & Monitoring                │  ← Logs everything
└──────────────────────────────────────┘
```

---

## 🎯 Roles

```
ROLE_VIEWER   → Read-only access (default for authenticated users)
ROLE_ADMIN    → Full access (write, delete, etc.)
ROLE_SYSTEM   → Internal system operations

@RBACMiddleware.require_role([ROLE_VIEWER, ROLE_ADMIN])
# Either VIEWER or ADMIN can access

@RBACMiddleware.require_role([ROLE_ADMIN])
# Only ADMIN can access
```

---

## 🧪 Test Coverage

```
42 Total Security Tests

Path Traversal Prevention    (11 tests) ✅
├─ Parent directory (..)
├─ URL encoding (%2e%2e)
├─ Backslash traversal
├─ Environment variables
├─ Command injection
└─ Valid paths accepted

Input Validation           (10 tests) ✅
├─ Realm IDs
├─ NPC IDs
├─ Seeds
├─ Hashes
└─ Format validation

Authentication             (6 tests) ✅
├─ Token creation
├─ Token verification
├─ Expiration
└─ Tampering detection

Authorization              (3 tests) ✅
├─ Role checking
├─ Access control
└─ Role differentiation

Error Handling             (2 tests) ✅
├─ Generic messages
└─ No info leakage

Audit Logging              (3 tests) ✅
├─ Action logging
├─ Timestamps
└─ Metadata

Integration                (3 tests) ✅
├─ Full workflows
└─ End-to-end flows

Compliance                 (4 tests) ✅
└─ All controls present
```

---

## 🔒 What's Protected?

| Attack | Pattern | Detection | Block |
|--------|---------|-----------|-------|
| **Path Traversal** | `../../../etc/passwd` | Regex patterns | ✅ |
| **URL Encoding** | `%2e%2e%2fetc` | Decoding + check | ✅ |
| **Command Injection** | `; rm -rf /` | Special chars | ✅ |
| **Env Variables** | `$HOME/.ssh` | $ detection | ✅ |
| **No Auth** | No token | Middleware | ✅ |
| **Wrong Role** | Viewer→Admin | RBAC check | ✅ |
| **SQL Injection** | Input validation | Parameterized | ✅ |
| **Error Leakage** | Stack trace | Secure handler | ✅ |

---

## 📊 GitHub Actions

```
┌─────────────────────────────────────┐
│ Git Push/PR to Main                 │
└─────────────────────────────────────┘
            ↓ Webhook
┌─────────────────────────────────────┐
│ overlord-sentinel-security.yml      │
├─────────────────────────────────────┤
│ ✓ TruffleHog (secrets)              │
│ ✓ Bandit (Python security)          │
│ ✓ Semgrep (pattern analysis)        │
│ ✓ pip-audit (dependencies)          │
│ → Upload to GitHub Security tab     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ phase6b-rest-api-security.yml       │
├─────────────────────────────────────┤
│ ✓ Path traversal detection          │
│ ✓ Auth enforcement checks           │
│ ✓ 42 security tests                 │
│ ✓ Semgrep custom rules              │
│ → Comment on PR with results        │
│ → Fail build if critical issues     │
└─────────────────────────────────────┘
            ↓
    ✅ ALL CHECKS PASSED
            ↓
  ✅ Safe to merge & deploy
```

---

## 🚨 Common Mistakes

```
❌ WRONG:
@app.post("/api/endpoint")
async def endpoint(filepath: str = Query(...)):
    open(filepath)  # Direct use of user input!

✅ CORRECT:
@app.post("/api/endpoint")
@RBACMiddleware.require_role([ROLE_ADMIN])
async def endpoint(
    filepath: str = Query(...),
    current_user: Dict = Depends(BearerAuth.get_current_user),
):
    safe_path = InputValidator.validate_filepath(filepath)
    open(safe_path)  # Validated!

---

❌ WRONG:
raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
# Exposes full error to client!

✅ CORRECT:
SecureErrorHandler.raise_safe_error(e, context="operation")
# Logs full error, returns generic message

---

❌ WRONG:
logger.info(f"User {user_id} saved file to {filepath}")
# Leaks PII and system paths!

✅ CORRECT:
AuditLogger.log_action(user_id, "save", filepath, "success")
# Structured, secure audit log
```

---

## 📦 File Locations

```
Security Modules:
├─ security_validators.py
│  └─ packages/com.twg.the-seed/seed/engine/
└─ auth_middleware.py
   └─ packages/com.twg.the-seed/seed/engine/

Tests:
└─ test_phase6b_rest_api_security.py
   └─ tests/

Workflows:
├─ overlord-sentinel-security.yml
│  └─ .github/workflows/
└─ phase6b-rest-api-security.yml
   └─ .github/workflows/

Documentation:
├─ SECURITY_API_FIXES.md (root)
├─ CI_CD_SECURITY_PIPELINE_GUIDE.md (root)
├─ SECURITY_IMPLEMENTATION_QUICKSTART.md (root)
└─ requirements-security-api.txt (root)
```

---

## 🎓 Learning Path

```
5 min  → Read this card
15 min → Read SECURITY_IMPLEMENTATION_QUICKSTART.md
30 min → Run pip install + pytest
45 min → Update phase6b_rest_api.py
60 min → Test manually with curl
90 min → Deploy to staging
2h     → Full integration complete
```

---

## 🔧 Environment Variables

```bash
# Required
JWT_SECRET=<strong-random-hex-string>

# Optional (defaults shown)
JWT_EXPIRY_HOURS=24
SNAPSHOT_BASE_DIR=./snapshots
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## ✅ Pre-Deployment Checklist

```
□ All 42 tests passing
□ JWT_SECRET set to strong value (NOT default)
□ CORS configured for actual domain
□ HTTPS/TLS enabled
□ Real user authentication implemented
□ Audit logs configured for secure storage
□ Rate limiting enabled
□ Monitoring & alerting setup
□ Secrets not in .env (use secrets manager)
□ Database credentials encrypted
```

---

## 📞 Need Help?

| Question | Answer |
|----------|--------|
| What are the vulnerabilities? | Read `SECURITY_API_FIXES.md` |
| How do I implement it? | Read `CI_CD_SECURITY_PIPELINE_GUIDE.md` |
| Quick start? | Read `SECURITY_IMPLEMENTATION_QUICKSTART.md` |
| Code examples? | See `test_phase6b_rest_api_security.py` |
| Architecture? | See `.zencoder/artifacts/REST_API_SECURITY_PIPELINE_OVERVIEW.md` |
| Workflow details? | See `.github/workflows/phase6b-rest-api-security.yml` |

---

## 🎯 Success Metrics

```
✅ All 42 tests passing
✅ GitHub Actions green
✅ Security tab shows 0 critical issues
✅ Manual token auth works
✅ Manual path traversal blocked
✅ Manual auth bypass blocked
✅ No hardcoded secrets
✅ Audit logs recording actions
✅ Ready for production!
```

---

**Last Updated**: 2025-11-01  
**Version**: 1.0 - Production Ready  
**Status**: ✅ Complete

Keep this card handy while implementing!