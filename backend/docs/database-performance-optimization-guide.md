# Database Performance Optimization Guide

## Overview

This guide provides comprehensive tools and strategies for monitoring and optimizing database performance in the Kuwait Social AI application.

## Performance Monitoring Tools

### 1. Query Performance Monitor

The `QueryPerformanceMonitor` class provides real-time query analysis:

```python
from utils.query_performance import QueryPerformanceMonitor

# Initialize monitor
monitor = QueryPerformanceMonitor(redis_client)

# Analyze current request queries
analysis = monitor.analyze_request_queries()

# Get slow query report
report = monitor.get_slow_query_report(days=7)
```

### 2. CLI Commands

Use Flask CLI commands for database analysis:

```bash
# Analyze slow queries from last 7 days
flask performance analyze-slow-queries --days 7

# Check for missing and unused indexes
flask performance check-indexes

# Monitor connection pool status
flask performance pool-status

# Get detailed table statistics
flask performance table-stats

# Run vacuum on tables with high bloat
flask performance vacuum --analyze

# Explain query execution plan
flask performance explain --query "SELECT * FROM posts WHERE client_id = 1"

# Show recommended PostgreSQL settings
flask performance optimize-settings
```

### 3. Admin API Endpoints

Access performance data via API:

```bash
# Get slow query report
GET /api/admin/performance/queries/slow?days=7

# Analyze specific query
POST /api/admin/performance/queries/analyze
Content-Type: application/json
{
    "query": "SELECT * FROM posts WHERE created_at > NOW() - INTERVAL '1 day'"
}

# Get database statistics
GET /api/admin/performance/database/stats

# Check system health
GET /api/admin/performance/system/health

# Find missing indexes
GET /api/admin/performance/database/missing-indexes
```

## Connection Pool Configuration

### Current Configuration

The application uses environment-specific connection pooling:

#### Production Settings
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,                    # Base connection pool size
    'max_overflow': 40,                 # Maximum overflow connections
    'pool_timeout': 30,                 # Timeout waiting for connection
    'pool_recycle': 3600,              # Recycle connections after 1 hour
    'pool_pre_ping': True,             # Verify connections before use
    'connect_args': {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
        'options': '-c statement_timeout=60000'
    }
}
```

#### Development Settings
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 10,
    'pool_pre_ping': True,
    'echo': True  # Log SQL statements
}
```

### Pool Sizing Calculator

Use this formula to determine optimal pool size:

```
Base Pool Size = Workers × Threads × DB Connections per Thread
Max Overflow = Base Pool Size × 1.5 to 2

Example for Gunicorn:
- 4 workers × 2 threads × 3 connections = 24 base pool size
- Max overflow = 24 × 1.5 = 36
```

### Environment Variables

Configure pool settings via environment variables:

```bash
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kuwait_social_ai
USE_PGBOUNCER=false
PGBOUNCER_PORT=6432
```

## Query Optimization Strategies

### 1. Index Optimization

#### Check for Missing Indexes
```sql
-- Tables with high sequential scan ratio
SELECT 
    schemaname,
    tablename,
    seq_scan,
    idx_scan,
    ROUND(100.0 * seq_scan / (seq_scan + idx_scan), 2) as seq_scan_pct
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
AND n_live_tup > 1000
ORDER BY seq_scan_pct DESC;
```

#### Find Unused Indexes
```sql
-- Indexes that are never used
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND NOT indisprimary
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 2. Query Pattern Optimization

#### N+1 Query Prevention
```python
# Bad - N+1 query
posts = Post.query.all()
for post in posts:
    print(post.author.name)  # Triggers additional query

# Good - Eager loading
posts = Post.query.options(joinedload(Post.author)).all()
for post in posts:
    print(post.author.name)  # No additional queries
```

#### Bulk Operations
```python
# Instead of individual inserts
for data in large_dataset:
    post = Post(**data)
    db.session.add(post)
db.session.commit()

# Use bulk operations
db.session.bulk_insert_mappings(Post, large_dataset)
db.session.commit()
```

### 3. Pagination Best Practices
```python
# Always use pagination for large datasets
posts = Post.query.paginate(
    page=1, 
    per_page=20, 
    error_out=False
)

# Use cursor-based pagination for real-time data
posts = Post.query.filter(
    Post.id > last_seen_id
).order_by(Post.id).limit(20)
```

## Monitoring Integration

### Application Integration

Add to your Flask app initialization:

```python
from middleware.performance_middleware import init_performance_monitoring

