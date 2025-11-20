# Odoo Kubernetes Deployment

Complete Kubernetes manifests for deploying Odoo 18 with full monitoring stack.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                  │
│                                                       │
│  ┌──────────────────────────────────────────────┐  │
│  │         Namespace: odoo-production            │  │
│  │                                                │  │
│  │  ┌──────────────┐      ┌──────────────┐     │  │
│  │  │     Odoo     │◄─────┤  PostgreSQL  │     │  │
│  │  │  Deployment  │      │  Deployment  │     │  │
│  │  │   (2 pods)   │      │   (1 pod)    │     │  │
│  │  └──────┬───────┘      └──────────────┘     │  │
│  │         │                                     │  │
│  │  ┌──────▼──────────────────────────────┐    │  │
│  │  │       Monitoring Stack               │    │  │
│  │  │  ┌─────────────┐  ┌─────────────┐   │    │  │
│  │  │  │ Prometheus  │  │   Grafana   │   │    │  │
│  │  │  └──────┬──────┘  └─────────────┘   │    │  │
│  │  │         │                             │    │  │
│  │  │  ┌──────▼──────────────────┐         │    │  │
│  │  │  │    Alertmanager         │         │    │  │
│  │  │  │  (Telegram Alerts)      │         │    │  │
│  │  │  └─────────────────────────┘         │    │  │
│  │  │                                       │    │  │
│  │  │  Exporters:                           │    │  │
│  │  │  • Node Exporter (DaemonSet)         │    │  │
│  │  │  • Postgres Exporter                 │    │  │
│  │  └───────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

## Components

### Application Layer
- **Odoo 18**: ERP application with 2 workers
- **PostgreSQL 15**: Database with persistent storage

### Monitoring Stack
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **Alertmanager**: Alert routing to Telegram
- **Node Exporter**: System metrics (CPU, memory, disk)
- **Postgres Exporter**: Database metrics

## Prerequisites

1. **Kubernetes Cluster**: v1.24+
   - Local: Minikube, Kind, or K3s
   - Cloud: EKS, GKE, AKS, or any managed Kubernetes

2. **kubectl**: Kubernetes CLI tool
   ```bash
   kubectl version --client
   ```

3. **Storage Class**: Ensure you have a default storage class
   ```bash
   kubectl get storageclass
   ```

4. **Ingress Controller** (Optional): For external access
   ```bash
   # NGINX Ingress Controller
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
   ```

## Quick Start

### 1. Deploy Everything

```bash
cd k8s
./deploy.sh
```

This script will:
- Create the namespace
- Deploy PostgreSQL with persistent storage
- Deploy Odoo application
- Deploy complete monitoring stack
- Configure alerting to Telegram

### 2. Check Deployment Status

```bash
kubectl get pods -n odoo-production
kubectl get svc -n odoo-production
kubectl get pvc -n odoo-production
```

### 3. Access Services Locally

```bash
# Odoo
kubectl port-forward -n odoo-production svc/odoo 8069:8069
# Access at: http://localhost:8069

# Grafana
kubectl port-forward -n odoo-production svc/grafana 3000:3000
# Access at: http://localhost:3000
# Default credentials: admin/admin

# Prometheus
kubectl port-forward -n odoo-production svc/prometheus 9090:9090
# Access at: http://localhost:9090

# Alertmanager
kubectl port-forward -n odoo-production svc/alertmanager 9093:9093
# Access at: http://localhost:9093
```

## File Structure

```
k8s/
├── namespace.yaml              # Namespace definition
├── deploy.sh                   # Automated deployment script
├── undeploy.sh                # Cleanup script
├── README.md                  # This file
│
├── base/                      # Application layer
│   ├── postgresql-secret.yaml
│   ├── postgresql-pvc.yaml
│   ├── postgresql-deployment.yaml
│   ├── postgresql-service.yaml
│   ├── odoo-pvc.yaml
│   ├── odoo-deployment.yaml
│   ├── odoo-service.yaml
│   └── ingress.yaml
│
└── monitoring/                # Monitoring stack
    ├── prometheus-rbac.yaml
    ├── prometheus-pvc.yaml
    ├── prometheus-configmap.yaml
    ├── prometheus-alerts-configmap.yaml
    ├── prometheus-deployment.yaml
    ├── prometheus-service.yaml
    ├── grafana-pvc.yaml
    ├── grafana-secret.yaml
    ├── grafana-deployment.yaml
    ├── grafana-service.yaml
    ├── alertmanager-pvc.yaml
    ├── alertmanager-secret.yaml
    ├── alertmanager-configmap.yaml
    ├── alertmanager-deployment.yaml
    ├── alertmanager-service.yaml
    ├── postgres-exporter-deployment.yaml
    ├── postgres-exporter-service.yaml
    ├── node-exporter-daemonset.yaml
    └── node-exporter-service.yaml
```

## Manual Deployment Steps

If you prefer manual control:

### 1. Create Namespace
```bash
kubectl apply -f namespace.yaml
```

### 2. Deploy Database
```bash
kubectl apply -f base/postgresql-secret.yaml
kubectl apply -f base/postgresql-pvc.yaml
kubectl apply -f base/postgresql-deployment.yaml
kubectl apply -f base/postgresql-service.yaml
```

### 3. Deploy Odoo
```bash
kubectl apply -f base/odoo-pvc.yaml
kubectl apply -f base/odoo-deployment.yaml
kubectl apply -f base/odoo-service.yaml
```

### 4. Deploy Monitoring
```bash
kubectl apply -f monitoring/
```

## Configuration

### Update Secrets

