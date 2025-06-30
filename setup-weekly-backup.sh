#!/bin/bash

# Setup script for weekly GitHub backup

SCRIPT_PATH="/Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/weekly-github-backup.sh"

echo "Setting up weekly GitHub backup..."

# Create a new cron job that runs every Sunday at 2 AM
CRON_JOB="0 2 * * 0 $SCRIPT_PATH >> /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backup.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Weekly backup scheduled!"
echo "The backup will run every Sunday at 2:00 AM"
echo "Logs will be saved to: backup.log"
echo ""
echo "To check your cron jobs: crontab -l"
echo "To remove the backup job: crontab -e (then delete the line)"
echo "To run backup manually: ./weekly-github-backup.sh"