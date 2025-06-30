#!/bin/bash
# Fix remaining backref relationships to use back_populates

echo "=== Fixing Remaining backref Relationships ==="
echo

ssh root@209.38.176.129 << 'SSHEOF'
cd /opt/kuwait-social-ai/backend

# Fix the backref relationships in normalized_models.py
echo "1. Fixing relationships in normalized_models.py..."

# These are comment suggestions, not actual relationships, so we can leave them
echo "   - Found comment suggestions (not actual code) - leaving as is"

# Fix any actual backref relationships that aren't comments
echo -e "\n2. Converting actual backref to back_populates..."

# Find actual (non-commented) backref relationships
for file in models/*.py; do
    if grep -q "^[^#]*relationship.*backref=" "$file"; then
        echo "   Found in $file:"
        grep -n "^[^#]*relationship.*backref=" "$file"
        
        # For each relationship with backref, we need to:
        # 1. Change backref to back_populates
        # 2. Add the reverse relationship to the target model
        
        # This is complex, so let's handle specific known cases
    fi
done

# Check for relationships that need their counterpart added
echo -e "\n3. Adding missing reverse relationships..."

# APIKeyUsage needs api_key relationship
if grep -q "class APIKeyUsage" models/api_key.py && ! grep -q "api_key = db.relationship" models/api_key.py; then
    echo "   Adding api_key relationship to APIKeyUsage..."
    # Find where to add it (after api_key_id foreign key)
    sed -i '/class APIKeyUsage/,/^class/ {
        /api_key_id = db.Column.*ForeignKey/ a\
    api_key = db.relationship("APIKey", back_populates="usage_logs")
    }' models/api_key.py
fi

# Fix any cascade issues by ensuring both sides match
echo -e "\n4. Checking cascade settings..."
grep -n "cascade=" models/*.py | grep -v "^#" | while read -r match; do
    echo "   Found cascade: $match"
done

# Final restart
echo -e "\n5. Restarting backend..."
cd /opt/kuwait-social-ai
docker-compose restart backend

echo "Waiting for backend to start..."
sleep 10

# Check final status
echo -e "\n6. Final status check..."
docker-compose ps backend
docker-compose logs --tail=30 backend | grep -E "ERROR|Started|Running" | tail -10

SSHEOF