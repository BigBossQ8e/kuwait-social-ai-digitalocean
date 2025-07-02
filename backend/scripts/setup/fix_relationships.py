#!/usr/bin/env python3
"""Fix relationship issues in models"""

import os
import re

def fix_normalized_models():
    """Fix the normalized_models.py file"""
    file_path = 'models/normalized_models.py'
    
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Comment out problematic relationships
    replacements = [
        # HashtagStrategy relationships
        (r"trending_hashtags = db\.relationship\('TrendingHashtag', backref='strategy', lazy='dynamic'\)",
         "# trending_hashtags = db.relationship('TrendingHashtag', backref='strategy', lazy='dynamic')  # FIX: Missing FK"),
        
        (r"recommended_combinations = db\.relationship\('HashtagCombination', backref='strategy', lazy='dynamic'\)",
         "# recommended_combinations = db.relationship('HashtagCombination', backref='strategy', lazy='dynamic')  # FIX: Missing FK"),
        
        # CompetitorDetail relationships
        (r"top_hashtags = db\.relationship\('CompetitorTopHashtag', backref='competitor_detail', lazy='dynamic'\)",
         "# top_hashtags = db.relationship('CompetitorTopHashtag', backref='competitor_detail', lazy='dynamic')  # FIX: Missing FK"),
        
        (r"top_posts = db\.relationship\('CompetitorTopPost', backref='competitor_detail', lazy='dynamic'\)",
         "# top_posts = db.relationship('CompetitorTopPost', backref='competitor_detail', lazy='dynamic')  # FIX: Missing FK"),
        
        (r"audience_demographics = db\.relationship\('CompetitorAudienceDemographic', backref='competitor_detail', lazy='dynamic'\)",
         "# audience_demographics = db.relationship('CompetitorAudienceDemographic', backref='competitor_detail', lazy='dynamic')  # FIX: Missing FK"),
        
        # ClientAnalysisDetail relationships
        (r"trending_hashtags = db\.relationship\('TrendingHashtag', backref='client_detail', lazy='dynamic'\)",
         "# trending_hashtags = db.relationship('TrendingHashtag', backref='client_detail', lazy='dynamic')  # FIX: Missing FK"),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Fixed {file_path}")

def check_other_issues():
    """Check for other potential relationship issues"""
    print("\nChecking for other relationship issues...")
    
    model_files = [
        'models/engagement_models.py',
        'models/hashtag_models.py',
        'models/competitor_analysis_models.py'
    ]
    
    issues = []
    
    for file_path in model_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for relationships that might have issues
            relationships = re.findall(r"(\w+)\s*=\s*db\.relationship\('(\w+)'.*backref='(\w+)'", content)
            
            for rel_name, target_model, backref_name in relationships:
                # Check if it's a potentially problematic relationship
                if 'Hashtag' in target_model or 'Trending' in target_model:
                    issues.append(f"{file_path}: {rel_name} -> {target_model} (backref: {backref_name})")
    
    if issues:
        print("\nPotential relationship issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("No additional relationship issues found.")

def main():
    print("=== Fixing Model Relationships ===\n")
    
    # Fix the main issues in normalized_models.py
    fix_normalized_models()
    
    # Check for other issues
    check_other_issues()
    
    print("\n✓ Relationship fixes complete!")
    print("\nNOTE: After fixing, you may need to:")
    print("1. Drop and recreate affected tables")
    print("2. Or add proper foreign key columns to link the tables")

if __name__ == "__main__":
    main()