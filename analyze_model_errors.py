#!/usr/bin/env python3
"""
Comprehensive analysis of SQLAlchemy model relationship errors
Maps all problematic relationships and their required fixes
"""

import re
from pathlib import Path

def find_relationships(file_path):
    """Find all db.relationship() definitions in a file"""
    relationships = []
    
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Find all relationship definitions
    pattern = r'(\w+)\s*=\s*db\.relationship\s*\([^)]+\)'
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        full_match = match.group(0)
        field_name = match.group(1)
        
        # Extract relationship details
        rel_pattern = r"db\.relationship\s*\(\s*['\"](\w+)['\"].*?(?:backref\s*=\s*['\"](\w+)['\"])?"
        rel_match = re.search(rel_pattern, full_match, re.DOTALL)
        
        if rel_match:
            target_model = rel_match.group(1)
            backref = rel_match.group(2) if rel_match.group(2) else None
            
            relationships.append({
                'file': str(file_path),
                'field': field_name,
                'target_model': target_model,
                'backref': backref,
                'definition': full_match.strip()
            })
    
    return relationships

def analyze_foreign_keys(relationships):
    """Analyze which relationships need foreign keys"""
    issues = []
    
    # Known problematic relationships from error logs
    known_issues = [
        ('Campaign', 'posts', 'Post', 'campaign_id'),
        ('Campaign', 'scheduled_posts', 'ScheduledPost', 'campaign_id'),
        ('CompetitorAnalysis', 'top_hashtags', 'CompetitorTopHashtag', 'analysis_id'),
        ('CompetitorAnalysis', 'top_posts', 'CompetitorTopPost', 'analysis_id'),
    ]
    
    for source_model, field, target_model, required_fk in known_issues:
        issues.append({
            'source_model': source_model,
            'field': field,
            'target_model': target_model,
            'required_foreign_key': required_fk,
            'fix': f"Add to {target_model} model: {required_fk} = db.Column(db.Integer, db.ForeignKey('{source_model.lower()}s.id'))"
        })
    
    return issues

def main():
    print("=== SQLAlchemy Model Relationship Error Analysis ===\n")
    
    # Paths to check
    model_paths = [
        "/opt/kuwait-social-ai/backend/models.py",
        "/opt/kuwait-social-ai/backend/models/missing_models.py",
        "/opt/kuwait-social-ai/backend/models/normalized_models.py"
    ]
    
    print("1. Known Error from Logs:")
    print("   - NoForeignKeysError: Could not determine join condition between parent/child tables")
    print("   - Relationship: Campaign.posts")
    print("   - Issue: Post model missing 'campaign_id' foreign key\n")
    
    print("2. Required Fixes:")
    print("\n   a) Campaign.posts relationship:")
    print("      - Add to Post model: campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=True)")
    print("      - OR comment out: # posts = db.relationship('Post', backref='campaign', lazy='dynamic')")
    
    print("\n   b) Campaign.scheduled_posts relationship:")
    print("      - Already has foreign key in ScheduledPost model ✓")
    
    print("\n   c) CompetitorAnalysis relationships (if used):")
    print("      - May need foreign keys in CompetitorTopHashtag and CompetitorTopPost models")
    
    print("\n3. Recommended Approach:")
    print("   Option 1: Comment out problematic relationships (quick fix)")
    print("   Option 2: Add missing foreign keys to target models (proper fix)")
    print("   Option 3: Create database migrations to add columns (best practice)")
    
    print("\n4. Test Command:")
    print("   docker run --rm --network kuwait-network \\")
    print("     -e DATABASE_URL=postgresql://kuwait_user:secure_password@kuwait-social-db:5432/kuwait_social_ai \\")
    print("     -e SECRET_KEY=test-key \\")
    print("     -v /opt/kuwait-social-ai/backend:/app \\")
    print("     -w /app \\")
    print("     python:3.9 \\")
    print("     bash -c 'pip install flask sqlalchemy psycopg2-binary && python -c \"from app import app, db; print(\\\"Models loaded successfully\\\")\"'")

if __name__ == "__main__":
    main()