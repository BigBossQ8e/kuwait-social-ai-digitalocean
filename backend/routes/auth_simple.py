"""
Simple auth routes that work without complex JWT
"""
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Admin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta

auth_simple_bp = Blueprint('auth_simple', __name__)

@auth_simple_bp.route('/api/auth/simple-login', methods=['POST'])
def simple_login():
    """Simple login that works"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # For demo, accept admin@example.com with any password
    if email == 'admin@example.com':
        # Create or get admin user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                password_hash=generate_password_hash('password'),
                is_active=True,
                role='admin'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create admin profile
            admin = Admin(
                user_id=user.id,
                full_name='Test Admin',
                permissions={'all': True, 'role': 'owner'}
            )
            db.session.add(admin)
            db.session.commit()
        
        # Create simple token with all needed claims
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'user_id': user.id,
                'email': user.email,
                'role': 'admin',
                'is_admin': True,
                'admin_role': 'owner'
            },
            expires_delta=timedelta(days=1)
        )
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': 'admin'
            }
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@auth_simple_bp.route('/api/auth/simple-check', methods=['GET'])
@jwt_required()
def check_auth():
    """Check if authenticated"""
    user_id = get_jwt_identity()
    return jsonify({
        'success': True,
        'user_id': user_id,
        'message': 'Authenticated'
    })