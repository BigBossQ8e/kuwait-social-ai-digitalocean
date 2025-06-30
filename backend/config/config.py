"""
Configuration classes for Kuwait Social AI
"""

import os
from datetime import timedelta
from .database_config import DatabaseConfig


class Config:
    """Base configuration"""
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # Ensure critical secrets are set
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set")
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable must be set")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/kuwait_social_ai')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Celery
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # 10MB default
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    
    # AI Services
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_CLOUD_KEY = os.getenv('GOOGLE_CLOUD_KEY')
    
    # Social Media
    INSTAGRAM_CLIENT_ID = os.getenv('INSTAGRAM_CLIENT_ID')
    INSTAGRAM_CLIENT_SECRET = os.getenv('INSTAGRAM_CLIENT_SECRET')
    SNAPCHAT_CLIENT_ID = os.getenv('SNAPCHAT_CLIENT_ID')
    SNAPCHAT_CLIENT_SECRET = os.getenv('SNAPCHAT_CLIENT_SECRET')
    
    # Payment Gateway
    MYFATOORAH_API_KEY = os.getenv('MYFATOORAH_API_KEY')
    MYFATOORAH_BASE_URL = os.getenv('MYFATOORAH_BASE_URL', 'https://api.myfatoorah.com')
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@kuwaitsocial.ai')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Allow default secrets in development only
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-ONLY-for-development')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-ONLY-for-development')
    
    # Development database configuration
    SQLALCHEMY_ENGINE_OPTIONS = DatabaseConfig.get_pool_config('development')


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Stricter security in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Ensure CORS is properly configured for production
    if not os.getenv('CORS_ORIGINS'):
        raise ValueError("CORS_ORIGINS must be explicitly set in production")
    
    # Production database should use optimized connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = DatabaseConfig.get_pool_config('production')


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Use test Redis database
    REDIS_URL = 'redis://localhost:6379/15'
    CELERY_BROKER_URL = 'redis://localhost:6379/15'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/15'
    
    # Testing database configuration
    SQLALCHEMY_ENGINE_OPTIONS = DatabaseConfig.get_pool_config('testing')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}