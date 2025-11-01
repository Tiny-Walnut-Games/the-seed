# 🛡️ Security Scanning - Quick Reference

## 🚀 TL;DR - Run Security Scans Now

### Windows
```powershell
# Using Docker (EASIEST - no setup required except Docker Desktop)
.\scripts\run-security-scan-local.ps1 -ScanType full
```

### Linux/Mac
```bash
# Using Docker (EASIEST - no setup required except Docker)
./scripts/run-security-scan-local.sh full

# Or native (Ubuntu/Debian only)
sudo apt-get install -y libxml2-dev libxslt1-dev python3-dev
pip install -r scripts/security-requirements.txt
bandit -r scripts/ src/
```

---

## 📋 What Each Tool Does

| Tool | Purpose | Command |
|------|---------|---------|
| **Bandit** | Python code security issues | `bandit -r scripts/` |
| **pip-audit** | Vulnerable dependencies | `pip-audit` |
| **Safety** | CVE database checks | `safety check` |
| **TruffleHog** | Detect leaked secrets | `trufflehog filesystem .` |
| **Semgrep** | Pattern-based code scanning | `semgrep --config=auto .` |

---

## 🔧 Setup by Platform

### Quick Setup (All Platforms)
**Option 1: Docker** ✅ RECOMMENDED
- Install Docker Desktop: https://www.docker.com/
- Run: `./scripts/run-security-scan-local.ps1 full` (Windows) or `./scripts/run-security-scan-local.sh full` (Linux/Mac)

### Native Setup (Optional)

**Ubuntu/Debian**
```bash
sudo apt-get install -y libxml2-dev libxslt1-dev python3-dev
pip install -r scripts/security-requirements.txt
```

**Fedora/RHEL**
```bash
sudo dnf install -y libxml2-devel libxslt-devel python3-devel
pip install -r scripts/security-requirements.txt
```

**macOS**
```bash
brew install libxml2 libxslt
export CFLAGS="-I$(brew --prefix libxml2)/include"
export LDFLAGS="-L$(brew --prefix libxml2)/lib"
pip install -r scripts/security-requirements.txt
```

**Windows (Visual C++ Required)**
- Install: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Run: `pip install -r scripts/security-requirements.txt`

---

## 🎯 Common Tasks

### Run Full Scan
```bash
# Docker (all platforms)
.\scripts\run-security-scan-local.ps1 -ScanType full

# Direct (Linux/Mac with native install)
bandit -r scripts/ && pip-audit && safety check && trufflehog filesystem . && semgrep --config=auto .
```

### Run Specific Tool
```bash
# Docker
.\scripts\run-security-scan-local.ps1 -ScanType bandit

# Direct
bandit -r scripts/ -f json -o bandit-results.json
```

### Check Dependency Vulnerabilities
```bash
pip-audit --format json --output pip-audit-results.json
```

### Scan for Secrets
```bash
trufflehog filesystem . --json > trufflehog-results.json
```

### Verify Installation
```bash
pip check
```

---

## ❌ Troubleshooting

| Error | Solution |
|-------|----------|
| `libxml2-dev not found` | Use Docker or install system libraries |
| `lxml failed to build` | Install dev libraries before pip install |
| `Docker not found` | Install Docker Desktop |
| `Permission denied` on results | Run `sudo chown -R $USER security-results` |

---

## 📊 Results

Scan results saved to: `./security-results/`
- `bandit-results.json` - Code security issues
- `pip-audit-results.json` - Vulnerable packages
- `safety-results.json` - CVE matches
- `trufflehog-results.json` - Detected secrets
- `semgrep-results.json` - Pattern-based issues

---

## 🔄 CI/CD

**GitHub Actions** runs automatically on:
- Push to `main`
- Pull requests
- Weekly schedule (Sundays at midnight)
- Manual trigger via workflow_dispatch

No setup needed - workflow handles everything!

---

## 📚 Full Documentation

See `SECURITY_SCAN_SETUP.md` for complete setup guide

---

**Pro Tip**: Use Docker for consistency across all platforms and CI/CD environments! 🐳