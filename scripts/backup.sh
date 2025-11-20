#!/bin/bash

# Backup Script for Odoo Application

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="postgres"

echo "======================================"
echo "Odoo Backup - $TIMESTAMP"
echo "======================================"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
docker-compose exec -T db pg_dump -U odoo $DB_NAME | gzip > $BACKUP_DIR/odoo_db_$TIMESTAMP.sql.gz

# Backup Odoo filestore
echo "Backing up Odoo filestore..."
docker-compose exec odoo tar czf - /var/lib/odoo/filestore > $BACKUP_DIR/odoo_filestore_$TIMESTAMP.tar.gz

# Backup custom addons
echo "Backing up custom addons..."
tar czf $BACKUP_DIR/odoo_addons_$TIMESTAMP.tar.gz addons/

# List backups
echo ""
echo "Backup completed successfully!"
echo "Backup files:"
ls -lh $BACKUP_DIR/*$TIMESTAMP*

# Clean old backups (keep last 7 days)
echo ""
echo "Cleaning old backups (keeping last 7 days)..."
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo ""
echo "======================================"
echo "Backup process completed!"
echo "======================================"
