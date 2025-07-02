#!/bin/bash

# Admin Panel Startup Script
echo "🚀 Starting Kuwait Social AI Admin Panel..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    echo "Try running: source venv/bin/activate"
    exit 1
fi

# Create test admin user
echo "👤 Creating test admin user..."
python create_test_admin.py || python3 create_test_admin.py

# Setup test data
echo "📊 Setting up test data..."
python setup_test_data.py || python3 setup_test_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting server on http://localhost:5001"
echo "📱 Admin panel URL: http://localhost:5001/admin-test"
echo ""
echo "🔑 Login credentials:"
echo "   Email: admin@example.com"
echo "   Password: password"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python wsgi.py || python3 wsgi.py