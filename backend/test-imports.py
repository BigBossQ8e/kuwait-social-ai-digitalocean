#!/usr/bin/env python3
"""
Test script to check if models can be imported correctly
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing from models.py directly
    print("Testing import from models.py...")
    from models import db, User, Client, Admin, Owner, Post, PostAnalytics, AuditLog
    print("✅ Successfully imported from models.py")
    print(f"   - User: {User}")
    print(f"   - Client: {Client}")
    print(f"   - Admin: {Admin}")
    print(f"   - Owner: {Owner}")
    print(f"   - Post: {Post}")
    print(f"   - PostAnalytics: {PostAnalytics}")
    print(f"   - AuditLog: {AuditLog}")
except ImportError as e:
    print(f"❌ Failed to import from models.py: {e}")

print("\n" + "="*50 + "\n")

try:
    # Test importing from models package
    print("Testing import from models package...")
    from models import db as models_db
    print("✅ Successfully imported db from models package")
    
    # Try importing submodules
    from models.api_key import APIKey
    from models.client_error import ClientError
    print("✅ Successfully imported submodules")
    print(f"   - APIKey: {APIKey}")
    print(f"   - ClientError: {ClientError}")
except ImportError as e:
    print(f"❌ Failed to import from models package: {e}")