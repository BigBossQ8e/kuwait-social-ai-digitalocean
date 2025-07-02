#!/usr/bin/env python3
"""
Simple server runner for admin panel
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Set environment variables to suppress errors
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

print("🚀 Starting Kuwait Social AI Server...")
print("=" * 50)

# Import and run
from wsgi import app

if __name__ == '__main__':
    print("\n✅ Server is starting...")
    print("\n📱 Access the admin panel at:")
    print("   http://localhost:5001/admin-demo")
    print("\n⚡ Features available:")
    print("   - Platform Management")
    print("   - Feature Flags")
    print("   - Service Packages")
    print("   - Activity Feed")
    print("\n🛑 Press Ctrl+C to stop\n")
    
    # Run the app
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=True)