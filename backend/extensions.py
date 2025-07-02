"""
Flask Extensions Module
Initialize extensions without app instance for use with application factory pattern
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from celery import Celery
import redis
import os

# Create extension instances but don't associate with an app yet
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"],
    storage_uri=os.getenv('RATELIMIT_STORAGE_URL', os.getenv('REDIS_URL', 'redis://localhost:6379'))
)
celery = Celery()
socketio = SocketIO()

# Redis client - will be initialized in app factory if Redis is available
redis_client = None

def init_redis(app):
    """Initialize Redis client if available"""
    global redis_client
    redis_url = app.config.get('REDIS_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        redis_client.ping()
        app.logger.info("Redis client initialized successfully")
    except Exception as e:
        app.logger.warning(f"Redis not available: {e}")
        redis_client = None