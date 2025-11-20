# Minikube Setup Complete!

Congratulations! Your local Kubernetes cluster is ready.

## What's Been Set Up

1. **Minikube Installed**: v1.37.0
2. **Kubernetes Running**: v1.34.0
3. **Docker Driver**: Using Docker as the container runtime
4. **Resources Allocated**:
   - Memory: 1800MB
   - CPUs: 2
5. **Addons Enabled**:
   - metrics-server (for resource monitoring)
   - storage-provisioner (for persistent volumes)
   - dashboard (Kubernetes web UI)

## Quick Start

### Deploy Odoo Application

```bash
# Deploy the full stack
./k8s/local/deploy-local.sh
```

This will:
1. Create the odoo-production namespace
2. Deploy PostgreSQL database
3. Deploy Odoo application
4. Wait for everything to be ready

**Expected time**: 3-5 minutes for first deployment

### Access Your Application

After deployment completes:

```bash
# Open Odoo in your browser
minikube service odoo-service -n odoo-production

# Or get the URL
minikube service odoo-service -n odoo-production --url
```

## Useful Commands

```bash
# View cluster status
minikube status

# View all pods
kubectl get pods -n odoo-production

# View logs
kubectl logs -f deployment/odoo -n odoo-production

# Open Kubernetes dashboard
minikube dashboard

# Stop Minikube (saves state)
minikube stop

# Start Minikube again
minikube start

# Delete everything (clean slate)
minikube delete
```

## What You Can Learn

With this setup, you can learn:

1. **Kubernetes Basics**:
   - Pods, Deployments, Services
   - Persistent Volumes
   - Namespaces
   - ConfigMaps and Secrets

2. **Application Deployment**:
   - Multi-container applications
   - Database connectivity
   - Service discovery
   - Health checks

3. **Troubleshooting**:
   - Reading logs
   - Debugging pod issues
   - Resource management
   - Networking

4. **Operations**:
   - Scaling applications
   - Rolling updates
   - Backup and restore
   - Monitoring

## File Structure

```
k8s/local/
├── README.md                    # Detailed documentation
├── QUICKSTART.md                # 5-minute quick start guide
├── start-minikube.sh            # Start Minikube cluster
├── deploy-local.sh              # Deploy Odoo application
├── undeploy-local.sh            # Remove Odoo application
├── namespace.yaml               # Kubernetes namespace
├── postgresql-local.yaml        # PostgreSQL database
└── odoo-local.yaml             # Odoo application
```

## Next Steps

1. **Read the Quick Start**: `k8s/local/QUICKSTART.md`
2. **Deploy Odoo**: Run `./k8s/local/deploy-local.sh`
3. **Explore the Dashboard**: Run `minikube dashboard`
4. **Learn kubectl**: Try `kubectl get all -n odoo-production`

## Important Notes

- **Memory**: Your system has limited RAM (1910MB total). Close other applications if you experience issues.
- **Performance**: The setup uses minimal resources. Expect slower performance than production systems.
- **Data Persistence**: Data persists between `minikube stop/start` but is lost on `minikube delete`.
- **Internet**: Required for pulling Docker images on first deployment.

## Troubleshooting

### Minikube won't start
```bash
minikube delete
minikube start --cpus=2 --memory=1800
```

### Out of memory
```bash
# Close other applications, then restart Minikube
minikube stop
minikube start
```

### Can't access Odoo
```bash
# Try port-forward instead
kubectl port-forward svc/odoo-service 8069:8069 -n odoo-production
# Then visit http://localhost:8069
```

## Resources

- **Minikube Docs**: https://minikube.sigs.k8s.io/docs/
- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Odoo Docs**: https://www.odoo.com/documentation/18.0/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/

## Cloud Deployment

Once you're comfortable with local Kubernetes, you can deploy to the cloud:

- The manifests in `k8s/base/` are cloud-ready
- Works with AWS EKS, Google GKE, Azure AKS
- See `k8s/README.md` for cloud deployment instructions

## System Status

```
✓ Minikube installed
✓ Kubernetes cluster running
✓ kubectl configured
✓ Docker driver active
✓ Addons enabled
✓ Ready for deployment
```

---

**You're all set! Run `./k8s/local/deploy-local.sh` to deploy Odoo.**

For questions and issues, check:
- `k8s/local/README.md` - Full documentation
- `k8s/local/QUICKSTART.md` - Quick start guide
