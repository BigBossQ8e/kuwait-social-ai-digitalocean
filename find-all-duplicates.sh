#!/bin/bash

echo "🔍 Deep Search for All Kuwait Social AI Files"
echo "==========================================="

ssh root@209.38.176.129 << 'ENDSSH'

echo "1. Searching for all Kuwait-related directories..."
echo "================================================="
find / -type d -name "*kuwait*" -o -name "*kwtsocial*" 2>/dev/null | grep -v -E "proc|sys|docker/overlay2" | sort

echo ""
echo "2. Checking for configuration files..."
echo "====================================="
echo "Nginx configs:"
find /etc/nginx -name "*kuwait*" -o -name "*kwtsocial*" 2>/dev/null

echo ""
echo "Apache configs (if any):"
find /etc/apache2 -name "*kuwait*" -o -name "*kwtsocial*" 2>/dev/null || echo "Apache not installed"

echo ""
echo "3. Database checks..."
echo "===================="
echo "PostgreSQL databases:"
docker exec kuwait-social-db psql -U postgres -c "\l" | grep -i kuwait

echo ""
echo "4. Checking for environment files..."
echo "==================================="
find / -name ".env" -type f 2>/dev/null | xargs grep -l "kuwait\|kwtsocial" 2>/dev/null | grep -v docker

echo ""
echo "5. Checking for git repositories..."
echo "=================================="
find / -name ".git" -type d 2>/dev/null | grep -E "kuwait|kwtsocial" | head -10

echo ""
echo "6. Checking user home directories..."
echo "===================================="
ls -la /home/
for user in $(ls /home/); do
    if [ -d "/home/$user" ]; then
        find /home/$user -maxdepth 3 -type d -name "*kuwait*" 2>/dev/null
    fi
done

echo ""
echo "7. Checking for backup archives..."
echo "================================="
find / -name "*.tar.gz" -o -name "*.zip" -o -name "*.tar" 2>/dev/null | grep -i kuwait | head -20

echo ""
echo "8. Checking running services on different ports..."
echo "================================================"
netstat -tlnp | grep -E "LISTEN" | grep -v -E "22|53|68"

echo ""
echo "9. Checking for multiple Python virtual environments..."
echo "====================================================="
find /opt/kuwait-social-ai -name "venv" -o -name "env" -o -name ".venv" -type d 2>/dev/null

echo ""
echo "10. Checking for log files in various locations..."
echo "================================================="
find / -name "*.log" 2>/dev/null | grep -i kuwait | grep -v docker | head -20

echo ""
echo "11. Checking for PM2 processes (Node.js process manager)..."
echo "=========================================================="
which pm2 && pm2 list || echo "PM2 not installed"

echo ""
echo "12. Checking supervisord configurations..."
echo "========================================="
if [ -d "/etc/supervisor/conf.d" ]; then
    ls -la /etc/supervisor/conf.d/ | grep -i kuwait
else
    echo "Supervisord not configured"
fi

echo ""
echo "13. Memory and process summary..."
echo "================================"
echo "Total Kuwait-related processes:"
ps aux | grep -i kuwait | grep -v grep | wc -l

echo ""
echo "Memory usage by Kuwait processes:"
ps aux | grep -i kuwait | grep -v grep | awk '{sum += $6} END {print "Total RSS: " sum/1024 " MB"}'

ENDSSH