# Docker Compose to Kubernetes Migration Guide

## Overview

This guide will help you migrate your existing Docker Compose Odoo stack to Kubernetes.

## What Changes?

### Before (Docker Compose)
```bash
docker-compose up -d
docker ps
docker logs odoo-app
```

### After (Kubernetes)
```bash
kubectl apply -f k8s/
kubectl get pods -n odoo-production
kubectl logs -f deployment/odoo -n odoo-production
```

## Architecture Comparison

| Component | Docker Compose | Kubernetes |
|-----------|---------------|------------|
| **Odoo** | Single container | Deployment with 1+ replicas |
| **PostgreSQL** | Single container | StatefulSet-like Deployment |
| **Prometheus** | Container | Deployment + ConfigMap |
| **Grafana** | Container | Deployment + Secret |
| **Alertmanager** | Container | Deployment + ConfigMap |
| **Storage** | Docker volumes | PersistentVolumeClaims |
| **Networking** | Docker network | Services + DNS |
| **Load Balancing** | Nginx | Ingress Controller |
| **Secrets** | .env files | Kubernetes Secrets |

## Migration Steps

### Step 1: Backup Your Data

**Backup PostgreSQL:**
```bash
docker exec odoo-db pg_dump -U odoo postgres > odoo-backup.sql
```

**Backup Odoo files:**
```bash
docker cp odoo-app:/var/lib/odoo ./odoo-backup
```

### Step 2: Stop Docker Compose Stack

```bash
docker-compose down
# Keep volumes for safety
# docker-compose down -v  # Only if you want to delete volumes
```

### Step 3: Setup Kubernetes Cluster

**Option A: Local (Minikube)**
```bash
minikube start --cpus=4 --memory=8192
```

**Option B: Local (K3s)**
```bash
curl -sfL https://get.k3s.io | sh -
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER ~/.kube/config
```

**Option C: Cloud (AWS EKS)**
```bash
eksctl create cluster \
  --name odoo-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4
```

### Step 4: Update Configuration

**Update storage class in PVC files:**
```bash
# Find your storage class
kubectl get storageclass

# Update all PVC files
sed -i 's/storageClassName: gp2/storageClassName: YOUR_STORAGE_CLASS/g' k8s/base/*-pvc.yaml
sed -i 's/storageClassName: gp2/storageClassName: YOUR_STORAGE_CLASS/g' k8s/monitoring/*-pvc.yaml
```

**Update secrets:**
```bash
# Edit PostgreSQL credentials
vi k8s/base/postgresql-secret.yaml

# Edit Grafana credentials
vi k8s/monitoring/grafana-secret.yaml

# Edit Telegram bot token
vi k8s/monitoring/alertmanager-configmap.yaml
```

### Step 5: Deploy to Kubernetes

```bash
cd k8s
./deploy.sh
```

### Step 6: Restore Your Data

**Wait for pods to be ready:**
```bash
kubectl wait --for=condition=ready pod -l app=postgresql -n odoo-production --timeout=300s
```

**Restore PostgreSQL:**
```bash
POSTGRES_POD=$(kubectl get pod -n odoo-production -l app=postgresql -o jsonpath='{.items[0].metadata.name}')

kubectl cp odoo-backup.sql odoo-production/$POSTGRES_POD:/tmp/
kubectl exec -n odoo-production $POSTGRES_POD -- psql -U odoo postgres < /tmp/odoo-backup.sql
```

**Restore Odoo files:**
```bash
ODOO_POD=$(kubectl get pod -n odoo-production -l app=odoo -o jsonpath='{.items[0].metadata.name}')

kubectl cp ./odoo-backup odoo-production/$ODOO_POD:/var/lib/odoo
kubectl rollout restart -n odoo-production deployment/odoo
```

### Step 7: Verify Migration

