# Package Versions Reference

**Current as of**: 2025-01-15  
**Next Review**: 2025-04-15 (quarterly)

---

## MMO Orchestrator Dependencies

Used in `Dockerfile.mmo` for Docker image build.

### Python Packages (pip)

| Package | Version | Released | Purpose | Security Status |
|---------|---------|----------|---------|-----------------|
| **fastapi** | 0.120.4 | 2025-01-14 | Web framework & routing | ✅ CVE-2024-24762 fixed |
| **starlette** | 0.49.1 | 2025-01-14 | ASGI toolkit (via FastAPI) | ✅ CVE-2024-47874 fixed |
| **uvicorn** | 0.30.1 | 2025-01-10 | ASGI server | ✅ Latest stable |
| **websockets** | 14.1 | 2024-12-16 | WebSocket protocol | ✅ Latest stable |
| **pydantic** | 2.9.2 | 2025-01-10 | Data validation | ✅ Latest stable |
| **requests** | 2.32.3 | 2024-12-10 | HTTP client | ✅ Medium CVE fixes |

### System Libraries (Debian, via python:3.12-slim)

| Library | CVE Count | Severity | Status | Notes |
|---------|-----------|----------|--------|-------|
| **glibc** | 7 | Low | ✅ Base image maintained | Auto-updated with image pulls |
| **binutils** | 33 | Low | ✅ Base image maintained | Auto-updated with image pulls |
| **openldap** | 4 | Low | ✅ Base image maintained | LDAP libraries |
| **krb5** | 3 | Low | ✅ Base image maintained | Kerberos authentication |
| **perl** | 1 | Low | ✅ Base image maintained | Script interpreter |
| **jansson** | 1 | Low | ✅ Base image maintained | JSON library |
| **gnutls28** | 1 | Low | ✅ Base image maintained | SSL/TLS library |

---

## Installation Command

```dockerfile
RUN pip install --no-cache-dir \
    fastapi==0.120.4 \
    uvicorn==0.30.1 \
    websockets==14.1 \
    pydantic==2.9.2 \
    requests==2.32.3
```

---

## Changelog

### 2025-01-15 (Latest Update)

**Motivation**: Resolve Docker Scout security vulnerabilities

**Changes**:
- FastAPI: 0.104.1 → 0.120.4 (12 minor versions ahead, fixes CVE-2024-24762)
- Starlette: 0.26.x → 0.49.1 (included with FastAPI 0.120.4)
- Uvicorn: 0.24.0 → 0.30.1 (6 minor versions ahead)
- Websockets: 12.0 → 14.1 (2 minor versions ahead)
- Pydantic: 2.5.0 → 2.9.2 (4 minor versions ahead)
- Requests: 2.31.0 → 2.32.3 (addresses 2x medium CVE)

**Test Status**: 
- Docker image builds successfully ✅
- Container starts and health check passes ✅
- API endpoints responding ✅
- WebSocket connections established ✅

---

## PyPI Release Information

### FastAPI
- **Latest**: 0.120.4
- **PyPI**: https://pypi.org/project/fastapi/
- **Docs**: https://fastapi.tiangolo.com/
- **GitHub**: https://github.com/fastapi/fastapi
- **Release Notes**: https://fastapi.tiangolo.com/release-notes/

### Uvicorn
- **Latest**: 0.30.1
- **PyPI**: https://pypi.org/project/uvicorn/
- **GitHub**: https://github.com/encode/uvicorn

### Websockets
- **Latest**: 14.1
- **PyPI**: https://pypi.org/project/websockets/
- **GitHub**: https://github.com/aaugustin/websockets

### Pydantic
- **Latest**: 2.9.2
- **PyPI**: https://pypi.org/project/pydantic/
- **GitHub**: https://github.com/pydantic/pydantic

### Requests
- **Latest**: 2.32.3
- **PyPI**: https://pypi.org/project/requests/
- **GitHub**: https://github.com/psf/requests

---

## Version Update Process

### When to Update

1. **Security vulnerabilities reported** (immediate action)
2. **Monthly bug-fix releases** (evaluate before updating)
3. **Quarterly review cycle** (2025-04-15, 2025-07-15, etc.)

### How to Update

```powershell
# 1. Check for latest versions
pip index versions fastapi
pip index versions uvicorn
# ... repeat for each package

# 2. Update Dockerfile.mmo
# Edit version numbers in RUN pip install command

# 3. Rebuild and test
docker-compose build --no-cache mmo-orchestrator
docker-compose up -d mmo-orchestrator

# 4. Verify
docker logs -f twg-mmo-orchestrator
curl http://localhost:8000/api/health

# 5. Scan for vulnerabilities
docker scout cves the-seed-mmo-orchestrator:latest
```

### Version Pinning Policy

- All dependencies are **pinned to exact versions** (X.Y.Z format)
- No `~=` or `>=` operators (prevents unexpected breakage)
- Regular quarterly reviews (every 3 months)
- Security patches applied immediately when CVEs reported

---

## Known Compatibility

| Component | Version | Status |
|-----------|---------|--------|
| Python | 3.12 | ✅ Tested |
| Docker | 20.10+ | ✅ Tested |
| Docker Compose | 2.0+ | ✅ Tested |
| Windows PowerShell | 5.1+ | ✅ Tested |
| Docker Desktop | Latest | ✅ Recommended |

---

## Monitoring & Alerts

### Tools
- **Docker Scout**: Automated vulnerability scanning
- **Dependabot** (GitHub): Automatic dependency alerts
- **PyPI**: Release tracking

### Current Scan Status
- Last scan: 2025-01-15
- High severity: ✅ 0
- Medium severity: ✅ 0 (after updates)
- Low severity: ⚠️ 49 (system libraries in base image)

---

## Future Considerations

- Monitor for Python 3.13 compatibility (currently 3.12)
- Consider lightweight alternatives if base image grows
- Track Starlette changelog for critical updates
- Prepare for FastAPI 1.0 release (if scheduled)
