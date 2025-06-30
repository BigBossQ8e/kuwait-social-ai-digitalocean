"""
Admin client management routes
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Client, db
from sqlalchemy import desc
import logging

logger = logging.getLogger(__name__)

admin_clients_bp = Blueprint('admin_clients', __name__)

def admin_required(fn):
    """Decorator to require admin role"""
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@admin_clients_bp.route('/clients', methods=['GET'])
@admin_required
def get_all_clients():
    """
    Get all clients with their details
    Returns: JSON array of client objects
    """
    try:
        # Get query parameters for filtering/pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        plan = request.args.get('plan', '')
        
        # Build query
        query = Client.query.join(User)
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Client.company_name.ilike(f'%{search}%'),
                    Client.contact_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        if status:
            query = query.filter(Client.subscription_status == status)
            
        if plan:
            query = query.filter(Client.subscription_plan == plan)
        
        # Order by created date
        query = query.order_by(desc(User.created_at))
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Build response
        clients = []
        for client in pagination.items:
            client_data = {
                'id': client.id,
                'user_id': client.user_id,
                'email': client.user.email,
                'company_name': client.company_name,
                'contact_name': client.contact_name,
                'phone': client.phone,
                'address': client.address,
                'subscription_plan': client.subscription_plan,
                'subscription_status': client.subscription_status,
                'subscription_start': client.subscription_start.isoformat() if client.subscription_start else None,
                'subscription_end': client.subscription_end.isoformat() if client.subscription_end else None,
                'monthly_posts_limit': client.monthly_posts_limit,
                'monthly_posts_used': client.monthly_posts_used,
                'is_active': client.user.is_active,
                'created_at': client.user.created_at.isoformat() if client.user.created_at else None,
                'last_login': client.user.last_login.isoformat() if client.user.last_login else None,
                'telegram_linked': bool(getattr(client, 'telegram_id', None)),
                
                # Additional stats
                'total_posts': len(client.posts) if hasattr(client, 'posts') else 0,
                'social_accounts': len(client.social_accounts) if hasattr(client, 'social_accounts') else 0,
            }
            clients.append(client_data)
        
        # Return paginated response
        return jsonify({
            'clients': clients,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}")
        return jsonify({'error': 'Failed to fetch clients'}), 500

@admin_clients_bp.route('/clients/<int:client_id>', methods=['GET'])
@admin_required
def get_client_details(client_id):
    """Get detailed information about a specific client"""
    try:
        client = Client.query.get(client_id)
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Build detailed response
        client_data = {
            'id': client.id,
            'user_id': client.user_id,
            'email': client.user.email,
            'company_name': client.company_name,
            'contact_name': client.contact_name,
            'phone': client.phone,
            'address': client.address,
            'subscription': {
                'plan': client.subscription_plan,
                'status': client.subscription_status,
                'start_date': client.subscription_start.isoformat() if client.subscription_start else None,
                'end_date': client.subscription_end.isoformat() if client.subscription_end else None,
                'monthly_posts_limit': client.monthly_posts_limit,
                'monthly_posts_used': client.monthly_posts_used,
                'posts_remaining': client.monthly_posts_limit - client.monthly_posts_used
            },
            'account': {
                'is_active': client.user.is_active,
                'created_at': client.user.created_at.isoformat() if client.user.created_at else None,
                'last_login': client.user.last_login.isoformat() if client.user.last_login else None,
                'telegram_linked': bool(getattr(client, 'telegram_id', None)),
                'telegram_linked_at': getattr(client, 'telegram_linked_at', None).isoformat() if getattr(client, 'telegram_linked_at', None) else None
            },
            'stats': {
                'total_posts': len(client.posts) if hasattr(client, 'posts') else 0,
                'social_accounts': len(client.social_accounts) if hasattr(client, 'social_accounts') else 0,
                'total_analytics': len(client.analytics) if hasattr(client, 'analytics') else 0
            }
        }
        
        # Add social accounts if available
        if hasattr(client, 'social_accounts'):
            client_data['social_accounts'] = [
                {
                    'id': acc.id,
                    'platform': acc.platform,
                    'account_name': acc.account_name,
                    'is_active': acc.is_active,
                    'connected_at': acc.connected_at.isoformat() if acc.connected_at else None
                }
                for acc in client.social_accounts
            ]
        
        return jsonify(client_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching client {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch client details'}), 500

@admin_clients_bp.route('/clients/<int:client_id>', methods=['PUT'])
@admin_required
def update_client(client_id):
    """Update client information"""
    try:
        client = Client.query.get(client_id)
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
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
        if 'subscription_status' in data:
            client.subscription_status = data['subscription_status']
        if 'monthly_posts_limit' in data:
            client.monthly_posts_limit = data['monthly_posts_limit']
        
        # Update user active status if provided
        if 'is_active' in data:
            client.user.is_active = data['is_active']
        
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
        logger.error(f"Error updating client {client_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update client'}), 500

@admin_clients_bp.route('/clients/stats', methods=['GET'])
@admin_required
def get_client_stats():
    """Get aggregate statistics about clients"""
    try:
        total_clients = Client.query.count()
        active_clients = Client.query.join(User).filter(User.is_active == True).count()
        
        # Count by subscription plan
        plan_counts = db.session.query(
            Client.subscription_plan, 
            db.func.count(Client.id)
        ).group_by(Client.subscription_plan).all()
        
        # Count by subscription status
        status_counts = db.session.query(
            Client.subscription_status, 
            db.func.count(Client.id)
        ).group_by(Client.subscription_status).all()
        
        stats = {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': total_clients - active_clients,
            'by_plan': dict(plan_counts),
            'by_status': dict(status_counts)
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error fetching client stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch client statistics'}), 500