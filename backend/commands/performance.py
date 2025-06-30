"""
CLI commands for performance monitoring and optimization
"""

import click
from flask.cli import with_appcontext
from models import db
from sqlalchemy import text
from utils.query_performance import QueryPerformanceMonitor, QueryOptimizationHelper
from config.database_config import ConnectionPoolMonitor
try:
    from tabulate import tabulate
except ImportError:
    tabulate = None
import json


@click.group()
def performance():
    """Performance monitoring and optimization commands"""
    pass


@performance.command()
@click.option('--days', default=7, help='Number of days to analyze')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@with_appcontext
def analyze_slow_queries(days, format):
    """Analyze slow queries from the past N days"""
    
    monitor = QueryPerformanceMonitor()
    report = monitor.get_slow_query_report(days)
    
    if format == 'json':
        click.echo(json.dumps(report, indent=2))
    else:
        # Display as table
        if report.get('query_patterns'):
            if not tabulate:
                click.echo("Install tabulate for table formatting: pip install tabulate")
                # Simple text output
                click.echo(f"\nTop 10 Slow Query Patterns (last {days} days):")
                for i, p in enumerate(report['query_patterns'][:10], 1):
                    click.echo(f"{i}. Pattern: {p['pattern'][:50]}...")
                    click.echo(f"   Count: {p['count']}, Avg: {p['average_duration']:.3f}s")
            else:
                headers = ['Pattern', 'Count', 'Avg Duration', 'Total Impact']
                rows = [
                    [
                        p['pattern'][:50] + '...',
                        p['count'],
                        f"{p['average_duration']:.3f}s",
                        f"{p['total_impact']:.3f}s"
                    ]
                    for p in report['query_patterns'][:10]
                ]
                
                click.echo(f"\nTop 10 Slow Query Patterns (last {days} days):")
                click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
            
            if report.get('recommendations'):
                click.echo("\nRecommendations:")
                for i, rec in enumerate(report['recommendations'], 1):
                    click.echo(f"{i}. [{rec['severity'].upper()}] {rec['description']}")


@performance.command()
@with_appcontext
def check_indexes():
    """Check for missing and unused indexes"""
    
    # Check for tables that might need indexes
    missing_query = """
    SELECT 
        schemaname,
        tablename,
        seq_scan,
        idx_scan,
        CASE 
            WHEN seq_scan + idx_scan > 0 THEN 
                ROUND(100.0 * seq_scan / (seq_scan + idx_scan), 2)
            ELSE 0 
        END as seq_scan_pct
    FROM pg_stat_user_tables
    WHERE seq_scan > idx_scan
    AND n_live_tup > 1000
    ORDER BY seq_scan DESC
    LIMIT 10;
    """
    
    result = db.session.execute(text(missing_query))
    missing_indexes = list(result)
    
    if missing_indexes:
        click.echo("\nTables that might benefit from indexes:")
        if tabulate:
            headers = ['Schema', 'Table', 'Seq Scans', 'Index Scans', 'Seq Scan %']
            rows = [
                [row[0], row[1], row[2], row[3], f"{row[4]}%"]
                for row in missing_indexes
            ]
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
        else:
            for row in missing_indexes:
                click.echo(f"  {row[0]}.{row[1]}: {row[2]} seq scans, {row[3]} index scans ({row[4]}%)")
    
    # Check for unused indexes
    unused_query = """
    SELECT 
        schemaname,
        tablename,
        indexname,
        pg_size_pretty(pg_relation_size(indexrelid)) as index_size
    FROM pg_stat_user_indexes
    JOIN pg_index ON pg_index.indexrelid = pg_stat_user_indexes.indexrelid
    WHERE idx_scan = 0
    AND NOT indisprimary
    ORDER BY pg_relation_size(indexrelid) DESC;
    """
    
    result = db.session.execute(text(unused_query))
    unused_indexes = list(result)
    
    if unused_indexes:
        click.echo("\n\nUnused indexes (candidates for removal):")
        if tabulate:
            headers = ['Schema', 'Table', 'Index', 'Size']
            rows = [
                [row[0], row[1], row[2], row[3]]
                for row in unused_indexes
            ]
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
        else:
            for row in unused_indexes:
                click.echo(f"  {row[0]}.{row[1]}.{row[2]}: {row[3]}")


@performance.command()
@with_appcontext
def pool_status():
    """Check database connection pool status"""
    
    engine = db.get_engine()
    monitor = ConnectionPoolMonitor(engine)
    
    status = monitor.check_pool_health()
    
    click.echo("\nConnection Pool Status:")
    click.echo(f"  Pool Size: {status['size']}")
    click.echo(f"  Checked Out: {status['checked_out']}")
    click.echo(f"  Overflow: {status['overflow']}")
    click.echo(f"  Total: {status['total']}")
    click.echo(f"  Available: {status['available']}")
    click.echo(f"  Status: {status['status'].upper()}")
    
    if status.get('recommendations'):
        click.echo("\nRecommendations:")
        for rec in status['recommendations']:
            click.echo(f"  - {rec}")


