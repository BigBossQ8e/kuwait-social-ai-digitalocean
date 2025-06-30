"""Telegram bot routes - placeholder"""
from flask import Blueprint, jsonify

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    return jsonify({"message": "Telegram webhook received"}), 200
