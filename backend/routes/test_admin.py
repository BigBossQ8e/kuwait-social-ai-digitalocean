"""
Test route for admin panel HTML
"""
from flask import Blueprint, send_from_directory
import os

test_admin_bp = Blueprint('test_admin', __name__)

@test_admin_bp.route('/admin-test')
def serve_admin_test():
    """Serve the admin test HTML page"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'admin-test.html')

@test_admin_bp.route('/admin-demo')
def serve_admin_demo():
    """Serve the admin demo HTML page (no auth required)"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'admin-demo.html')

@test_admin_bp.route('/admin-fixed')
def serve_admin_fixed():
    """Serve the fixed admin HTML page"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'admin-test-fixed.html')

@test_admin_bp.route('/admin-full')
def serve_admin_full():
    """Serve the full admin HTML page with all features"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'admin-full.html')

@test_admin_bp.route('/admin-preview')
def serve_admin_preview():
    """Serve the complete admin preview showing all features"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'admin-preview-complete.html')

@test_admin_bp.route('/admin-ai')
def serve_admin_ai():
    """Serve the AI & Services management page"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'admin-ai-services.html')

@test_admin_bp.route('/admin-prompts')
def serve_admin_prompts():
    """Serve the AI Prompts management page"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'admin-ai-prompts.html')