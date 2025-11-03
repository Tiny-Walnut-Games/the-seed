# 🔒 Phase 6B REST API Security Fixes

## Critical Issues Addressed

### 1. **Path Traversal Vulnerability** (CRITICAL)
**Location**: `phase6b_rest_api.py:914-945` - `save_snapshot` endpoint

**Issue**: File path parameter accepted directly without validation
```python
# VULNERABLE CODE
@self.app.post("/api/universe/snapshot/save")
async def save_snapshot(
    filepath: str = Query(..., description="File path to save snapshot"),
):
    exporter.export_to_file(self.orchestrator, filepath)  # ❌ No validation!
```

**Attack Example**:
```
POST /api/universe/snapshot/save?filepath=../../../etc/passwd
POST /api/universe/snapshot/save?filepath=../../.ssh/authorized_keys
```

**Fix Applied**:
```python
from security_validators import InputValidator

@self.app.post("/api/universe/snapshot/save")
async def save_snapshot(
    filepath: str = Query(..., description="Snapshot filename (no paths)"),
    current_user: Dict = Depends(BearerAuth.get_current_user),
):
    # ✅ Validate input
    validated_path = InputValidator.validate_filepath(filepath)
    
    # ✅ Log the action
    AuditLogger.log_action(
        current_user["user_id"],
        "snapshot_save",
        validated_path.name,
        "success"
    )
    
    exporter.export_to_file(self.orchestrator, str(validated_path))
```

---

### 2. **Missing Authentication** (CRITICAL)
**Location**: Multiple endpoints without auth checks

**Issues**:
- No authentication required on sensitive endpoints
- No authorization checks on data access
- Admin operations accessible to anyone

**Attack Example**:
```
# Anyone can access admin endpoints
GET /api/universe/snapshot/replay?seed=12345
POST /api/admin/audit-log
```

**Fix Applied**: Decorator-based access control
```python
from auth_middleware import RBACMiddleware, BearerAuth

# Viewer can read realms
@app.get("/api/realms")
@RBACMiddleware.require_role([ROLE_VIEWER, ROLE_ADMIN])
async def list_realms(current_user: Dict = Depends(BearerAuth.get_current_user)):
    return realms

# Only admin can save snapshots
@app.post("/api/universe/snapshot/save")
@RBACMiddleware.require_role([ROLE_ADMIN, ROLE_SYSTEM])
async def save_snapshot(
    filepath: str = Query(...),
    current_user: Dict = Depends(BearerAuth.get_current_user)
):
    return snapshot
```

---

### 3. **Error Information Leakage** (HIGH)
**Location**: Exception handlers expose raw error details

**Issue**:
```python
# VULNERABLE - Exposes implementation details
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")
```

**Attack Example**:
```
Response: "Save failed: File not found at /home/admin/.ssh/config"
         ↑ Reveals file system structure!
```

**Fix Applied**:
```python
from security_validators import SecureErrorHandler

try:
    exporter.export_to_file(self.orchestrator, filepath)
except Exception as e:
    # ✅ Logs full details internally, returns generic message
    SecureErrorHandler.raise_safe_error(e, context="snapshot export")
```

---

### 4. **Unauthenticated Data Exposure** (MEDIUM)
**Location**: Data endpoints without authorization

**Issues**:
- Tier/theme endpoints return detailed metadata
- No verification that user should access this data
- Potential information disclosure

**Fix Applied**:
```python
@self.app.get("/api/realms/{realm_id}/tier")
@RBACMiddleware.require_role([ROLE_VIEWER, ROLE_ADMIN])
async def get_realm_tier(
    realm_id: str = Path(...),
    current_user: Dict = Depends(BearerAuth.get_current_user)
):
    realm_id = InputValidator.validate_realm_id(realm_id)
    
    # ✅ User is authenticated and authorized
    return tier_metadata
```

---

### 5. **Incomplete Error Handling** (MEDIUM)
**Location**: Broad `except:` blocks without specific context

**Issues**:
```python
# VULNERABLE - Catches all exceptions silently
except:
    pass  # ❌ No logging or recovery
```

**Fix Applied**:
```python
try:
    tier_meta = await self.hierarchical_adapter.tier_registry.get_metadata(realm_id)
except AttributeError as e:
    logger.error(f"Tier registry not initialized: {e}")
    raise HTTPException(status_code=503, detail="Service unavailable")
except Exception as e:
    SecureErrorHandler.raise_safe_error(e, context="tier metadata retrieval")
```

---

### 6. **Insecure Logging** (MEDIUM)
**Location**: Logs contain PII and sensitive identifiers

**Issues**:
```python
# VULNERABLE - Logs sensitive data
logger.info(f"✅ Snapshot saved to {filepath}")  # Exposes file paths
logger.info(f"📝 Audit logged: {entry.action_type} on {entry.entity_id} by {entry.admin_id}")
```

**Fix Applied**:
```python
# ✅ Sanitized logging
logger.info(f"Snapshot saved (file_id: {hash(filepath)})")
logger.info(f"Audit logged: action_type={entry.action_type}")

# Sensitive details go only to secure audit log
AuditLogger.log_action(
    user_id=entry.admin_id,  # Still logged securely
    action=entry.action_type,
    resource=entry.entity_id,
    result="success"
)
```

---

## Implementation Steps

### Step 1: Install Security Dependencies
```bash
pip install PyJWT python-jose cryptography
```

### Step 2: Add Environment Variables
```bash
# .env file
JWT_SECRET=your-very-secure-secret-key-here
JWT_EXPIRY_HOURS=24
SNAPSHOT_BASE_DIR=./snapshots
```

### Step 3: Update API Server
Replace vulnerable endpoints with fixed versions (patch provided below).

### Step 4: Generate Test Token
```python
from auth_middleware import AuthToken

token = AuthToken.create_token(
    user_id="admin_user",
    role="admin",
    expires_in_hours=24
)
print(f"Authorization: Bearer {token}")
```

### Step 5: Use Token in Requests
```bash
curl -X POST "http://localhost:8000/api/universe/snapshot/save?filepath=snapshot.json" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Security Test Cases

See `test_phase6b_rest_api_security.py` for comprehensive security tests:
- ✅ Path traversal attempt prevention
- ✅ Authentication bypass attempts
- ✅ Authorization enforcement
- ✅ Error message leakage prevention
- ✅ Audit logging verification

---

## Compliance Checklist

- ✅ Input validation on all user-provided parameters
- ✅ Path traversal prevention (base directory confinement)
- ✅ Authentication required on sensitive endpoints
- ✅ Role-based authorization enforced
- ✅ Error messages don't leak implementation details
- ✅ All critical actions logged to audit trail
- ✅ Sensitive data not logged to application logs
- ✅ Exception handling is specific and logged
- ✅ CORS and security headers configured
- ✅ Rate limiting applied

---

## CI/CD Integration

These fixes integrate with the security pipeline:
- **Bandit** detects hardcoded secrets
- **Semgrep** catches path traversal patterns
- **Custom tests** verify auth enforcement
- **SAST scanning** in GitHub Actions

See `.github/workflows/overlord-sentinel-security.yml` for automated scanning.