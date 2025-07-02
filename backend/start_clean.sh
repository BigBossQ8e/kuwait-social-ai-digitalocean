#!/bin/bash

# Clean Startup Script for Kuwait Social AI Admin Panel
echo "🚀 Kuwait Social AI - Clean Startup"
echo "===================================="

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    echo "Using system Python instead..."
fi

# Apply all fixes
echo ""
echo "🔧 Applying all fixes..."
python apply_all_fixes.py || python3 apply_all_fixes.py

echo ""
echo "✅ All fixes applied!"
echo ""
echo "🌐 Starting server..."
echo ""

# Start the server
python wsgi.py || python3 wsgi.py