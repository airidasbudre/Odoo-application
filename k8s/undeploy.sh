#!/bin/bash

# Odoo Kubernetes Undeployment Script
# This script removes the entire Odoo stack from Kubernetes

set -e

echo "==================================="
echo "Odoo Kubernetes Undeployment"
echo "==================================="
echo ""

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}This will delete all resources in the odoo-production namespace${NC}"
echo -e "${RED}WARNING: All data will be lost unless you have backups!${NC}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Undeployment cancelled"
    exit 0
fi

echo ""
echo -e "${YELLOW}Deleting all resources...${NC}"

# Delete in reverse order
kubectl delete -f monitoring/ --ignore-not-found=true
kubectl delete -f base/ --ignore-not-found=true
kubectl delete -f namespace.yaml --ignore-not-found=true

echo ""
echo "Undeployment complete!"
echo ""
