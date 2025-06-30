"""
Simple admin client list endpoint
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.core import User, Client
from extensions import db

admin_clients_bp = Blueprint('admin_clients', __name__)

@admin_clients_bp.route('/clients', methods=['GET'])
@jwt_required()
def get_all_clients():
    """Get all clients - simplified version"""
    # Check if user is admin
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Get all clients with their users
        clients = db.session.query(Client, User).join(User, Client.user_id == User.id).all()
        
        client_list = []
        for client, user in clients:
            client_data = {
                'id': client.id,
                'user_id': client.user_id,
                'email': user.email,
                'company_name': client.company_name,
                'contact_name': client.contact_name,
                'phone': client.phone,
                'subscription_plan': client.subscription_plan,
                'subscription_status': client.subscription_status,
                'monthly_posts_limit': client.monthly_posts_limit,
                'monthly_posts_used': client.monthly_posts_used,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            client_list.append(client_data)
        
        return jsonify({
            'clients': client_list,
            'total': len(client_list)
        }), 200
        
    except Exception as e:
        print(f"Error in get_all_clients: {str(e)}")
        return jsonify({'error': str(e)}), 500