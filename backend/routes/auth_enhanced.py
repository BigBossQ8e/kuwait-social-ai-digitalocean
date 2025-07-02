"""
Enhanced Authentication Routes with JWT Refresh Tokens
Handles login, logout, token refresh, and password management
"""
from flask import Blueprint, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
from functools import wraps
import jwt

from models import db, User
from services.auth_service import auth_service
from utils.validators import validate_email, validate_password

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

auth_enhanced_bp = Blueprint('auth_enhanced', __name__)


# Request schemas
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))
    remember_me = fields.Boolean(missing=False)


class RefreshTokenSchema(Schema):
    refresh_token = fields.String(required=True)


class ChangePasswordSchema(Schema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))
    confirm_password = fields.String(required=True)


# Decorators
def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token format'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authentication token is missing'
            }), 401
        
        # Verify token
        payload, error = auth_service.verify_token(token)
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 401
        
        # Add user info to context
        g.current_user_id = payload['user_id']
        g.current_user = User.query.get(payload['user_id'])
        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated


# Routes
@auth_enhanced_bp.route('/api/auth/v2/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Enhanced login endpoint with refresh tokens"""
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({
            'success': False,
            'errors': e.messages
        }), 400
    
    # Get IP address for logging
    ip_address = request.remote_addr
    
    # Authenticate user
    user, error = auth_service.authenticate_user(
        data['email'],
        data['password'],
        ip_address
    )
    
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 401
    
    # Generate tokens
    tokens = auth_service.generate_tokens(user)
    
    # Prepare response
    response_data = {
        'success': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': getattr(user, 'name', user.email.split('@')[0]),  # Use email prefix if no name
            'role': user.role
        },
        'tokens': tokens
    }
    
    # Add role-specific data
    if user.role == 'admin' and user.admin_profile:
        response_data['user']['admin_role'] = user.admin_profile.role
        response_data['user']['permissions'] = tokens['permissions'] if 'permissions' in tokens else []
    elif user.role == 'client' and user.client_profile:
        response_data['user']['company'] = user.client_profile.company_name
        response_data['user']['client_id'] = user.client_profile.id
    
    return jsonify(response_data), 200


@auth_enhanced_bp.route('/api/auth/v2/refresh', methods=['POST'])
@limiter.limit("10 per minute")
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        schema = RefreshTokenSchema()
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({
            'success': False,
            'errors': e.messages
        }), 400
    
    # Get IP address
    ip_address = request.remote_addr
    
    # Refresh token
    tokens, error = auth_service.refresh_access_token(
        data['refresh_token'],
        ip_address
    )
    
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 401
    
    return jsonify({
        'success': True,
        'tokens': tokens
    }), 200


@auth_enhanced_bp.route('/api/auth/v2/logout', methods=['POST'])
@token_required
def logout():
    """Logout user and revoke tokens"""
    # Get token ID from payload
    token_id = g.token_payload.get('token_id')
    
    # Logout user
    auth_service.logout(g.current_user_id, token_id)
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@auth_enhanced_bp.route('/api/auth/v2/logout-all', methods=['POST'])
@token_required
def logout_all_devices():
    """Logout from all devices by revoking all tokens"""
    # Revoke all tokens
    auth_service.revoke_token(g.current_user_id)
    
    return jsonify({
        'success': True,
        'message': 'Logged out from all devices'
    }), 200


@auth_enhanced_bp.route('/api/auth/v2/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user information"""
    user = g.current_user
    
    response_data = {
        'success': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    }
    
    # Add role-specific data
    if user.role == 'admin' and user.admin_profile:
        admin = user.admin_profile
        response_data['user']['admin'] = {
            'id': admin.id,
            'role': admin.role,
            'department': admin.department,
            'permissions': g.token_payload.get('permissions', [])
        }
    elif user.role == 'client' and user.client_profile:
        client = user.client_profile
        response_data['user']['client'] = {
            'id': client.id,
            'company_name': client.company_name,
            'subscription_plan': client.subscription_plan,
            'is_active': client.is_active
        }
    
    # Check if impersonating
    if g.token_payload.get('impersonation'):
        response_data['impersonation'] = {
            'active': True,
            'by_admin_id': g.token_payload.get('impersonated_by')
        }
    
    return jsonify(response_data), 200


@auth_enhanced_bp.route('/api/auth/v2/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        schema = ChangePasswordSchema()
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({
            'success': False,
            'errors': e.messages
        }), 400
    
    # Validate passwords match
    if data['new_password'] != data['confirm_password']:
        return jsonify({
            'success': False,
            'error': 'New passwords do not match'
        }), 400
    
    # Validate password strength
    is_valid, message = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({
            'success': False,
            'error': message
        }), 400
    
    # Change password
    success, error = auth_service.change_password(
        g.current_user_id,
        data['current_password'],
        data['new_password']
    )
    
    if not success:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully. Please login again.'
    }), 200


@auth_enhanced_bp.route('/api/auth/v2/validate-token', methods=['GET'])
@token_required
def validate_token():
    """Validate current token"""
    return jsonify({
        'success': True,
        'valid': True,
        'user_id': g.current_user_id,
        'expires_at': g.token_payload.get('exp')
    }), 200


# Admin-only endpoints
@auth_enhanced_bp.route('/api/auth/v2/impersonate', methods=['POST'])
@token_required
def impersonate_user():
    """Create impersonation token (admin only)"""
    # Check if user is admin
    if g.current_user.role != 'admin':
        return jsonify({
            'success': False,
            'error': 'Insufficient permissions'
        }), 403
    
    data = request.get_json()
    target_user_id = data.get('user_id')
    duration = data.get('duration_minutes', 60)
    
    if not target_user_id:
        return jsonify({
            'success': False,
            'error': 'Target user ID is required'
        }), 400
    
    # Create impersonation token
    token, error = auth_service.create_impersonation_token(
        g.current_user.admin_profile.id,
        target_user_id,
        duration
    )
    
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    return jsonify({
        'success': True,
        'impersonation_token': token,
        'expires_in_minutes': duration
    }), 200


@auth_enhanced_bp.route('/api/auth/v2/sessions', methods=['GET'])
@token_required
def get_active_sessions():
    """Get user's active sessions (tokens)"""
    # This would require tracking sessions in database
    # For now, return placeholder
    return jsonify({
        'success': True,
        'sessions': [
            {
                'current': True,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'last_activity': g.token_payload.get('iat')
            }
        ]
    }), 200


# Error handlers
@auth_enhanced_bp.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'success': False,
        'error': 'Too many requests. Please try again later.'
    }), 429