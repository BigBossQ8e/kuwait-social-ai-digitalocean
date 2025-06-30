#!/bin/bash

# Setup daily database backup cron job

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKUP_SCRIPT="$SCRIPT_DIR/backup-database.sh"

echo "Setting up daily database backup cron job..."

# Make backup script executable
chmod +x "$BACKUP_SCRIPT"

# Add cron job for daily backup at 2 AM
CRON_JOB="0 2 * * * $BACKUP_SCRIPT >> /var/log/kuwait-social-backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "⚠️  Backup cron job already exists"
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Daily backup cron job added successfully"
    echo "   Backup will run daily at 2:00 AM"
fi

# Create log file with proper permissions
sudo touch /var/log/kuwait-social-backup.log
sudo chown $(whoami):$(whoami) /var/log/kuwait-social-backup.log

echo "✅ Backup setup completed!"
echo ""
echo "To view scheduled jobs: crontab -l"
echo "To view backup logs: tail -f /var/log/kuwait-social-backup.log"
echo "To run backup manually: $BACKUP_SCRIPT"