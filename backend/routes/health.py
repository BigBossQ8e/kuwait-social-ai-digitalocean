"""
Health check endpoints for monitoring
"""
from flask import Blueprint, jsonify
import os
import psutil
from datetime import datetime
from sqlalchemy import text
from extensions import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """Basic health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'kuwait-social-ai'
    })

@health_bp.route('/api/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with system info"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        db.session.execute(text('SELECT 1'))
        health_status['checks']['database'] = {'status': 'healthy', 'message': 'Connected'}
    except Exception as e:
        health_status['checks']['database'] = {'status': 'unhealthy', 'message': str(e)}
        health_status['status'] = 'unhealthy'
    
    # Memory check
    memory = psutil.virtual_memory()
    health_status['checks']['memory'] = {
        'status': 'healthy' if memory.percent < 90 else 'warning',
        'usage_percent': memory.percent,
        'available_mb': memory.available // (1024 * 1024)
    }
    
    # CPU check
    cpu_percent = psutil.cpu_percent(interval=1)
    health_status['checks']['cpu'] = {
        'status': 'healthy' if cpu_percent < 80 else 'warning',
        'usage_percent': cpu_percent
    }
    
    # Disk check
    disk = psutil.disk_usage('/')
    health_status['checks']['disk'] = {
        'status': 'healthy' if disk.percent < 90 else 'warning',
        'usage_percent': disk.percent,
        'free_gb': disk.free // (1024 * 1024 * 1024)
    }
    
    return jsonify(health_status)

@health_bp.route('/api/health/services', methods=['GET'])
def services_health_check():
    """Check health of individual services"""
    services_status = {
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    # Check Telegram bot
    try:
        if os.environ.get('DISABLE_TELEGRAM_BOT'):
            services_status['services']['telegram'] = {'status': 'disabled', 'message': 'Telegram bot is disabled'}
        else:
            from services.telegram_bot_manager import get_bot_manager
            bot_manager = get_bot_manager()
            active_bots = len(bot_manager.bots) if hasattr(bot_manager, 'bots') else 0
            services_status['services']['telegram'] = {
                'status': 'healthy',
                'active_bots': active_bots
            }
    except Exception as e:
        services_status['services']['telegram'] = {'status': 'unhealthy', 'error': str(e)}
    
    # Check Redis
    try:
        from extensions import redis_client
        if redis_client:
            redis_client.ping()
            services_status['services']['redis'] = {'status': 'healthy'}
        else:
            services_status['services']['redis'] = {'status': 'not_configured'}
    except Exception as e:
        services_status['services']['redis'] = {'status': 'unhealthy', 'error': str(e)}
    
    # Check AI services
    try:
        from services.ai_service import AIService
        services_status['services']['ai'] = {'status': 'healthy', 'provider': 'configured'}
    except Exception as e:
        services_status['services']['ai'] = {'status': 'unhealthy', 'error': str(e)}
    
    return jsonify(services_status)
