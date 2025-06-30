"""Payment routes - placeholder"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/plans')
def plans():
    """Get available payment plans"""
    return jsonify({"message": "Payment plans - Under construction"}), 200
