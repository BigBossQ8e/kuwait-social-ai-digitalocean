"""
Kuwait Social AI - Application Factory
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import extensions from centralized location
from extensions import db, migrate, jwt, limiter


def create_app(config_name='development'):
    """Create and configure the Flask application"""
    
    app = Flask(__name__)
    
    # Load configuration
    configure_app(app, config_name)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Configure security headers
    from middleware.security import init_security_headers
    init_security_headers(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Configure Celery
    # configure_celery(app)  # Disabled - celery not configured
    
    return app


def configure_app(app, config_name):
    """Load application configuration"""
    
    # Import configuration classes
    from config.config import config
    
    # Load configuration class
    config_class = config.get(config_name, config['default'])
    app.config.from_object(config_class)
    
    # Allow environment variables to override configuration
    # This is useful for secrets that shouldn't be in config files
    for key in dir(config_class):
        if key.isupper():
            # Check if there's an environment variable override
            env_value = os.getenv(key)
            if env_value is not None:
                # Don't override with env vars if already properly set from config class
                # This prevents type conversion issues
                if key not in app.config or isinstance(app.config[key], str):
                    app.config[key] = env_value


def initialize_extensions(app):
    """Initialize Flask extensions"""
    
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentication
    jwt.init_app(app)
    
    # Rate limiting
    limiter.init_app(app)
    
    # CORS
    # Get CORS origins from config, ensuring it's a list
    cors_origins = app.config.get('CORS_ORIGINS', [])
    if isinstance(cors_origins, str):
        # If it's a string (from env variable), split it
        cors_origins = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    
    # In production, never allow wildcard origins
    if app.config.get('ENV') == 'production' and '*' in cors_origins:
        app.logger.warning("Wildcard CORS origin detected in production - removing for security")
        cors_origins = [origin for origin in cors_origins if origin != '*']
    
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins if cors_origins else ['http://localhost:3000', 'http://localhost:5173'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })


def configure_logging(app):
    """Configure application logging"""
    
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        file_handler = RotatingFileHandler(
            'logs/kuwait-social-ai.log',
            maxBytes=10240000,
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Kuwait Social AI startup')


def register_blueprints(app):
    """Register all application blueprints"""
    
    from routes.auth import auth_bp
    from routes.owner import owner_bp
    from routes.admin import admin_bp
    from routes.admin_clients import admin_clients_bp
    from routes.client import client_bp
    from routes.content import content_bp
    from routes.content_enhanced import content_enhanced_bp
    from routes.analytics import analytics_bp
    from routes.translations import translations_bp
    from routes.social import social_bp
    from routes.telegram import telegram_bp
    from routes.payments import payments_bp
    from routes.prayer_times import prayer_times_bp
    from routes.ai_content import ai_content_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(owner_bp, url_prefix='/api/owner')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_clients_bp, url_prefix='/api')
    app.register_blueprint(client_bp, url_prefix='/api/client')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(content_enhanced_bp, url_prefix='/api/content-fb')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(social_bp, url_prefix='/api/social')
    app.register_blueprint(telegram_bp, url_prefix='/api/telegram')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(prayer_times_bp, url_prefix='/api/prayer-times')
    app.register_blueprint(translations_bp, url_prefix='/api')
    app.register_blueprint(ai_content_bp)  # New AI content routes


def register_error_handlers(app):
    """Register custom error handlers"""
    
    from exceptions import KuwaitSocialAIException
    
    @app.errorhandler(KuwaitSocialAIException)
    def handle_custom_exception(error):
        """Handle custom exceptions"""
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Resource not found',
            'error_code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        app.logger.error(f'Internal error: {str(error)}')
        return jsonify({
            'error': 'An internal error occurred',
            'error_code': 'INTERNAL_ERROR'
        }), 500
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit errors"""
        return jsonify({
            'error': 'Rate limit exceeded',
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'details': {
                'message': str(error.description),
                'retry_after': error.get_headers().get('Retry-After')
            }
        }), 429


# Celery configuration removed - not currently used