**PostgreSQL Credentials:**
Edit `base/postgresql-secret.yaml`:
```yaml
stringData:
  POSTGRES_DB: postgres
  POSTGRES_USER: your_user
  POSTGRES_PASSWORD: your_secure_password
```

**Grafana Credentials:**
Edit `monitoring/grafana-secret.yaml`:
```yaml
stringData:
  admin-user: your_admin_user
  admin-password: your_secure_password
```

**Telegram Bot:**
Edit `monitoring/alertmanager-secret.yaml` or `monitoring/alertmanager-configmap.yaml`:
```yaml
stringData:
  telegram-bot-token: "YOUR_BOT_TOKEN"
  telegram-chat-id: "YOUR_CHAT_ID"
```

### Storage Configuration

By default, manifests use `gp2` storage class (AWS EBS). Update if using different provider:

```yaml
spec:
  storageClassName: gp2  # Change to your storage class
```

Common storage classes:
- **AWS**: `gp2`, `gp3`, `io1`
- **GCP**: `standard`, `ssd`
- **Azure**: `default`, `managed-premium`
- **Local**: `standard`, `hostpath`

### Resource Limits

Adjust resource limits in deployment files based on your cluster capacity:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## Scaling

### Scale Odoo Workers
```bash
kubectl scale deployment odoo -n odoo-production --replicas=3
```

### Horizontal Pod Autoscaling
```bash
kubectl autoscale deployment odoo -n odoo-production \
  --cpu-percent=80 --min=2 --max=5
```

## Monitoring & Alerts

### Active Alert Rules

17 alert rules configured:

**System Alerts:**
- High CPU Usage (>80%)
- Critical CPU Usage (>95%)
- High Memory Usage (>85%)
- Critical Memory Usage (>95%)
- High Disk Usage
- High Disk I/O
- High System Load

**Database Alerts:**
- PostgreSQL Down
- High Database Connections
- Slow Queries

**Application Alerts:**
- Odoo Down
- High Response Time

### View Alerts in Prometheus
```bash
kubectl port-forward -n odoo-production svc/prometheus 9090:9090
# Open: http://localhost:9090/alerts
```

### Telegram Notifications

Alerts are automatically sent to Telegram with:
- 🚨 for firing alerts
- ✅ for resolved alerts
- Severity levels (critical, warning, info)
- Custom repeat intervals

## Backup & Recovery

### Database Backup
```bash
# Get PostgreSQL pod name
POSTGRES_POD=$(kubectl get pod -n odoo-production -l app=postgresql -o jsonpath='{.items[0].metadata.name}')

# Create backup
kubectl exec -n odoo-production $POSTGRES_POD -- \
  pg_dump -U odoo postgres > backup-$(date +%Y%m%d).sql
```

### Restore Database
```bash
kubectl exec -i -n odoo-production $POSTGRES_POD -- \
  psql -U odoo postgres < backup-20241112.sql
```

### PVC Snapshots
Use your cloud provider's snapshot functionality:
```bash
# AWS EBS Snapshot
aws ec2 create-snapshot --volume-id vol-xxxxx --description "odoo-backup"

# GCP Persistent Disk Snapshot
gcloud compute disks snapshot DISK_NAME --snapshot-names=odoo-backup
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n odoo-production
kubectl describe pod <pod-name> -n odoo-production
```

### View Logs
```bash
# Odoo logs
kubectl logs -f -n odoo-production deployment/odoo

# PostgreSQL logs
kubectl logs -f -n odoo-production deployment/postgresql

# Prometheus logs
kubectl logs -f -n odoo-production deployment/prometheus
```

### Common Issues

**Pod stuck in Pending:**
- Check PVC status: `kubectl get pvc -n odoo-production`
- Check storage class: `kubectl get storageclass`
- Check node resources: `kubectl describe node`

**Odoo can't connect to database:**
```bash
# Check PostgreSQL service
kubectl get svc postgresql -n odoo-production

# Test connection from Odoo pod
kubectl exec -it -n odoo-production deployment/odoo -- \
  nc -zv postgresql 5432
```

**Alerts not working:**
```bash
# Check Alertmanager logs
kubectl logs -f -n odoo-production deployment/alertmanager

# Check Alertmanager config
kubectl get configmap alertmanager-config -n odoo-production -o yaml
```

## Ingress Setup (Optional)

### Configure Domain Names

Edit `base/ingress.yaml`:
```yaml
spec:
  tls:
  - hosts:
    - odoo.yourdomain.com
    - grafana.yourdomain.com
  rules:
  - host: odoo.yourdomain.com
```

### Apply Ingress
```bash
kubectl apply -f base/ingress.yaml
```

### Install Cert-Manager (for SSL)
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## Cleanup

### Remove Everything
```bash
./undeploy.sh
```

### Or manually:
```bash
kubectl delete namespace odoo-production
```

## Next Steps

1. **Setup Ingress**: Configure domain names and SSL
2. **Configure Grafana Dashboards**: Import pre-built dashboards
3. **Setup Backups**: Automated database backups
4. **Add Horizontal Pod Autoscaling**: Auto-scale based on load
5. **Setup CI/CD**: Automated deployments with GitOps
6. **Configure Network Policies**: Enhance security

## Resources

- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Odoo Documentation**: https://www.odoo.com/documentation/18.0/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/

## Support

For issues and questions:
- Check logs: `kubectl logs -f -n odoo-production deployment/<name>`
- Describe resources: `kubectl describe <resource> -n odoo-production`
- Check events: `kubectl get events -n odoo-production --sort-by='.lastTimestamp'`
