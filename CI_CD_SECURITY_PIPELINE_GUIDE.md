# 🚀 CI/CD Security Pipeline Implementation Guide

## Overview

This guide explains how to integrate the comprehensive security pipeline into your Phase 6B REST API and automate security checks through GitHub Actions.

**Timeline**: ~2 hours to implement
**Components**: 
- Security validation library
- Authentication middleware
- Updated REST API endpoints
- Automated test suite
- GitHub Actions workflows

---

## Part 1: Project Structure

```
the-seed/
├── packages/com.twg.the-seed/seed/engine/
│   ├── phase6b_rest_api.py              (Main REST API - WILL BE UPDATED)
│   ├── security_validators.py           (NEW - Input validation)
│   ├── auth_middleware.py               (NEW - Auth & RBAC)
│   └── ...
├── tests/
│   ├── test_phase6b_rest_api.py        (Existing tests)
│   └── test_phase6b_rest_api_security.py (NEW - Security tests)
├── .github/workflows/
│   ├── overlord-sentinel-security.yml   (Existing general security)
│   └── phase6b-rest-api-security.yml    (NEW - API-specific security)
├── SECURITY_API_FIXES.md                (NEW - Detailed fix documentation)
├── CI_CD_SECURITY_PIPELINE_GUIDE.md     (THIS FILE)
└── .env.example                          (NEW - Environment variables)
```

---

## Part 2: Installation & Setup

### Step 1: Install Dependencies

```bash
# Core REST API dependencies
pip install fastapi uvicorn pydantic

# Authentication & security
pip install PyJWT python-jose cryptography

# Testing
pip install pytest pytest-asyncio httpx pytest-cov

# CLI tools
pip install bandit semgrep pip-audit
```

### Step 2: Environment Configuration

Create `.env` file in project root:

```bash
# JWT Configuration
JWT_SECRET="your-production-secret-key-here-change-immediately"
JWT_EXPIRY_HOURS=24

# Snapshot storage
SNAPSHOT_BASE_DIR="./snapshots"

# API Configuration
API_HOST="0.0.0.0"
API_PORT=8000
API_DEBUG=false

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"
```

Create `.env.example` (no secrets):

```bash
JWT_SECRET=<set-in-production>
JWT_EXPIRY_HOURS=24
SNAPSHOT_BASE_DIR=./snapshots
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
```

---

## Part 3: Integrate Security Validators

The `security_validators.py` module is already created. Now integrate it into your REST API:

### Usage Example:

```python
from security_validators import InputValidator, SecureErrorHandler
from auth_middleware import AuthToken, BearerAuth, RBACMiddleware

@self.app.post("/api/universe/snapshot/save")
@RBACMiddleware.require_role([ROLE_ADMIN])  # ← Add this
async def save_snapshot(
    filepath: str = Query(..., description="Snapshot filename"),
    current_user: Dict = Depends(BearerAuth.get_current_user),  # ← Add this
):
    try:
        # ✅ VALIDATE INPUT
        validated_path = InputValidator.validate_filepath(filepath)
        
        # ✅ LOG AUDIT
        AuditLogger.log_action(
            current_user["user_id"],
            "snapshot_save",
            validated_path.name,
            "success"
        )
        
        # Safe to use now
        snapshot = await exporter.export_to_file(
            self.orchestrator,
            str(validated_path)
        )
        
        return {"status": "saved", "filepath": str(validated_path)}
    
    except Exception as e:
        # ✅ SECURE ERROR HANDLING
        SecureErrorHandler.raise_safe_error(
            e, 
            context="snapshot export"
        )
```

---

## Part 4: Update phase6b_rest_api.py

### Changes Summary:

1. **Add imports** at top of file:
```python
from security_validators import InputValidator, SecureErrorHandler
from auth_middleware import (
    AuthToken, BearerAuth, RBACMiddleware, AuditLogger,
    ROLE_ADMIN, ROLE_VIEWER, ROLE_SYSTEM
)
```

2. **Add CORS & Security Headers** in `__init__`:
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add to __init__ method after app creation
self.app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Configure for your domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

self.app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"]
)
```

3. **Add Token Endpoint** for auth:
```python
@self.app.post("/api/auth/token")
async def get_token(username: str, password: str):
    """
    Generate JWT token (in production, validate against database).
    
    Example usage:
    ```
    curl -X POST "http://localhost:8000/api/auth/token" \
      -d "username=admin&password=secret"
    ```
    """
    # TODO: Replace with real authentication
    if username == "admin" and password == "admin":  # ⚠️ For demo only!
        token = AuthToken.create_token(username, role=ROLE_ADMIN)
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

