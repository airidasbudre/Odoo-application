#!/bin/bash

##############################################
# Odoo Migration Script
# This script helps migrate Odoo to a new server
##############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

##############################################
# STEP 1: CREATE BACKUP (Run on OLD server)
##############################################
backup_old_server() {
    print_info "Starting backup process on OLD server..."

    # Check if Docker is running
    if ! command_exists docker; then
        print_error "Docker is not installed!"
        exit 1
    fi

    # Check if containers are running
    if ! docker ps | grep -q "odoo-db"; then
        print_error "Odoo database container is not running!"
        exit 1
    fi

    print_info "Creating database backup..."
    docker exec odoo-db pg_dump -U odoo -d odoo_db -F c -f /var/lib/postgresql/data/pgdata/odoo_backup.dump

    print_info "Copying backup to host..."
    docker cp odoo-db:/var/lib/postgresql/data/pgdata/odoo_backup.dump /home/ubuntu/odoo_backup.dump

    print_info "Creating migration package..."
    cd /home/ubuntu
    tar -czf odoo_migration_package.tar.gz \
        docker-compose.yml \
        setup.sh \
        .env \
        addons/ \
        odoo_backup.dump

    BACKUP_SIZE=$(du -h odoo_migration_package.tar.gz | cut -f1)
    print_info "Migration package created: odoo_migration_package.tar.gz (${BACKUP_SIZE})"
    print_info "Backup file location: /home/ubuntu/odoo_migration_package.tar.gz"

    echo ""
    print_warning "NEXT STEPS:"
    echo "1. Transfer this file to the new server:"
    echo "   scp /home/ubuntu/odoo_migration_package.tar.gz user@NEW_SERVER:/home/ubuntu/"
    echo "2. On the new server, run: ./migrate.sh restore"
    echo ""
}

##############################################
# STEP 2: RESTORE ON NEW SERVER
##############################################
restore_new_server() {
    print_info "Starting restore process on NEW server..."

    # Check if migration package exists
    if [ ! -f "odoo_migration_package.tar.gz" ]; then
        print_error "Migration package not found!"
        print_info "Please transfer odoo_migration_package.tar.gz to this directory first."
        exit 1
    fi

    # Extract package
    print_info "Extracting migration package..."
    tar -xzf odoo_migration_package.tar.gz

    # Check if Docker is installed
    if ! command_exists docker; then
        print_warning "Docker is not installed. Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        print_info "Docker installed. You may need to log out and back in for group changes to take effect."
    fi

    # Check if Docker Compose is available
    if ! docker compose version >/dev/null 2>&1; then
        print_warning "Docker Compose plugin not found. Installing..."
        sudo apt-get update
        sudo apt-get install -y docker-compose-plugin
    fi

    # Stop any existing containers
    print_info "Stopping existing containers (if any)..."
    docker compose down 2>/dev/null || true

    # Start database container
    print_info "Starting database container..."
    docker compose up -d db

    print_info "Waiting for database to be ready (30 seconds)..."
    sleep 30

    # Check if database is ready
    print_info "Checking database connection..."
    docker exec odoo-db pg_isready -U odoo || {
        print_error "Database is not ready!"
        exit 1
    }

    # Copy backup to container
    print_info "Copying backup to database container..."
    docker cp odoo_backup.dump odoo-db:/tmp/

    # Drop existing database if it exists
    print_info "Preparing database..."
    docker exec odoo-db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo_db;" 2>/dev/null || true
    docker exec odoo-db psql -U odoo -d postgres -c "CREATE DATABASE odoo_db OWNER odoo;"

    # Restore database
    print_info "Restoring database (this may take a few minutes)..."
    docker exec odoo-db pg_restore -U odoo -d odoo_db /tmp/odoo_backup.dump || {
        print_warning "Some warnings during restore (usually normal for constraints)"
    }

    # Start Odoo container
    print_info "Starting Odoo container..."
    docker compose up -d odoo

    print_info "Waiting for Odoo to start (30 seconds)..."
    sleep 30

    # Check if Odoo is running
    if docker ps | grep -q "odoo-app"; then
        print_info "✓ Odoo is running!"
    else
        print_error "Odoo failed to start. Check logs with: docker compose logs odoo"
        exit 1
    fi

    echo ""
    print_info "================================================"
    print_info "Migration completed successfully!"
    print_info "================================================"
    echo ""
    print_info "Your Odoo instance is now running at:"
    echo "  http://localhost:8069"
    echo "  or"
    echo "  http://$(hostname -I | awk '{print $1}'):8069"
    echo ""
    print_warning "IMPORTANT NEXT STEPS:"
    echo "1. Update the base URL in Odoo settings:"
    echo "   Settings → General Settings → Website → Domain"
    echo ""
    echo "2. Or update via database:"
    echo "   docker exec odoo-db psql -U odoo -d odoo_db -c \"UPDATE ir_config_parameter SET value='http://YOUR_NEW_DOMAIN' WHERE key='web.base.url';\""
    echo ""
    echo "3. Check logs if needed:"
    echo "   docker compose logs -f odoo"
    echo ""
}

