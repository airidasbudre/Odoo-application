#!/bin/bash

# Undeploy Odoo from Minikube
set -e

echo "Undeploying Odoo from Minikube..."

# Check if namespace exists
if ! kubectl get namespace odoo-production &> /dev/null; then
    echo "Namespace odoo-production not found. Nothing to undeploy."
    exit 0
fi

echo ""
echo "Deleting Odoo deployment..."
kubectl delete -f k8s/local/odoo-local.yaml --ignore-not-found=true

echo ""
echo "Deleting PostgreSQL deployment..."
kubectl delete -f k8s/local/postgresql-local.yaml --ignore-not-found=true

echo ""
echo "Deleting namespace..."
kubectl delete -f k8s/local/namespace.yaml --ignore-not-found=true

echo ""
echo "Waiting for resources to be deleted..."
kubectl wait --for=delete namespace/odoo-production --timeout=60s || true

echo ""
echo "=========================================="
echo "Undeployment complete!"
echo "=========================================="
echo ""
echo "Note: PersistentVolumes may still exist in Minikube."
echo "To completely clean up, run: minikube delete"
