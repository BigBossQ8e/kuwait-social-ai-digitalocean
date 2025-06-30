#!/bin/bash
# Fix the missing relationships causing backend errors

echo "=== Fixing Missing Model Relationships ==="
echo

ssh root@209.38.176.129 << 'SSHEOF'
cd /opt/kuwait-social-ai/backend

# Backup files
echo "Creating backups..."
cp models/engagement_models.py models/engagement_models.py.backup_fix
cp models/missing_models.py models/missing_models.py.backup_fix 2>/dev/null || true

# Fix 1: Add original_message relationship to MessageThread
echo "Fixing MessageThread relationship..."
# Find the MessageThread class and add the relationship after sent_at column
sed -i '/class MessageThread/,/^class/ {
    /sent_at = db.Column/ a\
    \
    # Relationship back to UnifiedInboxMessage\
    original_message = db.relationship("UnifiedInboxMessage", back_populates="thread_messages")
}' models/engagement_models.py

# Fix 2: Find and comment out the CompetitorStrategyMetric relationship
echo "Looking for CompetitorStrategyMetric reference..."
# Search all model files for this reference
for file in models/*.py; do
    if grep -q "CompetitorStrategyMetric" "$file"; then
        echo "Found CompetitorStrategyMetric in $file"
        # Comment out any relationship referencing CompetitorStrategyMetric
        sed -i 's/.*relationship.*CompetitorStrategyMetric.*$/# &/' "$file"
    fi
done

# Alternative: Check if it's in the imports or somewhere else
grep -r "CompetitorStrategyMetric" . --include="*.py" | grep -v __pycache__ | grep -v backup

echo -e "\nVerifying fixes..."
echo "1. MessageThread fix:"
grep -A2 "original_message = db.relationship" models/engagement_models.py || echo "Fix not found - may need manual edit"

echo -e "\n2. Restarting backend..."
cd /opt/kuwait-social-ai
docker-compose restart backend

echo "Waiting for backend to start..."
sleep 10

# Check if backend started successfully
docker-compose ps backend
echo -e "\nChecking for errors..."
docker-compose logs --tail=50 backend | grep -E "ERROR|Exception|Started|Running" | tail -20

SSHEOF