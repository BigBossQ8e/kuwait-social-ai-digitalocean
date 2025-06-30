"""Social media routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

social_bp = Blueprint('social', __name__)

@social_bp.route('/accounts')
@jwt_required()
def accounts():
    """Social accounts endpoint"""
    return jsonify({"message": "Social accounts - Under construction"}), 200