app = Flask(__name__)
init_performance_monitoring(app)
```

### Performance Headers

The middleware adds these headers to responses:

```
X-Request-Duration: 0.245
X-Request-ID: 1640995200000
X-DB-Query-Count: 12
X-DB-Query-Time: 0.156
```

### Alerting Configuration

Set up alerts for performance thresholds:

```python
# Performance thresholds
SLOW_QUERY_THRESHOLD = 0.5      # 500ms
SLOW_REQUEST_THRESHOLD = 1.0     # 1 second
POOL_WARNING_UTILIZATION = 0.8   # 80%
```

## Production Optimization Checklist

### Database Server Settings

Recommended PostgreSQL settings for production:

```conf
# Memory settings
shared_buffers = 4GB                    # 25% of RAM
effective_cache_size = 12GB             # 75% of RAM
work_mem = 4MB                          # RAM / max_connections / 2
maintenance_work_mem = 512MB            # RAM / 8

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB

# Query planner settings
default_statistics_target = 100
random_page_cost = 1.1                  # For SSD storage
effective_io_concurrency = 200          # For SSD storage

# Connection settings
max_connections = 200                   # Adjust based on pool size
```

### Application-Level Optimizations

1. **Enable SQLAlchemy Query Debugging** (Development only):
   ```python
   SQLALCHEMY_ECHO = True
   SQLALCHEMY_RECORD_QUERIES = True
   ```

2. **Use Redis for Caching**:
   ```python
   from flask_caching import Cache
   
   cache = Cache(app, config={
       'CACHE_TYPE': 'redis',
       'CACHE_REDIS_URL': 'redis://localhost:6379'
   })
   
   @cache.memoize(timeout=300)
   def get_trending_hashtags():
       return Hashtag.query.filter_by(trending=True).all()
   ```

3. **Implement Query Timeout**:
   ```python
   # Set statement timeout in connection string
   'options': '-c statement_timeout=30000'  # 30 seconds
   ```

### Monitoring Dashboards

#### Key Metrics to Track

1. **Database Metrics**:
   - Query execution time distribution
   - Connection pool utilization
   - Index hit ratio
   - Buffer hit ratio
   - Locks and blocking queries

2. **Application Metrics**:
   - Request response time
   - Error rate
   - Database query count per request
   - Cache hit ratio

3. **System Metrics**:
   - CPU utilization
   - Memory usage
   - Disk I/O
   - Network latency

## Common Performance Issues and Solutions

### Issue 1: High Query Count per Request

**Symptoms**: `X-DB-Query-Count` header shows > 20 queries

**Solutions**:
- Use eager loading with `joinedload()`
- Implement query batching
- Add caching for frequently accessed data

### Issue 2: Slow Queries

**Symptoms**: Queries taking > 500ms

**Solutions**:
- Add database indexes
- Optimize WHERE clauses
- Use database functions instead of application logic
- Consider query rewriting

### Issue 3: Connection Pool Exhaustion

**Symptoms**: "QueuePool limit exceeded" errors

**Solutions**:
- Increase `pool_size` and `max_overflow`
- Fix connection leaks in application code
- Use connection pooler like PgBouncer
- Optimize long-running transactions

### Issue 4: High Database CPU

**Symptoms**: Database server CPU > 80%

**Solutions**:
- Identify expensive queries with `pg_stat_statements`
- Add missing indexes
- Optimize complex joins
- Consider read replicas for read-heavy workloads

## Automated Performance Testing

### Query Performance Tests

```python
import pytest
from utils.query_performance import monitor_query_performance

@monitor_query_performance
def test_post_listing_performance():
    """Test that post listing performs within acceptable limits"""
    start_time = time.time()
    
    posts = Post.query.filter_by(client_id=1).paginate(
        page=1, per_page=20
    )
    
    duration = time.time() - start_time
    assert duration < 0.1  # Should complete in < 100ms
```

### Load Testing with Database Monitoring

```bash
# Run load tests while monitoring database
flask performance pool-status &
ab -n 1000 -c 10 http://localhost:5000/api/posts
```

## Troubleshooting Guide

### High Memory Usage

1. Check for connection leaks:
   ```bash
   flask performance pool-status
   ```

2. Monitor query complexity:
   ```bash
   flask performance analyze-slow-queries --days 1
   ```

3. Check for memory-intensive operations:
   ```sql
   SELECT * FROM pg_stat_activity WHERE query LIKE '%ORDER BY%';
   ```

### Slow Response Times

1. Enable query debugging:
   ```python
   SQLALCHEMY_ECHO = True
   ```

2. Check for N+1 queries:
   ```bash
   curl -H "X-Debug: 1" http://localhost:5000/api/posts
   # Check X-DB-Query-Count header
   ```

3. Analyze execution plans:
   ```bash
   flask performance explain --query "YOUR_SLOW_QUERY"
   ```

This comprehensive performance monitoring system provides the tools needed to maintain optimal database performance in production environments.