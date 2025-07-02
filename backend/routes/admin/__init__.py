"""
Admin Routes Package
Consolidates all admin-related blueprints
"""
from flask import Blueprint

# Create parent admin blueprint
admin_bp = Blueprint('admin', __name__)

# Import all admin sub-blueprints
from .dashboard import admin_dashboard_bp
from .platforms import admin_platforms_bp
from .features import admin_features_bp
from .packages import admin_packages_bp
from .config_sync import admin_config_sync_bp

# Try to import AI prompts blueprint
try:
    from .ai_prompts import ai_prompts_bp
    ai_prompts_available = True
except ImportError:
    ai_prompts_available = False

# Register sub-blueprints
def register_admin_blueprints(app):
    """Register all admin blueprints with the app"""
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_platforms_bp)
    app.register_blueprint(admin_features_bp)
    app.register_blueprint(admin_packages_bp)
    app.register_blueprint(admin_config_sync_bp)
    
    if ai_prompts_available:
        app.register_blueprint(ai_prompts_bp)

# Export for easy import
__all__ = [
    'admin_bp',
    'register_admin_blueprints',
    'admin_dashboard_bp',
    'admin_platforms_bp',
    'admin_features_bp',
    'admin_packages_bp'
]