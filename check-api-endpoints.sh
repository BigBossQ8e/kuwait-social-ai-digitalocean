#!/bin/bash

echo "=== Checking Kuwait Social AI API Endpoints ==="
echo ""

# Test various endpoints
echo "1. Testing API endpoints:"
echo ""

echo "a) Root endpoint (/):"
curl -s http://209.38.176.129:5000/ | python3 -m json.tool 2>/dev/null || curl -s http://209.38.176.129:5000/

echo ""
echo "b) API root (/api):"
curl -s http://209.38.176.129:5000/api | python3 -m json.tool 2>/dev/null || curl -s http://209.38.176.129:5000/api

echo ""
echo "c) Auth endpoints:"
echo "   - /api/auth:"
curl -s http://209.38.176.129:5000/api/auth | head -20

echo ""
echo "   - /api/auth/login (GET):"
curl -s http://209.38.176.129:5000/api/auth/login | head -20

echo ""
echo "d) Testing POST to login:"
curl -X POST http://209.38.176.129:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}' \
  -w "\nStatus: %{http_code}\n" \
  -s 2>&1

echo ""
echo "2. Checking what routes are registered:"
ssh root@209.38.176.129 << 'EOF'
docker exec kuwait-social-backend python -c "
import sys
sys.path.insert(0, '/app')
from app_factory import create_app

app = create_app('production')

print('Registered routes:')
for rule in app.url_map.iter_rules():
    print(f'  {rule.methods} {rule.rule}')
" 2>/dev/null | head -30
EOF

echo ""
echo "3. Checking backend container health:"
ssh root@209.38.176.129 docker inspect kuwait-social-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "No health check configured"

echo ""
echo "=== End of API check ==="