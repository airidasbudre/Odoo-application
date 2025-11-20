#!/bin/bash

# Odoo Kubernetes Deployment Script
# This script deploys the entire Odoo stack to Kubernetes

set -e

echo "==================================="
echo "Odoo Kubernetes Deployment"
echo "==================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check cluster connection
echo -e "${YELLOW}Checking Kubernetes cluster connection...${NC}"
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Kubernetes cluster${NC}"
echo ""

# Create namespace
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl apply -f namespace.yaml
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Deploy database layer
echo -e "${YELLOW}Deploying PostgreSQL database...${NC}"
kubectl apply -f base/postgresql-secret.yaml
kubectl apply -f base/postgresql-pvc.yaml
kubectl apply -f base/postgresql-deployment.yaml
kubectl apply -f base/postgresql-service.yaml
echo -e "${GREEN}✓ PostgreSQL deployed${NC}"
echo ""

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=postgresql -n odoo-production --timeout=300s
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
echo ""

# Deploy Odoo application
echo -e "${YELLOW}Deploying Odoo application...${NC}"
kubectl apply -f base/odoo-pvc.yaml
kubectl apply -f base/odoo-deployment.yaml
kubectl apply -f base/odoo-service.yaml
echo -e "${GREEN}✓ Odoo deployed${NC}"
echo ""

# Deploy monitoring stack
echo -e "${YELLOW}Deploying monitoring stack...${NC}"

# Prometheus RBAC
kubectl apply -f monitoring/prometheus-rbac.yaml

# Prometheus
kubectl apply -f monitoring/prometheus-pvc.yaml
kubectl apply -f monitoring/prometheus-configmap.yaml
kubectl apply -f monitoring/prometheus-alerts-configmap.yaml
kubectl apply -f monitoring/prometheus-deployment.yaml
kubectl apply -f monitoring/prometheus-service.yaml

# Grafana
kubectl apply -f monitoring/grafana-pvc.yaml
kubectl apply -f monitoring/grafana-deployment.yaml
kubectl apply -f monitoring/grafana-service.yaml

# Alertmanager
kubectl apply -f monitoring/alertmanager-pvc.yaml
kubectl apply -f monitoring/alertmanager-secret.yaml
kubectl apply -f monitoring/alertmanager-configmap.yaml
kubectl apply -f monitoring/alertmanager-deployment.yaml
kubectl apply -f monitoring/alertmanager-service.yaml

# Exporters
kubectl apply -f monitoring/postgres-exporter-deployment.yaml
kubectl apply -f monitoring/postgres-exporter-service.yaml
kubectl apply -f monitoring/node-exporter-daemonset.yaml
kubectl apply -f monitoring/node-exporter-service.yaml

echo -e "${GREEN}✓ Monitoring stack deployed${NC}"
echo ""

# Optional: Deploy Ingress (uncomment if you have ingress controller)
# echo -e "${YELLOW}Deploying Ingress...${NC}"
# kubectl apply -f base/ingress.yaml
# echo -e "${GREEN}✓ Ingress deployed${NC}"
# echo ""

echo -e "${GREEN}==================================="
echo -e "Deployment Complete!"
echo -e "===================================${NC}"
echo ""
echo "To check the status of your deployments:"
echo "  kubectl get pods -n odoo-production"
echo ""
echo "To access services locally (port-forward):"
echo "  kubectl port-forward -n odoo-production svc/odoo 8069:8069"
echo "  kubectl port-forward -n odoo-production svc/grafana 3000:3000"
echo "  kubectl port-forward -n odoo-production svc/prometheus 9090:9090"
echo ""
echo "To view logs:"
echo "  kubectl logs -f -n odoo-production deployment/odoo"
echo "  kubectl logs -f -n odoo-production deployment/prometheus"
echo ""
