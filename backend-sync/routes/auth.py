"""
Authentication routes for Kuwait Social AI
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import re
from models import db, User, Client, Admin, Owner, AuditLog
# from utils.email import send_welcome_email  # TODO: Create email utility
from utils.validators import validate_request, sanitize_input
from schemas import (
    UserRegistrationSchema, UserLoginSchema, 
    PasswordChangeSchema, UserResponseSchema
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_request(UserRegistrationSchema)
def register(validated_data):
    """Register new client account"""
    
    # Check if user exists
    if User.query.filter_by(email=validated_data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    try:
        # Sanitize text inputs
        company_name = sanitize_input(validated_data['company_name'])
        contact_name = sanitize_input(validated_data['contact_name'])
        
        # Create user
        user = User(
            email=validated_data['email'],
            role='client'
        )
        user.set_password(validated_data['password'])
        db.session.add(user)
        db.session.flush()
        
        # Create client profile
        client = Client(
            user_id=user.id,
            company_name=company_name,
            contact_name=contact_name,
            phone=validated_data['phone'],
            address=sanitize_input(validated_data.get('address', '')),
            subscription_plan='trial',
            subscription_start=datetime.utcnow(),
            subscription_end=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(client)
        
        # Log registration
        audit = AuditLog(
            user_id=user.id,
            action='user_registered',
            resource_type='user',
            resource_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit)
        
        db.session.commit()
        
        # Send welcome email
        # send_welcome_email(user.email, client.contact_name)  # TODO: Implement email service
        
        # Create tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'client_id': client.id}
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'client_id': client.id}
        )
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'company_name': client.company_name,
                'trial_days_remaining': 7
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
@validate_request(UserLoginSchema)
def login(validated_data):
    """Login user"""
    
    # Find user
    user = User.query.filter_by(email=validated_data['email']).first()
    
    if not user or not user.check_password(validated_data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account suspended'}), 403
    
    # Get profile based on role
    profile_data = {}
    if user.role == 'client':
        client = Client.query.filter_by(user_id=user.id).first()
        if client:
            profile_data = {
                'client_id': client.id,
                'company_name': client.company_name,
                'subscription_plan': client.subscription_plan,
                'subscription_status': client.subscription_status
            }
    elif user.role == 'admin':
        admin = Admin.query.filter_by(user_id=user.id).first()
        if admin:
            profile_data = {
                'admin_id': admin.id,
                'full_name': admin.full_name,
                'permissions': admin.permissions
            }
    elif user.role == 'owner':
        owner = Owner.query.filter_by(user_id=user.id).first()
        if owner:
            profile_data = {
                'owner_id': owner.id,
                'company_name': owner.company_name
            }
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create tokens
    claims = {'role': user.role}
    claims.update(profile_data)
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=claims
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims=claims
    )
    
    # Log login
    audit = AuditLog(
        user_id=user.id,
        action='user_login',
        resource_type='user',
        resource_id=user.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            **profile_data
        }
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    identity = get_jwt_identity()
    claims = get_jwt()
    
    access_token = create_access_token(
        identity=identity,
        additional_claims={k: v for k, v in claims.items() if k not in ['exp', 'iat', 'jti', 'type']}
    )
    
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (token should be blacklisted in production)"""
    user_id = get_jwt_identity()
    
    # Log logout
    audit = AuditLog(
        user_id=int(user_id),
        action='user_logout',
        resource_type='user',
        resource_id=int(user_id),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    # Always return success to prevent email enumeration
    if user:
        # Generate reset token and send email
        # Implementation depends on your email service
        pass
    
    return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    
    required_fields = ['token', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate password
    password_error = validate_password(data['password'])
    if password_error:
        return jsonify({'error': password_error}), 400
    
    # Verify token and reset password
    # Implementation depends on your token strategy
    
    return jsonify({'message': 'Password reset successful'}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile = {
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    }
    
    # Add role-specific data
    if user.role == 'client':
        client = Client.query.filter_by(user_id=user.id).first()
        if client:
            profile.update({
                'company_name': client.company_name,
                'contact_name': client.contact_name,
                'phone': client.phone,
                'subscription_plan': client.subscription_plan,
                'subscription_status': client.subscription_status,
                'telegram_linked': bool(client.telegram_id),
                'monthly_posts_remaining': client.monthly_posts_limit - client.monthly_posts_used
            })
    
    return jsonify(profile), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@validate_request(PasswordChangeSchema)
def change_password(validated_data):
    """Change user password"""
    user_id = int(get_jwt_identity())
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify current password
    if not user.check_password(validated_data['current_password']):
        return jsonify({'error': 'Current password incorrect'}), 401
    
    # Update password
    user.set_password(validated_data['new_password'])
    
    # Log password change
    audit = AuditLog(
        user_id=user_id,
        action='password_changed',
        resource_type='user',
        resource_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200