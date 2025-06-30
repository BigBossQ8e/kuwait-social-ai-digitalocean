#!/bin/bash

echo "=== Checking Server Status ==="
echo ""

# Check if nginx (main server) is running
echo "1. MAIN SERVER (Nginx):"
if curl -I http://localhost 2>/dev/null | grep -q "nginx"; then
    echo "✓ Nginx is running"
else
    echo "✗ Nginx is NOT running"
fi

# Check nginx service
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx service is active"
else
    echo "✗ Nginx service is NOT active"
fi

echo ""
echo "2. BACKEND SERVER (Flask/Gunicorn on port 5000):"
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✓ Backend is responding"
else
    echo "✗ Backend is NOT responding on port 5000"
fi

# Check for gunicorn processes
if pgrep -f gunicorn > /dev/null; then
    echo "✓ Gunicorn process found"
    echo "  PIDs: $(pgrep -f gunicorn | tr '\n' ' ')"
else
    echo "✗ No Gunicorn process found"
fi

# Check for Flask dev server
if pgrep -f "flask run" > /dev/null; then
    echo "✓ Flask dev server found (WARNING: Not for production!)"
fi

echo ""
echo "3. FRONTEND SERVER (React on port 3000):"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ Frontend is responding"
else
    echo "✗ Frontend is NOT responding on port 3000"
fi

echo ""
echo "4. DATABASE (PostgreSQL):"
if systemctl is-active --quiet postgresql; then
    echo "✓ PostgreSQL service is active"
else
    echo "✗ PostgreSQL service is NOT active"
fi

echo ""
echo "5. REDIS:"
if systemctl is-active --quiet redis; then
    echo "✓ Redis service is active"
else
    echo "✗ Redis service is NOT active"
fi

echo ""
echo "=== Checking Logs ==="
echo ""
echo "Recent Nginx errors:"
sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "Cannot read nginx error log"

echo ""
echo "Recent backend logs:"
sudo journalctl -u kuwait-social-backend -n 5 --no-pager 2>/dev/null || echo "No systemd service logs found"