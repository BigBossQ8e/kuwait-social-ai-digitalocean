"""
Enhanced database configuration with optimized connection pooling
"""

import os
from typing import Dict, Any


class DatabaseConfig:
    """Database configuration with environment-specific optimizations"""
    
    @staticmethod
    def get_pool_config(environment: str = 'development') -> Dict[str, Any]:
        """Get optimized connection pool configuration based on environment"""
        
        # Check if using SQLite (for development/testing)
        db_url = os.getenv('DATABASE_URL', '')
        is_sqlite = 'sqlite' in db_url.lower()
        
        base_config = {
            # Connection pool settings
            'pool_pre_ping': True,  # Verify connections before using
            'pool_recycle': 3600,   # Recycle connections after 1 hour
            'echo_pool': environment == 'development',  # Log pool checkouts/checkins in dev
        }
        
        # Only add PostgreSQL-specific options if not using SQLite
        if not is_sqlite:
            base_config['connect_args'] = {
                'options': '-c statement_timeout=30000'  # 30 second statement timeout
            }
        
        if environment == 'production':
            # Production optimizations
            return {
                **base_config,
                'pool_size': int(os.getenv('DB_POOL_SIZE', 20)),  # Base connection pool size
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 40)),  # Maximum overflow connections
                'pool_timeout': 30,  # Timeout waiting for connection from pool
                
                # PostgreSQL specific optimizations (only if not SQLite)
                'connect_args': {
                    **base_config.get('connect_args', {}),
                    'keepalives': 1,
                    'keepalives_idle': 30,
                    'keepalives_interval': 10,
                    'keepalives_count': 5,
                    'options': '-c statement_timeout=60000 -c idle_in_transaction_session_timeout=60000'
                } if not is_sqlite else {},
                
                # Query execution options
                'execution_options': {
                    'isolation_level': 'READ COMMITTED',
                    'postgresql_readonly': False,
                    'postgresql_deferrable': False
                }
            }
        
        elif environment == 'development':
            # Development settings - smaller pool, more logging
            return {
                **base_config,
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 10,
                'echo': os.getenv('SQL_ECHO', 'false').lower() == 'true',  # Log all SQL statements
            }
        
        elif environment == 'testing':
            # Testing settings - minimal pool
            return {
                'pool_size': 1,
                'max_overflow': 0,
                'pool_pre_ping': False,
                'pool_recycle': -1  # Disable recycling for tests
            }
        
        return base_config
    
    @staticmethod
    def get_database_url(environment: str = 'development') -> str:
        """Get properly formatted database URL"""
        
        if environment == 'testing':
            return 'sqlite:///:memory:'
        
        # Get database credentials from environment
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'kuwait_social_ai')
        
        # Support for connection pooling services like PgBouncer
        if os.getenv('USE_PGBOUNCER', 'false').lower() == 'true':
            db_port = os.getenv('PGBOUNCER_PORT', '6432')
        
        # Build connection string
        if db_password:
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    @staticmethod
    def get_redis_pool_config() -> Dict[str, Any]:
        """Get Redis connection pool configuration"""
        
        return {
            'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', 50)),
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30
        }


class ConnectionPoolMonitor:
    """Monitor and log connection pool statistics"""
    
    def __init__(self, engine):
        self.engine = engine
        self.pool = engine.pool
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status"""
        return {
            'size': self.pool.size(),
            'checked_out': self.pool.checked_out(),
            'overflow': self.pool.overflow(),
            'total': self.pool.size() + self.pool.overflow(),
            'available': self.pool.size() - self.pool.checked_out()
        }
    
    def log_pool_status(self):
        """Log current pool status"""
        status = self.get_pool_status()
        
        # Log warning if pool is exhausted
        if status['available'] == 0 and status['overflow'] >= self.pool._max_overflow:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Connection pool exhausted: {status['checked_out']} checked out, "
                f"{status['overflow']} overflow connections"
            )
    
    def check_pool_health(self) -> Dict[str, Any]:
        """Check pool health and provide recommendations"""
        status = self.get_pool_status()
        health = {
            'status': 'healthy',
            'recommendations': []
        }
        
        # Check utilization
        utilization = status['checked_out'] / status['size'] if status['size'] > 0 else 0
        
        if utilization > 0.9:
            health['status'] = 'warning'
            health['recommendations'].append(
                f"High pool utilization ({utilization:.1%}). Consider increasing pool_size."
            )
        
        if status['overflow'] > status['size']:
            health['status'] = 'critical'
            health['recommendations'].append(
                f"Overflow connections ({status['overflow']}) exceed base pool size. "
                "This indicates pool exhaustion."
            )
        
        return {**status, **health}


# Connection pool best practices
POOL_SIZING_GUIDE = """
Connection Pool Sizing Guide:

1. **Calculate Base Pool Size**:
   - pool_size = (number_of_workers * average_connections_per_worker)
   - For Gunicorn: workers * threads * expected_db_connections_per_thread
   - Example: 4 workers * 2 threads * 3 connections = 24 pool_size

2. **Set Max Overflow**:
   - max_overflow = pool_size * 1.5 to 2
   - Handles traffic spikes without exhausting database

3. **Monitor and Adjust**:
   - Track pool utilization metrics
   - Increase if seeing frequent overflow usage
   - Decrease if connections sit idle

4. **Database Server Limits**:
   - PostgreSQL default max_connections = 100
   - Reserve connections for maintenance: usable = max_connections - 20
   - Total app connections should not exceed usable connections

5. **With PgBouncer**:
   - Can use smaller pool_size (5-10)
   - PgBouncer handles connection multiplexing
   - Set pgbouncer pool_mode = 'transaction' for best efficiency
"""


def optimize_query_performance():
    """
    Query performance optimization checklist:
    
    1. Use eager loading for relationships:
       query = Post.query.options(joinedload(Post.analytics)).all()
    
    2. Add database indexes:
       - Foreign keys (automatic in most cases)
       - Columns used in WHERE clauses
       - Columns used in ORDER BY
       - Columns used in JOIN conditions
    
    3. Use query pagination:
       posts = Post.query.paginate(page=1, per_page=20)
    
    4. Avoid N+1 queries:
       # Bad
       for post in posts:
           print(post.author.name)  # N+1 query
       
       # Good
       posts = Post.query.options(joinedload(Post.author)).all()
    
    5. Use bulk operations:
       db.session.bulk_insert_mappings(Model, data)
       db.session.bulk_update_mappings(Model, updates)
    
    6. Cache frequently accessed data:
       @cache.memoize(timeout=300)
       def get_trending_hashtags():
           return Hashtag.query.filter_by(trending=True).all()
    """
    pass