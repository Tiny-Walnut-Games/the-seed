#!/bin/bash

# Demo: Build Docker image and deploy to Docker Desktop Kubernetes

set -e

echo "🐳🔧 Docker Desktop + Kubernetes Demo for Warbler CDA"
echo "======================================================"
echo ""

# Check Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if kubectl is available and connected to Docker Desktop Kubernetes
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl is not connected to Kubernetes cluster."
    echo "   Please enable Kubernetes in Docker Desktop (Settings → Kubernetes → Enable Kubernetes)"
    exit 1
fi

echo "✅ Docker and Kubernetes are running!"

# Step 1: Build the Docker image
echo ""
echo "🔨 Step 1: Building Docker image (with full dependencies for API service)..."

# Handle directory navigation smartly
ORIGINAL_DIR=$(pwd)
PROJECT_DIR="$ORIGINAL_DIR"
if [[ "$ORIGINAL_DIR" == *"/k8s" ]]; then
    PROJECT_DIR="${ORIGINAL_DIR%/k8s}"
fi

echo "   Building from directory: $PROJECT_DIR"
cd "$PROJECT_DIR"
docker build -t warbler-cda:latest .
cd "$ORIGINAL_DIR"
echo "✅ Image built successfully!"

# Step 2: Deploy to Kubernetes
echo ""
echo "🚀 Step 2: Deploying to Kubernetes..."

# Debug: Check if deploy.sh exists and is executable
if [[ ! -f "deploy.sh" ]] || [[ ! -x "deploy.sh" ]]; then
    echo "❌ deploy.sh not found or not executable"
    exit 1
fi

echo "   Running deploy.sh..."
if ! ./deploy.sh; then
    echo "❌ Deployment failed! Checking logs..."
    echo ""
    echo "🔍 Recent events in default namespace:"
    kubectl get events --sort-by=.metadata.creationTimestamp | tail -10
    echo ""
    echo "🔍 Check pod status if deployment partially succeeded:"
    kubectl get pods -n warbler-cda 2>/dev/null || echo "   Namespace not yet created"

    # Don't exit - let user troubleshoot
    echo ""
    echo "⚠️  Deployment had issues but continuing with troubleshooting steps..."
fi

# Step 3: Wait for deployment and show access info
echo ""
echo "⏳ Step 3: Setting up port forwarding..."
echo "   (This will make your app accessible at http://localhost:8001)"
echo ""
echo "   In a new terminal, run:"
echo "   kubectl port-forward svc/warbler-cda-service 8001:80 -n warbler-cda"
echo ""
echo "   Then visit: http://localhost:8001/health"
echo ""
echo "📊 Current status:"
kubectl get pods -n warbler-cda
kubectl get svc -n warbler-cda
echo ""
echo "🔍 View logs:"
echo "   kubectl logs -f deployment/warbler-cda -n warbler-cda"
echo ""
echo "🧹 Cleanup when done:"
echo "   kubectl delete -f k8s/"
echo ""
echo "🎉 Demo complete! Your Warbler CDA is now running on Kubernetes!"
