#!/usr/bin/env python3
"""
Safe application startup script with error handling and diagnostics
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check and set up environment"""
    logger.info("Checking environment...")
    
    # Ensure we're in the right directory
    if not os.path.exists('app_factory.py'):
        logger.error("Error: app_factory.py not found. Are you in the backend directory?")
        sys.exit(1)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Set default environment variables
    defaults = {
        'FLASK_ENV': 'development',
        'DISABLE_TELEGRAM_BOT': '1',  # Disable by default to avoid errors
        'SECRET_KEY': 'dev-secret-key-change-in-production',
        'JWT_SECRET_KEY': 'dev-jwt-secret-change-in-production'
    }
    
    for key, value in defaults.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.info(f"Set default {key}={value}")
    
    # Check database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.warning("DATABASE_URL not set, using default PostgreSQL connection")
        os.environ['DATABASE_URL'] = 'postgresql://localhost/kuwait_social_ai'
    elif db_url.startswith('postgres://'):
        # Fix for SQLAlchemy
        os.environ['DATABASE_URL'] = db_url.replace('postgres://', 'postgresql://', 1)
        logger.info("Fixed DATABASE_URL for SQLAlchemy")

def test_imports():
    """Test critical imports before starting"""
    logger.info("Testing imports...")
    
    try:
        from app_factory import create_app
        logger.info("✅ app_factory imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import app_factory: {e}")
        logger.error("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    try:
        from extensions import db, jwt
        logger.info("✅ Extensions imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import extensions: {e}")
        sys.exit(1)
    
    try:
        from models import User, Client
        logger.info("✅ Models imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import models: {e}")
        sys.exit(1)

def test_database():
    """Test database connection"""
    logger.info("Testing database connection...")
    
    try:
        from app_factory import create_app
        from extensions import db
        from sqlalchemy import text
        
        app = create_app('development')
        
        with app.app_context():
            # Test connection
            result = db.session.execute(text('SELECT 1'))
            logger.info("✅ Database connection successful")
            
            # Check if tables exist
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            
            if table_count == 0:
                logger.warning("⚠️  No tables found in database")
                logger.info("Running database migrations...")
                os.system("flask db upgrade")
            else:
                logger.info(f"✅ Found {table_count} tables in database")
                
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        logger.error("Make sure PostgreSQL is running and DATABASE_URL is correct")
        sys.exit(1)

def start_development_server():
    """Start the Flask development server"""
    logger.info("Starting Flask development server...")
    
    try:
        from app_factory import create_app
        
        app = create_app('development')
        
        # Get port from environment or use default
        port = int(os.getenv('PORT', 5001))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info("Press CTRL+C to stop")
        logger.info("")
        logger.info("Available endpoints:")
        logger.info(f"  Admin Preview: http://localhost:{port}/admin-preview")
        logger.info(f"  AI Services: http://localhost:{port}/admin-ai")
        logger.info(f"  Health Check: http://localhost:{port}/api/health")
        logger.info("")
        
        # Run the app
        app.run(host=host, port=port, debug=True)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main entry point"""
    logger.info("Kuwait Social AI - Safe Startup")
    logger.info("=" * 50)
    
    # Run checks
    check_environment()
    test_imports()
    test_database()
    
    # Start server
    start_development_server()

if __name__ == "__main__":
    main()