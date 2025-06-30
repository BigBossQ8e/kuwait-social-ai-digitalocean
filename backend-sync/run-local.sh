#!/bin/bash

# Script to run the backend locally with virtual environment

echo "🚀 Starting Kuwait Social AI Backend..."
echo "=================================================================================="

# Change to backend directory
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Load environment variables from parent directory
if [ -f "../.env" ]; then
    echo "📋 Loading environment variables..."
    # Load .env file while ignoring comments and empty lines
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! "$key" =~ ^[[:space:]]*# ]] && [[ -n "$key" ]]; then
            # Remove leading/trailing whitespace and quotes
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            # Export the variable
            export "$key=$value"
        fi
    done < ../.env
fi

# Set Flask environment variables
export FLASK_APP=wsgi.py
export FLASK_ENV=development

# Start the application
echo "🚀 Starting Flask application..."
echo "=================================================================================="
echo "Access the API at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "=================================================================================="

python wsgi.py