```bash
# Check all pods are running
kubectl get pods -n odoo-production

# Check services
kubectl get svc -n odoo-production

# Access Odoo
kubectl port-forward -n odoo-production svc/odoo 8069:8069
# Open: http://localhost:8069

# Check logs
kubectl logs -f -n odoo-production deployment/odoo
```

## Key Differences to Understand

### 1. Networking

**Docker Compose:**
- Services communicate via service names on the same network
- Example: `postgresql://db:5432/postgres`

**Kubernetes:**
- Services communicate via DNS names
- Example: `postgresql://postgresql.odoo-production.svc.cluster.local:5432/postgres`
- Short form works within same namespace: `postgresql://postgresql:5432/postgres`

### 2. Storage

**Docker Compose:**
```yaml
volumes:
  odoo-db-data:
```

**Kubernetes:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 3. Environment Variables

**Docker Compose:**
```yaml
environment:
  - POSTGRES_USER=odoo
  - POSTGRES_PASSWORD=odoo123
```

**Kubernetes:**
```yaml
env:
- name: POSTGRES_USER
  valueFrom:
    secretKeyRef:
      name: postgres-secret
      key: POSTGRES_USER
```

### 4. Restart Policies

**Docker Compose:**
```yaml
restart: unless-stopped
```

**Kubernetes:**
- Automatic by default
- Controlled by Deployment strategy
- Self-healing: pods restart automatically

### 5. Scaling

**Docker Compose:**
```bash
docker-compose up --scale odoo=3
```

**Kubernetes:**
```bash
kubectl scale deployment odoo -n odoo-production --replicas=3
```

## Benefits of Kubernetes

### 1. High Availability
- Automatic pod restarts
- Self-healing
- Multiple replicas
- Node failure tolerance

### 2. Scalability
```bash
# Scale horizontally
kubectl scale deployment odoo -n odoo-production --replicas=5

# Auto-scaling
kubectl autoscale deployment odoo -n odoo-production --cpu-percent=80 --min=2 --max=10
```

### 3. Rolling Updates
```bash
# Zero-downtime deployments
kubectl set image deployment/odoo odoo=odoo:18.1 -n odoo-production
kubectl rollout status deployment/odoo -n odoo-production

# Rollback if needed
kubectl rollout undo deployment/odoo -n odoo-production
```

### 4. Resource Management
```yaml
resources:
  requests:
    memory: "768Mi"
    cpu: "500m"
  limits:
    memory: "1280Mi"
    cpu: "1000m"
```

### 5. Service Discovery
- Built-in DNS
- Automatic load balancing
- Health checks

### 6. Configuration Management
- Secrets for sensitive data
- ConfigMaps for configuration
- Version controlled

## Common Commands Mapping

| Task | Docker Compose | Kubernetes |
|------|---------------|------------|
| **Start** | `docker-compose up -d` | `kubectl apply -f k8s/` |
| **Stop** | `docker-compose down` | `kubectl delete -f k8s/` |
| **Logs** | `docker logs -f odoo-app` | `kubectl logs -f deployment/odoo -n odoo-production` |
| **Restart** | `docker-compose restart odoo` | `kubectl rollout restart deployment/odoo -n odoo-production` |
| **Scale** | `docker-compose up --scale odoo=3` | `kubectl scale deployment odoo --replicas=3 -n odoo-production` |
| **Exec** | `docker exec -it odoo-app bash` | `kubectl exec -it deployment/odoo -n odoo-production -- bash` |
| **Status** | `docker ps` | `kubectl get pods -n odoo-production` |
| **Stats** | `docker stats` | `kubectl top pods -n odoo-production` |

## Monitoring Comparison

### Docker Compose
- Manual Prometheus setup
- Local storage
- Limited visibility

### Kubernetes
- Native service discovery
- Automatic pod monitoring
- Built-in metrics
- Easy to add more exporters

## Troubleshooting

### Issue: Pods stuck in Pending

**Check:**
```bash
kubectl describe pod <pod-name> -n odoo-production
```

