#!/usr/bin/env python3
"""
Test script to capture the exact ORM initialization error
"""

import sys
import traceback

# Simulate the Flask app initialization to catch ORM errors
test_code = '''
import sys
sys.path.insert(0, '/app')

try:
    # This is where the ORM error occurs - during model imports
    from models import db, User, Client, Post, Campaign
    from models.missing_models import Competitor, ScheduledPost
    print("SUCCESS: All models loaded without ORM errors")
except Exception as e:
    print(f"ORM ERROR TYPE: {type(e).__name__}")
    print(f"ORM ERROR MESSAGE: {str(e)}")
    print("\\nFULL TRACEBACK:")
    import traceback
    traceback.print_exc()
    
    # Analyze the error
    if "NoForeignKeysError" in str(e):
        print("\\nANALYSIS: This is an ORM relationship mapping error")
        print("LAYER: ORM Layer (Layer 3)")
        print("PHASE: Model initialization/import phase")
        print("SOLUTION: Fix relationship definitions or add missing foreign keys")
'''

# Create a test container command
test_command = f"""
ssh root@209.38.176.129 << 'EOF'
cd /opt/kuwait-social-ai
docker run --rm --network kuwait-network \
  -e DATABASE_URL=postgresql://kuwait_user:secure_password@kuwait-social-db:5432/kuwait_social_ai \
  -e SECRET_KEY=test-secret-key \
  -e FLASK_APP=app.py \
  -v /opt/kuwait-social-ai/backend:/app \
  -w /app \
  python:3.9 \
  bash -c "pip install -q flask flask-sqlalchemy psycopg2-binary flask-jwt-extended flask-cors python-dotenv && python -c '{test_code}'"
EOF
"""

print("Testing ORM initialization errors...")
print("=" * 60)
print(test_command)