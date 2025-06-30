#!/usr/bin/env python3
"""
Syntax and import validation check
Tests code syntax without requiring full dependencies
"""

import ast
import sys
from pathlib import Path

def check_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def check_files():
    """Check all performance monitoring related files"""
    
    backend_dir = Path(__file__).parent.parent
    
    files_to_check = [
        'utils/query_performance.py',
        'config/database_config.py',
        'middleware/performance_middleware.py',
        'routes/admin/performance.py',
        'routes/client/features.py',
        'commands/performance.py',
        'scripts/verify_pool_config.py',
    ]
    
    print("🔍 Checking Syntax of Performance Monitoring Files...")
    print("=" * 60)
    
    all_valid = True
    
    for file_path in files_to_check:
        full_path = backend_dir / file_path
        
        if not full_path.exists():
            print(f"❌ {file_path}: File not found")
            all_valid = False
            continue
        
        is_valid, error = check_syntax(full_path)
        
        if is_valid:
            print(f"✅ {file_path}: Valid syntax")
        else:
            print(f"❌ {file_path}: {error}")
            all_valid = False
    
    return all_valid

def check_imports_structure():
    """Check import structure without actually importing"""
    
    print("\n🔗 Checking Import Structure...")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent.parent
    
    # Check for circular imports and structure
    import_patterns = {
        'utils/query_performance.py': [
            'from flask import',
            'from models import db',
            'from redis import Redis'
        ],
        'config/database_config.py': [
            'import os',
            'from typing import'
        ],
        'middleware/performance_middleware.py': [
            'from flask import Flask',
            'from utils.query_performance import',
            'from config.database_config import'
        ],
        'routes/admin/performance.py': [
            'from flask import Blueprint',
            'from utils.query_performance import',
            'from models import db'
        ]
    }
    
    issues = []
    
    for file_path, expected_imports in import_patterns.items():
        full_path = backend_dir / file_path
        
        if not full_path.exists():
            issues.append(f"{file_path}: File not found")
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for expected_import in expected_imports:
                if expected_import not in content:
                    issues.append(f"{file_path}: Missing expected import '{expected_import}'")
                else:
                    print(f"✅ {file_path}: Found '{expected_import}'")
        
        except Exception as e:
            issues.append(f"{file_path}: Error reading file - {e}")
    
    if issues:
        print("\n⚠️  Import Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True

def check_configuration_consistency():
    """Check configuration file consistency"""
    
    print("\n⚙️  Checking Configuration Consistency...")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent.parent
    
    # Check if we have consistent configuration
    config_files = [
        'config.py',  # Root config
        'config/config.py',  # New structured config
        'config/database_config.py'
    ]
    
    existing_configs = []
    
    for config_file in config_files:
        full_path = backend_dir / config_file
        if full_path.exists():
            existing_configs.append(config_file)
            print(f"✅ Found: {config_file}")
        else:
            print(f"❌ Missing: {config_file}")
    
    # Check for potential conflicts
    if 'config.py' in existing_configs and 'config/config.py' in existing_configs:
        print("⚠️  Warning: Both root config.py and config/config.py exist")
        print("   This may cause import conflicts")
        return False
    
    return True

def validate_blueprint_structure():
    """Validate Flask blueprint structure"""
    
    print("\n🔗 Checking Blueprint Structure...")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent.parent
    
    # Check client blueprint structure
    client_files = [
        'routes/client/__init__.py',
        'routes/client/dashboard.py',
        'routes/client/posts.py',
        'routes/client/analytics.py',
        'routes/client/competitors.py',
        'routes/client/features.py'
    ]
    
    missing_files = []
    
    for file_path in client_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    # Check admin blueprint
    admin_files = [
        'routes/admin/performance.py'
    ]
    
    for file_path in admin_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def main():
    """Run all syntax and structure checks"""
    
    print("🔍 Kuwait Social AI - Syntax & Structure Check")
    print("=" * 80)
    
    checks = [
        ("Syntax Validation", check_syntax),
        ("Import Structure", check_imports_structure),
        ("Configuration Consistency", check_configuration_consistency),
        ("Blueprint Structure", validate_blueprint_structure)
    ]
    
    all_passed = True
    
    # Run syntax check first
    if not check_files():
        all_passed = False
    
    # Run other checks
    for check_name, check_func in checks[1:]:  # Skip syntax check as we ran it above
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"\n❌ {check_name} failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ All syntax and structure checks passed!")
        print("\n📋 NEXT STEPS:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment variables")
        print("3. Run full integration test")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())