#!/bin/bash
# EXP-09 Quick Start Script
# Simplified setup and operation of the CLI API service

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SEED_ENGINE="$PROJECT_ROOT/seed/engine"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  EXP-09 CLI API Service - Quick Start                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo

# Parse command
COMMAND=${1:-help}

case "$COMMAND" in
  
  "help"|"--help"|"-h")
    echo "Usage: ./exp09-quickstart.sh [COMMAND]"
    echo
    echo "Commands:"
    echo "  setup              Install dependencies and prepare environment"
    echo "  docker-build       Build Docker image"
    echo "  docker-run         Run container (single instance)"
    echo "  docker-compose     Start with docker-compose"
    echo "  cli-health         Check service health"
    echo "  cli-query          Run a single test query"
    echo "  cli-bulk           Run bulk concurrent queries"
    echo "  cli-stress-test    Run EXP-10 stress test"
    echo "  clean              Remove containers and build artifacts"
    echo "  help               Show this help message"
    echo
    echo "Examples:"
    echo "  ./exp09-quickstart.sh docker-compose    # Start service"
    echo "  ./exp09-quickstart.sh cli-health         # Check health"
    echo "  ./exp09-quickstart.sh cli-stress-test    # Run EXP-10 test"
    ;;

  "setup")
    echo "Setting up EXP-09 environment..."
    echo
    
    # Check Python
    echo "✓ Checking Python version..."
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo "  Found Python $python_version"
    
    # Install dependencies
    echo "✓ Installing Python dependencies..."
    pip install -q -r "$SEED_ENGINE/requirements-exp09.txt"
    echo "  Dependencies installed"
    
    echo
    echo "✅ Setup complete! Run commands:"
    echo "   ./exp09-quickstart.sh docker-compose   (recommended)"
    echo "   or"
    echo "   python $SEED_ENGINE/exp09_api_service.py"
    ;;

  "docker-build")
    echo "Building Docker image..."
    cd "$SEED_ENGINE"
    docker build -t exp09-api:latest .
    echo "✅ Image built: exp09-api:latest"
    ;;

  "docker-run")
    echo "Starting container..."
    docker run --rm -it -p 8000:8000 \
      --name exp09-api \
      -v "$SEED_ENGINE:/app" \
      exp09-api:latest
    ;;

  "docker-compose")
    echo "Starting with docker-compose..."
    cd "$SEED_ENGINE"
    
    if ! command -v docker-compose &> /dev/null; then
      echo "❌ docker-compose not found. Install Docker Desktop."
      exit 1
    fi
    
    docker-compose up -d
    
    echo
    sleep 2
    echo "✅ Services started!"
    echo
    docker-compose ps
    echo
    echo "Running health check..."
    sleep 2
    python "$SEED_ENGINE/exp09_cli.py" health
    ;;

  "cli-health")
    echo "Checking service health..."
    python "$SEED_ENGINE/exp09_cli.py" health
    ;;

  "cli-query")
    echo "Running single query..."
    python "$SEED_ENGINE/exp09_cli.py" query \
      --query-id "quickstart_$(date +%s)" \
      --semantic "find wisdom about growth" \
      --hybrid
    ;;

  "cli-bulk")
    echo "Running bulk concurrent queries..."
    python "$SEED_ENGINE/exp09_cli.py" bulk \
      --num-queries 5 \
      --concurrency 3 \
      --hybrid
    ;;

  "cli-stress-test")
    OUTPUT_FILE="exp09_stress_test_$(date +%Y%m%d_%H%M%S).json"
    echo "Running EXP-10 stress test..."
    echo "Output will be saved to: $OUTPUT_FILE"
    echo
    
    python "$SEED_ENGINE/exp09_cli.py" stress-test \
      --num-scenarios 3 \
      --queries-per-scenario 10 \
      --use-hybrid \
      --output-file "$OUTPUT_FILE"
    
    echo
    if [ -f "$OUTPUT_FILE" ]; then
      echo "✅ Results saved to $OUTPUT_FILE"
      echo
      echo "Summary:"
      python -c "
import json
with open('$OUTPUT_FILE') as f:
    data = json.load(f)
    print(f\"Average Coherence: {data.get('average_coherence', 0):.3f}\")
    print(f\"Status: {'PASS ✓' if data.get('average_coherence', 0) > 0.7 else 'FAIL ✗'}\")
"
    fi
    ;;

  "clean")
    echo "Cleaning up..."
    
    if command -v docker-compose &> /dev/null; then
      echo "Stopping docker-compose services..."
      cd "$SEED_ENGINE" 2>/dev/null || true
      docker-compose down 2>/dev/null || true
    fi
    
    echo "Removing containers..."
    docker rm -f exp09-api 2>/dev/null || true
    
    echo "✅ Cleanup complete"
    ;;

  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run './exp09-quickstart.sh help' for usage"
    exit 1
    ;;

esac