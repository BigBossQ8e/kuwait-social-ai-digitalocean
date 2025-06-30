"""
Test route for login without model dependencies
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
import psycopg2
from werkzeug.security import check_password_hash
from datetime import datetime

test_bp = Blueprint('test', __name__)

# Database connection
DB_CONFIG = {
    'host': 'kuwait-social-db',
    'port': 5432,
    'database': 'kuwait_social_ai',
    'user': 'kuwait_user',
    'password': 'secure_password'
}

@test_bp.route('/test-login', methods=['POST'])
def test_login():
    """Test login endpoint that bypasses model issues"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        # Connect directly to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query user
        cursor.execute(
            "SELECT id, email, password_hash, role, is_active FROM users WHERE email = %s",
            (data['email'],)
        )
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_id, email, password_hash, role, is_active = result
        
        if not is_active:
            return jsonify({'error': 'Account suspended'}), 403
        
        # Check password
        if not check_password_hash(password_hash, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get additional profile data
        profile_data = {'role': role}
        
        if role == 'admin':
            cursor.execute(
                "SELECT id, full_name FROM admins WHERE user_id = %s",
                (user_id,)
            )
            admin_result = cursor.fetchone()
            if admin_result:
                profile_data['admin_id'] = admin_result[0]
                profile_data['full_name'] = admin_result[1]
        
        # Update last login
        cursor.execute(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.utcnow(), user_id)
        )
        conn.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims=profile_data
        )
        refresh_token = create_refresh_token(
            identity=str(user_id),
            additional_claims=profile_data
        )
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user_id,
                'email': email,
                'role': role,
                **profile_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500