"""
Query performance monitoring and optimization tools
Tracks slow queries, provides analysis, and suggests optimizations
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from functools import wraps
from flask import g, current_app
from flask_sqlalchemy import get_debug_queries
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query
from models import db
import json
from redis import Redis

logger = logging.getLogger(__name__)


class QueryPerformanceMonitor:
    """Monitor and analyze database query performance"""
    
    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis_client = redis_client
        self.slow_query_threshold = 0.5  # 500ms
        self.query_stats = {}
        self._setup_listeners()
    
    def _setup_listeners(self):
        """Set up SQLAlchemy event listeners for query monitoring"""
        
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            if current_app.config.get('DEBUG'):
                logger.debug(f"Query: {statement[:100]}...")
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            
            # Store query performance data
            if hasattr(g, 'query_performance'):
                g.query_performance.append({
                    'statement': statement,
                    'parameters': parameters,
                    'duration': total,
                    'timestamp': datetime.utcnow()
                })
            
            # Log slow queries
            if total > self.slow_query_threshold:
                self._log_slow_query(statement, parameters, total)
    
    def _log_slow_query(self, statement: str, parameters: Any, duration: float):
        """Log slow queries for analysis"""
        slow_query = {
            'statement': statement[:500],  # Truncate long queries
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat(),
            'parameters': str(parameters)[:200] if parameters else None
        }
        
        logger.warning(f"Slow query detected ({duration:.2f}s): {statement[:100]}...")
        
        # Store in Redis for analysis
        if self.redis_client:
            key = f"slow_queries:{datetime.utcnow().strftime('%Y-%m-%d')}"
            self.redis_client.lpush(key, json.dumps(slow_query))
            self.redis_client.expire(key, 86400 * 7)  # Keep for 7 days
    
    def analyze_request_queries(self) -> Dict[str, Any]:
        """Analyze queries from the current request"""
        if not hasattr(g, 'query_performance'):
            return {'error': 'No query data available'}
        
        queries = g.query_performance
        if not queries:
            return {'total_queries': 0}
        
        total_time = sum(q['duration'] for q in queries)
        slow_queries = [q for q in queries if q['duration'] > self.slow_query_threshold]
        
        return {
            'total_queries': len(queries),
            'total_time': total_time,
            'average_time': total_time / len(queries),
            'slow_queries': len(slow_queries),
            'slowest_query': max(queries, key=lambda x: x['duration']) if queries else None,
            'queries': queries if current_app.config.get('DEBUG') else None
        }
    
    def get_slow_query_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate a report of slow queries over the specified period"""
        if not self.redis_client:
            return {'error': 'Redis not configured'}
        
        slow_queries = []
        query_patterns = {}
        
        # Collect slow queries from Redis
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            key = f"slow_queries:{date}"
            
            queries = self.redis_client.lrange(key, 0, -1)
            for query_data in queries:
                query = json.loads(query_data)
                slow_queries.append(query)
                
                # Group by query pattern
                pattern = self._extract_query_pattern(query['statement'])
                if pattern not in query_patterns:
                    query_patterns[pattern] = {
                        'count': 0,
                        'total_duration': 0,
                        'max_duration': 0,
                        'examples': []
                    }
                
                query_patterns[pattern]['count'] += 1
                query_patterns[pattern]['total_duration'] += query['duration']
                query_patterns[pattern]['max_duration'] = max(
                    query_patterns[pattern]['max_duration'],
                    query['duration']
                )
                
                if len(query_patterns[pattern]['examples']) < 3:
                    query_patterns[pattern]['examples'].append(query)
        
        # Sort patterns by total impact
        sorted_patterns = sorted(
            query_patterns.items(),
            key=lambda x: x[1]['total_duration'],
            reverse=True
        )
        
        return {
            'period_days': days,
            'total_slow_queries': len(slow_queries),
            'query_patterns': [
                {
                    'pattern': pattern,
                    'count': data['count'],
                    'average_duration': data['total_duration'] / data['count'],
                    'max_duration': data['max_duration'],
                    'total_impact': data['total_duration'],
                    'examples': data['examples']
                }
                for pattern, data in sorted_patterns[:20]  # Top 20 patterns
            ],
            'recommendations': self._generate_optimization_recommendations(sorted_patterns)
        }
    
    def _extract_query_pattern(self, query: str) -> str:
        """Extract a generalized pattern from a SQL query"""
        # Remove specific values to identify query patterns
        import re
        
        # Remove quoted strings
        pattern = re.sub(r"'[^']*'", "'?'", query)
        # Remove numbers
        pattern = re.sub(r'\b\d+\b', '?', pattern)
        # Remove excessive whitespace
        pattern = ' '.join(pattern.split())
        
        return pattern[:200]  # Truncate for storage
    
    def _generate_optimization_recommendations(self, patterns: List[Tuple[str, Dict]]) -> List[Dict[str, str]]:
        """Generate optimization recommendations based on query patterns"""
        recommendations = []
        
        for pattern, data in patterns[:10]:
            if 'SELECT' in pattern.upper():
                # Check for missing indexes
                if 'WHERE' in pattern.upper() and data['average_duration'] > 0.1:
                    recommendations.append({
                        'type': 'index',
                        'severity': 'high',
                        'description': f"Consider adding index for frequently queried columns",
                        'pattern': pattern[:100]
                    })
                
                # Check for N+1 queries
                if data['count'] > 100 and 'JOIN' not in pattern.upper():
                    recommendations.append({
                        'type': 'n+1',
                        'severity': 'high',
                        'description': f"Possible N+1 query pattern detected ({data['count']} similar queries)",
                        'pattern': pattern[:100]
                    })
                
                # Check for missing LIMIT
                if 'LIMIT' not in pattern.upper() and data['average_duration'] > 0.5:
                    recommendations.append({
                        'type': 'pagination',
                        'severity': 'medium',
                        'description': "Consider adding pagination with LIMIT clause",
                        'pattern': pattern[:100]
                    })
        
        return recommendations
    
    def profile_query(self, query: Query) -> Dict[str, Any]:
        """Profile a specific SQLAlchemy query"""
        # Get query execution plan
        statement = query.statement.compile(compile_kwargs={"literal_binds": True})
        
        # Execute EXPLAIN ANALYZE
        result = db.session.execute(f"EXPLAIN ANALYZE {statement}")
        plan = [row[0] for row in result]
        
        return {
            'query': str(statement)[:500],
            'execution_plan': plan,
            'recommendations': self._analyze_execution_plan(plan)
        }
    
    def _analyze_execution_plan(self, plan: List[str]) -> List[str]:
        """Analyze execution plan and provide recommendations"""
        recommendations = []
        
        plan_text = '\n'.join(plan)
        
        # Check for sequential scans
        if 'Seq Scan' in plan_text:
            recommendations.append("Sequential scan detected - consider adding an index")
        
        # Check for high cost operations
        if 'Sort' in plan_text and 'cost=' in plan_text:
            recommendations.append("Expensive sort operation - consider adding an index on ORDER BY columns")
        
        # Check for nested loops with high iterations
        if 'Nested Loop' in plan_text:
            recommendations.append("Nested loop join detected - may be inefficient for large datasets")
        
        return recommendations


