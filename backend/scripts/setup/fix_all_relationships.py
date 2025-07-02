#!/usr/bin/env python3
"""
Comprehensive fix for all SQLAlchemy relationship issues
Based on the analysis showing 12 missing relationships
"""

import re

def apply_comprehensive_fixes():
    print("Applying comprehensive relationship fixes to models.py...")
    
    with open('models.py', 'r') as f:
        content = f.read()
    
    fixes_applied = []
    
    # Fix 1: Add user relationship to Admin model
    admin_match = re.search(r'(class Admin\(db\.Model\):.*?)(?=class|\Z)', content, re.DOTALL)
    if admin_match and 'user = db.relationship' not in admin_match.group():
        # Find where to insert (after user_id column)
        admin_section = admin_match.group()
        insert_point = admin_section.find('user_id = db.Column')
        if insert_point != -1:
            # Find the end of the line
            line_end = admin_section.find('\n', insert_point)
            new_section = (
                admin_section[:line_end + 1] +
                '    user = db.relationship("User", back_populates="admin_profile")\n' +
                admin_section[line_end + 1:]
            )
            content = content.replace(admin_section, new_section)
            fixes_applied.append("Added user relationship to Admin model")
    
    # Fix 2: Add user relationship to Client model
    client_match = re.search(r'(class Client\(db\.Model\):.*?)(?=class|\Z)', content, re.DOTALL)
    if client_match and 'user = db.relationship' not in client_match.group():
        client_section = client_match.group()
        insert_point = client_section.find('user_id = db.Column')
        if insert_point != -1:
            line_end = client_section.find('\n', insert_point)
            new_section = (
                client_section[:line_end + 1] +
                '    user = db.relationship("User", back_populates="client_profile")\n' +
                client_section[line_end + 1:]
            )
            content = content.replace(client_section, new_section)
            fixes_applied.append("Added user relationship to Client model")
    
    # Fix 3: Fix Owner.user relationship (wrong back_populates)
    owner_match = re.search(r'(class Owner\(db\.Model\):.*?)(?=class|\Z)', content, re.DOTALL)
    if owner_match:
        owner_section = owner_match.group()
        if 'back_populates="admin_profile"' in owner_section or 'back_populates="client_profile"' in owner_section:
            new_section = re.sub(
                r'user = db\.relationship\("User", back_populates="(?:admin_profile|client_profile)"\)',
                'user = db.relationship("User", back_populates="owner_profile")',
                owner_section
            )
            content = content.replace(owner_section, new_section)
            fixes_applied.append("Fixed Owner.user relationship back_populates")
    
    # Fix 4: Add client relationship to Post model
    post_match = re.search(r'(class Post\(db\.Model\):.*?)(?=class|\Z)', content, re.DOTALL)
    if post_match and 'client = db.relationship' not in post_match.group():
        post_section = post_match.group()
        insert_point = post_section.find('client_id = db.Column')
        if insert_point != -1:
            line_end = post_section.find('\n', insert_point)
            new_section = (
                post_section[:line_end + 1] +
                '    client = db.relationship("Client", back_populates="posts")\n' +
                post_section[line_end + 1:]
            )
            content = content.replace(post_section, new_section)
            fixes_applied.append("Added client relationship to Post model")
    
    # Fix 5: Add posts relationship to SocialAccount model
    social_match = re.search(r'(class SocialAccount\(db\.Model\):.*?)(?=class|\Z)', content, re.DOTALL)
    if social_match and 'posts = db.relationship' not in social_match.group():
        social_section = social_match.group()
        # Find a good insertion point (after last column or existing relationship)
        insert_point = social_section.rfind('db.Column')
        if insert_point != -1:
            line_end = social_section.find('\n', insert_point)
            new_section = (
                social_section[:line_end + 1] +
                '\n    # Relationships\n' +
                '    posts = db.relationship("Post", back_populates="social_account")\n' +
                social_section[line_end + 1:]
            )
            content = content.replace(social_section, new_section)
            fixes_applied.append("Added posts relationship to SocialAccount model")
    
    # Fix 6: Add analytics relationship to Post model (if not exists)
    post_match = re.search(r'(class Post\(db\.Model\):.*?)(?=class|\Z)', content, re.DOTALL)
    if post_match and 'analytics = db.relationship' not in post_match.group():
        post_section = post_match.group()
        # Find where to insert (after other relationships)
        if 'campaign = db.relationship' in post_section:
            insert_point = post_section.find('campaign = db.relationship')
            line_end = post_section.find('\n', insert_point)
            new_section = (
                post_section[:line_end + 1] +
                '    analytics = db.relationship("PostAnalytics", back_populates="post", uselist=False)\n' +
                post_section[line_end + 1:]
            )
            content = content.replace(post_section, new_section)
            fixes_applied.append("Added analytics relationship to Post model")
    
    # Fix 7: Add client relationship to Analytics model
    analytics_match = re.search(r'(class Analytics\(db\.Model\):.*?)(?=class|\Z)', content, re.DOTALL)
    if analytics_match and 'client = db.relationship' not in analytics_match.group():
        analytics_section = analytics_match.group()
        insert_point = analytics_section.find('client_id = db.Column')
        if insert_point != -1:
            line_end = analytics_section.find('\n', insert_point)
            new_section = (
                analytics_section[:line_end + 1] +
                '    client = db.relationship("Client", back_populates="analytics")\n' +
                analytics_section[line_end + 1:]
            )
            content = content.replace(analytics_section, new_section)
            fixes_applied.append("Added client relationship to Analytics model")
    
    # Fix 8: Ensure Client.analytics points to Analytics (not PostAnalytics)
    client_match = re.search(r'(class Client\(db\.Model\):.*?)(?=class|\Z)', content, re.DOTALL)
    if client_match:
        client_section = client_match.group()
        if 'analytics = db.relationship("PostAnalytics"' in client_section:
            new_section = client_section.replace(
                'analytics = db.relationship("PostAnalytics"',
                'analytics = db.relationship("Analytics"'
            )
            content = content.replace(client_section, new_section)
            fixes_applied.append("Fixed Client.analytics to point to Analytics model")
    
    # Write the fixed content
    with open('models.py', 'w') as f:
        f.write(content)
    
    return fixes_applied

if __name__ == '__main__':
    print("=== Comprehensive Relationship Fix ===\n")
    
    # Backup first
    import shutil
    import datetime
    backup_name = f"models.py.backup-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy('models.py', backup_name)
    print(f"✓ Created backup: {backup_name}")
    
    # Apply fixes
    fixes = apply_comprehensive_fixes()
    
    print("\n✅ Applied fixes:")
    for fix in fixes:
        print(f"  - {fix}")
    
    print(f"\nTotal fixes applied: {len(fixes)}")
    
    # Re-run analysis to verify
    print("\n=== Verifying fixes ===")
    import subprocess
    subprocess.run(['python3', 'analyze_relationships.py'])