**Common causes:**
- Insufficient resources
- Storage class not available
- Node selector mismatch

**Fix:**
```bash
# Check node resources
kubectl describe nodes

# Check storage class
kubectl get storageclass
```

### Issue: Can't connect to database

**Check:**
```bash
# Verify PostgreSQL is running
kubectl get pods -n odoo-production -l app=postgresql

# Check service
kubectl get svc postgresql -n odoo-production

# Test connection
ODOO_POD=$(kubectl get pod -n odoo-production -l app=odoo -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n odoo-production $ODOO_POD -- nc -zv postgresql 5432
```

### Issue: Data lost after pod restart

**Check PVC:**
```bash
kubectl get pvc -n odoo-production
```

**Verify volumes are bound:**
```bash
kubectl describe pvc postgres-pvc -n odoo-production
```

## Rollback Plan

If you need to rollback to Docker Compose:

### 1. Backup data from Kubernetes
```bash
# Backup PostgreSQL
POSTGRES_POD=$(kubectl get pod -n odoo-production -l app=postgresql -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n odoo-production $POSTGRES_POD -- pg_dump -U odoo postgres > k8s-backup.sql

# Backup Odoo files
ODOO_POD=$(kubectl get pod -n odoo-production -l app=odoo -o jsonpath='{.items[0].metadata.name}')
kubectl cp odoo-production/$ODOO_POD:/var/lib/odoo ./k8s-odoo-backup
```

### 2. Stop Kubernetes deployment
```bash
cd k8s
./undeploy.sh
```

### 3. Start Docker Compose
```bash
docker-compose up -d
```

### 4. Restore data
```bash
docker cp k8s-backup.sql odoo-db:/tmp/
docker exec odoo-db psql -U odoo postgres < /tmp/k8s-backup.sql
```

## Production Considerations

### 1. Use separate database
- Managed database (RDS, Cloud SQL, Azure Database)
- Better performance
- Automated backups
- High availability

### 2. Setup Ingress
- External access without port-forward
- SSL/TLS certificates
- Domain names
- Load balancing

### 3. Implement GitOps
- ArgoCD or Flux
- Automated deployments
- Git as source of truth

### 4. Setup CI/CD
- Automated testing
- Automated deployments
- Blue-green deployments

### 5. Monitoring enhancements
- Add more dashboards
- Custom alerts
- Log aggregation (ELK/Loki)

### 6. Security
- Network policies
- Pod security policies
- RBAC
- Secrets encryption

## Cost Considerations

### Docker Compose (EC2 t3.small)
- Fixed cost: ~$15-20/month
- Single VM
- Limited scalability

### Kubernetes
- More flexible scaling
- Pay for what you use
- Can be more cost-effective at scale
- Consider:
  - Managed Kubernetes: $70-150/month
  - Plus node costs
  - Storage costs
  - Load balancer costs

**Cost optimization tips:**
- Use spot instances for non-critical workloads
- Right-size your nodes
- Use cluster autoscaler
- Implement resource quotas

## Next Steps

1. **Test thoroughly**: Run tests in development first
2. **Monitor closely**: Watch metrics for first few days
3. **Setup alerts**: Ensure you get notified of issues
4. **Document**: Keep notes of your specific setup
5. **Plan scaling**: Prepare for growth
6. **Setup backups**: Automated backup strategy
7. **Security audit**: Review security settings

## Resources

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [12-Factor App Methodology](https://12factor.net/)
- [Odoo on Kubernetes Guide](https://www.odoo.com/documentation/)

## Support

If you encounter issues:
1. Check pod logs
2. Check events: `kubectl get events -n odoo-production`
3. Describe resources: `kubectl describe <resource>`
4. Check resource usage: `kubectl top pods -n odoo-production`

---

**Congratulations on migrating to Kubernetes!** 🎉

Your infrastructure is now more scalable, resilient, and production-ready.
