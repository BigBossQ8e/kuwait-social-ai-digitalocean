#!/bin/bash

echo "🔧 Fixing Backend Issues and Testing Startup"
echo "=================================================================================="

cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Create missing route files
echo "📝 Creating missing route files..."

# Create owner routes
cat > routes/owner.py << 'EOF'
"""Owner routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

owner_bp = Blueprint('owner', __name__)

@owner_bp.route('/dashboard')
@jwt_required()
def dashboard():
    """Owner dashboard endpoint"""
    return jsonify({"message": "Owner dashboard - Under construction"}), 200
EOF

# Create admin routes
cat > routes/admin.py << 'EOF'
"""Admin routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@jwt_required()
def dashboard():
    """Admin dashboard endpoint"""
    return jsonify({"message": "Admin dashboard - Under construction"}), 200
EOF

# Create analytics routes
cat > routes/analytics.py << 'EOF'
"""Analytics routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/overview')
@jwt_required()
def overview():
    """Analytics overview endpoint"""
    return jsonify({"message": "Analytics overview - Under construction"}), 200
EOF

# Create social routes
cat > routes/social.py << 'EOF'
"""Social media routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

social_bp = Blueprint('social', __name__)

@social_bp.route('/accounts')
@jwt_required()
def accounts():
    """Social accounts endpoint"""
    return jsonify({"message": "Social accounts - Under construction"}), 200
EOF

# Create telegram routes
cat > routes/telegram.py << 'EOF'
"""Telegram bot routes - placeholder"""
from flask import Blueprint, jsonify

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    return jsonify({"message": "Telegram webhook received"}), 200
EOF

# Create payments routes
cat > routes/payments.py << 'EOF'
"""Payment routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/plans')
def plans():
    """Get available payment plans"""
    return jsonify({"message": "Payment plans - Under construction"}), 200
EOF

echo "✅ Created missing route files"
echo ""
echo "🚀 Starting backend..."
echo "=================================================================================="
python wsgi.py