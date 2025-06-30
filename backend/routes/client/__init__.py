"""
Client routes package for Kuwait Social AI
Organized into focused sub-modules for better maintainability
"""

from flask import Blueprint

# Create parent blueprint
client_bp = Blueprint('client', __name__)

# Import and register sub-blueprints
from .dashboard import dashboard_bp
from .posts import posts_bp
from .analytics import analytics_bp
from .competitors import competitors_bp
from .features import features_bp

# Register sub-blueprints with URL prefixes
client_bp.register_blueprint(dashboard_bp, url_prefix='/dashboard')
client_bp.register_blueprint(posts_bp, url_prefix='/posts')
client_bp.register_blueprint(analytics_bp, url_prefix='/analytics')
client_bp.register_blueprint(competitors_bp, url_prefix='/competitors')
client_bp.register_blueprint(features_bp, url_prefix='/features')

__all__ = ['client_bp']