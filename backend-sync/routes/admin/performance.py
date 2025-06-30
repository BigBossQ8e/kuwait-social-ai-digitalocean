"""
Performance monitoring and optimization routes for admin panel
"""

import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from utils.query_performance import QueryPerformanceMonitor, QueryOptimizationHelper
from models import db
from datetime import datetime
try:
    import psutil
except ImportError:
    psutil = None
import redis
from sqlalchemy import text

performance_bp = Blueprint('performance', __name__)

# Initialize monitor with Redis
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
query_monitor = QueryPerformanceMonitor(redis_client)


@performance_bp.route('/queries/slow', methods=['GET'])
@jwt_required()
@admin_required
def get_slow_queries():
    """Get report of slow queries"""
    days = request.args.get('days', 7, type=int)
    
    report = query_monitor.get_slow_query_report(days)
    
    return jsonify(report), 200


@performance_bp.route('/queries/analyze', methods=['POST'])
@jwt_required()
@admin_required
def analyze_query():
    """Analyze a specific query for performance issues"""
    data = request.get_json()
    query_string = data.get('query')
    
    if not query_string:
        return jsonify({'error': 'Query string required'}), 400
    
    try:
        # Execute EXPLAIN ANALYZE
        result = db.session.execute(
            text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query_string}")
        )
        
        execution_plan = result.fetchone()[0]
        
        # Analyze the plan
        analysis = {
            'execution_plan': execution_plan,
            'recommendations': [],
            'estimated_cost': execution_plan[0]['Plan']['Total Cost'],
            'actual_time': execution_plan[0]['Plan']['Actual Total Time'],
            'planning_time': execution_plan[0]['Planning Time'],
            'execution_time': execution_plan[0]['Execution Time']
        }
        
        # Check for common issues
        plan_text = str(execution_plan)
        
        if 'Seq Scan' in plan_text:
            analysis['recommendations'].append({
                'type': 'index',
                'severity': 'high',
                'description': 'Sequential scan detected - consider adding an index'
            })
        
        if 'Nested Loop' in plan_text and execution_plan[0]['Plan']['Actual Loops'] > 1000:
            analysis['recommendations'].append({
                'type': 'join',
                'severity': 'medium',
                'description': 'High iteration nested loop - consider optimizing join conditions'
            })
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': f'Query analysis failed: {str(e)}'}), 500


