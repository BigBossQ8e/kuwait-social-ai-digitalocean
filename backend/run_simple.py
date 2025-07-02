#!/usr/bin/env python3
"""
Simple server runner that bypasses Telegram bot initialization
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Disable Telegram bot initialization
os.environ['DISABLE_TELEGRAM_BOT'] = '1'

print("🚀 Starting Kuwait Social AI Admin Panel (Simple Mode)")
print("=" * 50)

# Modify the app factory temporarily to skip Telegram bot
import app_factory

# Store original create_app
original_create_app = app_factory.create_app

def create_app_no_telegram(config_name='development'):
    """Create app without Telegram bot initialization"""
    app = original_create_app(config_name)
    return app

# Replace the create_app function
app_factory.create_app = create_app_no_telegram

# Now import and run the app
from wsgi import app

# Remove the Telegram bot initialization from the app context
import app_factory as af
original_code = af.create_app.__code__

# Create a modified version that skips Telegram
def create_app_modified(config_name='development'):
    from flask import Flask, jsonify
    from flask_cors import CORS
    import os
    import logging
    from logging.handlers import RotatingFileHandler
    from dotenv import load_dotenv
    
    load_dotenv()
    
    app = Flask(__name__)
    
    # Load configuration
    af.configure_app(app, config_name)
    
    # Initialize extensions
    af.initialize_extensions(app)
    
    # Configure security headers
    from middleware.security import init_security_headers
    init_security_headers(app)
    
    # Configure logging
    af.configure_logging(app)
    
    # Register blueprints
    af.register_blueprints(app)
    
    # Register error handlers
    af.register_error_handlers(app)
    
    # Initialize WebSocket handlers
    af.initialize_websocket_handlers(app)
    
    # Skip Telegram bot initialization
    app.logger.info("Skipping Telegram bot initialization")
    
    return app

# Use the modified version
from wsgi import application

if __name__ == '__main__':
    print("\n✅ Server starting...")
    print("\n📱 Access the admin panel at:")
    print("   http://localhost:5001/admin-demo (NO LOGIN REQUIRED)")
    print("   http://localhost:5001/admin-test (login: admin@example.com / password)")
    print("\n🛑 Press Ctrl+C to stop\n")
    
    # Run with simple server
    from werkzeug.serving import run_simple
    run_simple('localhost', 5001, application, use_debugger=True, use_reloader=False)