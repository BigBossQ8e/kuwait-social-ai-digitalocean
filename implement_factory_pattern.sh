#!/bin/bash
# Implement proper Flask factory pattern with extensions.py

echo "=== Implementing Flask Factory Pattern with extensions.py ==="
echo

ssh root@209.38.176.129 << 'SSHEOF'
cd /opt/kuwait-social-ai/backend

# Backup current state
echo "1. Creating backups..."
cp -r models models.backup_factory_pattern
cp app_factory.py app_factory.py.backup_factory_pattern

# Step 1: Create extensions.py
echo "2. Creating extensions.py..."
cat > extensions.py << 'EOF'
"""
Flask extensions initialization
All extensions should be initialized here to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create extension instances
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
EOF

# Step 2: Update all model imports
echo "3. Updating model imports to use extensions.py..."

# Update models/__init__.py
sed -i 's/from flask_sqlalchemy import SQLAlchemy/# Moved to extensions.py/' models/__init__.py
sed -i 's/db = SQLAlchemy()/from extensions import db/' models/__init__.py

# Update all model files to import from extensions
for file in models/*.py; do
    if [ -f "$file" ] && grep -q "from \. import db\|from models import db" "$file"; then
        echo "  Updating $file"
        # Replace various import patterns
        sed -i 's/from \. import db/from extensions import db/' "$file"
        sed -i 's/from models import db/from extensions import db/' "$file"
        sed -i 's/from app import db/from extensions import db/' "$file"
        sed -i 's/from app_factory import db/from extensions import db/' "$file"
    fi
done

# Update models.py if it exists
if [ -f "models.py" ]; then
    echo "  Updating models.py"
    sed -i 's/from models import db/from extensions import db/' models.py
    sed -i 's/# db = SQLAlchemy()/from extensions import db/' models.py
fi

# Step 3: Update app_factory.py
echo "4. Updating app_factory.py to use extensions..."
cat > app_factory_new.py << 'EOF'
"""
Flask Application Factory
"""
from flask import Flask, jsonify
import os
import logging
from logging.handlers import RotatingFileHandler

# Import extensions from centralized location
from extensions import db, migrate, jwt, cors, limiter

# Import configuration
from config.config import Config
from config.database_config import DatabaseConfig
from config.platform_config import PlatformConfig

# Import models to ensure they're registered
import models

def create_app(config_name=None):
    """Create Flask application with factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    app.config.from_object(Config)
    
    # Database configuration
    database_config = DatabaseConfig()
    app.config['SQLALCHEMY_DATABASE_URI'] = database_config.get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # JWT configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.JWT_REFRESH_TOKEN_EXPIRES
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=Config.CORS_ORIGINS)
    limiter.init_app(app)
    
    # Setup logging
    if not app.debug:
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
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.client import client_bp
    from routes.admin import admin_bp
    from routes.owner import owner_bp
    from routes.analytics import analytics_bp
    from routes.content import content_bp
    from routes.social import social_bp
    from routes.payments import payments_bp
    from routes.health import health_bp
    from routes.prayer_times import prayer_bp
    from routes.monitoring import monitoring_bp
    from routes.client_errors import client_errors_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(client_bp, url_prefix='/api/client')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(owner_bp, url_prefix='/api/owner')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(social_bp, url_prefix='/api/social')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(prayer_bp, url_prefix='/api/prayer-times')
    app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')
    app.register_blueprint(client_errors_bp, url_prefix='/api/errors')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found', 'error_code': 'NOT_FOUND'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return jsonify({'error': 'An internal error occurred', 'error_code': 'INTERNAL_ERROR'}), 500
    
    return app
EOF

# Backup old app_factory and replace
mv app_factory.py app_factory_old.py
mv app_factory_new.py app_factory.py

# Step 4: Update route imports if needed
echo "5. Updating route imports..."
for file in routes/*.py; do
    if grep -q "from app_factory import db\|from models import db\|from app import db" "$file"; then
        echo "  Updating imports in $file"
        sed -i 's/from app_factory import db/from extensions import db/' "$file"
        sed -i 's/from models import db/from extensions import db/' "$file"
        sed -i 's/from app import db/from extensions import db/' "$file"
    fi
done

# Step 5: Update wsgi.py to use the factory
echo "6. Updating wsgi.py..."
cat > wsgi.py << 'EOF'
"""
WSGI entry point
"""
import os
from app_factory import create_app

app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

# Step 6: Verify changes
echo -e "\n7. Verifying changes..."
echo "Extensions.py created:"
ls -la extensions.py

echo -e "\nChecking db imports:"
grep -n "from extensions import db" models/__init__.py models/*.py | head -5

echo -e "\nChecking SQLAlchemy instances:"
grep "db = SQLAlchemy()" *.py models/*.py | grep -v "^#" | grep -v backup

# Step 7: Restart backend
echo -e "\n8. Restarting backend..."
cd /opt/kuwait-social-ai
docker-compose restart backend

echo "Waiting for backend to start..."
sleep 15

# Check status
echo -e "\n9. Final status check..."
docker-compose ps backend
docker-compose logs --tail=50 backend | grep -E "ERROR|Exception|SQLAlchemy|startup|Running" | tail -20

SSHEOF