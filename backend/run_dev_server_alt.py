#!/usr/bin/env python3
"""Run Flask development server on alternative port"""

import sys
from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app

app = create_app()

if __name__ == '__main__':
    port = 5001  # Alternative port
    
    # Check if port was provided as argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    print("=== Starting Kuwait Social AI Backend ===")
    print(f"API URL: http://localhost:{port}")
    print(f"Test login: http://localhost:{port}/api/auth/login")
    print("\nTest credentials:")
    print("  Email: test@restaurant.com")
    print("  Password: password123")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    app.run(debug=True, host='0.0.0.0', port=port)