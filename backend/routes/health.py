"""Health check endpoint for monitoring"""
from flask import Blueprint, jsonify
from sqlalchemy import text
import redis
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring services
    Returns the status of all critical components
    """
    health_status = {
        'status': 'healthy',
        'services': {}
    }
    
    # Check database connection
    try:
        db.session.execute(text('SELECT 1'))
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = 'unhealthy'
        health_status['status'] = 'unhealthy'
    
    # Check Redis connection if configured
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        try:
            r = redis.from_url(redis_url)
            r.ping()
            health_status['services']['redis'] = 'healthy'
        except Exception as e:
            health_status['services']['redis'] = 'unhealthy'
            health_status['status'] = 'degraded'
    
    # Check file system (uploads directory)
    upload_dir = os.getenv('UPLOAD_FOLDER', './uploads')
    if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK):
        health_status['services']['filesystem'] = 'healthy'
    else:
        health_status['services']['filesystem'] = 'unhealthy'
        health_status['status'] = 'degraded'
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return jsonify(health_status), status_code

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check to determine if the app is ready to serve requests
    """
    try:
        # Check if database migrations are up to date
        db.session.execute(text('SELECT 1 FROM users LIMIT 1'))
        return jsonify({'ready': True}), 200
    except Exception as e:
        return jsonify({'ready': False, 'error': str(e)}), 503