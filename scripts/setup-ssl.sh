#!/bin/bash

# SSL Setup Script for Odoo Application
# This script sets up Let's Encrypt SSL certificates

set -e

# Configuration
DOMAIN="${DOMAIN:-your-domain.com}"
EMAIL="${EMAIL:-admin@your-domain.com}"

echo "======================================"
echo "SSL Certificate Setup"
echo "======================================"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Check if domain is configured
if [ "$DOMAIN" = "your-domain.com" ]; then
    echo "ERROR: Please set your domain name"
    echo "Usage: DOMAIN=yourdomain.com EMAIL=you@email.com ./scripts/setup-ssl.sh"
    exit 1
fi

# Create directories
mkdir -p nginx/ssl
mkdir -p nginx/www

# Request certificate
echo "Requesting SSL certificate..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

echo ""
echo "SSL certificate obtained successfully!"
echo "Certificate location: nginx/ssl/live/$DOMAIN/"
echo ""
echo "Don't forget to:"
echo "1. Update nginx/nginx.conf with your domain name"
echo "2. Restart nginx: docker-compose restart nginx"
echo ""
