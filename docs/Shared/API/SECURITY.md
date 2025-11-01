# 🔒 Security Reference Guide

**Status**: Production Ready  
**Last Updated**: 2025-01-15  
**Scope**: REST API, WebSocket, and System Security  

---

## Table of Contents

1. [Reporting Security Vulnerabilities](#reporting-vulnerabilities)
2. [Security Policy](#security-policy)
3. [REST API Security Fixes](#rest-api-security-fixes)
4. [Security Patches Summary](#security-patches)
5. [Implementation Guide](#implementation-guide)
6. [Security Checklist](#security-checklist)

---

## Reporting Vulnerabilities

### 🚨 Immediate Actions Required

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. **DO NOT** share vulnerability details in public forums
3. **DO** report through secure channels (below)

### Secure Reporting Channels

#### Primary: GitHub Security Advisories
- Go to repository's Security tab
- Click "Report a vulnerability"
- Fill out the private vulnerability report form
- Include detailed information

#### Alternative: Email
- Send to: `security@tiny-walnut-games.dev`
- Use PGP encryption if possible
- Include "[SECURITY]" in the subject line

### Report Information Needed

- **Vulnerability Type**: Classification of the security issue
- **Affected Components**: Which parts are vulnerable
- **Attack Vector**: How could it be exploited
- **Impact Assessment**: What could an attacker accomplish
- **Proof of Concept**: Steps to reproduce (if safe)
- **Suggested Fix**: Any remediation ideas (optional)

### Response Timeline

- **Initial Response**: Within 24 hours
- **Vulnerability Assessment**: Within 72 hours
- **Fix Development**: Within 7 days (critical issues)
- **Public Disclosure**: 30 days after fix deployment (coordinated)

---

## Security Policy

### In Scope

**Core Components Covered**:
- REST API endpoints and authentication
- WebSocket communication layer
- Python backend services
- CI/CD workflow security
- Configuration and secrets management
- Input validation and sanitization
- Error handling and logging

**Security-Relevant Areas**:
- Input validation in Python/C# code
- File system operations
- Command execution in scripts
- Configuration file parsing
- Data serialization/deserialization
- Session and token management
- Access controls and authorization

### Out of Scope

- Third-party dependencies (report to maintainers)
- User's custom implementations
- Infrastructure hosting (GitHub responsibility)
- Social engineering attacks
- Physical security

---

## REST API Security Fixes

### 1. Path Traversal Vulnerability (CRITICAL)

**Location**: `phase6b_rest_api.py:914-945` - `save_snapshot` endpoint

**Issue**: File paths accepted directly without validation

```python
# ❌ VULNERABLE
@self.app.post("/api/universe/snapshot/save")
async def save_snapshot(
    filepath: str = Query(..., description="File path to save"),
):
    exporter.export_to_file(self.orchestrator, filepath)  # No validation!
```

**Attack Examples**:
```
POST /api/universe/snapshot/save?filepath=../../../etc/passwd
POST /api/universe/snapshot/save?filepath=../../.ssh/authorized_keys
```

**✅ Fixed Implementation**:
```python
from security_validators import InputValidator

@self.app.post("/api/universe/snapshot/save")
async def save_snapshot(
    filepath: str = Query(..., description="Snapshot filename only"),
    current_user: Dict = Depends(BearerAuth.get_current_user),
):
    # ✅ Validate and confine to base directory
    validated_path = InputValidator.validate_filepath(filepath)
    
    # ✅ Log the action securely
    AuditLogger.log_action(
        current_user["user_id"],
        "snapshot_save",
        validated_path.name,
        "success"
    )
    
    exporter.export_to_file(self.orchestrator, str(validated_path))
```

**Prevention Mechanism**:
- Use `pathlib.Path` to resolve absolute paths
- Confine operations to designated base directory
- Reject paths containing `..` or other traversal attempts

---

### 2. Missing Authentication (CRITICAL)

**Issue**: Sensitive endpoints have no authentication requirements

**Vulnerable Endpoints**:
```
GET /api/universe/snapshot/replay?seed=12345
POST /api/admin/audit-log
GET /api/realms/...
```

**✅ Fixed Implementation**:

```python
from auth_middleware import RBACMiddleware, BearerAuth

# Viewer can read realms
@app.get("/api/realms")
@RBACMiddleware.require_role([ROLE_VIEWER, ROLE_ADMIN])
async def list_realms(
    current_user: Dict = Depends(BearerAuth.get_current_user)
):
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

**Role-Based Access Control (RBAC)**:
- `ROLE_VIEWER`: Read-only access to public data
- `ROLE_ADMIN`: Full access including snapshot operations
- `ROLE_SYSTEM`: Internal system operations only

---

### 3. Error Information Leakage (HIGH)

**Issue**: Exception handlers expose implementation details

```python
# ❌ VULNERABLE
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")
    # Response: "Save failed: File not found at /home/admin/.ssh/config"
    #           ↑ Reveals file system structure!
```

**✅ Fixed Implementation**:

```python
from security_validators import SecureErrorHandler

try:
    exporter.export_to_file(self.orchestrator, filepath)
except Exception as e:
    # ✅ Log full details internally
    logger.error(f"Snapshot export failed: {e}", exc_info=True)
    
    # ✅ Return generic message to client
    SecureErrorHandler.raise_safe_error(
        e, 
        context="snapshot export",
        user_message="Snapshot export failed. Please try again later."
    )
```

**Result**: Users see generic message; developers get full details in logs.

---

### 4. Unauthenticated Data Exposure (MEDIUM)

**Issue**: Data endpoints return detailed metadata without authorization

**✅ Fixed Implementation**:

```python
@self.app.get("/api/realms/{realm_id}/tier")
@RBACMiddleware.require_role([ROLE_VIEWER, ROLE_ADMIN])
async def get_realm_tier(
    realm_id: str = Path(...),
    current_user: Dict = Depends(BearerAuth.get_current_user)
):
    # ✅ User is authenticated and authorized
    realm_id = InputValidator.validate_realm_id(realm_id)
    return tier_metadata
```

**Pattern**: All data-returning endpoints must require authentication and authorization.

---

### 5. Insecure Logging (MEDIUM)

**Issue**: Logs contain PII and sensitive identifiers

```python
# ❌ VULNERABLE
logger.info(f"Snapshot saved to {filepath}")  # Exposes file paths
logger.info(f"Audit: {action} by {admin_id}")  # Exposes IDs
```

**✅ Fixed Implementation**:

```python
# ✅ Application logs: sanitized only
logger.info(f"Snapshot saved (file_id: {hash(filepath)})")
logger.info(f"Audit: action={action}")

# ✅ Sensitive details: secure audit log only
AuditLogger.log_action(
    user_id=admin_id,           # Still logged securely
    action=action,
    resource=entity_id,
    result="success",
    timestamp=datetime.utcnow(),
    ip_address=request.client.host
)
```

**Logging Rules**:
- Never log file paths, user IDs, or entity IDs to application logs
- Log action types and results only
- Maintain separate secure audit log for sensitive data
- All audit log entries must be cryptographically signed

---

### 6. Input Validation (HIGH)

**Issue**: No validation on user-provided parameters

**✅ Fixed Implementation**:

```python
from security_validators import InputValidator

class InputValidator:
    @staticmethod
    def validate_filepath(filepath: str) -> Path:
        """Validate and confine file path."""
        if not filepath or not isinstance(filepath, str):
            raise ValueError("Invalid filepath")
        
        # Remove path traversal attempts
        if ".." in filepath or filepath.startswith("/"):
            raise ValueError("Path traversal detected")
        
        # Confine to base directory
        base_dir = Path("./snapshots").resolve()
        target_path = (base_dir / filepath).resolve()
        
        if not str(target_path).startswith(str(base_dir)):
            raise ValueError("Path outside allowed directory")
        
        return target_path
    
    @staticmethod
    def validate_realm_id(realm_id: str) -> str:
        """Validate realm ID format."""
        if not realm_id or len(realm_id) > 256:
            raise ValueError("Invalid realm ID")
        
        if not realm_id.isalnum() and "_" not in realm_id:
            raise ValueError("Realm ID contains invalid characters")
        
        return realm_id
```

---

## Security Patches

### Overlord Sentinel Security Summary

**Status**: ✅ All critical issues resolved  
**Date**: 2025-10-24  
**Fixes Applied**: 15 (5 CRITICAL + 6 HIGH + 4 MEDIUM)

#### CRITICAL Fixes 🔴

1. **Missing Constant Definitions**
   - Added: `MIN_DAILY_APPROVALS = 1`, `MAX_DAILY_APPROVALS = 1000`

2. **Wrong Package Name in Security Workflow**
   - Fixed: `truffleHog3` → `trufflehog==5.0.0`

3. **GitHub Token in Log Output**
   - Added: Token masking in error handlers

4. **Plaintext Secrets in YAML**
   - Fixed: Moved config to `.gitignore`, created `.template` version

5. **Bare Except Clauses**
   - Fixed: 3 instances with specific exception handling

#### HIGH Fixes 🟠

6. **Missing Timeout Configuration** - Added 5000ms timeout
7. **Daily Counter Reset** - Now uses calendar date (not process restart)
8. **Hardcoded Config Path** - Now uses absolute path resolution
9. **Unvalidated Context** - Added validation on all entry points
10. **Regex DoS Vulnerability** - Added length limits and safe regex patterns

#### MEDIUM Fixes 🟡

11. **Missing Token Validation** - Added warning check
12. **Placeholder Methods** - Implemented proper audit comment generation
13. **Response Validation** - Added object checking on GitHub API responses
14. **Severity Logic** - Corrected HIGH/MEDIUM/LOW level mapping

---

## Implementation Guide

### Step 1: Install Security Dependencies

```bash
pip install PyJWT python-jose cryptography fastapi-security
pip install bandit==1.7.5 pip-audit==2.6.1 safety==3.0.1 trufflehog==5.0.0
```

### Step 2: Add Environment Variables

Create `.env` file:
```bash
# Authentication
JWT_SECRET=your-very-secure-secret-key-here
JWT_EXPIRY_HOURS=24

# File Operations
SNAPSHOT_BASE_DIR=./snapshots

# Security Limits
MAX_DAILY_APPROVALS=1000
REQUEST_TIMEOUT_MS=5000
```

### Step 3: Update API Server

Replace vulnerable endpoints with the fixed implementations shown above in Section 2.

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
TOKEN="<generated-token>"

curl -X POST "http://localhost:8000/api/universe/snapshot/save?filepath=snapshot.json" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Security Checklist

### Before Each Release

- [ ] Run `bandit` security linter: `bandit -r src/ scripts/`
- [ ] Run `safety check` for dependencies
- [ ] Run `trufflehog` for secrets: `trufflehog filesystem . --json`
- [ ] Verify all endpoints require authentication
- [ ] Test path traversal attempts (should fail)
- [ ] Verify error messages don't leak details
- [ ] Audit log entries are cryptographically signed
- [ ] No hardcoded secrets in code or configs

### Monthly Security Tasks

- [ ] Update all Python packages to latest versions
- [ ] Review repository collaborators and access permissions
- [ ] Run comprehensive secret scanning tools
- [ ] Check for new CVEs in dependencies
- [ ] Review all audit log entries for suspicious activity
- [ ] Verify encryption keys are rotated

### Quarterly Security Review

- [ ] Review security policy for updates
- [ ] Test incident response procedures
- [ ] Update threat model documentation
- [ ] Review access control policies
- [ ] Conduct security training

---

## Security Testing

**Test Location**: `test_phase6b_rest_api_security.py`

**Test Coverage**:
- ✅ Path traversal attempt prevention
- ✅ Authentication bypass attempts
- ✅ Authorization enforcement
- ✅ Error message leakage prevention
- ✅ Audit logging verification
- ✅ Token validation and expiry
- ✅ Rate limiting enforcement
- ✅ Input validation on all parameters

**Running Tests**:
```bash
pytest tests/test_phase6b_rest_api_security.py -v
```

---

## CI/CD Integration

### Automated Security Scanning

GitHub Actions workflow (`.github/workflows/overlord-sentinel-security.yml`):

```yaml
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit
        run: bandit -r src/ scripts/ --format json --output bandit-report.json
      
      - name: Run Safety
        run: safety check --json > safety-report.json
      
      - name: Run Trufflehog
        run: trufflehog filesystem . --json > secrets-report.json
      
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
            secrets-report.json
```

---

## FAQ

**Q: How often are security audits performed?**
A: Continuous via CI/CD pipeline, plus quarterly manual reviews.

**Q: What should I do if I find a security vulnerability?**
A: Report it immediately using the secure channels in "Reporting Vulnerabilities" section.

**Q: Are secrets encrypted?**
A: Secrets must be stored in environment variables, never committed to version control.

**Q: How are audit logs protected?**
A: Audit logs are stored separately, cryptographically signed, and never exposed in API responses.

---

**Last Updated**: 2025-01-15  
**Version**: 1.0.0  
**Next Review**: 2025-04-15  
**Maintained By**: Security Team