class QueryPerformanceMiddleware:
    """Flask middleware for query performance monitoring"""
    
    def __init__(self, app=None, monitor=None):
        self.app = app
        self.monitor = monitor
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Initialize query performance tracking for request"""
        g.query_performance = []
        g.request_start_time = time.time()
    
    def after_request(self, response):
        """Analyze queries after request completion"""
        if hasattr(g, 'query_performance') and g.query_performance:
            # Add performance headers in debug mode
            if current_app.config.get('DEBUG'):
                analysis = self.monitor.analyze_request_queries()
                response.headers['X-DB-Query-Count'] = str(analysis['total_queries'])
                response.headers['X-DB-Query-Time'] = f"{analysis['total_time']:.3f}"
                
                # Log if too many queries
                if analysis['total_queries'] > 20:
                    logger.warning(f"High query count: {analysis['total_queries']} queries in request")
        
        return response


def monitor_query_performance(f):
    """Decorator to monitor query performance for specific functions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        initial_queries = len(get_debug_queries()) if current_app.config.get('DEBUG') else 0
        
        result = f(*args, **kwargs)
        
        execution_time = time.time() - start_time
        
        if current_app.config.get('DEBUG'):
            queries = get_debug_queries()[initial_queries:]
            total_query_time = sum(q.duration for q in queries)
            
            if len(queries) > 10 or total_query_time > 1.0:
                logger.warning(
                    f"{f.__name__}: {len(queries)} queries in {total_query_time:.2f}s "
                    f"(function time: {execution_time:.2f}s)"
                )
        
        return result
    
    return decorated_function


# Query optimization utilities
class QueryOptimizationHelper:
    """Helper class for query optimization suggestions"""
    
    @staticmethod
    def suggest_eager_loading(model_class, relationships: List[str]) -> str:
        """Suggest eager loading for relationships"""
        options = [f"joinedload({rel})" for rel in relationships]
        return f"""
# Optimize by eager loading relationships:
from sqlalchemy.orm import joinedload

query = {model_class.__name__}.query.options(
    {', '.join(options)}
).all()
"""
    
    @staticmethod
    def suggest_bulk_operations(operation: str, count: int) -> str:
        """Suggest bulk operations instead of individual queries"""
        if operation == 'insert':
            return f"""
# Use bulk_insert_mappings for {count} inserts:
db.session.bulk_insert_mappings(Model, [
    {{'field1': value1, 'field2': value2}}
    for value1, value2 in data
])
db.session.commit()
"""
        elif operation == 'update':
            return f"""
# Use bulk_update_mappings for {count} updates:
db.session.bulk_update_mappings(Model, [
    {{'id': id, 'field1': value1, 'field2': value2}}
    for id, value1, value2 in updates
])
db.session.commit()
"""
    
    @staticmethod
    def suggest_query_optimization(query_type: str, table: str) -> List[str]:
        """Provide query optimization suggestions based on query type"""
        suggestions = []
        
        if query_type == 'count':
            suggestions.append(f"Use SELECT COUNT(*) instead of loading all records")
            suggestions.append(f"Consider caching count results for table '{table}'")
        
        elif query_type == 'exists':
            suggestions.append(f"Use .exists() instead of .count() > 0")
            suggestions.append(f"Use db.session.query(db.exists().where(...)).scalar()")
        
        elif query_type == 'aggregate':
            suggestions.append(f"Use database aggregation functions (SUM, AVG, etc.)")
            suggestions.append(f"Consider materialized views for complex aggregations")
        
        return suggestions