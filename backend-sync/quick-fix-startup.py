#!/usr/bin/env python3
"""
Quick fix script to get the backend running
This creates a minimal working configuration
"""

import os
import sys

# Change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

# Create a minimal app.py that bypasses all the import issues
minimal_app = '''
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import timedelta

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///kuwait_social.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'])
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Basic routes
@app.route('/')
def index():
    return jsonify({
        "message": "Kuwait Social AI API",
        "version": "1.0.0",
        "status": "running"
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    # Placeholder login
    return jsonify({
        "access_token": "mock_token",
        "user": {
            "id": 1,
            "email": "test@example.com",
            "role": "client"
        }
    })

@app.route('/api/client/dashboard')
def client_dashboard():
    return jsonify({
        "message": "Client dashboard data",
        "stats": {
            "posts": 10,
            "followers": 1000,
            "engagement": 5.5
        }
    })

if __name__ == '__main__':
    print("\\n" + "="*60)
    print("🚀 Kuwait Social AI Backend - Minimal Mode")
    print("="*60)
    print("✅ API running at: http://localhost:5000")
    print("✅ Health check: http://localhost:5000/api/health")
    print("\\nPress Ctrl+C to stop the server")
    print("="*60 + "\\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
'''

# Write the minimal app
with open('app_minimal.py', 'w') as f:
    f.write(minimal_app)

print("✅ Created minimal app configuration")
print("🚀 Starting backend with minimal configuration...")
print("")

# Run the minimal app
os.system(f"{sys.executable} app_minimal.py")