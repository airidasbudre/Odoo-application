# Quick Start Guide

## Prerequisites
- Kubernetes cluster running (minikube, k3s, EKS, GKE, etc.)
- kubectl installed and configured
- Storage class available

## Deploy in 3 Steps

### 1. Check your cluster
```bash
kubectl cluster-info
kubectl get storageclass
```

### 2. Deploy the stack
```bash
cd k8s
./deploy.sh
```

### 3. Access services
```bash
# Odoo
kubectl port-forward -n odoo-production svc/odoo 8069:8069
# Open: http://localhost:8069

# Grafana
kubectl port-forward -n odoo-production svc/grafana 3000:3000
# Open: http://localhost:3000 (admin/admin)

# Prometheus
kubectl port-forward -n odoo-production svc/prometheus 9090:9090
# Open: http://localhost:9090
```

## Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n odoo-production

# Should show all pods in Running state:
# - postgresql
# - odoo
# - prometheus
# - grafana
# - alertmanager
# - postgres-exporter
# - node-exporter
```

## What You Get

✅ **Odoo 18** - Full ERP application
✅ **PostgreSQL 15** - Production database
✅ **Prometheus** - Metrics collection
✅ **Grafana** - Monitoring dashboards
✅ **Alertmanager** - Telegram notifications
✅ **17 Active Alerts** - System, DB, and app monitoring
✅ **Persistent Storage** - All data survives pod restarts
✅ **Auto-restart** - Pods automatically restart on failure

## Common Commands

```bash
# View logs
kubectl logs -f -n odoo-production deployment/odoo

# Scale Odoo
kubectl scale deployment odoo -n odoo-production --replicas=3

# Restart a service
kubectl rollout restart -n odoo-production deployment/odoo

# Delete everything
./undeploy.sh
```

## Troubleshooting

**Pods stuck in Pending?**
```bash
kubectl describe pod <pod-name> -n odoo-production
# Check for storage or resource issues
```

**Can't access services?**
```bash
# Check services
kubectl get svc -n odoo-production

# Check if port-forward is running
ps aux | grep port-forward
```

## Next Steps

1. Configure your domain in `base/ingress.yaml`
2. Update secrets in `base/postgresql-secret.yaml`
3. Import Grafana dashboards
4. Setup automated backups

Read the full README.md for detailed documentation.
