"""
Password Strength Check Endpoint
Provides real-time password strength feedback
"""

from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.password_strength import check_password_strength
from marshmallow import Schema, fields

# Create blueprint
password_check_bp = Blueprint('password_check', __name__)

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=None
)


class PasswordCheckSchema(Schema):
    """Schema for password strength check request"""
    password = fields.Str(required=True, validate=lambda x: len(x) <= 128)
    username = fields.Str(missing=None)
    email = fields.Email(missing=None)
    company_name = fields.Str(missing=None)


@password_check_bp.route('/check-password', methods=['POST'])
@limiter.limit("30 per minute")  # Limit to prevent abuse
def check_password():
    """
    Check password strength without creating account
    
    This endpoint is useful for real-time password strength feedback
    during registration or password change flows.
    
    Request body:
    {
        "password": "string",
        "username": "string (optional)",
        "email": "string (optional)",
        "company_name": "string (optional)"
    }
    
    Response:
    {
        "is_valid": boolean,
        "score": 0-4,
        "strength": "too weak|weak|fair|good|strong",
        "estimated_crack_time": "string",
        "warnings": ["string"],
        "suggestions": ["string"],
        "feedback": "string",
        "meets_requirements": {
            "length": boolean,
            "uppercase": boolean,
            "lowercase": boolean,
            "number": boolean,
            "special": boolean
        }
    }
    """
    # Validate request
    schema = PasswordCheckSchema()
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({
            'error': 'Invalid request',
            'details': str(e)
        }), 400
    
    # Build user inputs for context
    user_inputs = []
    if data.get('username'):
        user_inputs.append(data['username'])
    if data.get('email'):
        user_inputs.append(data['email'])
        # Also add email username part
        user_inputs.append(data['email'].split('@')[0])
    if data.get('company_name'):
        user_inputs.append(data['company_name'])
    
    # Check password strength
    result = check_password_strength(
        password=data['password'],
        user_inputs=user_inputs
    )
    
    # Add UI hints
    result['ui_hints'] = _get_ui_hints(result)
    
    return jsonify(result), 200


def _get_ui_hints(result: dict) -> dict:
    """Get UI hints for visual feedback"""
    score = result['score']
    
    # Color hints
    color_map = {
        0: '#dc2626',  # red-600
        1: '#f97316',  # orange-600
        2: '#eab308',  # yellow-600
        3: '#22c55e',  # green-600
        4: '#10b981'   # emerald-600
    }
    
    # Progress percentage
    progress_map = {
        0: 20,
        1: 40,
        2: 60,
        3: 80,
        4: 100
    }
    
    return {
        'color': color_map.get(score, '#6b7280'),
        'progress': progress_map.get(score, 0),
        'icon': _get_strength_icon(score),
        'show_success': result['is_valid']
    }


def _get_strength_icon(score: int) -> str:
    """Get icon class for strength level"""
    icons = {
        0: 'fa-times-circle',
        1: 'fa-exclamation-circle',
        2: 'fa-minus-circle',
        3: 'fa-check-circle',
        4: 'fa-shield-alt'
    }
    return icons.get(score, 'fa-question-circle')