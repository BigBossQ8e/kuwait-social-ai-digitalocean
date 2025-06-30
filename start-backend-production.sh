#!/bin/bash

echo "=== Starting Kuwait Social AI Backend ==="

# Navigate to backend directory
cd /var/www/kuwait-social-ai/backend || {
    echo "Error: Backend directory not found!"
    echo "Trying alternative paths..."
    cd /home/kuwait-social-ai/backend || cd /opt/kuwait-social-ai/backend || {
        echo "Cannot find backend directory. Please check installation path."
        exit 1
    }
}

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found!"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    if [ -f ".env.production" ]; then
        echo "Using .env.production"
        cp .env.production .env
    fi
fi

# Kill any existing gunicorn processes
echo "Stopping any existing Gunicorn processes..."
pkill -f gunicorn

# Start Gunicorn
echo "Starting Gunicorn on port 5000..."
gunicorn --bind 0.0.0.0:5000 \
         --workers 3 \
         --timeout 120 \
         --access-logfile - \
         --error-logfile - \
         --log-level info \
         wsgi:application &

# Wait a moment for startup
sleep 3

# Check if it started successfully
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✓ Backend started successfully!"
else
    echo "✗ Backend failed to start. Checking logs..."
    tail -20 logs/kuwait-social-ai.log 2>/dev/null || echo "No log file found"
fi

# Show running processes
echo ""
echo "Running processes:"
ps aux | grep gunicorn | grep -v grep