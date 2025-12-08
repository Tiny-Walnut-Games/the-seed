# Docker Desktop + Kubernetes Setup for Warbler CDA

Since you're using Docker, you can test the Kubernetes deployment locally using Docker Desktop's built-in Kubernetes feature.

## Prerequisites

1. **Enable Kubernetes in Docker Desktop:**
   - Open Docker Desktop
   - Go to Settings → Kubernetes
   - Check "Enable Kubernetes"
   - Apply & Restart

2. **Verify Kubernetes is running:**
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

## Quick Start with Docker Desktop K8s

### Option 1: Use the deployment script

```bash
cd k8s
./deploy.sh
```

### Option 2: Manual deployment

1. **Build and load image directly to Docker Desktop:**
```bash
# Build the image
docker build -t warbler-cda:latest .

# The image is now available to K8s since Docker Desktop shares images
```

2. **Deploy to local Kubernetes:**
```bash
cd k8s
kubectl apply -f .
```

3. **Check deployment:**
```bash
kubectl get pods -n warbler-cda
kubectl get svc -n warbler-cda
kubectl get ingress -n warbler-cda
```

4. **Access the application:**

**Option A: Use port-forwarding (recommended for development)**
```bash
kubectl port-forward svc/warbler-cda-service 8001:80 -n warbler-cda
```
Then visit: http://localhost:8001/health

**Option B: Access via Ingress (requires ingress controller)**

First, enable ingress in Docker Desktop and install NGINX Ingress:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

Then update your ingress.yaml to use a local domain or use port forwarding.

## Compare: Docker Compose vs Kubernetes

| Feature | Docker Compose | Kubernetes |
|---------|---------------|------------|
| Scaling | Manual replica adjustment | Auto-scaling, rolling updates |
| Networking | Simple service discovery | Complex service mesh |
| Storage | Local volumes | Persistent volumes, storage classes |
| Health Checks | Basic | Liveness/readiness probes |
| Resource Limits | Basic | Detailed QoS, limits/requests |
| Environment | Single host | Multi-node clusters |

## Local Development Workflow

1. **Develop with Docker Compose** (faster iteration):
   ```bash
   docker-compose up --build
   ```

2. **Test production deployment with Kubernetes:**
   ```bash
   cd k8s && ./deploy.sh
   kubectl port-forward svc/warbler-cda-service 8001:80 -n warbler-cda
   ```

3. **Debug if needed:**
   ```bash
   kubectl logs -f deployment/warbler-cda -n warbler-cda
   kubectl describe pod -n warbler-cda
   ```

## Benefits of Docker Desktop Kubernetes

- **Same deployment as production** - test your exact K8s manifests
- **Resource isolation** - proper containerization like production
- **Networking simulation** - test service communication
- **Storage testing** - validate PVC behavior
- **Health check validation** - ensure probes work correctly

## Troubleshooting Docker Desktop K8s

**Common issues:**

1. **"ImagePullBackOff" error:**
   - Make sure you built the image: `docker build -t warbler-cda:latest .`
   - Update deployment.yaml image to `warbler-cda:latest`

2. **PVC pending:**
   - Docker Desktop K8s has storage classes, but storage might not provision immediately
   - Check: `kubectl get pvc -n warbler-cda`
   - You can use hostPath storage for local testing

3. **Ingress not working:**
   - Install ingress controller first
   - Use port-forwarding for simpler local access

4. **Resource constraints:**
   - Docker Desktop K8s shares resources with Docker
   - Reduce resource requests in deployment.yaml if needed

## Converting Docker Compose to Kubernetes

Your `docker-compose.yml` has been converted to K8s with these mappings:

| Docker Compose | Kubernetes Equivalent |
|---------------|----------------------|
| `image: .` | `deployment.yaml` with image build step |
| `ports: - "8001:8000"` | `service.yaml` + `ingress.yaml` |
| `environment:` | `configmap.yaml` + envFrom |
| `volumes: ./data:/app/data` | `pvc.yaml` + volumeMounts |
| `restart: unless-stopped` | Deployment with replicas |

The Kubernetes setup provides production-grade features while maintaining the same application behavior as your Docker Compose setup.
