#!/bin/bash

echo "🔍 Testing Backend Import Issues..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "Testing Python imports..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    print("1. Testing basic imports...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    print("2. Testing config...")
    from config.config import Config
    
    print("3. Testing models...")
    from models import db
    
    print("4. Testing app_factory...")
    from app_factory import create_app
    
    print("5. Creating app...")
    app = create_app()
    
    print("\n✅ All imports successful!")
    print(f"App created: {app}")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
EOF

ENDSSH