"""
Updated registration route that stores the client's requested plan
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from extensions import db
from models import User, Client, AuditLog
from utils.validators import validate_request, sanitize_input
from schemas import UserRegistrationSchema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_request(UserRegistrationSchema)
def register(validated_data):
    """Register new client account with plan selection"""
    
    # Check if user exists
    if User.query.filter_by(email=validated_data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    try:
        # Sanitize text inputs
        company_name = sanitize_input(validated_data['company_name'])
        contact_name = sanitize_input(validated_data['contact_name'])
        
        # Get requested plan
        requested_plan = validated_data.get('requested_plan', 'professional')
        
        # Create user (inactive until admin approval)
        user = User(
            email=validated_data['email'],
            role='client',
            is_active=False  # Requires admin approval
        )
        user.set_password(validated_data['password'])
        db.session.add(user)
        db.session.flush()
        
        # Create client profile with requested plan
        client = Client(
            user_id=user.id,
            company_name=company_name,
            contact_name=contact_name,
            phone=validated_data['phone'],
            address=sanitize_input(validated_data.get('address', '')),
            subscription_plan='pending',  # Will be set to requested_plan after approval
            subscription_status='pending_approval',
            subscription_start=None,
            subscription_end=None,
            # Store requested plan in metadata or custom field
            requested_plan=requested_plan  # Add this field to Client model
        )
        db.session.add(client)
        
        # Log registration with plan info
        audit = AuditLog(
            user_id=user.id,
            action='user_registered',
            resource_type='user',
            resource_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={
                'status': 'pending_approval',
                'requested_plan': requested_plan,
                'company_name': company_name
            }
        )
        db.session.add(audit)
        
        db.session.commit()
        
        # TODO: Send notification to admin about new registration
        # Include the requested plan in the notification
        
        return jsonify({
            'message': f'Registration successful. Your account is pending approval. You selected the {requested_plan} plan.',
            'status': 'pending_approval',
            'user': {
                'id': user.id,
                'email': user.email,
                'company_name': client.company_name,
                'requested_plan': requested_plan
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500