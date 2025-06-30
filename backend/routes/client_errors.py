"""
Client Error Logging Endpoint
Receives and processes frontend error reports
"""

from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
from marshmallow import Schema, fields, validate
import logging

# Create blueprint
client_errors_bp = Blueprint('client_errors', __name__)

# Logger
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=None
)


class ClientErrorSchema(Schema):
    """Schema for client error entries"""
    type = fields.Str(required=True, validate=validate.OneOf([
        'javascript-error', 'unhandled-promise', 'console-error',
        'api-error', 'custom-event', 'performance', 'manual-capture'
    ]))
    message = fields.Str(required=True, validate=validate.Length(max=1000))
    severity = fields.Str(missing='error', validate=validate.OneOf([
        'info', 'warning', 'error', 'critical'
    ]))
    source = fields.Str(missing=None)
    line = fields.Int(missing=None)
    column = fields.Int(missing=None)
    stack = fields.Str(missing=None, validate=validate.Length(max=5000))
    sessionId = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)
    context = fields.Dict(missing={})
    metadata = fields.Dict(missing={})


class ClientErrorBatchSchema(Schema):
    """Schema for batch error submission"""
    errors = fields.List(fields.Nested(ClientErrorSchema), required=True, validate=validate.Length(max=100))
    metadata = fields.Dict(missing={})
    isRetry = fields.Bool(missing=False)


@client_errors_bp.route('/client-errors', methods=['POST'])
@limiter.limit("100 per minute")  # Higher limit for error reporting
def log_client_errors():
    """
    Receive and process client-side errors
    
    This endpoint accepts batched error reports from the frontend
    and stores them for monitoring and analysis.
    """
    # Validate request
    schema = ClientErrorBatchSchema()
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({
            'error': 'Invalid error data',
            'details': str(e)
        }), 400
    
    # Get additional context
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    session_id = request.headers.get('X-Session-ID', 'Unknown')
    
    # Process errors
    processed_count = 0
    critical_errors = []
    
    for error_data in data['errors']:
        try:
            # Store in database
            store_client_error(error_data, client_ip, user_agent)
            processed_count += 1
            
            # Track critical errors
            if error_data.get('severity') == 'critical':
                critical_errors.append(error_data)
                
        except Exception as e:
            logger.error(f"Failed to store client error: {str(e)}")
    
    # Send alerts for critical errors
    if critical_errors:
        send_critical_error_alerts(critical_errors, session_id)
    
    # Update error metrics
    update_error_metrics(data['errors'])
    
    return jsonify({
        'success': True,
        'processed': processed_count,
        'total': len(data['errors'])
    }), 200


def store_client_error(error_data, client_ip, user_agent):
    """Store client error in database"""
    from models.client_error import ClientError
    
    error = ClientError(
        type=error_data['type'],
        message=error_data['message'],
        severity=error_data.get('severity', 'error'),
        source=error_data.get('source'),
        line_number=error_data.get('line'),
        column_number=error_data.get('column'),
        stack_trace=error_data.get('stack'),
        session_id=error_data['sessionId'],
        user_agent=user_agent,
        client_ip=client_ip,
        context=error_data.get('context', {}),
        metadata=error_data.get('metadata', {}),
        timestamp=error_data['timestamp']
    )
    
    # Extract user info from context if available
    user_context = error_data.get('context', {}).get('user')
    if user_context:
        error.user_id = user_context.get('id')
        error.user_role = user_context.get('role')
    
    db.session.add(error)
    db.session.commit()


def send_critical_error_alerts(critical_errors, session_id):
    """Send alerts for critical client-side errors"""
    try:
        from services.admin_notification_service import send_critical_alert
        
        # Group errors by type
        error_types = {}
        for error in critical_errors:
            error_type = error['type']
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(error['message'])
        
        # Build alert message
        message = f"Critical client-side errors detected\n\n"
        message += f"Session: {session_id}\n"
        message += f"Total critical errors: {len(critical_errors)}\n\n"
        
        for error_type, messages in error_types.items():
            message += f"{error_type}:\n"
            for msg in messages[:5]:  # Show first 5 of each type
                message += f"  - {msg[:100]}...\n"
            if len(messages) > 5:
                message += f"  ... and {len(messages) - 5} more\n"
            message += "\n"
        
        send_critical_alert(
            subject="Critical Frontend Errors Detected",
            message=message,
            service="FrontendErrorLogger",
            priority="HIGH"
        )
    except Exception as e:
        logger.error(f"Failed to send critical error alert: {str(e)}")


def update_error_metrics(errors):
    """Update error rate metrics"""
    try:
        from services.metrics_service import MetricsService
        
        metrics = MetricsService()
        
        # Count errors by type and severity
        for error in errors:
            error_type = error['type']
            severity = error.get('severity', 'error')
            
            # Increment counters
            metrics.increment(f'frontend.errors.{error_type}')
            metrics.increment(f'frontend.errors.severity.{severity}')
            
            # Track specific error patterns
            if error_type == 'api-error':
                endpoint = error.get('endpoint', 'unknown')
                status = error.get('status', 'unknown')
                metrics.increment(f'frontend.api_errors.{endpoint}.{status}')
                
    except ImportError:
        # Metrics service not available yet
        pass
    except Exception as e:
        logger.error(f"Failed to update error metrics: {str(e)}")


@client_errors_bp.route('/client-errors/stats', methods=['GET'])
@limiter.limit("10 per minute")
def get_error_stats():
    """
    Get client error statistics
    
    Returns aggregated error data for monitoring dashboards
    """
    from models.client_error import ClientError
    from sqlalchemy import func
    from datetime import timedelta
    
    # Time range (last 24 hours by default)
    hours = request.args.get('hours', 24, type=int)
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get error counts by type
    error_counts = db.session.query(
        ClientError.type,
        func.count(ClientError.id).label('count')
    ).filter(
        ClientError.created_at >= start_time
    ).group_by(
        ClientError.type
    ).all()
    
    # Get error counts by severity
    severity_counts = db.session.query(
        ClientError.severity,
        func.count(ClientError.id).label('count')
    ).filter(
        ClientError.created_at >= start_time
    ).group_by(
        ClientError.severity
    ).all()
    
    # Get top error messages
    top_errors = db.session.query(
        ClientError.message,
        func.count(ClientError.id).label('count')
    ).filter(
        ClientError.created_at >= start_time
    ).group_by(
        ClientError.message
    ).order_by(
        func.count(ClientError.id).desc()
    ).limit(10).all()
    
    # Get affected users count
    affected_users = db.session.query(
        func.count(func.distinct(ClientError.user_id))
    ).filter(
        ClientError.created_at >= start_time,
        ClientError.user_id.isnot(None)
    ).scalar()
    
    # Get affected sessions count
    affected_sessions = db.session.query(
        func.count(func.distinct(ClientError.session_id))
    ).filter(
        ClientError.created_at >= start_time
    ).scalar()
    
    return jsonify({
        'timeRange': {
            'hours': hours,
            'startTime': start_time.isoformat(),
            'endTime': datetime.utcnow().isoformat()
        },
        'summary': {
            'totalErrors': sum(c[1] for c in error_counts),
            'affectedUsers': affected_users or 0,
            'affectedSessions': affected_sessions or 0
        },
        'byType': {c[0]: c[1] for c in error_counts},
        'bySeverity': {c[0]: c[1] for c in severity_counts},
        'topErrors': [
            {'message': e[0], 'count': e[1]} for e in top_errors
        ]
    }), 200