##############################################
# STEP 3: UPDATE DOMAIN/URL
##############################################
update_domain() {
    if [ -z "$1" ]; then
        print_error "Please provide the new domain!"
        echo "Usage: ./migrate.sh update-domain https://newdomain.com"
        exit 1
    fi

    NEW_DOMAIN="$1"

    print_info "Updating base URL to: ${NEW_DOMAIN}"
    docker exec odoo-db psql -U odoo -d odoo_db -c \
        "UPDATE ir_config_parameter SET value='${NEW_DOMAIN}' WHERE key='web.base.url';"

    print_info "Restarting Odoo..."
    docker compose restart odoo

    print_info "✓ Domain updated successfully!"
    print_info "Your site is now configured for: ${NEW_DOMAIN}"
}

##############################################
# STEP 4: VERIFY MIGRATION
##############################################
verify_migration() {
    print_info "Verifying migration..."

    # Check if containers are running
    if ! docker ps | grep -q "odoo-db"; then
        print_error "Database container is not running!"
        return 1
    fi

    if ! docker ps | grep -q "odoo-app"; then
        print_error "Odoo container is not running!"
        return 1
    fi

    # Check database connection
    docker exec odoo-db psql -U odoo -d odoo_db -c "SELECT COUNT(*) FROM res_company;" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_info "✓ Database is accessible"
    else
        print_error "✗ Database connection failed"
        return 1
    fi

    # Check if Odoo is responding
    print_info "Checking Odoo web interface..."
    if command_exists curl; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/database/selector 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 303 ]; then
            print_info "✓ Odoo web interface is responding"
        else
            print_warning "Odoo may still be starting up (HTTP $HTTP_CODE)"
        fi
    fi

    print_info "✓ Migration verification complete!"
}

##############################################
# MAIN SCRIPT
##############################################

case "$1" in
    backup)
        backup_old_server
        ;;
    restore)
        restore_new_server
        verify_migration
        ;;
    update-domain)
        update_domain "$2"
        ;;
    verify)
        verify_migration
        ;;
    *)
        echo "Odoo Migration Script"
        echo "===================="
        echo ""
        echo "Usage:"
        echo "  ./migrate.sh backup           - Create backup on OLD server"
        echo "  ./migrate.sh restore          - Restore on NEW server"
        echo "  ./migrate.sh update-domain <url> - Update base URL"
        echo "  ./migrate.sh verify           - Verify migration"
        echo ""
        echo "Example workflow:"
        echo "  1. On OLD server: ./migrate.sh backup"
        echo "  2. Transfer file: scp odoo_migration_package.tar.gz user@new-server:~/"
        echo "  3. On NEW server: ./migrate.sh restore"
        echo "  4. Update domain: ./migrate.sh update-domain https://newdomain.com"
        echo ""
        exit 1
        ;;
esac
