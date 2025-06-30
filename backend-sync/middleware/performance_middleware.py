"""
Performance monitoring middleware integration
"""

from flask import Flask, g, request, current_app
from werkzeug.exceptions import InternalServerError
from utils.query_performance import QueryPerformanceMonitor, QueryPerformanceMiddleware
from config.database_config import ConnectionPoolMonitor
from datetime import datetime
import time
import logging
import redis
import json

logger = logging.getLogger(__name__)


def init_performance_monitoring(app: Flask):
    """Initialize performance monitoring for the Flask application"""
    
    # Initialize Redis for storing performance metrics
    redis_client = redis.from_url(app.config.get('REDIS_URL', 'redis://localhost:6379'))
    
    # Initialize query monitor
    query_monitor = QueryPerformanceMonitor(redis_client)
    
    # Initialize middleware
    middleware = QueryPerformanceMiddleware(app, query_monitor)
    
    # Store monitors in app context
    app.query_monitor = query_monitor
    app.redis_client = redis_client
    
    # Add request timing
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = request.headers.get('X-Request-ID', str(int(time.time() * 1000)))
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            # Calculate request duration
            duration = time.time() - g.start_time
            
            # Add timing headers
            response.headers['X-Request-Duration'] = f"{duration:.3f}"
            response.headers['X-Request-ID'] = g.get('request_id', '')
            
            # Log slow requests
            if duration > 1.0:  # Requests taking more than 1 second
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s (Request ID: {g.request_id})"
                )
                
                # Store slow request data
                slow_request = {
                    'method': request.method,
                    'path': request.path,
                    'duration': duration,
                    'timestamp': datetime.utcnow().isoformat(),
                    'request_id': g.request_id,
                    'user_agent': request.user_agent.string,
                    'ip': request.remote_addr
                }
                
                key = f"slow_requests:{datetime.utcnow().strftime('%Y-%m-%d')}"
                redis_client.lpush(key, json.dumps(slow_request))
                redis_client.expire(key, 86400 * 7)  # Keep for 7 days
        
        return response
    
    # Add error tracking
    @app.errorhandler(Exception)
    def handle_error(error):
        if hasattr(g, 'query_performance'):
            # Log queries that led to the error
            analysis = query_monitor.analyze_request_queries()
            if analysis.get('slow_queries', 0) > 0:
                logger.error(
                    f"Error occurred with {analysis['slow_queries']} slow queries. "
                    f"Total query time: {analysis.get('total_time', 0):.2f}s"
                )
        
        # Re-raise the error for normal handling
        if isinstance(error, InternalServerError):
            return error
        raise error
    
    # Add periodic connection pool monitoring (optional - requires APScheduler)
    if app.config.get('ENV') == 'production':
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            
            scheduler = BackgroundScheduler()
            
            def monitor_connection_pool():
                """Periodic connection pool health check"""
                try:
                    from models import db
                    engine = db.get_engine(app)
                    monitor = ConnectionPoolMonitor(engine)
                    health = monitor.check_pool_health()
                    
                    if health['status'] != 'healthy':
                        logger.warning(
                            f"Connection pool unhealthy: {health['status']}. "
                            f"Checked out: {health['checked_out']}/{health['size']}"
                        )
                        
                        # Store metrics
                        metrics = {
                            'timestamp': datetime.utcnow().isoformat(),
                            'pool_status': health,
                            'app_name': app.name
                        }
                        
                        redis_client.lpush('pool_metrics', json.dumps(metrics))
                        redis_client.ltrim('pool_metrics', 0, 1000)  # Keep last 1000 entries
                        
                except Exception as e:
                    logger.error(f"Error monitoring connection pool: {str(e)}")
            
            # Schedule pool monitoring every 30 seconds
            scheduler.add_job(
                monitor_connection_pool,
                'interval',
                seconds=30,
                id='pool_monitor',
                replace_existing=True
            )
            
            scheduler.start()
            
            # Ensure scheduler stops on app shutdown
            import atexit
            atexit.register(lambda: scheduler.shutdown())
            
        except ImportError:
            logger.info("APScheduler not available - skipping periodic monitoring. Install with: pip install apscheduler")
    
    logger.info("Performance monitoring initialized")


def get_performance_metrics(app: Flask) -> dict:
    """Get current performance metrics"""
    
    redis_client = getattr(app, 'redis_client', None)
    if not redis_client:
        return {'error': 'Performance monitoring not initialized'}
    
    # Get slow queries
    today = datetime.utcnow().strftime('%Y-%m-%d')
    slow_queries = redis_client.llen(f"slow_queries:{today}")
    slow_requests = redis_client.llen(f"slow_requests:{today}")
    
    # Get pool metrics
    pool_metrics = redis_client.lrange('pool_metrics', 0, 10)
    latest_pool = json.loads(pool_metrics[0]) if pool_metrics else None
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'slow_queries_today': slow_queries,
        'slow_requests_today': slow_requests,
        'connection_pool': latest_pool['pool_status'] if latest_pool else None,
        'monitoring_active': True
    }


class PerformanceConfig:
    """Performance monitoring configuration"""
    
    # Query performance thresholds
    SLOW_QUERY_THRESHOLD = 0.5  # 500ms
    CRITICAL_QUERY_THRESHOLD = 2.0  # 2 seconds
    
    # Request performance thresholds
    SLOW_REQUEST_THRESHOLD = 1.0  # 1 second
    CRITICAL_REQUEST_THRESHOLD = 5.0  # 5 seconds
    
    # Connection pool thresholds
    POOL_WARNING_UTILIZATION = 0.8  # 80% utilization
    POOL_CRITICAL_UTILIZATION = 0.95  # 95% utilization
    
    # Monitoring intervals
    POOL_MONITOR_INTERVAL = 30  # seconds
    METRICS_CLEANUP_INTERVAL = 3600  # 1 hour
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        import os
        
        cls.SLOW_QUERY_THRESHOLD = float(os.getenv('SLOW_QUERY_THRESHOLD', cls.SLOW_QUERY_THRESHOLD))
        cls.SLOW_REQUEST_THRESHOLD = float(os.getenv('SLOW_REQUEST_THRESHOLD', cls.SLOW_REQUEST_THRESHOLD))
        
        return cls