"""Analytics routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/overview')
@jwt_required()
def overview():
    """Analytics overview endpoint"""
    return jsonify({"message": "Analytics overview - Under construction"}), 200
