#!/bin/bash

set -e

echo "================================="
echo "Odoo 18 AWS Free Tier Setup"
echo "================================="
echo ""

# Add swap space (important for t2.micro with 1GB RAM)
echo "1. Setting up 2GB swap space..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "   ✓ Swap created"
else
    echo "   ✓ Swap already exists"
fi
echo ""

# Install Docker
echo "2. Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "   ✓ Docker installed"
else
    echo "   ✓ Docker already installed"
fi
echo ""

# Install Docker Compose
echo "3. Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    echo "   ✓ Docker Compose installed"
else
    echo "   ✓ Docker Compose already installed"
fi
echo ""

# Create directories
echo "4. Creating directories..."
mkdir -p addons
echo "   ✓ Directories created"
echo ""

# Copy environment file if needed
if [ -f .env.example ] && [ ! -f .env ]; then
    cp .env.example .env
    echo "5. Environment file created (.env)"
else
    echo "5. Using existing .env file"
fi
echo ""

# Start Docker service
echo "6. Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker
echo "   ✓ Docker service started"
echo ""

# Pull images (this may take a few minutes)
echo "7. Pulling Docker images (this may take 5-10 minutes)..."
docker compose pull
echo "   ✓ Images pulled"
echo ""

# Start services
echo "8. Starting Odoo and PostgreSQL..."
docker compose up -d
echo "   ✓ Services started"
echo ""

# Wait for services to be ready
echo "9. Waiting for services to be ready..."
sleep 15
echo ""

# Check status
echo "10. Checking status..."
docker compose ps
echo ""

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "Unable to fetch")

echo "================================="
echo "Setup Complete!"
echo "================================="
echo ""
echo "Odoo is running at:"
echo "  http://$PUBLIC_IP:8069"
echo ""
echo "Default credentials for development:"
echo "  Database: postgres"
echo "  User: odoo"
echo "  Password: odoo123"
echo ""
echo "Useful commands:"
echo "  docker compose logs -f     # View logs"
echo "  docker compose ps          # Check status"
echo "  docker compose restart     # Restart services"
echo "  docker compose down        # Stop services"
echo ""
echo "IMPORTANT: If you just installed Docker, run:"
echo "  newgrp docker"
echo "  Then re-run this script."
echo ""
