# Minikube Quick Start Guide

Get Odoo running on your local machine in 5 minutes!

## Prerequisites Check

```bash
docker --version   # Should show Docker version
kubectl version --client  # Should show kubectl version
minikube version  # Should show minikube version
```

All three should be installed. If not, run the setup script first.

## 3 Simple Steps

### 1. Start Minikube

```bash
./k8s/local/start-minikube.sh
```

This will:
- Start a local Kubernetes cluster
- Configure it with appropriate resources
- Enable necessary addons

**Wait time:** ~2-3 minutes

### 2. Deploy Odoo

```bash
./k8s/local/deploy-local.sh
```

This will:
- Create namespace
- Deploy PostgreSQL database
- Deploy Odoo application

**Wait time:** ~3-5 minutes

### 3. Access Odoo

```bash
minikube service odoo-service -n odoo-production
```

This opens Odoo in your browser automatically!

**Alternative:** Get the URL manually:
```bash
minikube service odoo-service -n odoo-production --url
```

## First Time Setup in Odoo

When you first access Odoo:

1. **Create Database**
   - Master Password: `admin` (default)
   - Database Name: `odoo` or any name you like
   - Email: your email
   - Password: choose a strong password
   - Country: your country
   - Demo Data: choose based on preference

2. **Login**
   - Use the email and password you just created

## Common Commands

```bash
# Check if everything is running
kubectl get pods -n odoo-production

# View Odoo logs
kubectl logs -f deployment/odoo -n odoo-production

# View PostgreSQL logs
kubectl logs -f deployment/postgresql -n odoo-production

# Restart Odoo (after making changes)
kubectl rollout restart deployment/odoo -n odoo-production

# Stop Minikube (keeps data)
minikube stop

# Start Minikube again
minikube start

# Clean up everything
./k8s/local/undeploy-local.sh
minikube delete
```

## Accessing Services

### Odoo Web Interface
```bash
minikube service odoo-service -n odoo-production
```

### Kubernetes Dashboard
```bash
minikube dashboard
```

### All Services
```bash
minikube service list -n odoo-production
```

## Troubleshooting

### "Connection Refused" or Can't Access Odoo

```bash
# Check if pods are running
kubectl get pods -n odoo-production

# Both should show "Running" and "1/1" ready
# If not, check logs
kubectl logs -f deployment/odoo -n odoo-production
```

### Pods Stuck in "Pending"

```bash
# Check Minikube resources
kubectl top nodes

# Restart with more resources
minikube delete
minikube start --cpus=4 --memory=8192
./k8s/local/deploy-local.sh
```

### "ImagePullBackOff" Error

```bash
# Minikube might need internet access to download images
# Check your connection and try again
kubectl delete pod -l app=odoo -n odoo-production
```

### Want to Start Fresh

```bash
# Delete everything and start over
./k8s/local/undeploy-local.sh
minikube delete
./k8s/local/start-minikube.sh
./k8s/local/deploy-local.sh
```

## What's Running?

After successful deployment:

- **PostgreSQL**: Database running on port 5432 (internal)
- **Odoo**: Application running on NodePort 30069
- **Storage**: 10GB for PostgreSQL, 5GB for Odoo

## Resource Usage

Typical resource usage:
- **PostgreSQL**: ~200-500MB RAM, ~10-20% CPU
- **Odoo**: ~1-1.5GB RAM, ~20-50% CPU
- **Total**: ~2GB RAM, ~1 CPU core

## Next Steps

1. **Learn Kubernetes**:
   - Try `kubectl get all -n odoo-production`
   - Explore `minikube dashboard`
   - Read the full README.md

2. **Customize Odoo**:
   - Install apps/modules
   - Configure settings
   - Add users

3. **Add Monitoring** (optional):
   - Deploy Prometheus and Grafana
   - See monitoring-local.yaml

4. **Deploy to Cloud**:
   - The skills learned here transfer directly to cloud Kubernetes
   - See parent k8s/ directory for cloud deployment

## Tips

- Minikube data persists between stops/starts
- Use `minikube stop` when not using (saves resources)
- Use `minikube delete` to completely clean up
- Odoo takes 2-3 minutes to fully start up (be patient!)
- The first database creation takes longer than subsequent ones

## Help

- Full documentation: `k8s/local/README.md`
- Minikube docs: https://minikube.sigs.k8s.io/docs/
- Kubernetes docs: https://kubernetes.io/docs/
- Odoo docs: https://www.odoo.com/documentation/

Enjoy learning Kubernetes! 🚀
