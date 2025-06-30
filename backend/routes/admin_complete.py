"""Admin routes for Kuwait Social AI"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from extensions import db
from models import User, Client, Post, Admin
from functools import wraps
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

def admin_required(fn):
    """Decorator to ensure user is an admin"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/stats')
@admin_required
def get_stats():
    """Get admin dashboard statistics"""
    try:
        total_clients = Client.query.count()
        active_clients = Client.query.filter_by(subscription_status='active').count()
        trial_clients = Client.query.filter_by(subscription_status='trial').count()
        total_posts = Post.query.count()
        
        return jsonify({
            'total_clients': total_clients,
            'active_clients': active_clients,
            'trial_clients': trial_clients,
            'total_posts': total_posts
        }), 200
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@admin_bp.route('/clients')
@admin_required
def get_clients():
    """Get list of all clients with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Query clients with user info
        pagination = db.session.query(Client, User).join(
            User, Client.user_id == User.id
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        clients = []
        for client, user in pagination.items:
            clients.append({
                'id': client.id,
                'company_name': client.company_name,
                'contact_name': client.contact_name,
                'email': user.email,
                'phone': client.phone,
                'subscription_plan': client.subscription_plan,
                'subscription_status': client.subscription_status,
                'monthly_posts_used': client.monthly_posts_used,
                'monthly_posts_limit': client.monthly_posts_limit,
                'created_at': client.created_at.isoformat() if client.created_at else None,
                'subscription_end': client.subscription_end.isoformat() if client.subscription_end else None
            })
        
        return jsonify({
            'clients': clients,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}")
        return jsonify({'error': 'Failed to fetch clients'}), 500

@admin_bp.route('/clients/<int:client_id>')
@admin_required
def get_client(client_id):
    """Get single client details"""
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
            
        user = User.query.get(client.user_id)
        
        return jsonify({
            'id': client.id,
            'company_name': client.company_name,
            'contact_name': client.contact_name,
            'email': user.email,
            'phone': client.phone,
            'address': client.address,
            'subscription_plan': client.subscription_plan,
            'subscription_status': client.subscription_status,
            'monthly_posts_used': client.monthly_posts_used,
            'monthly_posts_limit': client.monthly_posts_limit,
            'created_at': client.created_at.isoformat() if client.created_at else None,
            'subscription_start': client.subscription_start.isoformat() if client.subscription_start else None,
            'subscription_end': client.subscription_end.isoformat() if client.subscription_end else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching client {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch client'}), 500

@admin_bp.route('/clients', methods=['POST'])
@admin_required
def create_client():
    """Create new client account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['company_name', 'contact_name', 'email', 'password', 'phone', 'subscription_plan']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        user = User(
            email=data['email'],
            role='client'
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        # Set subscription dates based on plan
        subscription_start = datetime.utcnow()
        if data['subscription_plan'] == 'trial':
            subscription_end = subscription_start + timedelta(days=7)
        else:
            subscription_end = subscription_start + timedelta(days=30)
        
        # Set monthly posts limit based on plan
        posts_limit_map = {
            'trial': 10,
            'basic': 30,
            'professional': 100,
            'premium': 500
        }
        monthly_posts_limit = posts_limit_map.get(data['subscription_plan'], 30)
        
        # Create client profile
        client = Client(
            user_id=user.id,
            company_name=data['company_name'],
            contact_name=data['contact_name'],
            phone=data['phone'],
            address=data.get('address', ''),
            subscription_plan=data['subscription_plan'],
            subscription_status='trial' if data['subscription_plan'] == 'trial' else 'active',
            subscription_start=subscription_start,
            subscription_end=subscription_end,
            monthly_posts_limit=monthly_posts_limit,
            monthly_posts_used=0
        )
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'message': 'Client created successfully',
            'client': {
                'id': client.id,
                'company_name': client.company_name,
                'email': user.email,
                'subscription_plan': client.subscription_plan
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating client: {str(e)}")
        return jsonify({'error': 'Failed to create client'}), 500

@admin_bp.route('/clients/<int:client_id>', methods=['PUT'])
@admin_required
def update_client(client_id):
    """Update client details"""
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.get_json()
        
        # Update client fields
        if 'company_name' in data:
            client.company_name = data['company_name']
        if 'contact_name' in data:
            client.contact_name = data['contact_name']
        if 'phone' in data:
            client.phone = data['phone']
        if 'address' in data:
            client.address = data['address']
        if 'subscription_plan' in data:
            client.subscription_plan = data['subscription_plan']
            # Update posts limit based on new plan
            posts_limit_map = {
                'trial': 10,
                'basic': 30,
                'professional': 100,
                'premium': 500
            }
            client.monthly_posts_limit = posts_limit_map.get(data['subscription_plan'], 30)
        if 'subscription_status' in data:
            client.subscription_status = data['subscription_status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Client updated successfully',
            'client': {
                'id': client.id,
                'company_name': client.company_name,
                'subscription_plan': client.subscription_plan,
                'subscription_status': client.subscription_status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating client {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to update client'}), 500

@admin_bp.route('/clients/<int:client_id>/suspend', methods=['POST'])
@admin_required
def suspend_client(client_id):
    """Suspend client account"""
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        client.subscription_status = 'suspended'
        user = User.query.get(client.user_id)
        user.is_active = False
        
        db.session.commit()
        
        return jsonify({'message': 'Client suspended successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error suspending client {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to suspend client'}), 500

@admin_bp.route('/clients/<int:client_id>/activate', methods=['POST'])
@admin_required
def activate_client(client_id):
    """Activate client account"""
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        client.subscription_status = 'active'
        user = User.query.get(client.user_id)
        user.is_active = True
        
        db.session.commit()
        
        return jsonify({'message': 'Client activated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error activating client {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to activate client'}), 500

@admin_bp.route('/clients/<int:client_id>', methods=['DELETE'])
@admin_required
def delete_client(client_id):
    """Delete client account (soft delete)"""
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        user = User.query.get(client.user_id)
        
        # Soft delete - just mark as inactive
        user.is_active = False
        client.subscription_status = 'deleted'
        
        db.session.commit()
        
        return jsonify({'message': 'Client deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting client {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete client'}), 500

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard endpoint - returns summary data"""
    try:
        # Get various statistics
        total_clients = Client.query.count()
        active_clients = Client.query.filter_by(subscription_status='active').count()
        trial_clients = Client.query.filter_by(subscription_status='trial').count()
        total_posts = Post.query.count()
        
        # Get recent clients
        recent_clients = db.session.query(Client, User).join(
            User, Client.user_id == User.id
        ).order_by(Client.created_at.desc()).limit(5).all()
        
        recent_clients_data = []
        for client, user in recent_clients:
            recent_clients_data.append({
                'company_name': client.company_name,
                'email': user.email,
                'subscription_plan': client.subscription_plan,
                'created_at': client.created_at.isoformat() if client.created_at else None
            })
        
        return jsonify({
            'stats': {
                'total_clients': total_clients,
                'active_clients': active_clients,
                'trial_clients': trial_clients,
                'total_posts': total_posts
            },
            'recent_clients': recent_clients_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500