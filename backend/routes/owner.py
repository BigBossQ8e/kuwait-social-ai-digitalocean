"""Owner routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

owner_bp = Blueprint('owner', __name__)

@owner_bp.route('/dashboard')
@jwt_required()
def dashboard():
    """Owner dashboard endpoint"""
    return jsonify({"message": "Owner dashboard - Under construction"}), 200
