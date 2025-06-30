#!/bin/bash

# Kuwait Social AI - Database Backup Script
# This script creates daily backups of the PostgreSQL database

set -e

# Configuration
BACKUP_DIR="/var/backups/kuwait-social-ai"
DB_NAME="kuwait_social"
DB_USER="kuwait_user"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${DB_NAME}_${DATE}.sql.gz"
RETENTION_DAYS=7

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Kuwait Social AI database backup...${NC}"

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Creating backup directory: $BACKUP_DIR"
    sudo mkdir -p "$BACKUP_DIR"
    sudo chown $(whoami):$(whoami) "$BACKUP_DIR"
fi

# Perform backup
echo "Backing up database: $DB_NAME"
if pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    echo -e "${GREEN}✅ Backup created successfully: $BACKUP_FILE${NC}"
    
    # Get file size
    SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    echo "Backup size: $SIZE"
else
    echo -e "${RED}❌ Backup failed!${NC}"
    exit 1
fi

# Remove old backups
echo "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "backup_${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# List current backups
echo -e "\n${GREEN}Current backups:${NC}"
ls -lh "$BACKUP_DIR"/backup_${DB_NAME}_*.sql.gz 2>/dev/null | tail -5

# Optional: Upload to cloud storage
# Uncomment and configure if using cloud backup
# echo "Uploading to cloud storage..."
# aws s3 cp "$BACKUP_FILE" s3://your-backup-bucket/kuwait-social-ai/

echo -e "\n${GREEN}✅ Backup process completed!${NC}"