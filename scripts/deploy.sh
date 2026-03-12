#!/bin/bash

# Deployment Script for Odoo Application

set -e

echo "======================================"
echo "Odoo Application Deployment"
echo "======================================"

# Pull latest changes
echo "Pulling latest changes from Git..."
git pull origin main

# Build and start services
echo "Building and starting Docker containers..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Show running containers
echo ""
echo "Running containers:"
docker-compose ps

echo ""
echo "======================================"
echo "Deployment completed successfully!"
echo "======================================"
echo ""
echo "Access your services:"
echo "- Odoo: https://your-domain.com"
echo "- Grafana: http://your-server-ip:3000"
echo "- Prometheus: http://your-server-ip:9090"
echo ""