4. **Update All Endpoints** following this pattern:

```python
# BEFORE (Vulnerable)
@self.app.post("/api/universe/snapshot/save")
async def save_snapshot(
    filepath: str = Query(...),
    include_enrichments: bool = Query(True),
    include_audit_trail: bool = Query(True),
):
    try:
        exporter.export_to_file(self.orchestrator, filepath)
        return {"status": "saved", "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")

# AFTER (Secured)
@self.app.post("/api/universe/snapshot/save")
@RBACMiddleware.require_role([ROLE_ADMIN, ROLE_SYSTEM])
async def save_snapshot(
    filepath: str = Query(..., description="Snapshot filename"),
    include_enrichments: bool = Query(True),
    include_audit_trail: bool = Query(True),
    current_user: Dict = Depends(BearerAuth.get_current_user),
):
    try:
        # Input validation
        validated_path = InputValidator.validate_filepath(filepath)
        
        # Audit log
        AuditLogger.log_action(
            current_user["user_id"],
            "snapshot_save",
            validated_path.name,
            "initiated",
            {"include_enrichments": include_enrichments}
        )
        
        # Execute
        snapshot = await exporter.export_to_file(
            self.orchestrator,
            str(validated_path)
        )
        
        # Log success
        AuditLogger.log_action(
            current_user["user_id"],
            "snapshot_save",
            validated_path.name,
            "success"
        )
        
        return {
            "status": "saved",
            "filepath": str(validated_path),
            "seed": snapshot.seed,
            "universe_hash": snapshot.universe_hash,
        }
    
    except Exception as e:
        # Log failure
        AuditLogger.log_action(
            current_user["user_id"],
            "snapshot_save",
            filepath,
            "failed",
            {"error": type(e).__name__}
        )
        SecureErrorHandler.raise_safe_error(e, context="snapshot export")
```

---

## Part 5: GitHub Actions Integration

### Workflow Files:

Two workflows are configured:

1. **`overlord-sentinel-security.yml`** - General security scanning
   - Bandit, TruffleHog, Safety, pip-audit, Semgrep
   - Runs on all pushes and PRs
   - Uploads to GitHub Security tab

2. **`phase6b-rest-api-security.yml`** - API-specific scanning
   - Path traversal detection
   - Authentication enforcement checks
   - Input validation testing
   - Security test suite
   - Runs when API files change

### Enable Workflows:

1. Workflows are in `.github/workflows/` and auto-enabled
2. Check **Actions** tab in GitHub for execution
3. Results appear in **Security** tab

### Local Testing:

Run security checks locally before pushing:

```bash
# Run security validators
pytest tests/test_phase6b_rest_api_security.py -v

# Run Bandit
bandit -r packages/com.twg.the-seed/seed/engine/phase6b_rest_api.py

# Run Semgrep
semgrep --config=.semgrep-rules/ packages/com.twg.the-seed/seed/engine/
```

---

## Part 6: Testing

### Test Execution

```bash
# Run all API security tests
pytest tests/test_phase6b_rest_api_security.py -v

# Run specific test class
pytest tests/test_phase6b_rest_api_security.py::TestPathTraversalPrevention -v

# Run with coverage
pytest tests/test_phase6b_rest_api_security.py --cov=packages/com.twg.the-seed/seed/engine

# Run in CI mode
pytest tests/test_phase6b_rest_api_security.py --junit-xml=results.xml
```

### Test Coverage

Test file covers:
- ✅ Path traversal prevention (11 tests)
- ✅ Input validation (10 tests)
- ✅ Authentication (6 tests)
- ✅ Authorization (3 tests)
- ✅ Error handling (2 tests)
- ✅ Audit logging (3 tests)
- ✅ Integration (3 tests)
- ✅ Compliance (4 tests)

**Total: 42 security-focused tests**

---

## Part 7: Manual Testing with curl

### Generate Token

```bash
# Get authentication token
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/token" \
  -d "username=admin&password=admin" \
  -s | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

### Test Authenticated Endpoint

```bash
# Valid request
curl -X POST "http://localhost:8000/api/universe/snapshot/save?filepath=snapshot.json" \
  -H "Authorization: Bearer $TOKEN" \
  -v

# Attempt path traversal (should be blocked)
curl -X POST "http://localhost:8000/api/universe/snapshot/save?filepath=../../../etc/passwd" \
  -H "Authorization: Bearer $TOKEN" \
  -v

# Unauthenticated request (should fail)
curl -X POST "http://localhost:8000/api/universe/snapshot/save?filepath=snapshot.json" \
  -v
