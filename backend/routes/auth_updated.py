"""
Updated authentication routes - No automatic trial assignment
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime
from extensions import db
from models import User, Client, Admin, Owner, AuditLog
from utils.validators import validate_request, sanitize_input
from schemas import UserRegistrationSchema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_request(UserRegistrationSchema)
def register(validated_data):
    """Register new client account - No automatic trial"""
    
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
            role='client',
            is_active=False  # Account requires admin approval
        )
        user.set_password(validated_data['password'])
        db.session.add(user)
        db.session.flush()
        
        # Create client profile WITHOUT trial
        client = Client(
            user_id=user.id,
            company_name=company_name,
            contact_name=contact_name,
            phone=validated_data['phone'],
            address=sanitize_input(validated_data.get('address', '')),
            subscription_plan='pending',  # Pending admin approval
            subscription_status='pending_approval',
            subscription_start=None,  # No subscription until admin approves
            subscription_end=None
        )
        db.session.add(client)
        
        # Log registration
        audit = AuditLog(
            user_id=user.id,
            action='user_registered',
            resource_type='user',
            resource_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={'status': 'pending_approval'}
        )
        db.session.add(audit)
        
        db.session.commit()
        
        # Send notification to admin about new registration
        # TODO: Implement admin notification system
        
        return jsonify({
            'message': 'Registration successful. Your account is pending approval.',
            'status': 'pending_approval',
            'user': {
                'id': user.id,
                'email': user.email,
                'company_name': client.company_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


# Admin endpoint to approve client and optionally gift trial
@auth_bp.route('/admin/approve-client/<int:client_id>', methods=['POST'])
@jwt_required()
def approve_client(client_id):
    """Admin approves client and optionally gifts trial days"""
    
    # Verify admin role
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role not in ['admin', 'owner']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get request data
    data = request.get_json()
    gift_trial_days = data.get('gift_trial_days', 0)  # Default: no trial
    subscription_plan = data.get('subscription_plan', 'basic')
    
    try:
        # Find client
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Get associated user
        user = User.query.get(client.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Activate user account
        user.is_active = True
        
        # Set subscription based on admin decision
        if gift_trial_days > 0:
            # Gift trial period
            client.subscription_plan = 'trial'
            client.subscription_status = 'trial'
            client.subscription_start = datetime.utcnow()
            client.subscription_end = datetime.utcnow() + timedelta(days=gift_trial_days)
            approval_message = f"Account approved with {gift_trial_days} day trial"
        else:
            # Regular subscription (requires payment)
            client.subscription_plan = subscription_plan
            client.subscription_status = 'pending_payment'
            client.subscription_start = None
            client.subscription_end = None
            approval_message = "Account approved. Payment required to activate."
        
        # Log approval
        audit = AuditLog(
            user_id=current_user_id,
            action='client_approved',
            resource_type='client',
            resource_id=client_id,
            details={
                'approved_by': current_user.email,
                'gift_trial_days': gift_trial_days,
                'subscription_plan': subscription_plan
            }
        )
        db.session.add(audit)
        
        db.session.commit()
        
        # TODO: Send approval email to client
        
        return jsonify({
            'success': True,
            'message': approval_message,
            'client': {
                'id': client.id,
                'company_name': client.company_name,
                'email': user.email,
                'subscription_plan': client.subscription_plan,
                'subscription_status': client.subscription_status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Approval failed', 'details': str(e)}), 500


# Admin endpoint to list pending approvals
@auth_bp.route('/admin/pending-clients', methods=['GET'])
@jwt_required()
def get_pending_clients():
    """Get list of clients pending approval"""
    
    # Verify admin role
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role not in ['admin', 'owner']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Find all pending clients
        pending_clients = db.session.query(Client, User).join(
            User, Client.user_id == User.id
        ).filter(
            Client.subscription_status == 'pending_approval'
        ).all()
        
        clients_list = []
        for client, user in pending_clients:
            clients_list.append({
                'client_id': client.id,
                'company_name': client.company_name,
                'contact_name': client.contact_name,
                'email': user.email,
                'phone': client.phone,
                'registered_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            'success': True,
            'pending_count': len(clients_list),
            'clients': clients_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch pending clients', 'details': str(e)}), 500