@performance_bp.route('/database/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_database_stats():
    """Get database performance statistics"""
    try:
        # Get connection pool stats
        engine = db.get_engine()
        pool = engine.pool
        
        pool_stats = {
            'size': pool.size(),
            'checked_out': pool.checked_out(),
            'overflow': pool.overflow(),
            'total': pool.size() + pool.overflow()
        }
        
        # Get database statistics
        stats_query = """
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples,
            last_vacuum,
            last_autovacuum
        FROM pg_stat_user_tables
        ORDER BY n_live_tup DESC
        LIMIT 20;
        """
        
        result = db.session.execute(text(stats_query))
        table_stats = [
            {
                'schema': row[0],
                'table': row[1],
                'inserts': row[2],
                'updates': row[3],
                'deletes': row[4],
                'live_tuples': row[5],
                'dead_tuples': row[6],
                'last_vacuum': row[7].isoformat() if row[7] else None,
                'last_autovacuum': row[8].isoformat() if row[8] else None
            }
            for row in result
        ]
        
        # Get index usage
        index_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan as index_scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM pg_stat_user_indexes
        WHERE idx_scan = 0
        ORDER BY schemaname, tablename;
        """
        
        result = db.session.execute(text(index_query))
        unused_indexes = [
            {
                'schema': row[0],
                'table': row[1],
                'index': row[2]
            }
            for row in result
        ]
        
        return jsonify({
            'connection_pool': pool_stats,
            'table_statistics': table_stats,
            'unused_indexes': unused_indexes,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get database stats: {str(e)}'}), 500


@performance_bp.route('/database/missing-indexes', methods=['GET'])
@jwt_required()
@admin_required
def get_missing_indexes():
    """Identify potentially missing indexes"""
    try:
        # Query to find missing indexes based on pg_stat_user_tables
        missing_index_query = """
        SELECT 
            schemaname,
            tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            n_live_tup,
            CASE 
                WHEN seq_scan > 0 THEN 
                    ROUND(100.0 * seq_scan / (seq_scan + idx_scan), 2)
                ELSE 0 
            END as seq_scan_pct
        FROM pg_stat_user_tables
        WHERE seq_scan > idx_scan
        AND n_live_tup > 1000
        ORDER BY seq_tup_read DESC
        LIMIT 20;
        """
        
        result = db.session.execute(text(missing_index_query))
        
        potential_indexes = []
        for row in result:
            recommendation = {
                'schema': row[0],
                'table': row[1],
                'seq_scans': row[2],
                'rows_read_seq': row[3],
                'index_scans': row[4],
                'total_rows': row[5],
                'seq_scan_percentage': float(row[6]),
                'impact': 'high' if row[6] > 80 else 'medium' if row[6] > 50 else 'low'
            }
            potential_indexes.append(recommendation)
        
        return jsonify({
            'missing_indexes': potential_indexes,
            'recommendations': _generate_index_recommendations(potential_indexes)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to analyze indexes: {str(e)}'}), 500


@performance_bp.route('/system/health', methods=['GET'])
@jwt_required()
@admin_required
def get_system_health():
    """Get overall system health metrics"""
    try:
        if not psutil:
            return jsonify({'error': 'psutil not installed - run: pip install psutil'}), 500
            
        # CPU and Memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database connections
        connection_query = """
        SELECT 
            state,
            COUNT(*) as count
        FROM pg_stat_activity
        WHERE datname = current_database()
        GROUP BY state;
        """
        
        result = db.session.execute(text(connection_query))
        connections = {row[0]: row[1] for row in result}
        
        # Check for long-running queries
        long_query = """
        SELECT 
            pid,
            now() - pg_stat_activity.query_start AS duration,
            query
        FROM pg_stat_activity
        WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
        AND state = 'active';
        """
        
        result = db.session.execute(text(long_query))
        long_running = [
            {
                'pid': row[0],
                'duration': str(row[1]),
                'query': row[2][:200]
            }
            for row in result
        ]
        
        health_score = _calculate_health_score(cpu_percent, memory.percent, connections, long_running)
        
        return jsonify({
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            },
            'database': {
                'connections': connections,
                'long_running_queries': long_running
            },
            'health_score': health_score,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get system health: {str(e)}'}), 500


@performance_bp.route('/optimize/vacuum', methods=['POST'])
@jwt_required()
@admin_required
def run_vacuum():
    """Run VACUUM ANALYZE on specified tables"""
    data = request.get_json()
    tables = data.get('tables', [])
    analyze = data.get('analyze', True)
    
    try:
        results = []
        
        if not tables:
            # Get all user tables
            table_query = """
            SELECT schemaname, tablename 
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 1000
            ORDER BY n_dead_tup DESC
            LIMIT 10;
            """
            result = db.session.execute(text(table_query))
            tables = [f"{row[0]}.{row[1]}" for row in result]
        
        for table in tables:
            try:
                command = f"VACUUM {'ANALYZE' if analyze else ''} {table}"
                db.session.execute(text(command))
                db.session.commit()
                results.append({
                    'table': table,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'table': table,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Vacuum operation failed: {str(e)}'}), 500


def _generate_index_recommendations(indexes: List[Dict]) -> List[Dict]:
    """Generate specific index recommendations"""
    recommendations = []
    
    for idx in indexes:
        if idx['impact'] == 'high':
            recommendations.append({
                'table': f"{idx['schema']}.{idx['table']}",
                'suggestion': f"CREATE INDEX idx_{idx['table']}_optimized ON {idx['schema']}.{idx['table']} (...);",
                'reason': f"Table has {idx['seq_scan_percentage']}% sequential scans",
                'priority': 'high'
            })
    
    return recommendations


def _calculate_health_score(cpu: float, memory: float, connections: Dict, long_queries: List) -> Dict:
    """Calculate overall system health score"""
    score = 100
    issues = []
    
    # CPU scoring
    if cpu > 90:
        score -= 30
        issues.append("CPU usage critical")
    elif cpu > 70:
        score -= 15
        issues.append("CPU usage high")
    
    # Memory scoring
    if memory > 90:
        score -= 30
        issues.append("Memory usage critical")
    elif memory > 80:
        score -= 15
        issues.append("Memory usage high")
    
    # Connection scoring
    total_connections = sum(connections.values())
    if total_connections > 80:
        score -= 20
        issues.append("High number of database connections")
    
    # Long query scoring
    if len(long_queries) > 5:
        score -= 20
        issues.append(f"{len(long_queries)} long-running queries detected")
    elif len(long_queries) > 0:
        score -= 10
        issues.append(f"{len(long_queries)} long-running queries")
    
    return {
        'score': max(0, score),
        'status': 'healthy' if score > 80 else 'warning' if score > 50 else 'critical',
        'issues': issues
    }