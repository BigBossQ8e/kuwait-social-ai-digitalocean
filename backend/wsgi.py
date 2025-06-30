"""
WSGI entry point for production deployment
"""

import os
from dotenv import load_dotenv
from app_factory import create_app

# Load environment variables
load_dotenv()

# Create application
application = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    application.run()