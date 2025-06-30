#!/bin/bash

echo "=== Starting Backend with Database Connection ==="

# Set database password to avoid prompt
export DATABASE_URL="postgresql://doadmin:AVNS_b-Yu6tYsVvTh4GHch3B@db-postgresql-fra1-29054-do-user-23461250-0.f.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# Navigate to backend
cd /var/www/kuwait-social-ai/backend || cd /home/kuwait-social-ai/backend || {
    echo "Error: Cannot find backend directory"
    exit 1
}

# Copy production env if .env doesn't exist
if [ ! -f ".env" ] && [ -f ".env.production" ]; then
    echo "Creating .env from .env.production..."
    cp .env.production .env
fi

# Activate virtual environment
source venv/bin/activate || source .venv/bin/activate

# Start Gunicorn (password won't be prompted because DATABASE_URL is set)
echo "Starting Gunicorn..."
gunicorn --bind 0.0.0.0:5000 \
         --workers 3 \
         --timeout 120 \
         --access-logfile - \
         --error-logfile - \
         wsgi:application