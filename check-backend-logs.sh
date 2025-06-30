#!/bin/bash

echo "=== Checking Backend Error Logs ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
echo "1. Recent backend errors:"
docker logs kuwait-social-backend 2>&1 | grep -A 10 -B 2 "ERROR\|Traceback\|500" | tail -50

echo ""
echo "2. Testing if database tables exist:"
docker exec kuwait-social-backend python -c "
import sys
sys.path.insert(0, '/app')
try:
    from app_factory import create_app
    from models import db, User
    
    app = create_app('production')
    with app.app_context():
        # Check if User table exists
        result = db.session.execute(db.text('SELECT COUNT(*) FROM users'))
        count = result.scalar()
        print(f'✅ User table exists with {count} users')
except Exception as e:
    print(f'❌ Database error: {e}')
    print('Need to create tables...')
"

echo ""
echo "3. Creating database tables if needed:"
docker exec kuwait-social-backend python -c "
import sys
sys.path.insert(0, '/app')
try:
    from app_factory import create_app
    from models import db
    
    app = create_app('production')
    with app.app_context():
        db.create_all()
        print('✅ Database tables created/verified')
        
        # List tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'Tables in database: {", ".join(tables)}')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "=== End of error check ==="
EOF