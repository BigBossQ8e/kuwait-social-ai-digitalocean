#!/usr/bin/env python3
"""
Kuwait Social AI - Main Application Entry Point
Using Application Factory Pattern
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from app_factory import create_app, db, celery

# Load environment variables
load_dotenv()

# Determine configuration
config_name = os.getenv('FLASK_ENV', 'development')

# Create application
app = create_app(config_name)

# Celery is already accessible from app_factory import

# Create database tables
@app.before_first_request
def create_tables():
    """Create database tables if they don't exist"""
    db.create_all()

# Health check endpoint
@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return {
        'status': 'healthy',
        'environment': config_name,
        'timestamp': datetime.utcnow().isoformat()
    }

if __name__ == '__main__':
    # Run the application
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])