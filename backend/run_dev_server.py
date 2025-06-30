#!/usr/bin/env python3
"""Run Flask development server"""

from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app

app = create_app()

if __name__ == '__main__':
    print("=== Starting Kuwait Social AI Backend ===")
    print("API URL: http://localhost:5000")
    print("Test login: http://localhost:5000/api/auth/login")
    print("\nTest credentials:")
    print("  Email: test@restaurant.com")
    print("  Password: password123")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    app.run(debug=True, host='0.0.0.0', port=5000)