@performance.command()
@click.option('--table', help='Specific table to analyze')
@with_appcontext
def table_stats(table):
    """Show detailed table statistics"""
    
    if table:
        where_clause = f"WHERE tablename = '{table}'"
    else:
        where_clause = "ORDER BY n_live_tup DESC LIMIT 10"
    
    query = f"""
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
        pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
        n_live_tup as live_rows,
        n_dead_tup as dead_rows,
        CASE 
            WHEN n_live_tup > 0 THEN 
                ROUND(100.0 * n_dead_tup / n_live_tup, 2)
            ELSE 0 
        END as bloat_pct,
        last_vacuum,
        last_autovacuum,
        last_analyze
    FROM pg_stat_user_tables
    {where_clause};
    """
    
    result = db.session.execute(text(query))
    tables = list(result)
    
    if tables:
        click.echo("\nTable Statistics:")
        if tabulate:
            headers = [
                'Schema', 'Table', 'Total Size', 'Table Size', 
                'Live Rows', 'Dead Rows', 'Bloat %', 
                'Last Vacuum', 'Last Autovacuum', 'Last Analyze'
            ]
            rows = [
                [
                    row[0], row[1], row[2], row[3], 
                    f"{row[4]:,}", f"{row[5]:,}", f"{row[6]}%",
                    str(row[7])[:10] if row[7] else 'Never',
                    str(row[8])[:10] if row[8] else 'Never',
                    str(row[9])[:10] if row[9] else 'Never'
                ]
                for row in tables
            ]
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
        else:
            for row in tables:
                click.echo(f"  {row[0]}.{row[1]}: {row[2]} total, {row[4]:,} live rows, {row[6]}% bloat")
        
        # Recommendations
        for row in tables:
            if row[6] > 20:  # Bloat > 20%
                click.echo(f"\n⚠️  Table {row[0]}.{row[1]} has {row[6]}% bloat. Consider running VACUUM.")


@performance.command()
@click.option('--analyze', is_flag=True, help='Also run ANALYZE')
@click.option('--full', is_flag=True, help='Run VACUUM FULL (locks table)')
@click.option('--table', help='Specific table to vacuum')
@click.confirmation_option(prompt='This will run VACUUM on the database. Continue?')
@with_appcontext
def vacuum(analyze, full, table):
    """Run VACUUM on database tables"""
    
    try:
        if table:
            tables = [table]
        else:
            # Get tables with high bloat
            query = """
            SELECT schemaname || '.' || tablename
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 1000
            AND n_live_tup > 0
            AND (n_dead_tup::float / n_live_tup) > 0.1
            ORDER BY n_dead_tup DESC
            LIMIT 10;
            """
            result = db.session.execute(text(query))
            tables = [row[0] for row in result]
        
        if not tables:
            click.echo("No tables need vacuum.")
            return
        
        click.echo(f"Vacuuming {len(tables)} table(s)...")
        
        for table in tables:
            try:
                vacuum_cmd = "VACUUM"
                if full:
                    vacuum_cmd += " FULL"
                if analyze:
                    vacuum_cmd += " ANALYZE"
                vacuum_cmd += f" {table}"
                
                click.echo(f"Running: {vacuum_cmd}")
                db.session.execute(text(vacuum_cmd))
                db.session.commit()
                click.echo(f"✓ Completed: {table}")
                
            except Exception as e:
                click.echo(f"✗ Failed {table}: {str(e)}", err=True)
        
        click.echo("\nVacuum operation completed.")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@performance.command()
@click.option('--query', prompt='SQL Query', help='Query to explain')
@click.option('--analyze', is_flag=True, help='Use EXPLAIN ANALYZE')
@with_appcontext
def explain(query, analyze):
    """Run EXPLAIN on a query to see execution plan"""
    
    try:
        explain_cmd = "EXPLAIN"
        if analyze:
            explain_cmd += " (ANALYZE, BUFFERS)"
        explain_cmd += f" {query}"
        
        result = db.session.execute(text(explain_cmd))
        
        click.echo("\nExecution Plan:")
        for row in result:
            click.echo(row[0])
        
        # Basic analysis
        plan_text = '\n'.join([row[0] for row in result])
        
        click.echo("\nAnalysis:")
        if 'Seq Scan' in plan_text:
            click.echo("⚠️  Sequential scan detected - consider adding an index")
        if 'Nested Loop' in plan_text:
            click.echo("⚠️  Nested loop join - may be slow for large datasets")
        if 'Sort' in plan_text:
            click.echo("ℹ️  Sort operation - ensure indexed if used in ORDER BY")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@performance.command()
@with_appcontext
def optimize_settings():
    """Show recommended PostgreSQL settings for performance"""
    
    # Get current settings
    settings_query = """
    SELECT name, setting, unit, short_desc
    FROM pg_settings
    WHERE name IN (
        'shared_buffers', 'effective_cache_size', 'work_mem',
        'maintenance_work_mem', 'max_connections', 'checkpoint_completion_target',
        'wal_buffers', 'default_statistics_target', 'random_page_cost',
        'effective_io_concurrency', 'min_wal_size', 'max_wal_size'
    )
    ORDER BY name;
    """
    
    result = db.session.execute(text(settings_query))
    current_settings = {row[0]: row[1] for row in result}
    
    click.echo("\nCurrent PostgreSQL Performance Settings:")
    for name, value in current_settings.items():
        click.echo(f"  {name}: {value}")
    
    click.echo("\nRecommended Settings for Production:")
    click.echo("  shared_buffers: 25% of RAM (e.g., '4GB')")
    click.echo("  effective_cache_size: 75% of RAM (e.g., '12GB')")
    click.echo("  work_mem: RAM / max_connections / 2 (e.g., '4MB')")
    click.echo("  maintenance_work_mem: RAM / 8 (e.g., '512MB')")
    click.echo("  checkpoint_completion_target: 0.9")
    click.echo("  wal_buffers: 16MB")
    click.echo("  default_statistics_target: 100")
    click.echo("  random_page_cost: 1.1 (for SSD)")
    click.echo("  effective_io_concurrency: 200 (for SSD)")
    click.echo("  max_wal_size: 4GB")
    click.echo("  min_wal_size: 1GB")
    
    click.echo("\n💡 To apply these settings, add them to postgresql.conf and restart PostgreSQL")


# Register commands
def register_performance_commands(app):
    """Register performance commands with Flask app"""
    app.cli.add_command(performance)