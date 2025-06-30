#!/bin/bash
# Fix multiple SQLAlchemy instances issue

echo "=== Fixing Multiple SQLAlchemy Instances ==="
echo

ssh root@209.38.176.129 << 'SSHEOF'
cd /opt/kuwait-social-ai/backend

# Backup files
echo "Creating backups..."
cp app_factory.py app_factory.py.backup_sqlalchemy
cp models.py models.py.backup_sqlalchemy

# Step 1: Remove SQLAlchemy instance from models.py
echo "1. Fixing models.py..."
# Comment out the SQLAlchemy instantiation
sed -i 's/^db = SQLAlchemy()/# db = SQLAlchemy()  # Moved to models\/__init__.py/' models.py

# Add import from models package
if ! grep -q "from models import db" models.py; then
    sed -i '/from flask_sqlalchemy import SQLAlchemy/a from models import db' models.py
fi

# Step 2: Fix app_factory.py to use the db from models
echo "2. Fixing app_factory.py..."
# Comment out the SQLAlchemy instantiation
sed -i 's/^db = SQLAlchemy()/# db = SQLAlchemy()  # Using instance from models/' app_factory.py

# Add import from models
if ! grep -q "from models import db" app_factory.py; then
    # Add after other imports
    sed -i '/import logging/a from models import db' app_factory.py
fi

# Step 3: Ensure routes are importing db correctly
echo "3. Checking route imports..."
for file in routes/*.py; do
    if grep -q "from app_factory import db" "$file"; then
        echo "  Fixing import in $file"
        sed -i 's/from app_factory import db/from models import db/' "$file"
    fi
    if grep -q "from models.py import db" "$file"; then
        echo "  Fixing import in $file"
        sed -i 's/from models.py import db/from models import db/' "$file"
    fi
done

# Step 4: Verify the changes
echo -e "\n4. Verifying changes..."
echo "SQLAlchemy instances found:"
grep -n "db = SQLAlchemy()" *.py models/*.py | grep -v "^#" | grep -v backup

echo -e "\ndb imports in app_factory.py:"
grep "import db\|from.*import db" app_factory.py

echo -e "\ndb imports in models.py:"
grep "import db\|from.*import db" models.py

# Step 5: Restart backend
echo -e "\n5. Restarting backend..."
cd /opt/kuwait-social-ai
docker-compose restart backend

echo "Waiting for backend to start..."
sleep 15

# Check status
echo -e "\n6. Checking backend status..."
docker-compose ps backend
docker-compose logs --tail=30 backend | grep -E "ERROR|Exception|SQLAlchemy|Running" | tail -20

SSHEOF