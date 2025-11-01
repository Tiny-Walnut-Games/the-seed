#!/bin/bash
# Bash script to run security scans locally using Docker
# Usage: ./scripts/run-security-scan-local.sh [scan_type]

set -e

SCAN_TYPE=${1:-full}  # full, bandit, pip-audit, semgrep, trufflehog
SCAN_PATH=${2:-.}

echo "🛡️  Security Scan Runner (Local Docker)"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "   Install from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"
echo ""

# Build security Docker image
echo "🔨 Building security scanning image..."
IMAGE_TAG="twg-security-scanner:latest"

docker build -f Dockerfile.security -t $IMAGE_TAG . || {
    echo "❌ Docker build failed"
    exit 1
}

echo "✅ Image built successfully"
echo ""

# Define scan commands
declare -A SCAN_COMMANDS
SCAN_COMMANDS[bandit]="bandit -r scripts/ src/ packages/ -f json -o /results/bandit-results.json"
SCAN_COMMANDS[pip-audit]="pip-audit --format json --output /results/pip-audit-results.json"
SCAN_COMMANDS[safety]="safety check --json --output /results/safety-results.json"
SCAN_COMMANDS[trufflehog]="trufflehog filesystem /code --json > /results/trufflehog-results.json"
SCAN_COMMANDS[semgrep]="semgrep --config=auto --json --output=/results/semgrep-results.json /code/scripts /code/packages"
SCAN_COMMANDS[full]="bash -c 'echo Running full security scan... && (bandit -r scripts/ src/ packages/ -f json -o /results/bandit.json 2>/dev/null || true) && (pip-audit --format json --output /results/pip-audit.json 2>/dev/null || true) && (safety check --json --output /results/safety.json 2>/dev/null || true) && (trufflehog filesystem /code --json > /results/trufflehog.json 2>/dev/null || true) && (semgrep --config=auto --json --output=/results/semgrep.json /code 2>/dev/null || true) && echo ✅ Full scan complete'"

# Get command or show available options
if [[ -z "${SCAN_COMMANDS[$SCAN_TYPE]}" ]]; then
    echo "❌ Unknown scan type: $SCAN_TYPE"
    echo "Available options: $(IFS=', '; echo "${!SCAN_COMMANDS[@]}")"
    exit 1
fi

COMMAND="${SCAN_COMMANDS[$SCAN_TYPE]}"

# Create results directory
RESULTS_DIR="$(pwd)/security-results"
mkdir -p "$RESULTS_DIR"

echo "🔍 Running $SCAN_TYPE scan..."
echo ""

# Run container
docker run --rm \
    -v "$(pwd):/code" \
    -v "$RESULTS_DIR:/results" \
    $IMAGE_TAG \
    bash -c "$COMMAND"

SCAN_EXIT_CODE=$?

echo ""
if [ $SCAN_EXIT_CODE -eq 0 ]; then
    echo "✅ Scan completed successfully"
else
    echo "⚠️  Scan completed with warnings or non-critical issues"
fi

echo "📁 Results saved to: $RESULTS_DIR"
echo ""
echo "📊 Result files:"
ls -lh "$RESULTS_DIR" | tail -n +2 | awk '{print "   - " $9}'

echo ""
echo "🛡️  Security scan runner finished"