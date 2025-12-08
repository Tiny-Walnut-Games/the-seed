#!/bin/bash

# Warbler CDA Kubernetes Deployment Script

set -e

echo "🚀 Deploying Warbler CDA to Kubernetes..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed or not in PATH${NC}"
    exit 1
fi

# Check kubectl connection
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Connected to Kubernetes cluster${NC}"

# Apply manifests in order
echo "📦 Applying Kubernetes manifests..."

# Create namespace first
echo "  - Creating namespace..."
kubectl apply -f namespace.yaml

# Apply other resources with individual error checking
echo "  - Applying ConfigMap..."
if ! kubectl apply -f configmap.yaml; then
    echo "❌ Failed to apply ConfigMap"
    exit 1
fi

echo "  - Creating PersistentVolumeClaim..."
if ! kubectl apply -f pvc.yaml; then
    echo "❌ Failed to apply PVC"
    exit 1
fi

echo "  - Deploying application..."
if ! kubectl apply -f deployment.yaml; then
    echo "❌ Failed to deploy application"
    exit 1
fi

echo "  - Creating Service..."
if ! kubectl apply -f service.yaml; then
    echo "❌ Failed to create service"
    exit 1
fi

echo "  - Creating Ingress..."
if ! kubectl apply -f ingress.yaml; then
    echo "⚠️  Failed to create ingress (this is optional)"
    # Don't exit for ingress failure - it's not critical
fi

echo -e "${GREEN}✅ All manifests applied successfully!${NC}"

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/warbler-cda -n warbler-cda

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment is ready!${NC}"

    # Show status
    echo ""
    echo "📊 Deployment Status:"
    kubectl get pods -n warbler-cda
    echo ""
    kubectl get svc -n warbler-cda
    echo ""
    kubectl get ingress -n warbler-cda

    echo ""
    echo -e "${GREEN}🎉 Warbler CDA has been deployed successfully!${NC}"
    echo ""
    echo "📖 Access your application:"
    echo "  - Internal: http://warbler-cda-service.warbler-cda.svc.cluster.local"
    echo "  - External: Configure DNS for 'warbler-cda.local' or use port-forward:"
    echo "    kubectl port-forward svc/warbler-cda-service 8000:80 -n warbler-cda"
    echo ""
    echo "🔍 View logs:"
    echo "  kubectl logs -f deployment/warbler-cda -n warbler-cda"

else
    echo -e "${RED}❌ Deployment failed or timed out${NC}"
    echo "🔍 Check pod status:"
    kubectl get pods -n warbler-cda
    echo ""
    echo "🔍 Check pod logs:"
    kubectl logs deployment/warbler-cda -n warbler-cda
    exit 1
fi
