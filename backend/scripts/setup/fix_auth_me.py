#!/usr/bin/env python3
"""Fix script for /auth/me endpoint"""

# This is the corrected version of the get_current_user function
# Copy this into routes/auth.py replacing the existing get_current_user function

fix_code = '''
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        # Get user ID from JWT (might be string)
        user_id = get_jwt_identity()
        
        # Convert to int if needed
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        # Get user
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Basic user data
        user_data = {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'is_active': getattr(user, 'is_active', True),
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
        }
        
        # Add role-specific data
        if user.role == 'client':
            client = Client.query.filter_by(user_id=user.id).first()
            if client:
                user_data.update({
                    'client_id': client.id,
                    'company_name': getattr(client, 'company_name', 'N/A'),
                    'subscription_plan': getattr(client, 'subscription_plan', 'basic'),
                    'subscription_status': getattr(client, 'subscription_status', 'trial')
                })
        
        return jsonify(user_data), 200
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in /auth/me: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
'''

print("Fix code for /auth/me endpoint:")
print("=" * 50)
print(fix_code)
print("=" * 50)
print("\nTo apply this fix:")
print("1. SSH into your server: ssh root@209.38.176.129")
print("2. Edit the auth.py file in the container:")
print("   docker exec -it backend-web-1 bash")
print("   cd /app/routes")
print("   vi auth.py")
print("3. Find the get_current_user function and replace it with the code above")
print("4. Exit and restart the container:")
print("   exit")
print("   docker restart backend-web-1")