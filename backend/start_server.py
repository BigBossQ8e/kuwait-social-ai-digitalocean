#!/usr/bin/env python3
"""Start Flask development server with proper configuration"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Remove MAX_CONTENT_LENGTH from environment to avoid string conversion issue
if 'MAX_CONTENT_LENGTH' in os.environ:
    del os.environ['MAX_CONTENT_LENGTH']

from app_factory import create_app

app = create_app('development')

if __name__ == '__main__':
    print("=== Starting Kuwait Social AI Backend ===")
    print("API Base URL: http://localhost:8000")
    print("\nAvailable endpoints:")
    print("  POST /api/auth/login          - Login")
    print("  POST /api/auth/register       - Register new user")
    print("  GET  /api/auth/profile        - Get user profile (requires auth)")
    print("  GET  /api/admin/dashboard     - Admin dashboard (requires admin auth)")
    print("  GET  /api/client/dashboard    - Client dashboard (requires client auth)")
    print("\nTest credentials:")
    print("  Email: test@restaurant.com")
    print("  Password: password123")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=True, host='localhost', port=8000)