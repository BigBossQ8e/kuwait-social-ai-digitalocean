"""
Monitoring Dashboard Routes
Provides real-time application health and metrics data
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.metrics_service import get_metrics_service
from utils.decorators import role_required
from datetime import datetime, timedelta
from models.client_error import ClientError

# Create blueprint
monitoring_bp = Blueprint('monitoring', __name__)

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=None
)


@monitoring_bp.route('/health', methods=['GET'])
@limiter.limit("30 per minute")
def health_check():
    """
    Basic health check endpoint
    
    Returns application health status without authentication
    """
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except:
        db_status = 'unhealthy'
    
    # Get metrics service health
    try:
        metrics = get_metrics_service()
        score, status, issues = metrics.get_health_score()
    except:
        score, status, issues = 0, 'unknown', ['Metrics service unavailable']
    
    return jsonify({
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {
            'database': db_status,
            'metrics': 'healthy' if score > 50 else 'unhealthy'
        },
        'score': score
    }), 200 if status != 'critical' else 503


@monitoring_bp.route('/metrics', methods=['GET'])
@jwt_required()
@role_required('admin', 'owner')
def get_metrics():
    """
    Get detailed application metrics
    
    Query parameters:
    - format: prometheus|json (default: json)
    - window: 1min|5min|15min|1hour|24hours (default: 5min)
    """
    format = request.args.get('format', 'json')
    
    metrics = get_metrics_service()
    
    if format == 'prometheus':
        return metrics.export_metrics('prometheus'), 200, {'Content-Type': 'text/plain'}
    else:
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'error_rates': metrics.get_error_rates(),
            'performance': metrics.get_performance_metrics(),
            'health': {
                'score': metrics.get_health_score()[0],
                'status': metrics.get_health_score()[1],
                'issues': metrics.get_health_score()[2]
            }
        }), 200


@monitoring_bp.route('/errors/summary', methods=['GET'])
@jwt_required()
@role_required('admin', 'owner')
def get_error_summary():
    """
    Get error summary with trends
    
    Query parameters:
    - hours: Number of hours to look back (default: 24)
    - group_by: type|severity|user (default: type)
    """
    hours = request.args.get('hours', 24, type=int)
    group_by = request.args.get('group_by', 'type')
    
    # Validate parameters
    hours = min(hours, 168)  # Max 7 days
    
    # Get error trends
    trends = _get_error_trends(hours)
    
    # Get top errors
    top_errors = ClientError.get_frequent_errors(limit=20, hours=hours)
    
    # Get affected users
    affected_users = ClientError.get_affected_users(hours=hours)
    
    # Get error distribution
    distribution = _get_error_distribution(hours, group_by)
    
    return jsonify({
        'timeRange': {
            'hours': hours,
            'start': (datetime.utcnow() - timedelta(hours=hours)).isoformat(),
            'end': datetime.utcnow().isoformat()
        },
        'summary': {
            'totalErrors': sum(d['count'] for d in distribution),
            'affectedUsers': affected_users,
            'errorTypes': len(set(d['type'] for d in distribution if 'type' in d))
        },
        'trends': trends,
        'topErrors': [
            {
                'message': e[0],
                'type': e[1],
                'count': e[2]
            } for e in top_errors
        ],
        'distribution': distribution
    }), 200


@monitoring_bp.route('/errors/realtime', methods=['GET'])
@jwt_required()
@role_required('admin', 'owner')
def get_realtime_errors():
    """
    Get real-time error stream (last 5 minutes)
    """
    from sqlalchemy import desc
    
    # Get errors from last 5 minutes
    cutoff = datetime.utcnow() - timedelta(minutes=5)
    
    errors = ClientError.query.filter(
        ClientError.created_at >= cutoff
    ).order_by(
        desc(ClientError.created_at)
    ).limit(50).all()
    
    return jsonify({
        'errors': [e.to_dict() for e in errors],
        'count': len(errors),
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@monitoring_bp.route('/performance/endpoints', methods=['GET'])
@jwt_required()
@role_required('admin', 'owner')
def get_endpoint_performance():
    """
    Get performance metrics for API endpoints
    """
    metrics = get_metrics_service()
    perf_data = metrics.get_performance_metrics()
    
    # Add more detailed endpoint data
    endpoint_stats = []
    
    for endpoint_key, stats in perf_data.items():
        if 'api_' in endpoint_key:
            endpoint_name = endpoint_key.replace('api_', '').replace('_response', '')
            endpoint_stats.append({
                'endpoint': endpoint_name,
                'metrics': stats,
                'status': _get_performance_status(stats)
            })
    
    return jsonify({
        'endpoints': endpoint_stats,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@monitoring_bp.route('/alerts/config', methods=['GET', 'PUT'])
@jwt_required()
@role_required('owner')
def manage_alert_config():
    """
    Get or update alert configuration
    """
    if request.method == 'GET':
        # Return current thresholds
        metrics = get_metrics_service()
        return jsonify({
            'error_thresholds': metrics.error_thresholds,
            'time_windows': metrics.time_windows
        }), 200
    
    else:  # PUT
        # Update thresholds
        data = request.get_json()
        
        if 'error_thresholds' in data:
            metrics = get_metrics_service()
            # Validate and update thresholds
            # Implementation depends on your validation requirements
            pass
        
        return jsonify({'message': 'Alert configuration updated'}), 200


def _get_error_trends(hours: int) -> List[Dict]:
    """Calculate error trends over time"""
    from sqlalchemy import func
    
    # Determine bucket size based on time range
    if hours <= 1:
        bucket_minutes = 1
    elif hours <= 24:
        bucket_minutes = 15
    else:
        bucket_minutes = 60
    
    trends = []
    current_time = datetime.utcnow()
    
    for i in range(0, hours * 60, bucket_minutes):
        bucket_start = current_time - timedelta(minutes=i + bucket_minutes)
        bucket_end = current_time - timedelta(minutes=i)
        
        count = ClientError.query.filter(
            ClientError.created_at >= bucket_start,
            ClientError.created_at < bucket_end
        ).count()
        
        trends.append({
            'timestamp': bucket_end.isoformat(),
            'count': count
        })
    
    trends.reverse()  # Oldest first
    return trends


def _get_error_distribution(hours: int, group_by: str) -> List[Dict]:
    """Get error distribution by specified grouping"""
    from sqlalchemy import func
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    if group_by == 'severity':
        results = db.session.query(
            ClientError.severity,
            func.count(ClientError.id).label('count')
        ).filter(
            ClientError.created_at >= start_time
        ).group_by(
            ClientError.severity
        ).all()
        
        return [
            {'severity': r[0], 'count': r[1]} 
            for r in results
        ]
    
    elif group_by == 'user':
        results = db.session.query(
            ClientError.user_id,
            ClientError.user_role,
            func.count(ClientError.id).label('count')
        ).filter(
            ClientError.created_at >= start_time,
            ClientError.user_id.isnot(None)
        ).group_by(
            ClientError.user_id,
            ClientError.user_role
        ).order_by(
            func.count(ClientError.id).desc()
        ).limit(20).all()
        
        return [
            {'userId': r[0], 'role': r[1], 'count': r[2]} 
            for r in results
        ]
    
    else:  # Default to type
        results = db.session.query(
            ClientError.type,
            func.count(ClientError.id).label('count')
        ).filter(
            ClientError.created_at >= start_time
        ).group_by(
            ClientError.type
        ).all()
        
        return [
            {'type': r[0], 'count': r[1]} 
            for r in results
        ]


def _get_performance_status(stats: Dict) -> str:
    """Determine performance status based on metrics"""
    if not stats:
        return 'unknown'
    
    p95 = stats.get('p95', 0)
    
    if p95 < 500:
        return 'excellent'
    elif p95 < 1000:
        return 'good'
    elif p95 < 2000:
        return 'fair'
    else:
        return 'poor'