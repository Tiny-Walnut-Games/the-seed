# Kubernetes Deployment for Warbler CDA

This directory contains Kubernetes manifests to deploy Warbler CDA on a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (kubectl configured)
- Docker registry access (if using external registry)
- NGINX Ingress Controller (for external access)

## Components

- `namespace.yaml`: Creates the `warbler-cda` namespace
- `configmap.yaml`: Configuration settings (environment variables)
- `pvc.yaml`: Persistent volume claim for data storage
- `deployment.yaml`: Application deployment with health checks and resource limits
- `service.yaml`: Service to expose the application within the cluster
- `ingress.yaml`: Ingress for external access (requires NGINX Ingress Controller)

## Deployment Instructions

### 1. Build and Push Docker Image

First, build your Docker image and push it to a registry:

```bash
# Build the image
docker build -t your-registry/warbler-cda:latest .

# Push to registry
docker push your-registry/warbler-cda:latest
```

Update the image reference in `deployment.yaml` to point to your registry.

### 2. Deploy to Kubernetes

Apply all manifests:

```bash
kubectl apply -f k8s/
```

Or deploy in order:

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

### 3. Check Deployment Status

```bash
# Check pod status
kubectl get pods -n warbler-cda

# Check service
kubectl get svc -n warbler-cda

# Check ingress
kubectl get ingress -n warbler-cda

# View logs
kubectl logs -f deployment/warbler-cda -n warbler-cda
```

### 4. Access the Application

- **Internal cluster access**: `http://warbler-cda-service.warbler-cda.svc.cluster.local`
- **External access**: Configure DNS to point to your ingress controller IP for `warbler-cda.local`

## Health Checks

The deployment includes:
- **Liveness Probe**: `/health` endpoint (restarts pod if unhealthy)
- **Readiness Probe**: `/health` endpoint (removes pod from service if unhealthy)

## Scaling

To scale the deployment:

```bash
kubectl scale deployment warbler-cda --replicas=3 -n warbler-cda
```

## Configuration

### Environment Variables

Modify `configmap.yaml` to change:
- `FRACTALSTAT_TESTING`: Enable/disable testing mode
- Other environment variables as needed

### Resources

Adjust CPU/memory requests and limits in `deployment.yaml` based on your cluster resources.

### Storage

The PVC requests 10Gi by default. Adjust in `pvc.yaml` if needed.

## Troubleshooting

### Common Issues

1. **Pod won't start**: Check image name/tag and registry access
2. **No external access**: Ensure Ingress Controller is installed and configured
3. **Health checks failing**: Verify the `/health` endpoint is responding

### Debug Commands

```bash
# Describe pod for detailed status
kubectl describe pod -n warbler-cda

# Check events
kubectl get events -n warbler-cda

# Port-forward for local testing
kubectl port-forward svc/warbler-cda-service 8000:80 -n warbler-cda
```

## Notes

- The deployment uses a persistent volume for data persistence
- Health checks are configured for the FastAPI `/health` endpoint
- Resource limits are set for a basic deployment - adjust for your needs
- The Ingress uses `warbler-cda.local` as default host - change for production
