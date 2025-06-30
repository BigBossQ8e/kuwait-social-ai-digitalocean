#!/bin/bash
# Fix SQLAlchemy relationship errors in original backend

echo "=== Fixing SQLAlchemy Model Relationships ==="
echo

# SSH connection details
SERVER="209.38.176.129"
BACKEND_PATH="/opt/kuwait-social-ai/backend"

# Option 1: Quick fix - Comment out problematic relationships
echo "Applying quick fix - commenting out problematic relationships..."

ssh root@$SERVER << 'EOF'
cd /opt/kuwait-social-ai/backend

# Backup original files
cp models/missing_models.py models/missing_models.py.backup
cp models/normalized_models.py models/normalized_models.py.backup 2>/dev/null || true

# Fix Campaign.posts relationship in missing_models.py
sed -i 's/posts = db.relationship/# posts = db.relationship/g' models/missing_models.py

# Fix any CompetitorAnalysis relationships if they exist
if [ -f models/normalized_models.py ]; then
    sed -i 's/top_hashtags = db.relationship/# top_hashtags = db.relationship/g' models/normalized_models.py
    sed -i 's/top_posts = db.relationship/# top_posts = db.relationship/g' models/normalized_models.py
fi

echo "Fixes applied. Restarting backend..."
cd /opt/kuwait-social-ai
docker-compose restart backend

echo "Waiting for backend to start..."
sleep 10

# Check if backend is running
docker-compose ps backend
docker-compose logs --tail=50 backend | grep -i "error\|running on\|started"
EOF

echo
echo "Fix applied. You can test login at https://kwtsocial.com"
echo "Credentials: admin@kwtsocial.com / AdminPass123!"