#!/usr/bin/env python3
"""
Fix SQLAlchemy ORM NoForeignKeysError by adding proper foreign keys and back_populates
"""

# Fix 1: Add campaign_id to Post model
post_model_fix = """
# Add this to the Post model in models.py:
campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=True)
campaign = db.relationship('Campaign', back_populates='posts')
"""

# Fix 2: Update Campaign model to use back_populates
campaign_model_fix = """
# In models/missing_models.py, update the Campaign model:
# Change this:
posts = db.relationship('Post', backref='campaign', lazy='dynamic')

# To this:
posts = db.relationship('Post', back_populates='campaign', lazy='dynamic')
"""

# Complete fix script
fix_script = """
#!/bin/bash
echo "Applying SQLAlchemy ORM relationship fixes..."

# SSH to server and apply fixes
ssh root@209.38.176.129 << 'SSHEOF'
cd /opt/kuwait-social-ai/backend

# Backup files
cp models.py models.py.backup_orm
cp models/missing_models.py models/missing_models.py.backup_orm

# Fix 1: Add campaign_id and relationship to Post model
echo "Adding campaign_id to Post model..."
# Find the Post class and add the foreign key after other columns
sed -i '/class Post(db.Model):/,/def __repr__/ {
    /updated_at = db.Column/ a\\
    \\
    # Campaign relationship\\
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=True)\\
    campaign = db.relationship("Campaign", back_populates="posts")
}' models.py

# Fix 2: Update Campaign model to use back_populates
echo "Updating Campaign model relationship..."
sed -i "s/posts = db.relationship('Post', backref='campaign', lazy='dynamic')/posts = db.relationship('Post', back_populates='campaign', lazy='dynamic')/" models/missing_models.py

# Fix 3: Also update ScheduledPost relationship if needed
sed -i "s/scheduled_posts = db.relationship('ScheduledPost', backref='campaign', lazy='dynamic')/scheduled_posts = db.relationship('ScheduledPost', back_populates='campaign', lazy='dynamic')/" models/missing_models.py

# Add corresponding relationship to ScheduledPost if missing
grep -q "campaign = db.relationship" models/missing_models.py || sed -i '/class ScheduledPost(db.Model):/,/def __repr__/ {
    /campaign_id = db.Column/ a\\
    campaign = db.relationship("Campaign", back_populates="scheduled_posts")
}' models/missing_models.py

echo "Fixes applied. Restarting backend..."
cd /opt/kuwait-social-ai
docker-compose restart backend

echo "Waiting for backend to start..."
sleep 10

# Check if backend started successfully
docker-compose ps backend
echo ""
echo "Checking for errors..."
docker-compose logs --tail=50 backend | grep -E "Running on|ERROR|NoForeignKeysError" || echo "No errors found!"

SSHEOF
"""

print("=== SQLAlchemy ORM Relationship Fix ===")
print("\nThe fix involves:")
print("1. Adding campaign_id foreign key to Post model")
print("2. Adding campaign relationship with back_populates to Post model")
print("3. Updating Campaign.posts to use back_populates instead of backref")
print("\nThis creates a proper bidirectional relationship that SQLAlchemy can understand.")
print("\nExecute this command to apply the fix:")
print(fix_script)