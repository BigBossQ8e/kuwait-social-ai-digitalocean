#!/usr/bin/env python3
"""
Fix SQLAlchemy relationship mismatches in models.py
"""

import re

def fix_relationships():
    print("Reading models.py...")
    
    with open('models.py', 'r') as f:
        content = f.read()
    
    # Track changes
    changes = []
    
    # Fix 1: Add user relationship to Admin model
    if 'class Admin(db.Model):' in content and 'admin_profile = db.relationship' not in content:
        # Find Admin class and add relationship after user_id
        pattern = r'(class Admin\(db\.Model\):.*?user_id = db\.Column.*?\n)'
        replacement = r'\1    user = db.relationship("User", back_populates="admin_profile")\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        changes.append("Added user relationship to Admin model")
    
    # Fix 2: Add user relationship to Client model
    # First check if it exists
    client_class = re.search(r'class Client\(db\.Model\):.*?(?=class|\Z)', content, re.DOTALL)
    if client_class and 'user = db.relationship' not in client_class.group():
        pattern = r'(class Client\(db\.Model\):.*?user_id = db\.Column.*?\n)'
        replacement = r'\1    user = db.relationship("User", back_populates="client_profile")\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        changes.append("Added user relationship to Client model")
    
    # Fix 3: Fix Owner user relationship (wrong back_populates)
    if 'back_populates="admin_profile"' in content and 'class Owner' in content:
        # Fix in Owner class context
        owner_section = re.search(r'class Owner\(db\.Model\):.*?(?=class|\Z)', content, re.DOTALL)
        if owner_section:
            fixed_section = owner_section.group().replace(
                'back_populates="admin_profile"', 
                'back_populates="owner_profile"'
            )
            if 'back_populates="client_profile"' in fixed_section:
                fixed_section = fixed_section.replace(
                    'back_populates="client_profile"', 
                    'back_populates="owner_profile"'
                )
            content = content.replace(owner_section.group(), fixed_section)
            changes.append("Fixed Owner user relationship back_populates")
    
    # Fix 4: Add client relationship to Post model
    post_class = re.search(r'class Post\(db\.Model\):.*?(?=class|\Z)', content, re.DOTALL)
    if post_class and 'client = db.relationship' not in post_class.group():
        pattern = r'(class Post\(db\.Model\):.*?client_id = db\.Column.*?\n)'
        replacement = r'\1    client = db.relationship("Client", back_populates="posts")\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        changes.append("Added client relationship to Post model")
    
    # Fix 5: Add posts relationship to SocialAccount model
    social_class = re.search(r'class SocialAccount\(db\.Model\):.*?(?=class|\Z)', content, re.DOTALL)
    if social_class and 'posts = db.relationship' not in social_class.group():
        # Find a good place to add it (after last column definition)
        pattern = r'(class SocialAccount\(db\.Model\):.*?last_sync = db\.Column.*?\n)'
        replacement = r'\1    \n    # Relationships\n    posts = db.relationship("Post", back_populates="social_account")\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        changes.append("Added posts relationship to SocialAccount model")
    
    # Fix 6: Add analytics relationship to Post model
    if 'analytics = db.relationship("PostAnalytics"' not in content:
        # Add after existing relationships in Post
        pattern = r'(class Post\(db\.Model\):.*?)(campaign = db\.relationship.*?\n)'
        replacement = r'\1\2    analytics = db.relationship("PostAnalytics", back_populates="post", uselist=False)\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        changes.append("Added analytics relationship to Post model")
    
    # Fix 7: Add client relationship to Analytics model
    analytics_class = re.search(r'class Analytics\(db\.Model\):.*?(?=class|\Z)', content, re.DOTALL)
    if analytics_class and 'client = db.relationship' not in analytics_class.group():
        pattern = r'(class Analytics\(db\.Model\):.*?client_id = db\.Column.*?\n)'
        replacement = r'\1    client = db.relationship("Client", back_populates="analytics")\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        changes.append("Added client relationship to Analytics model")
    
    # Write back
    with open('models.py', 'w') as f:
        f.write(content)
    
    print("\n✅ Fixed relationships:")
    for change in changes:
        print(f"  - {change}")
    
    if not changes:
        print("  No changes needed - all relationships appear correct")
    
    return len(changes)

if __name__ == '__main__':
    print("=== Fixing Model Relationships ===\n")
    num_fixes = fix_relationships()
    
    print(f"\nTotal fixes applied: {num_fixes}")
    print("\nNext steps:")
    print("1. Review the changes in models.py")
    print("2. Test the application")
    print("3. Run migrations if needed")