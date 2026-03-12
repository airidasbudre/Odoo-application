# Odoo Cross-Account AWS Migration Report

## Summary
Successfully migrated Odoo 18 application from AWS Account A (723977204493, us-east-1)
to AWS Account B (623859664395, eu-north-1).

---

## What Was Migrated

| Component | Source | Destination |
|-----------|--------|-------------|
| EC2 Instance | us-east-1 (t3.small) | eu-north-1 (t3.small) |
| PostgreSQL Database | odoo_db | odoo_db |
| Odoo Filestore | odoo-web-data volume | odoo-web-data volume |
| Custom Addons | /home/ubuntu/addons | /home/ubuntu/addons |
| App Config | docker-compose, .env | docker-compose, .env |
| Monitoring | Prometheus, Grafana | Prometheus, Grafana |

---

## Migration Steps Performed

1. **Created new AWS account** and configured IAM user with CLI access
2. **Created S3 bucket** `odoo-terraform-state-623859664395` in eu-north-1 for Terraform state
3. **Created DynamoDB table** `terraform-state-lock` for state locking
4. **Ran prepare-migration.sh** — backed up database and granted cross-account S3 access
5. **Configured new-account AWS profile** on old server
6. **Ran Terraform** with new account credentials to provision EC2, VPC, security groups
7. **Copied app files** — docker-compose, .env, monitoring, scripts via scp
8. **Started Docker containers** on new server
9. **Backed up correct database** (odoo_db) and copied to new server
10. **Created odoo_db** on new server and restored backup
11. **Copied filestore** from old container and fixed nested directory issue
12. **Copied custom addons** (ica_website_theme, ica_web_responsive, etc.)
13. **Reset user password** and verified login

---

## What Made It Complicated

### 1. Wrong database backed up
The backup script was configured with `DB_NAME="postgres"` instead of `DB_NAME="odoo_db"`.
The actual Odoo database was `odoo_db` — discovered only after migration when Odoo
showed the "create database" screen instead of the login page.

**Fix applied:** Updated `scripts/backup.sh` to use correct database name.

### 2. Filestore not included in migration
Only the PostgreSQL database was migrated initially. Odoo stores attachments,
images, and compiled CSS/JS assets in a separate Docker volume (`odoo-web-data`).
This caused the app to load without styles and with broken images.

**Fix applied:** Manually copied filestore using `docker cp` and `scp`.

### 3. Filestore copied to wrong path
When copying the filestore, it landed in a nested directory:
`/var/lib/odoo/filestore/odoo_db/odoo_filestore/` instead of
`/var/lib/odoo/filestore/odoo_db/`. Required root access inside container to fix.

### 4. Custom addons not copied
The `addons/` folder was not included in the initial file copy. This caused
404 errors for custom theme assets (`ica_website_theme`). The addons folder
had permission issues requiring `sudo tar` to copy correctly.

### 5. AWS credentials not on new server
The new EC2 instance had no AWS credentials, blocking S3 operations.
Workaround: downloaded backup locally then `scp`'d it directly to new server.

### 6. Elastic IP cannot transfer between accounts
Unlike same-account migrations where the EIP stays the same, cross-account
migration requires a new EIP and DNS update. Users must update any hardcoded
IPs or DNS records manually.

### 7. SSH key differences between accounts
AWS key pairs are account-specific. The old `.pem` key doesn't work on the
new account's EC2. Required copying the new `.pem` from laptop to old server
with correct permissions (chmod 400).

### 8. Ansible backup running on wrong server
Initial Ansible setup pointed to `34.225.138.32` (an empty EC2) while
containers were running on `172.31.11.228`. Fixed by using `localhost`
connection in inventory.ini.

### 9. Backend S3 region mismatch
Terraform backend was initially configured for us-east-1 but infrastructure
moved to eu-north-1. Required `-reconfigure` flag and `AWS_PROFILE` on every
Terraform command.

---

## Improvements for Future Migrations

### 1. Complete backup script
The backup script should always include all three Odoo components:
```bash
# Database
docker exec odoo-db pg_dump -U odoo odoo_db | gzip > db.sql.gz

# Filestore
docker cp odoo-app:/var/lib/odoo/filestore/odoo_db ./filestore
tar czf filestore.tar.gz filestore/

# Upload both to S3
aws s3 cp db.sql.gz s3://bucket/backups/
aws s3 cp filestore.tar.gz s3://bucket/backups/
```

### 2. Single migration script
Create one script that handles everything end-to-end:
```
migrate.sh <new_account_id> <new_server_ip>
  → backup database + filestore
  → copy all files
  → restore on new server
  → verify health
```

### 3. IAM role on EC2 instead of credentials
Attach an IAM role to EC2 at Terraform provisioning time so the server
automatically has S3 access without manual credential configuration.
Add to `modules/ec2/main.tf`:
```hcl
iam_instance_profile = aws_iam_instance_profile.odoo.name
```

### 4. Docker volume backup in CI/CD
Add filestore backup to the GitHub Actions scheduled job alongside
the database backup so both are always in S3 and in sync.

### 5. Health check after migration
Automate verification steps:
```bash
# Check Odoo responds
curl -f http://$NEW_IP:8069/web/database/selector

# Check database has data
docker exec odoo-db psql -U odoo -d odoo_db -c "SELECT count(*) FROM res_users;"

# Check filestore has files
docker exec odoo-app ls /var/lib/odoo/filestore/odoo_db/ | wc -l
```

### 6. Document database name
Store the database name in `.env` so it's never hardcoded differently
across scripts:
```bash
ODOO_DB_NAME=odoo_db
```

### 7. Test migration on staging first
Always run the full migration to a staging environment before production
to catch issues like wrong database names, missing addons, permission errors.

---

## New Server Details

| Detail | Value |
|--------|-------|
| AWS Account | 623859664395 |
| Region | eu-north-1 (Stockholm) |
| Server IP | 51.20.15.18 |
| Odoo URL | http://51.20.15.18:8069 |
| Grafana URL | http://51.20.15.18:3000 |
| Instance Type | t3.small |
| OS | Ubuntu 22.04 LTS |
| Login | pakelkdrona@gmail.com |

---

## Post-Migration Checklist

- [x] Odoo accessible at new IP
- [x] Styles and images loading correctly
- [x] Database restored with all data
- [x] Custom addons working
- [x] User login working
- [ ] Update GitHub secrets (PRODUCTION_SERVER_IP, SSH_PRIVATE_KEY)
- [ ] Update DNS to point to 51.20.15.18
- [ ] Set up backup automation on new server
- [ ] Destroy old server to stop billing
- [ ] Enable Terraform remote backend for new account
