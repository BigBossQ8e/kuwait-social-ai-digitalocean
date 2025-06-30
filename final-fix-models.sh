#!/bin/bash

echo "🔧 Final comprehensive model fix..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "1. Backing up current models.py..."
cp models.py models.py.backup-$(date +%Y%m%d-%H%M%S)

echo "2. Adding all missing models from backups..."
# Add remaining kuwait features models
for model in KuwaitHistoricalFact KuwaitTrendingTopic KuwaitBusinessDirectory CulturalGuideline LocalInfluencer; do
    if ! grep -q "class $model" models.py; then
        echo "  Adding $model..."
        grep -A30 "class $model" models.backup_factory_pattern/kuwait_features_models.py >> models.py
        echo "" >> models.py
    fi
done

# Check for any other missing models
echo "3. Checking for other missing imports..."
python3 << 'PYTHON'
import re

# Read current error log
try:
    with open('logs/error.log', 'r') as f:
        errors = f.read()
    
    # Find ImportError patterns
    missing = re.findall(r"cannot import name '(\w+)' from 'models'", errors)
    if missing:
        print(f"Found missing models: {set(missing)}")
except:
    pass

# Check if all engagement models are present
needed = ['CommentTemplate', 'UnifiedInboxMessage', 'MessageThread', 
          'ResponseMetrics', 'CustomerProfile', 'EngagementAutomation']
with open('models.py', 'r') as f:
    content = f.read()
    
for model in needed:
    if f'class {model}' not in content:
        print(f"Still missing: {model}")
PYTHON

echo "4. Fixing any duplicate table definitions..."
# Remove duplicates by checking line by line
python3 << 'PYTHON'
seen_tables = set()
lines = []
with open('models.py', 'r') as f:
    for line in f:
        if '__tablename__' in line:
            table_name = line.split("'")[1]
            if table_name in seen_tables:
                print(f"Skipping duplicate table: {table_name}")
                # Skip until next class or end
                continue
            seen_tables.add(table_name)
        lines.append(line)

# Write back
with open('models.py.clean', 'w') as f:
    f.writelines(lines)
PYTHON

if [ -f models.py.clean ]; then
    mv models.py.clean models.py
fi

echo "5. Starting backend..."
pkill -f gunicorn
sleep 2

export $(grep -v '^#' .env | xargs)
/usr/local/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --daemon \
    --pid /tmp/gunicorn.pid \
    --error-logfile logs/error.log \
    wsgi:app

sleep 7

echo "6. Final status check..."
if ps -p $(cat /tmp/gunicorn.pid 2>/dev/null) > /dev/null 2>&1; then
    echo "✅ Backend is running!"
    echo "Testing API..."
    curl -s http://localhost:5000/api/health || echo "API not responding"
else
    echo "❌ Backend failed"
    echo "Latest errors:"
    tail -15 logs/error.log | grep -E "Error|Import|Module"
fi

ENDSSH

echo ""
echo "7. External test..."
curl -s https://kwtsocial.com/api/health