```

---

## Part 8: Monitoring & Alerting

### GitHub Security Features

1. **Security Tab** - Shows SARIF results from workflows
2. **Code Scanning Alerts** - Lists all detected issues
3. **Dependency Alerts** - Warns about vulnerable packages
4. **Branch Protection** - Can require checks to pass before merge

### Setup Branch Protection

1. Go to **Settings → Branches**
2. Add rule for `main` branch
3. Enable "Require status checks to pass":
   - `API Security Analysis` ✅
   - `Dependency Security Check` ✅
4. Enable "Dismiss stale pull request approvals"

---

## Part 9: Deployment Checklist

### Before Deploying to Production

- [ ] All tests passing locally
- [ ] Security scans passing (0 critical issues)
- [ ] Authentication configured with real users
- [ ] JWT secret set to strong random value (NOT default)
- [ ] CORS configured for actual domain
- [ ] Logging configured for production (structured JSON)
- [ ] Audit logs sent to secure storage
- [ ] Rate limiting configured
- [ ] HTTPS/TLS enabled
- [ ] Database backups automated
- [ ] Monitoring & alerting setup

### Environment-Specific Configuration

**Development (.env.dev)**:
```
JWT_SECRET=dev-key-not-for-production
API_DEBUG=true
LOG_LEVEL=DEBUG
```

**Staging (.env.staging)**:
```
JWT_SECRET=$(openssl rand -hex 32)
API_DEBUG=false
LOG_LEVEL=INFO
```

**Production (.env.prod)**:
```
JWT_SECRET=$(openssl rand -hex 32)  # Use secrets manager
API_DEBUG=false
LOG_LEVEL=WARNING
```

---

## Part 10: Troubleshooting

### Issue: "Token validation failed"

```python
# Ensure JWT_SECRET is consistent across all instances
# If using multiple processes, use same secret

# Generate strong secret
import secrets
secret = secrets.token_hex(32)
print(f"JWT_SECRET={secret}")
```

### Issue: "Access denied" on authenticated endpoint

```python
# Check token has correct role
# Generate token with correct role
token = AuthToken.create_token("user", role=ROLE_ADMIN)

# Verify token payload
payload = AuthToken.verify_token(token)
print(payload)  # Should show role: admin
```

### Issue: "Path traversal detected"

```python
# Only use filename, not paths
# ✅ CORRECT
InputValidator.validate_filepath("snapshot.json")

# ❌ WRONG
InputValidator.validate_filepath("../snapshots/file.json")
```

### Issue: Security tests failing in CI

1. Check Python version: `python3 --version` (should be 3.11+)
2. Check dependencies: `pip list | grep pytest`
3. Run locally first: `pytest tests/test_phase6b_rest_api_security.py -v`
4. Check workflow logs in GitHub Actions

---

## Part 11: Next Steps

### Phase 6B Enhancements

1. **Database Integration**
   - Store user credentials securely (bcrypt, not plaintext)
   - Persistent audit logs
   - User session management

2. **Advanced RBAC**
   - Role definitions in database
   - Fine-grained permissions
   - Resource-level authorization

3. **Rate Limiting**
   - Implement slowdown.py or similar
   - Per-user rate limits
   - Endpoint-specific thresholds

4. **API Versioning**
   - Support `/api/v1/`, `/api/v2/`
   - Deprecation timelines
   - Backward compatibility

### Monitoring

1. **Application Performance**
   - Response times
   - Error rates
   - Resource usage

2. **Security Events**
   - Failed auth attempts
   - Path traversal blocks
   - Access denied logs

3. **Compliance**
   - Audit trail retention
   - Regulatory reporting
   - Data retention policies

---

## Quick Reference

```bash
# Start REST API server
python run_stat7.py

# Generate auth token
curl -X POST "http://localhost:8000/api/auth/token" \
  -d "username=admin&password=admin"

# Run security tests
pytest tests/test_phase6b_rest_api_security.py -v

# Run security scans locally
bandit -r packages/com.twg.the-seed/seed/engine/

# Check compliance
./scripts/run-security-scan-local.ps1 -ScanType full  # Windows
./scripts/run-security-scan-local.sh full              # Linux/Mac
```

---

## Support & Issues

For security vulnerabilities, see [SECURITY.md](SECURITY.md)

For questions on implementation, check:
- `SECURITY_API_FIXES.md` - Detailed vulnerability explanations
- `test_phase6b_rest_api_security.py` - Working examples
- `.github/workflows/phase6b-rest-api-security.yml` - Automation details