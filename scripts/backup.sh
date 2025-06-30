#!/bin/bash
#
# Kuwait Social AI - DigitalOcean Backup Script
# Manages backups for database and uploads
#

set -euo pipefail

# Configuration
BACKUP_DIR="/opt/kuwait-social-ai/backups"
S3_BUCKET="${S3_BUCKET:-}"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}Starting backup process...${NC}"

# 1. Database backup
echo -e "\n${YELLOW}Backing up database...${NC}"
docker exec kuwait_social_ai_postgres pg_dump -U kuwait_user kuwait_social_ai | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# 2. Uploads backup
echo -e "${YELLOW}Backing up uploads...${NC}"
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C /opt/kuwait-social-ai uploads/ 2>/dev/null || true

# 3. Configuration backup
echo -e "${YELLOW}Backing up configuration...${NC}"
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C /opt/kuwait-social-ai .env docker-compose.yml 2>/dev/null || true

# 4. Create snapshot via DO API (if configured)
if command -v doctl &> /dev/null && doctl auth list &> /dev/null; then
    echo -e "${YELLOW}Creating DigitalOcean snapshot...${NC}"
    DROPLET_ID=$(curl -s http://169.254.169.254/metadata/v1/id 2>/dev/null || echo "")
    if [[ ! -z "$DROPLET_ID" ]]; then
        doctl compute droplet-action snapshot $DROPLET_ID \
            --snapshot-name "kuwait-social-ai-auto-$DATE" \
            --wait || echo "Snapshot creation failed"
    fi
fi

# 5. Upload to S3 (if configured)
if [[ ! -z "$S3_BUCKET" ]] && command -v aws &> /dev/null; then
    echo -e "${YELLOW}Uploading to S3...${NC}"
    aws s3 sync "$BACKUP_DIR" "s3://$S3_BUCKET/backups/" \
        --exclude "*" \
        --include "*_$DATE.*"
fi

# 6. Clean old backups
echo -e "${YELLOW}Cleaning old backups...${NC}"
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

# 7. Clean old DO snapshots (keep last 3)
if command -v doctl &> /dev/null; then
    echo -e "${YELLOW}Cleaning old snapshots...${NC}"
    doctl compute snapshot list \
        --format ID,Name,CreatedAt \
        --no-header | \
        grep "kuwait-social-ai-auto" | \
        sort -k3 -r | \
        tail -n +4 | \
        awk '{print $1}' | \
        xargs -I {} doctl compute snapshot delete {} --force 2>/dev/null || true
fi

# Calculate backup sizes
DB_SIZE=$(du -h "$BACKUP_DIR/db_$DATE.sql.gz" | cut -f1)
UPLOAD_SIZE=$(du -h "$BACKUP_DIR/uploads_$DATE.tar.gz" 2>/dev/null | cut -f1 || echo "0")
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

# Summary
echo -e "\n${GREEN}✅ Backup completed successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Database backup: $DB_SIZE"
echo "Uploads backup: $UPLOAD_SIZE"
echo "Total backup size: $TOTAL_SIZE"
echo "Backup location: $BACKUP_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Log the backup
echo "[$(date)] Backup completed - DB: $DB_SIZE, Uploads: $UPLOAD_SIZE" >> /var/log/kuwait-social-ai/backup.log