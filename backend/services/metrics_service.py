"""
Metrics Service for Error Rate Monitoring
Tracks application health metrics and error rates
"""

import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import logging
from collections import defaultdict
from threading import Timer
import os


class MetricsService:
    """
    Service for tracking and monitoring application metrics
    with focus on error rates and performance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Redis connection for metrics storage
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Metrics configuration
        self.time_windows = {
            '1min': 60,
            '5min': 300,
            '15min': 900,
            '1hour': 3600,
            '24hours': 86400
        }
        
        # Thresholds for alerts
        self.error_thresholds = {
            'critical': {
                '1min': 10,    # 10 errors per minute
                '5min': 30,    # 30 errors per 5 minutes
                '15min': 50,   # 50 errors per 15 minutes
                '1hour': 100   # 100 errors per hour
            },
            'warning': {
                '1min': 5,
                '5min': 15,
                '15min': 25,
                '1hour': 50
            }
        }
        
        # Start background tasks
        self._start_background_tasks()
    
    def increment(self, metric_name: str, value: int = 1, tags: Dict = None):
        """Increment a metric counter"""
        try:
            # Create metric key with tags
            key = self._build_metric_key(metric_name, tags)
            
            # Increment for each time window
            pipe = self.redis_client.pipeline()
            timestamp = int(datetime.utcnow().timestamp())
            
            for window_name, window_seconds in self.time_windows.items():
                window_key = f"{key}:{window_name}:{timestamp // window_seconds}"
                pipe.incr(window_key, value)
                pipe.expire(window_key, window_seconds * 2)  # Keep for 2x the window
            
            pipe.execute()
            
            # Check if thresholds are exceeded
            self._check_thresholds(metric_name, tags)
            
        except Exception as e:
            self.logger.error(f"Failed to increment metric {metric_name}: {str(e)}")
    
    def gauge(self, metric_name: str, value: float, tags: Dict = None):
        """Set a gauge metric (absolute value)"""
        try:
            key = self._build_metric_key(metric_name, tags)
            timestamp = int(datetime.utcnow().timestamp())
            
            # Store with timestamp
            gauge_key = f"{key}:gauge:{timestamp}"
            self.redis_client.setex(gauge_key, 3600, value)  # Keep for 1 hour
            
            # Also store latest value
            self.redis_client.set(f"{key}:latest", value)
            
        except Exception as e:
            self.logger.error(f"Failed to set gauge {metric_name}: {str(e)}")
    
    def timing(self, metric_name: str, duration_ms: float, tags: Dict = None):
        """Record timing metric"""
        try:
            key = self._build_metric_key(metric_name, tags)
            timestamp = int(datetime.utcnow().timestamp())
            
            # Store timing data
            timing_key = f"{key}:timing:{timestamp // 60}"  # Group by minute
            self.redis_client.lpush(timing_key, duration_ms)
            self.redis_client.ltrim(timing_key, 0, 999)  # Keep last 1000
            self.redis_client.expire(timing_key, 3600)  # Keep for 1 hour
            
        except Exception as e:
            self.logger.error(f"Failed to record timing {metric_name}: {str(e)}")
    
    def get_metric_stats(self, metric_name: str, window: str = '5min', tags: Dict = None) -> Dict:
        """Get statistics for a metric"""
        try:
            key = self._build_metric_key(metric_name, tags)
            window_seconds = self.time_windows.get(window, 300)
            
            # Get all values for the window
            timestamp = int(datetime.utcnow().timestamp())
            window_start = timestamp - window_seconds
            
            total = 0
            pattern = f"{key}:{window}:*"
            for metric_key in self.redis_client.scan_iter(match=pattern):
                # Check if key is within our window
                key_timestamp = int(metric_key.split(':')[-1]) * window_seconds
                if key_timestamp >= window_start:
                    value = self.redis_client.get(metric_key)
                    if value:
                        total += int(value)
            
            # Calculate rate
            rate = total / (window_seconds / 60)  # Per minute
            
            return {
                'total': total,
                'rate_per_minute': round(rate, 2),
                'window': window,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stats for {metric_name}: {str(e)}")
            return {}
    
    def get_error_rates(self) -> Dict[str, Dict]:
        """Get current error rates across all time windows"""
        error_rates = {}
        
        # Frontend errors
        for error_type in ['javascript-error', 'api-error', 'unhandled-promise']:
            metric = f'frontend.errors.{error_type}'
            error_rates[error_type] = {}
            
            for window in self.time_windows.keys():
                stats = self.get_metric_stats(metric, window)
                error_rates[error_type][window] = stats
        
        # Backend errors
        for status_code in ['500', '502', '503']:
            metric = f'backend.errors.{status_code}'
            error_rates[f'backend_{status_code}'] = {}
            
            for window in self.time_windows.keys():
                stats = self.get_metric_stats(metric, window)
                error_rates[f'backend_{status_code}'][window] = stats
        
        return error_rates
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        metrics = {}
        
        # API response times
        for endpoint in ['auth', 'content', 'posts']:
            timing_key = f"api.response_time.{endpoint}:timing:*"
            timings = []
            
            for key in self.redis_client.scan_iter(match=timing_key):
                values = self.redis_client.lrange(key, 0, -1)
                timings.extend([float(v) for v in values])
            
            if timings:
                metrics[f'api_{endpoint}_response'] = {
                    'avg': round(sum(timings) / len(timings), 2),
                    'min': round(min(timings), 2),
                    'max': round(max(timings), 2),
                    'p95': round(self._percentile(timings, 95), 2),
                    'count': len(timings)
                }
        
        # Frontend performance
        page_load_key = "frontend.performance.page_load:latest"
        page_load = self.redis_client.get(page_load_key)
        if page_load:
            metrics['page_load_time'] = float(page_load)
        
        return metrics
    
    def get_health_score(self) -> Tuple[int, str, List[str]]:
        """
        Calculate overall application health score
        
        Returns:
            Tuple of (score 0-100, status, list of issues)
        """
        score = 100
        issues = []
        
        # Check error rates
        error_rates = self.get_error_rates()
        
        for error_type, windows in error_rates.items():
            for window, stats in windows.items():
                if stats.get('total', 0) > 0:
                    # Check against thresholds
                    if window in self.error_thresholds['critical']:
                        if stats['total'] > self.error_thresholds['critical'][window]:
                            score -= 30
                            issues.append(f"Critical: {error_type} errors exceed threshold in {window}")
                        elif stats['total'] > self.error_thresholds['warning'][window]:
                            score -= 10
                            issues.append(f"Warning: {error_type} errors high in {window}")
        
        # Check performance
        perf_metrics = self.get_performance_metrics()
        for endpoint, metrics in perf_metrics.items():
            if 'api_' in endpoint and 'p95' in metrics:
                if metrics['p95'] > 2000:  # 2 seconds
                    score -= 10
                    issues.append(f"Performance: {endpoint} response time high (p95: {metrics['p95']}ms)")
        
        # Determine status
        if score >= 90:
            status = 'healthy'
        elif score >= 70:
            status = 'degraded'
        elif score >= 50:
            status = 'unhealthy'
        else:
            status = 'critical'
        
        return max(0, score), status, issues
    
    def _build_metric_key(self, metric_name: str, tags: Dict = None) -> str:
        """Build Redis key for metric"""
        key_parts = [metric_name]
        
        if tags:
            for tag_key, tag_value in sorted(tags.items()):
                key_parts.append(f"{tag_key}:{tag_value}")
        
        return ":".join(key_parts)
    
    def _check_thresholds(self, metric_name: str, tags: Dict = None):
        """Check if metric exceeds thresholds and send alerts"""
        # Only check error metrics
        if 'error' not in metric_name:
            return
        
        for window, threshold in self.error_thresholds['critical'].items():
            stats = self.get_metric_stats(metric_name, window, tags)
            
            if stats.get('total', 0) > threshold:
                self._send_threshold_alert(metric_name, window, stats['total'], threshold, 'critical')
                break  # Only send one alert
            elif stats.get('total', 0) > self.error_thresholds['warning'].get(window, 0):
                self._send_threshold_alert(metric_name, window, stats['total'], 
                                         self.error_thresholds['warning'][window], 'warning')
                break
    
    def _send_threshold_alert(self, metric_name: str, window: str, value: int, threshold: int, level: str):
        """Send alert when threshold is exceeded"""
        try:
            # Check if we've already sent this alert recently
            alert_key = f"alert_sent:{metric_name}:{window}:{level}"
            if self.redis_client.get(alert_key):
                return  # Already sent
            
            # Mark as sent (prevent spam for 30 minutes)
            self.redis_client.setex(alert_key, 1800, 1)
            
            # Send alert
            from services.admin_notification_service import send_critical_alert
            
            message = f"""
