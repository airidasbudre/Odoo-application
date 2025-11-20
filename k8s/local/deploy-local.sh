#!/bin/bash

# Local deployment script for Odoo on Minikube
set -e

echo "Deploying Odoo to Minikube..."

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo "Error: Minikube is not running!"
    echo "Please run: ./k8s/local/start-minikube.sh"
    exit 1
fi

# Ensure we're using the minikube context
kubectl config use-context minikube

echo ""
echo "Step 1: Creating namespace..."
kubectl apply -f k8s/local/namespace.yaml

echo ""
echo "Step 2: Deploying PostgreSQL..."
kubectl apply -f k8s/local/postgresql-local.yaml

echo ""
echo "Waiting for PostgreSQL to be ready (this may take a few minutes)..."
kubectl wait --for=condition=ready pod -l app=postgresql -n odoo-production --timeout=300s || {
    echo "PostgreSQL failed to start. Checking logs..."
    kubectl logs -l app=postgresql -n odoo-production --tail=50
    exit 1
}

echo ""
echo "Step 3: Deploying Odoo..."
kubectl apply -f k8s/local/odoo-local.yaml

echo ""
echo "Waiting for Odoo to be ready (this may take a few minutes)..."
kubectl wait --for=condition=ready pod -l app=odoo -n odoo-production --timeout=600s || {
    echo "Odoo failed to start. Checking logs..."
    kubectl logs -l app=odoo -n odoo-production --tail=50
    exit 1
}

echo ""
echo "=========================================="
echo "Deployment successful!"
echo "=========================================="
echo ""

# Get the Minikube IP
MINIKUBE_IP=$(minikube ip)
NODE_PORT=$(kubectl get svc odoo-service -n odoo-production -o jsonpath='{.spec.ports[0].nodePort}')

echo "Access Odoo at:"
echo "  http://${MINIKUBE_IP}:${NODE_PORT}"
echo ""
echo "Or use this command to open in browser:"
echo "  minikube service odoo-service -n odoo-production"
echo ""
echo "Useful commands:"
echo "  View pods:          kubectl get pods -n odoo-production"
echo "  View services:      kubectl get svc -n odoo-production"
echo "  View logs (Odoo):   kubectl logs -f deployment/odoo -n odoo-production"
echo "  View logs (Postgres): kubectl logs -f deployment/postgresql -n odoo-production"
echo "  Dashboard:          minikube dashboard"
echo ""
echo "To undeploy:"
echo "  ./k8s/local/undeploy-local.sh"
