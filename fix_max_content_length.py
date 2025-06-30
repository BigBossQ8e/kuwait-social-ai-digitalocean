#!/usr/bin/env python3
"""
Script to fix MAX_CONTENT_LENGTH type issue in Kuwait Social AI backend
"""

import os
import re

def find_and_fix_max_content_length():
    """Find and fix MAX_CONTENT_LENGTH type conversion issues"""
    
    print("=== Fixing MAX_CONTENT_LENGTH Type Issue ===\n")
    
    # Common patterns where the fix is needed
    patterns_to_fix = [
        {
            'file': 'config/config.py',
            'patterns': [
                # Pattern 1: Simple os.getenv without type conversion
                (r"MAX_CONTENT_LENGTH\s*=\s*os\.getenv\(['\"](MAX_CONTENT_LENGTH)['\"](?:,\s*['\"]?\d+['\"]?)?\)",
                 lambda m: f"MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB default"),
                
                # Pattern 2: os.environ.get without type conversion
                (r"MAX_CONTENT_LENGTH\s*=\s*os\.environ\.get\(['\"](MAX_CONTENT_LENGTH)['\"](?:,\s*['\"]?\d+['\"]?)?\)",
                 lambda m: f"MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))  # 16MB default"),
                
                # Pattern 3: Direct assignment that might need int conversion
                (r"app\.config\[['\"](MAX_CONTENT_LENGTH)['\"]\]\s*=\s*os\.getenv\(['\"]MAX_CONTENT_LENGTH['\"](?:,\s*['\"]?\d+['\"]?)?\)",
                 lambda m: f"app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB default"),
            ]
        },
        {
            'file': 'app_factory.py',
            'patterns': [
                # Pattern for app.config assignment
                (r"app\.config\[['\"](MAX_CONTENT_LENGTH)['\"]\]\s*=\s*([^#\n]+)(?!.*int\()",
                 lambda m: f"app.config['MAX_CONTENT_LENGTH'] = int({m.group(2).strip()}) if isinstance({m.group(2).strip()}, str) else {m.group(2).strip()}")
            ]
        }
    ]
    
    fixes_applied = []
    
    for fix_config in patterns_to_fix:
        file_path = fix_config['file']
        if os.path.exists(file_path):
            print(f"Checking {file_path}...")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            for pattern, replacement in fix_config['patterns']:
                matches = list(re.finditer(pattern, content))
                if matches:
                    print(f"  Found {len(matches)} match(es) for pattern")
                    for match in matches:
                        old_line = match.group(0)
                        new_line = replacement(match) if callable(replacement) else replacement
                        content = content.replace(old_line, new_line)
                        fixes_applied.append({
                            'file': file_path,
                            'old': old_line,
                            'new': new_line
                        })
            
            if content != original_content:
                # Create backup
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w') as f:
                    f.write(original_content)
                print(f"  Created backup: {backup_path}")
                
                # Write fixed content
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"  Updated {file_path}")
        else:
            print(f"File not found: {file_path}")
    
    # Summary
    print("\n=== Summary ===")
    if fixes_applied:
        print(f"Applied {len(fixes_applied)} fix(es):")
        for fix in fixes_applied:
            print(f"\nFile: {fix['file']}")
            print(f"Old: {fix['old'].strip()}")
            print(f"New: {fix['new'].strip()}")
    else:
        print("No fixes needed or patterns not found.")
    
    # Additional check for environment variable
    print("\n=== Environment Variable Check ===")
    max_content_env = os.getenv('MAX_CONTENT_LENGTH')
    if max_content_env:
        print(f"MAX_CONTENT_LENGTH is set to: {max_content_env}")
        try:
            int(max_content_env)
            print("✓ Value can be converted to integer")
        except ValueError:
            print("✗ WARNING: Value cannot be converted to integer!")
            print("  You should set MAX_CONTENT_LENGTH to a numeric value in your environment")
    else:
        print("MAX_CONTENT_LENGTH is not set in environment")
    
    return fixes_applied

if __name__ == "__main__":
    find_and_fix_max_content_length()