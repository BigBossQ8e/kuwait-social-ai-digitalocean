#!/bin/bash

echo "=== Fixing Backend Structure ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai/backend

echo "1. Checking Flask app structure..."
echo "Current directory structure:"
ls -la

echo ""
echo "2. Creating __init__.py if missing..."
touch __init__.py

echo ""
echo "3. Fixing import issue - updating wsgi.py..."
cat > wsgi.py << 'WSGI'
"""
WSGI entry point for production deployment
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from app_factory import create_app

# Load environment variables
load_dotenv()

# Create application
application = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    application.run()
WSGI

echo ""
echo "4. Checking if migrations directory exists..."
if [ ! -d "migrations" ]; then
    echo "Creating migrations directory..."
    docker exec kuwait-social-backend flask db init
fi

echo ""
echo "5. Creating database tables directly..."
docker exec kuwait-social-backend python << 'PYTHON'
import sys
sys.path.insert(0, '/app')

from app_factory import create_app
from models import db

app = create_app('production')

with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nCreated tables: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
PYTHON

echo ""
echo "6. Testing login endpoint with proper request..."
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}' \
  2>/dev/null | python3 -m json.tool

echo ""
echo "7. Checking backend health..."
docker exec kuwait-social-backend python << 'HEALTHCHECK'
import requests
try:
    # Test root endpoint
    resp = requests.get('http://localhost:5000/')
    print(f"Root endpoint: {resp.status_code}")
    
    # Test auth endpoints
    resp = requests.get('http://localhost:5000/api/auth/')
    print(f"Auth endpoint: {resp.status_code}")
    
except Exception as e:
    print(f"Health check error: {e}")
HEALTHCHECK

echo ""
echo "=== Backend structure fix complete! ==="
EOF