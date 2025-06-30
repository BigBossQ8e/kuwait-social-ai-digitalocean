#!/bin/bash
# Fix ALL SQLAlchemy relationship errors properly

echo "=== Fixing ALL SQLAlchemy Model Relationships ==="
echo

ssh root@209.38.176.129 << 'SSHEOF'
cd /opt/kuwait-social-ai/backend

# First, let's find all the relationship definitions that need fixing
echo "Analyzing all relationship definitions..."

# Check what models exist in normalized_models.py
echo -e "\n1. Finding all relationships in normalized_models.py:"
grep -n "db.relationship" models/normalized_models.py

echo -e "\n2. Checking for CompetitorTopHashtag model definition:"
grep -A10 "class CompetitorTopHashtag" models/normalized_models.py

echo -e "\n3. Checking for CompetitorTopPost model definition:"
grep -A10 "class CompetitorTopPost" models/normalized_models.py

echo -e "\n4. Checking for CompetitorAudienceDemographic model definition:"
grep -A10 "class CompetitorAudienceDemographic" models/normalized_models.py

# Now let's apply the fixes
echo -e "\n5. Applying fixes..."

# Fix 1: Uncomment the relationships we commented out earlier
sed -i "s/# top_hashtags = db.relationship/top_hashtags = db.relationship/g" models/normalized_models.py
sed -i "s/# top_posts = db.relationship/top_posts = db.relationship/g" models/normalized_models.py
sed -i "s/# audience_demographics = db.relationship/audience_demographics = db.relationship/g" models/normalized_models.py

# Fix 2: Update relationships to use back_populates
sed -i "s/top_hashtags = db.relationship('CompetitorTopHashtag', backref='analysis', lazy='dynamic')/top_hashtags = db.relationship('CompetitorTopHashtag', back_populates='analysis', lazy='dynamic')/" models/normalized_models.py
sed -i "s/top_posts = db.relationship('CompetitorTopPost', backref='analysis', lazy='dynamic')/top_posts = db.relationship('CompetitorTopPost', back_populates='analysis', lazy='dynamic')/" models/normalized_models.py
sed -i "s/audience_demographics = db.relationship('CompetitorAudienceDemographic', backref='analysis', lazy='dynamic')/audience_demographics = db.relationship('CompetitorAudienceDemographic', back_populates='analysis', lazy='dynamic')/" models/normalized_models.py

# Fix 3: Add the missing foreign keys and relationships to the target models
# For CompetitorTopHashtag
if grep -q "class CompetitorTopHashtag" models/normalized_models.py; then
    echo "Adding analysis_id to CompetitorTopHashtag..."
    # Add after the hashtag column
    sed -i '/class CompetitorTopHashtag/,/^class/ {
        /count = db.Column/ a\
    analysis_id = db.Column(db.Integer, db.ForeignKey("competitor_analysis.id"), nullable=False)\
    analysis = db.relationship("CompetitorAnalysis", back_populates="top_hashtags")
    }' models/normalized_models.py
fi

# For CompetitorTopPost
if grep -q "class CompetitorTopPost" models/normalized_models.py; then
    echo "Adding analysis_id to CompetitorTopPost..."
    sed -i '/class CompetitorTopPost/,/^class/ {
        /metrics = db.Column/ a\
    analysis_id = db.Column(db.Integer, db.ForeignKey("competitor_analysis.id"), nullable=False)\
    analysis = db.relationship("CompetitorAnalysis", back_populates="top_posts")
    }' models/normalized_models.py
fi

# For CompetitorAudienceDemographic
if grep -q "class CompetitorAudienceDemographic" models/normalized_models.py; then
    echo "Adding analysis_id to CompetitorAudienceDemographic..."
    sed -i '/class CompetitorAudienceDemographic/,/^class/ {
        /percentage = db.Column/ a\
    analysis_id = db.Column(db.Integer, db.ForeignKey("competitor_analysis.id"), nullable=False)\
    analysis = db.relationship("CompetitorAnalysis", back_populates="audience_demographics")
    }' models/normalized_models.py
fi

echo -e "\n6. Verifying the fixes:"
echo "CompetitorAnalysis relationships:"
grep -A1 "top_hashtags = db.relationship\|top_posts = db.relationship\|audience_demographics = db.relationship" models/normalized_models.py

echo -e "\nChecking for analysis_id in related models:"
grep -B2 -A2 "analysis_id = db.Column" models/normalized_models.py

echo -e "\n7. Restarting backend..."
cd /opt/kuwait-social-ai
docker-compose restart backend

echo "Waiting for backend to start..."
sleep 10

# Check if backend started successfully
docker-compose ps backend
echo -e "\nChecking for errors..."
docker-compose logs --tail=50 backend | grep -E "Running on|Started|ERROR|NoForeignKeysError" || echo "No errors found!"

SSHEOF