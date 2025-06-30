#!/bin/bash

# Quick fix for backend API

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

# Kill any running python/gunicorn processes
pkill -f python3
pkill -f gunicorn

# Comment out translations import temporarily
sed -i '84s/^/#/' app_factory.py
sed -i '100s/^/#/' app_factory.py

# Start gunicorn properly
/usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --daemon wsgi:app

sleep 5

# Test
echo "Testing API..."
curl -s http://localhost:5000/api/health

ENDSSH