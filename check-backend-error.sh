#!/bin/bash

echo "=== Checking Backend Error ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
echo "1. Backend container logs (last 50 lines):"
echo "----------------------------------------"
docker logs kuwait-social-backend --tail=50

echo ""
echo "2. Checking database connection:"
echo "----------------------------------------"
docker exec kuwait-social-backend python -c "
from app_factory import create_app
from models import db
app = create_app('production')
with app.app_context():
    try:
        # Test database connection
        db.engine.execute('SELECT 1')
        print('✅ Database connection successful')
    except Exception as e:
        print(f'❌ Database error: {e}')
"

echo ""
echo "3. Checking if database tables exist:"
echo "----------------------------------------"
docker exec kuwait-social-db psql -U postgres -d kuwait_social_ai -c "\dt"

echo ""
echo "4. Testing login endpoint directly:"
echo "----------------------------------------"
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}' \
  -v 2>&1 | grep -E "(< HTTP|{|error)"

echo ""
echo "5. Checking environment variables:"
echo "----------------------------------------"
docker exec kuwait-social-backend printenv | grep -E "(DATABASE|SECRET|JWT)" | sed 's/=.*/=***/'
EOF