# 🛡️ Security Scan Setup Guide

This guide explains how to run security scans locally and in CI/CD pipelines.

## Problem: System Dependencies for lxml

The security scanning tools require `cyclonedx-bom`, which depends on `lxml`. The `lxml` library requires system-level C libraries to compile:
- **Linux/Mac**: `libxml2-dev` and `libxslt1-dev`
- **Windows**: Requires Visual C++ build tools or pre-compiled wheels

## ✅ Solutions

### Option 1: Docker (Recommended for All Platforms) 🐳

**Best for:** Windows users, consistent environments, CI/CD pipelines

Docker handles all system dependencies automatically and provides a consistent environment across Windows, Mac, and Linux.

#### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running

#### Run Full Security Scan
```bash
# Windows (PowerShell)
.\scripts\run-security-scan-local.ps1 -ScanType full

# Linux/Mac
./scripts/run-security-scan-local.sh full
```

#### Run Specific Scans
```bash
# Available scan types: bandit, pip-audit, safety, trufflehog, semgrep

# PowerShell
.\scripts\run-security-scan-local.ps1 -ScanType bandit

# Bash
./scripts/run-security-scan-local.sh pip-audit
```

#### Manual Docker Command
```bash
# Build the security image
docker build -f Dockerfile.security -t twg-security-scanner:latest .

# Run a specific scan
docker run --rm \
  -v "$(pwd):/code" \
  -v "$(pwd)/security-results:/results" \
  twg-security-scanner:latest \
  bash -c "bandit -r /code/scripts -f json -o /results/bandit-results.json"
```

Results will be saved to `./security-results/` directory.

---

### Option 2: Ubuntu/Debian (Native Installation) 🐧

**Best for:** Ubuntu/Debian developers, native performance

Install system dependencies, then Python packages:

```bash
# 1. Install system libraries
sudo apt-get update
sudo apt-get install -y libxml2-dev libxslt1-dev python3-dev build-essential

# 2. Install Python security tools
pip install -r scripts/security-requirements.txt

# 3. Verify installation
pip check
```

Then run individual tools:
```bash
bandit -r scripts/ src/
pip-audit
safety check
trufflehog filesystem .
semgrep --config=auto --json .
```

---

### Option 3: Fedora/RHEL (Native Installation) 🔴

**Best for:** Fedora/RHEL developers, native performance

```bash
# 1. Install system libraries
sudo dnf install -y libxml2-devel libxslt-devel python3-devel

# 2. Install Python security tools
pip install -r scripts/security-requirements.txt

# 3. Verify installation
pip check
```

---

### Option 4: macOS (Native Installation) 🍎

**Best for:** Mac developers with Homebrew

```bash
# 1. Install system libraries using Homebrew
brew install libxml2 libxslt

# 2. Set environment variables
export CFLAGS="-I$(brew --prefix libxml2)/include -I$(brew --prefix libxslt)/include"
export LDFLAGS="-L$(brew --prefix libxml2)/lib -L$(brew --prefix libxslt)/lib"

# 3. Install Python security tools
pip install -r scripts/security-requirements.txt

# 4. Verify installation
pip check
```

---

### Option 5: Windows with Visual C++ Build Tools 🪟

**Best for:** Windows developers who prefer native installation

#### Prerequisites
- Visual C++ Build Tools or Visual Studio Community Edition
- Python 3.x installed

#### Steps
```powershell
# 1. Download and install Visual C++ Build Tools from:
#    https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 2. Install Python security tools
pip install -r scripts/security-requirements.txt

# 3. Verify installation
pip check
```

Alternatively, use pre-compiled wheels:
```powershell
# Some packages provide pre-compiled wheels for Windows
pip install --only-binary :all: -r scripts/security-requirements.txt
```

---

## 📋 Available Security Tools

### 1. **Bandit** - Python Security Linter
Detects common security issues in Python code.
```bash
bandit -r scripts/ src/ -f json -o bandit-results.json
```

### 2. **pip-audit** - Dependency Vulnerability Scanner
Scans Python dependencies for known vulnerabilities.
```bash
pip-audit --format json --output pip-audit-results.json
```

### 3. **Safety** - Security Advisory Database
Checks installed packages against a vulnerability database.
```bash
safety check --json --output safety-results.json
```

### 4. **TruffleHog** - Secret Detection
Scans for accidentally committed secrets using entropy analysis.
```bash
trufflehog filesystem . --json
```

### 5. **Semgrep** - Multi-Language Pattern Scanner
Detects security issues using customizable rules.
```bash
semgrep --config=auto --json --output semgrep-results.json .
```

---

## 🔄 CI/CD Pipeline Integration

The GitHub Actions workflow (`.github/workflows/overlord-sentinel-security.yml`) automatically:
1. ✅ Installs system dependencies (Ubuntu runner)
2. ✅ Installs Python security tools from `scripts/security-requirements.txt`
3. ✅ Runs all security scans
4. ✅ Converts results to SARIF format for GitHub Security tab

**No manual action required** - just push to main or open a PR!

---

## 🧪 Troubleshooting

### Error: "libxml2-dev not found"
**Solution**: Use Docker (Option 1) or install system libraries (Options 2-4)

### Error: "lxml failed to build"
**Solution**: Ensure system development libraries are installed before pip install

### Docker build fails
```bash
# Try clearing Docker cache
docker system prune -a
docker build -f Dockerfile.security -t twg-security-scanner:latest .
```

### Results directory permission denied
```bash
# On Linux/Mac, ensure directory permissions
sudo chown -R $USER security-results
chmod -R 755 security-results
```

---

## 📊 Interpreting Results

Security scan results are saved as:
- `bandit-results.json` - Python code security issues
- `pip-audit-results.json` - Vulnerable dependencies
- `safety-results.json` - Advisory database matches
- `trufflehog-results.json` - Detected secrets
- `semgrep-results.json` - Pattern-based security issues

Results are also converted to **SARIF format** for GitHub Security dashboard integration.

---

## 🚀 Quick Start

### For Windows Users:
```powershell
# Using Docker (easiest)
.\scripts\run-security-scan-local.ps1 -ScanType full
```

### For Linux/Mac Users:
```bash
# Using Docker
./scripts/run-security-scan-local.sh full

# Or native installation (Ubuntu)
sudo apt-get install -y libxml2-dev libxslt1-dev python3-dev
pip install -r scripts/security-requirements.txt
bandit -r scripts/ src/
```

---

## 📚 References

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [pip-audit GitHub](https://github.com/pypa/pip-audit)
- [Safety Checks](https://docs.safetycli.com/)
- [TruffleHog GitHub](https://github.com/trufflesecurity/truffleHog)
- [Semgrep Documentation](https://semgrep.dev/)

---

## ✅ Verification Checklist

- [ ] Docker Desktop installed (for Docker approach)
- [ ] System libraries installed (for native approach)
- [ ] `scripts/security-requirements.txt` available
- [ ] Run test scan: `pip-audit` or `bandit -r scripts/`
- [ ] Results saved successfully
- [ ] No installation errors

---

**Last Updated**: November 2024