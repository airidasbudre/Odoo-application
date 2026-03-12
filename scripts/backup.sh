#!/bin/bash
set -e

# ── Config ────────────────────────────────────────────────
BUCKET="odoo-backups-623859664395"
REGION="eu-north-1"
DB_CONTAINER="odoo-db"
DB_USER="odoo"
DB_NAME="odoo_db"
KEEP_BACKUPS=30
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_KEY="backups/odoo-${TIMESTAMP}.sql.gz"
LOG="$HOME/odoo-backup.log"
# ──────────────────────────────────────────────────────────

echo "[$(date)] Starting backup..." | tee -a $LOG

# 1. Dump database from Docker container and upload directly to S3
docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME | \
  gzip | \
  aws s3 cp - s3://$BUCKET/$BACKUP_KEY --region $REGION

echo "[$(date)] Backup uploaded: $BACKUP_KEY" | tee -a $LOG

# 2. Delete old backups — keep only the last $KEEP_BACKUPS
BACKUP_COUNT=$(aws s3 ls s3://$BUCKET/backups/ --region $REGION | wc -l)

if [ "$BACKUP_COUNT" -gt "$KEEP_BACKUPS" ]; then
  DELETE_COUNT=$((BACKUP_COUNT - KEEP_BACKUPS))
  echo "[$(date)] Removing $DELETE_COUNT old backup(s)..." | tee -a $LOG

  aws s3 ls s3://$BUCKET/backups/ --region $REGION | \
    sort | \
    head -n $DELETE_COUNT | \
    awk '{print $4}' | \
    xargs -I{} aws s3 rm s3://$BUCKET/backups/{} --region $REGION
fi

echo "[$(date)] Backup complete." | tee -a $LOG
