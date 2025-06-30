"""
Flask Extensions Module
Initialize extensions without app instance for use with application factory pattern
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
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