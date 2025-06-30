#\!/usr/bin/env python3
"""Minimal working Flask app for Kuwait Social AI"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
CORS(app, origins=['https://kwtsocial.com'])

# Database connection
def get_db():
    return psycopg2.connect(
        host='kuwait-social-db',
        database='kuwait_social_ai',
        user='kuwait_user',
        password='secure_password',
        cursor_factory=RealDictCursor
    )

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'kuwait-social-ai'})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get user
    cur.execute(
        "SELECT id, email, username, password_hash, role, company_name, is_active FROM users WHERE email = %s",
        (data['email'],)
    )
    user = cur.fetchone()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check password
    if not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user['is_active']:
        return jsonify({'error': 'Account suspended'}), 403
    
    # Create token
    token_payload = {
        'user_id': user['id'],
        'email': user['email'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    # Update last login
    cur.execute(
        "UPDATE users SET last_login = %s WHERE id = %s",
        (datetime.utcnow(), user['id'])
    )
    conn.commit()
    
    cur.close()
    conn.close()
    
    return jsonify({
        'access_token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'username': user['username'],
            'role': user['role'],
            'company_name': user['company_name']
        }
    })

@app.route('/api/auth/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No authorization token'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({
            'user_id': payload['user_id'],
            'email': payload['email'],
            'role': payload['role']
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
