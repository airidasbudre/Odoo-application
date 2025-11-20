# Local Kubernetes Development with Minikube

This guide helps you run the Odoo application on your local machine using Minikube.

## Prerequisites

- Docker installed and running
- kubectl installed
- Minikube installed
- At least 4GB RAM available for Minikube
- At least 20GB free disk space

## Quick Start

```bash
# Start Minikube with sufficient resources
./k8s/local/start-minikube.sh

# Deploy Odoo application
./k8s/local/deploy-local.sh

# Access the application
minikube service odoo-service -n odoo-production
```

## What's Different from Cloud Deployment?

1. **No LoadBalancer**: Uses NodePort instead
2. **Local Storage**: Uses hostPath instead of cloud PVCs
3. **Smaller Resources**: Reduced CPU/memory limits for local machine
4. **No Ingress Controller**: Direct service access via NodePort
5. **Simplified Monitoring**: Optional lightweight monitoring

## Step-by-Step Setup

### 1. Start Minikube

```bash
# Start with 4GB RAM and 2 CPUs (adjust based on your system)
minikube start --cpus=2 --memory=4096 --driver=docker

# Enable required addons
minikube addons enable metrics-server
minikube addons enable storage-provisioner
```

### 2. Configure Secrets

Edit the secret values before deploying:

```bash
# PostgreSQL password
kubectl create namespace odoo-production
kubectl create secret generic postgresql-secret \
  --from-literal=postgresql-password=your-password \
  -n odoo-production

# Alertmanager secrets (optional, for monitoring)
kubectl create secret generic alertmanager-secret \
  --from-literal=telegram-bot-token=YOUR_TOKEN \
  --from-literal=telegram-chat-id=YOUR_CHAT_ID \
  -n odoo-production
```

### 3. Deploy Application

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/local/postgresql-local.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgresql -n odoo-production --timeout=300s

# Deploy Odoo
kubectl apply -f k8s/local/odoo-local.yaml

# Wait for Odoo to be ready
kubectl wait --for=condition=ready pod -l app=odoo -n odoo-production --timeout=300s
```

### 4. Access the Application

```bash
# Get the Odoo URL
minikube service odoo-service -n odoo-production --url

# Or open in browser directly
minikube service odoo-service -n odoo-production
```

### 5. Access Monitoring (Optional)

```bash
# Deploy monitoring stack
kubectl apply -f k8s/local/monitoring-local.yaml

# Access Grafana
minikube service grafana-service -n odoo-production

# Access Prometheus
minikube service prometheus-service -n odoo-production
```

## Managing Your Cluster

### Check Status
```bash
# Cluster status
minikube status

# Pod status
kubectl get pods -n odoo-production

# Service URLs
minikube service list -n odoo-production
```

### View Logs
```bash
# Odoo logs
kubectl logs -f deployment/odoo -n odoo-production

# PostgreSQL logs
kubectl logs -f deployment/postgresql -n odoo-production
```

### Restart Services
```bash
# Restart Odoo
kubectl rollout restart deployment/odoo -n odoo-production

# Restart PostgreSQL
kubectl rollout restart deployment/postgresql -n odoo-production
```

### Stop and Clean Up
```bash
# Stop Minikube (preserves data)
minikube stop

# Delete everything (clean slate)
minikube delete

# Delete just the application
kubectl delete namespace odoo-production
```

## Troubleshooting

### Issue: Pods stuck in Pending
```bash
# Check events
kubectl describe pod <pod-name> -n odoo-production

# Check resources
kubectl top nodes
```

### Issue: Can't access services
```bash
# Make sure Minikube is running
minikube status

# Check service status
kubectl get svc -n odoo-production

# Try port-forward as alternative
kubectl port-forward svc/odoo-service 8069:8069 -n odoo-production
```

### Issue: Out of resources
```bash
# Restart with more resources
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Issue: Docker driver issues
```bash
# Make sure Docker is running
docker ps

# Try alternative driver
minikube start --driver=virtualbox  # or --driver=hyperv on Windows
```

## Resource Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB disk space

**Recommended:**
- 4 CPU cores
- 8GB RAM
- 40GB disk space

## Data Persistence

Data is stored in Minikube's VM:
- PostgreSQL data: `/data/postgresql`
- Odoo data: `/data/odoo`

**Important:** Data persists between `minikube stop/start` but is lost on `minikube delete`.

To backup data:
```bash
# Backup PostgreSQL
kubectl exec -n odoo-production deployment/postgresql -- \
  pg_dump -U odoo odoo > backup.sql

# Restore PostgreSQL
cat backup.sql | kubectl exec -i -n odoo-production deployment/postgresql -- \
  psql -U odoo odoo
```

## Next Steps

1. **Learn Kubernetes**: Experiment with scaling, rolling updates, etc.
2. **Add Features**: Try adding new services or modifying deployments
3. **Deploy to Cloud**: Use the same manifests in `k8s/base/` with minor adjustments
4. **CI/CD**: Test your CI/CD pipeline locally before cloud deployment

## Tips for Learning

- Use `kubectl get all -n odoo-production` to see everything
- Use `kubectl describe` to understand resource configurations
- Use `kubectl logs` to debug issues
- Use `kubectl exec` to access containers
- Dashboard: `minikube dashboard` for a visual interface

## Differences from Production

This local setup is simplified for learning:
- Single-node cluster (production uses multiple nodes)
- NodePort services (production uses LoadBalancer/Ingress)
- Local storage (production uses cloud PVCs)
- Reduced resources (production needs more CPU/RAM)
- No SSL/TLS (production requires HTTPS)
- No high availability (production has replicas)
