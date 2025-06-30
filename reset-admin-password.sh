#!/bin/bash

echo "🔐 Resetting Admin Password"
echo "=========================="

ssh root@209.38.176.129 << 'ENDSSH'

echo "Updating admin@kwtsocial.com password to Kuwait2025@AI!"

# Direct SQL update using docker
docker exec kuwait-social-db psql -U kuwait_user -d kuwait_social_ai << 'SQL'

-- First, let's see current admin users
SELECT id, email, username, role FROM users WHERE role='admin';

-- Generate new password hash using pgcrypto
-- Note: This is a simplified version, ideally use werkzeug
UPDATE users 
SET password_hash = crypt('Kuwait2025@AI!', gen_salt('bf', 8))
WHERE email = 'admin@kwtsocial.com';

-- Verify update
SELECT email, substring(password_hash, 1, 20) as hash_start FROM users WHERE email='admin@kwtsocial.com';

SQL

echo ""
echo "Testing password update with Python..."
cd /opt/kuwait-social-ai/backend

python3 << 'PYTHON'
from werkzeug.security import generate_password_hash
import subprocess
import sys

# Generate proper werkzeug hash
new_hash = generate_password_hash('Kuwait2025@AI!')
print(f"Generated hash: {new_hash[:20]}...")

# Update via docker exec
cmd = f"""docker exec kuwait-social-db psql -U kuwait_user -d kuwait_social_ai -c "UPDATE users SET password_hash='{new_hash}' WHERE email='admin@kwtsocial.com';" """
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Password updated successfully!")
else:
    print(f"❌ Error: {result.stderr}")

# Also update the second admin
cmd2 = f"""docker exec kuwait-social-db psql -U kuwait_user -d kuwait_social_ai -c "UPDATE users SET password_hash='{new_hash}' WHERE email='admin@kuwaitsocial.ai';" """
subprocess.run(cmd2, shell=True)
print("✅ Also updated admin@kuwaitsocial.ai with same password")

PYTHON

echo ""
echo "✅ Password reset complete!"
echo ""
echo "📧 Admin Accounts:"
echo "1. admin@kwtsocial.com / Kuwait2025@AI!"
echo "2. admin@kuwaitsocial.ai / Kuwait2025@AI!"
echo ""
echo "🌐 Login at: https://kwtsocial.com/admin"

ENDSSH