"""
Minimal Flask app for testing - Fixed version
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Simple User model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False)
    
    def check_password(self, password):
        # Simple password check for testing
        return True  # Always return True for testing
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role
        }

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Kuwait Social AI API - Minimal Version"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # For testing, create a mock user response
        # In production, you would query the database
        
        # Create test user data based on email
        if email == 'test@restaurant.com':
            user_data = {
                'id': 1,
                'email': email,
                'role': 'client',
                'company_name': 'Test Restaurant'
            }
            client_id = 1
        elif email == 'admin@kuwaitsocial.ai':
            user_data = {
                'id': 2,
                'email': email,
                'role': 'admin',
                'full_name': 'Admin User'
            }
            client_id = None
        else:
            # Default client user
            user_data = {
                'id': 3,
                'email': email,
                'role': 'client',
                'company_name': 'Default Restaurant'
            }
            client_id = 3
        
        # Create token
        additional_claims = {'role': user_data['role']}
        if user_data['role'] == 'client':
            additional_claims['client_id'] = client_id
        
        access_token = create_access_token(
            identity=str(user_data['id']),
            additional_claims=additional_claims
        )
        
        return jsonify({
            'access_token': access_token,
            'user': user_data
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db else 'disconnected',
        'version': '1.0.0-minimal'
    })

if __name__ == '__main__':
    print("Starting Kuwait Social AI - Minimal Version")
    print("Login endpoint: http://localhost:5001/api/auth/login")
    print("\nTest credentials:")
    print("- test@restaurant.com / any password")
    print("- admin@kuwaitsocial.ai / any password")
    
    app.run(debug=True, port=5001)