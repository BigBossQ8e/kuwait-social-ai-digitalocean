#!/bin/bash

echo "🔧 Applying MAX_CONTENT_LENGTH fix from our previous solution..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "1. Current issue in app_factory.py line 76:"
sed -n '74,78p' app_factory.py

echo ""
echo "2. Backing up app_factory.py..."
cp app_factory.py app_factory.py.backup-$(date +%Y%m%d-%H%M%S)

echo ""
echo "3. Applying the fix to handle MAX_CONTENT_LENGTH as integer..."

# Create a Python script to fix it properly
cat > fix_app_factory.py << 'PYTHON'
import re

with open('app_factory.py', 'r') as f:
    content = f.read()

# Find the section where env variables are loaded
lines = content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # After the line that sets app.config[key] = env_value
    if 'app.config[key] = env_value' in line:
        # Get the indentation
        indent = len(line) - len(line.lstrip())
        # Replace this line with type-aware setting
        new_lines[-1] = ' ' * indent + 'if key in ["MAX_CONTENT_LENGTH", "SQLALCHEMY_POOL_SIZE", "JWT_ACCESS_TOKEN_EXPIRES"]:'
        new_lines.append(' ' * (indent + 4) + 'app.config[key] = int(env_value)')
        new_lines.append(' ' * indent + 'else:')
        new_lines.append(' ' * (indent + 4) + 'app.config[key] = env_value')

with open('app_factory.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("✅ Fixed app_factory.py")
PYTHON

python3 fix_app_factory.py
rm fix_app_factory.py

echo ""
echo "4. Verifying the fix:"
sed -n '74,82p' app_factory.py

echo ""
echo "5. Restarting backend..."
pkill -f gunicorn
sleep 2

export $(grep -v '^#' .env | xargs)
/usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --daemon --pid /tmp/gunicorn.pid wsgi:app

sleep 5

echo ""
echo "6. Testing login endpoint..."
response=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kwtsocial.com","password":"Kuwait2025@AI!"}' \
  -s -w "\nHTTP_STATUS:%{http_code}")

echo "$response" | head -1 | python3 -m json.tool 2>/dev/null || echo "$response"
status=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)

if [ "$status" = "200" ]; then
    echo ""
    echo "✅ SUCCESS! Login is working!"
else
    echo ""
    echo "❌ Still not working. Checking logs..."
    tail -5 logs/kuwait-social-ai.log | grep -v INFO
fi

ENDSSH