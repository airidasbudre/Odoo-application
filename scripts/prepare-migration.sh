#!/bin/bash
set -e

# ── Config ────────────────────────────────────────────────
BUCKET="odoo-backups-623859664395"
REGION="eu-north-1"
LOG="/home/ubuntu/migration-prep.log"
# ──────────────────────────────────────────────────────────

if [ -z "$1" ]; then
  echo "Usage: ./prepare-migration.sh <NEW_AWS_ACCOUNT_ID>"
  echo "Example: ./prepare-migration.sh 112233445566"
  exit 1
fi

NEW_ACCOUNT_ID=$1

echo "[$(date)] Starting migration preparation..." | tee -a $LOG

# ── Step 1: Backup database ───────────────────────────────
echo "[$(date)] Step 1/4 - Creating fresh database backup..." | tee -a $LOG
/home/ubuntu/scripts/backup.sh
LATEST=$(aws s3 ls s3://$BUCKET/backups/ --region $REGION | sort | tail -1 | awk '{print $4}')
echo "[$(date)] Latest backup: $LATEST" | tee -a $LOG

# ── Step 2: Grant new account access to S3 backups ───────
echo "[$(date)] Step 2/4 - Granting cross-account S3 access to account $NEW_ACCOUNT_ID..." | tee -a $LOG
aws s3api put-bucket-policy \
  --bucket $BUCKET \
  --policy "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Effect\": \"Allow\",
      \"Principal\": {\"AWS\": \"arn:aws:iam::${NEW_ACCOUNT_ID}:root\"},
      \"Action\": [\"s3:GetObject\", \"s3:ListBucket\"],
      \"Resource\": [
        \"arn:aws:s3:::${BUCKET}\",
        \"arn:aws:s3:::${BUCKET}/backups/*\"
      ]
    }]
  }"
echo "[$(date)] S3 cross-account access granted." | tee -a $LOG

# ── Step 3: Export current config ────────────────────────
echo "[$(date)] Step 3/4 - Exporting current configuration..." | tee -a $LOG

CURRENT_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
INSTANCE_TYPE=$(curl -s http://169.254.169.254/latest/meta-data/instance-type)

cat > /home/ubuntu/migration-info.txt <<EOF
Migration Info - $(date)
========================
Source Account:   $(aws sts get-caller-identity --query Account --output text)
Target Account:   $NEW_ACCOUNT_ID
Current Server:   $INSTANCE_ID ($INSTANCE_TYPE)
Current IP:       $CURRENT_IP
Latest Backup:    s3://$BUCKET/backups/$LATEST
Backup Region:    $REGION
Terraform State:  s3://$BUCKET/odoo/terraform.tfstate
========================
Next Steps:
1. In new AWS account - run: terraform apply
2. Restore backup:    aws s3 cp s3://$BUCKET/backups/$LATEST - | gunzip | docker exec -i odoo-db psql -U odoo postgres
3. Start services:    docker compose up -d
4. Verify Odoo works at new server IP
5. Update DNS to new server IP
6. Decommission this server
EOF

echo "[$(date)] Config exported to /home/ubuntu/migration-info.txt" | tee -a $LOG

# ── Step 4: Upload migration info to S3 ──────────────────
echo "[$(date)] Step 4/4 - Uploading migration info to S3..." | tee -a $LOG
aws s3 cp /home/ubuntu/migration-info.txt \
  s3://$BUCKET/migration/migration-info-$(date +%Y%m%d-%H%M%S).txt \
  --region $REGION

echo "" | tee -a $LOG
echo "========================================" | tee -a $LOG
echo "Migration preparation complete!" | tee -a $LOG
echo "Latest backup: $LATEST" | tee -a $LOG
echo "New account $NEW_ACCOUNT_ID can now access S3 backups." | tee -a $LOG
echo "See /home/ubuntu/migration-info.txt for full details." | tee -a $LOG
echo "========================================" | tee -a $LOG
