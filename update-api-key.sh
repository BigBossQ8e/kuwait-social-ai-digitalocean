#!/bin/bash

echo "🔑 Updating OpenAI API Key..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

# Backup current .env
cp .env .env.backup-$(date +%Y%m%d-%H%M%S)

# Update the OpenAI API key
sed -i 's#OPENAI_API_KEY=.*#OPENAI_API_KEY=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#' .env

echo "✅ Updated OpenAI API key"
echo ""
echo "Current key in .env:"
grep OPENAI_API_KEY .env | sed 's/\(sk-[^-]*-\).*\(....\)$/\1***\2/'

echo ""
echo "🔄 Restarting backend to apply changes..."
pkill -f gunicorn
sleep 2

export $(grep -v '^#' .env | xargs)
/usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --daemon --pid /tmp/gunicorn.pid wsgi:app

sleep 5

echo ""
echo "✅ Backend restarted with new API key"

# Test if API is working
echo ""
echo "Testing API..."
curl -s http://localhost:5000/api/ -w "\nHTTP Status: %{http_code}\n"

ENDSSH