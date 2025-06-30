#\!/bin/bash

# Load environment variables
cd /opt/kuwait-social-ai
source .env

# Export all variables
export $(cat .env  < /dev/null |  grep -v '^#' | xargs)

# Kill any existing gunicorn processes
pkill -f gunicorn || true

# Start gunicorn
cd /opt/kuwait-social-ai/backend
gunicorn --bind 0.0.0.0:5000 --workers 3 --daemon --pid /tmp/gunicorn.pid wsgi:app

echo "Backend started successfully"