Error rate threshold exceeded!

Metric: {metric_name}
Window: {window}
Current value: {value}
Threshold: {threshold}
Level: {level.upper()}

Please investigate immediately.
            """
            
            send_critical_alert(
                subject=f"{level.upper()}: Error rate threshold exceeded",
                message=message,
                service="MetricsService",
                priority="HIGH" if level == 'critical' else "MEDIUM"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send threshold alert: {str(e)}")
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Cleanup old metrics every hour
        def cleanup_old_metrics():
            try:
                cutoff = datetime.utcnow() - timedelta(days=7)
                # Implementation of cleanup logic
                pass
            except Exception as e:
                self.logger.error(f"Cleanup failed: {str(e)}")
            
            # Schedule next cleanup
            Timer(3600, cleanup_old_metrics).start()
        
        # Start cleanup task
        Timer(3600, cleanup_old_metrics).start()
    
    def export_metrics(self, format: str = 'prometheus') -> str:
        """Export metrics in various formats"""
        if format == 'prometheus':
            return self._export_prometheus()
        elif format == 'json':
            return self._export_json()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Error rates
        error_rates = self.get_error_rates()
        for error_type, windows in error_rates.items():
            for window, stats in windows.items():
                metric_name = f"app_error_rate{{type=\"{error_type}\",window=\"{window}\"}}"
                lines.append(f"{metric_name} {stats.get('rate_per_minute', 0)}")
        
        # Performance metrics
        perf_metrics = self.get_performance_metrics()
        for endpoint, metrics in perf_metrics.items():
            if 'avg' in metrics:
                metric_name = f"app_response_time_ms{{endpoint=\"{endpoint}\",percentile=\"avg\"}}"
                lines.append(f"{metric_name} {metrics['avg']}")
            if 'p95' in metrics:
                metric_name = f"app_response_time_ms{{endpoint=\"{endpoint}\",percentile=\"p95\"}}"
                lines.append(f"{metric_name} {metrics['p95']}")
        
        # Health score
        score, status, _ = self.get_health_score()
        lines.append(f"app_health_score {score}")
        lines.append(f"app_health_status{{status=\"{status}\"}} 1")
        
        return "\n".join(lines)
    
    def _export_json(self) -> str:
        """Export metrics in JSON format"""
        return json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'error_rates': self.get_error_rates(),
            'performance': self.get_performance_metrics(),
            'health': {
                'score': self.get_health_score()[0],
                'status': self.get_health_score()[1],
                'issues': self.get_health_score()[2]
            }
        }, indent=2)


# Singleton instance
_metrics_service = None


def get_metrics_service() -> MetricsService:
    """Get singleton metrics service instance"""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service