"""Admin routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@jwt_required()
def dashboard():
    """Admin dashboard endpoint"""
    return jsonify({"message": "Admin dashboard - Under construction"}), 200
