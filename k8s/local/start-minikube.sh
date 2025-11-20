#!/bin/bash

# Minikube startup script for Odoo development
# This script starts Minikube with appropriate resources for running Odoo

set -e

echo "Starting Minikube for Odoo development..."

# Check if Minikube is already running
if minikube status | grep -q "Running"; then
    echo "Minikube is already running!"
    minikube status
    exit 0
fi

# Detect system resources
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
TOTAL_CPU=$(nproc)

# Calculate resources to allocate (75% of system resources for Minikube)
MINIKUBE_MEM=$((TOTAL_MEM * 75 / 100))
# Minikube requires minimum 2 CPUs
if [ $TOTAL_CPU -lt 2 ]; then
    echo "Error: Minikube requires at least 2 CPU cores"
    echo "Your system has: ${TOTAL_CPU} cores"
    exit 1
fi
MINIKUBE_CPU=2

# Recommended minimums
REC_MEM=4096
REC_CPU=2

# Absolute minimums for basic functionality (Minikube requires 1800MB minimum)
ABS_MIN_MEM=1800
ABS_MIN_CPU=2

# Check absolute minimum
if [ $MINIKUBE_MEM -lt $ABS_MIN_MEM ]; then
    echo "Error: Calculated ${MINIKUBE_MEM}MB, but need at least ${ABS_MIN_MEM}MB"
    echo "System total: ${TOTAL_MEM}MB"
    echo "Trying to allocate absolute minimum: ${ABS_MIN_MEM}MB"
    MINIKUBE_MEM=$ABS_MIN_MEM
fi

# Verify system can handle it
if [ $TOTAL_MEM -lt $ABS_MIN_MEM ]; then
    echo "Error: System only has ${TOTAL_MEM}MB total RAM"
    echo "Odoo requires at least ${ABS_MIN_MEM}MB to run minimally"
    exit 1
fi

# Warn if below recommended
if [ $MINIKUBE_MEM -lt $REC_MEM ]; then
    echo "Warning: Allocating ${MINIKUBE_MEM}MB (recommended: ${REC_MEM}MB)"
    echo "         Performance may be limited. Consider closing other applications."
    echo ""
fi

if [ $MINIKUBE_CPU -lt $ABS_MIN_CPU ]; then
    MINIKUBE_CPU=$ABS_MIN_CPU
fi

echo "System Resources:"
echo "  Total Memory: ${TOTAL_MEM}MB"
echo "  Total CPUs: ${TOTAL_CPU}"
echo ""
echo "Allocating to Minikube:"
echo "  Memory: ${MINIKUBE_MEM}MB"
echo "  CPUs: ${MINIKUBE_CPU}"
echo ""

# Start Minikube
echo "Starting Minikube cluster..."
minikube start \
    --cpus=$MINIKUBE_CPU \
    --memory=$MINIKUBE_MEM \
    --driver=docker \
    --disk-size=20g \
    --kubernetes-version=stable

echo ""
echo "Enabling addons..."

# Enable useful addons
minikube addons enable metrics-server
minikube addons enable storage-provisioner
minikube addons enable dashboard

echo ""
echo "Minikube started successfully!"
echo ""
echo "Cluster Info:"
minikube status
echo ""

echo "kubectl is configured to use minikube context"
kubectl config current-context

echo ""
echo "Next steps:"
echo "  1. Deploy application: ./k8s/local/deploy-local.sh"
echo "  2. View dashboard: minikube dashboard"
echo "  3. Check status: kubectl get pods -A"
