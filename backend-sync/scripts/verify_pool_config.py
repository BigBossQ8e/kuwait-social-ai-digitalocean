#!/usr/bin/env python3
"""
Connection pool configuration verification script
Validates and tests database connection pool settings
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from config.database_config import DatabaseConfig


def test_connection_pool():
    """Test connection pool configuration and behavior"""
    
    print("🔍 Testing Database Connection Pool Configuration\n")
    
    # Get configuration
    env = os.getenv('FLASK_ENV', 'development')
    pool_config = DatabaseConfig.get_pool_config(env)
    db_url = DatabaseConfig.get_database_url(env)
    
    print(f"Environment: {env}")
    print(f"Database URL: {db_url.split('@')[0]}@***")  # Hide credentials
    print("\nPool Configuration:")
    for key, value in pool_config.items():
        print(f"  {key}: {value}")
    
    # Create engine with pool configuration
    engine = create_engine(db_url, **pool_config)
    
    # Test basic connectivity
    print("\n📡 Testing Basic Connectivity...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            assert result.fetchone()[0] == 1
        print("✅ Basic connectivity test passed")
    except Exception as e:
        print(f"❌ Basic connectivity test failed: {e}")
        return False
    
    # Test pool behavior
    print("\n🏊 Testing Pool Behavior...")
    
    pool = engine.pool
    print(f"Initial pool size: {pool.size()}")
    print(f"Initial checked out: {pool.checked_out()}")
    
    # Test concurrent connections
    print("\n🔄 Testing Concurrent Connections...")
    
    def test_connection(connection_id):
        """Test function for concurrent connections"""
        try:
            with engine.connect() as conn:
                # Simulate work
                result = conn.execute(text("SELECT pg_sleep(0.1), :id as conn_id"), {"id": connection_id})
                return result.fetchone()[1]
        except Exception as e:
            return f"Error-{connection_id}: {str(e)}"
    
    # Test with number of connections equal to pool size
    num_connections = pool_config.get('pool_size', 5)
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_connections) as executor:
        futures = [executor.submit(test_connection, i) for i in range(num_connections)]
        
        # Check pool status during execution
        time.sleep(0.05)  # Let connections start
        print(f"Pool size during execution: {pool.size()}")
        print(f"Checked out during execution: {pool.checked_out()}")
        print(f"Overflow during execution: {pool.overflow()}")
        
        # Wait for completion
        results = [future.result() for future in as_completed(futures)]
    
    execution_time = time.time() - start_time
    print(f"Concurrent connections completed in {execution_time:.2f} seconds")
    print(f"Results: {results}")
    
    # Test overflow behavior (if max_overflow is configured)
    if pool_config.get('max_overflow', 0) > 0:
        print("\n🌊 Testing Overflow Behavior...")
        
        # Test with more connections than pool size
        overflow_connections = num_connections + 2
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=overflow_connections) as executor:
            futures = [executor.submit(test_connection, i) for i in range(overflow_connections)]
            
            # Check pool status
            time.sleep(0.05)
            print(f"Pool size with overflow: {pool.size()}")
            print(f"Checked out with overflow: {pool.checked_out()}")
            print(f"Overflow connections: {pool.overflow()}")
            
            results = [future.result() for future in as_completed(futures)]
        
        execution_time = time.time() - start_time
        print(f"Overflow test completed in {execution_time:.2f} seconds")
        
        # Check for any errors
        errors = [r for r in results if str(r).startswith('Error')]
        if errors:
            print(f"⚠️  Errors during overflow test: {errors}")
        else:
            print("✅ Overflow test passed")
    
    # Test pool recovery
    print("\n🔄 Testing Pool Recovery...")
    initial_checked_out = pool.checked_out()
    
    # Force close all connections
    pool.dispose()
    
    # Test recovery
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'recovered' as status"))
            status = result.fetchone()[0]
            print(f"✅ Pool recovery test passed: {status}")
    except Exception as e:
        print(f"❌ Pool recovery test failed: {e}")
        return False
    
    print(f"Pool recovered - checked out: {pool.checked_out()}")
    
    return True


def test_query_timeout():
    """Test query timeout configuration"""
    
    print("\n⏱️  Testing Query Timeout Configuration...")
    
    env = os.getenv('FLASK_ENV', 'development')
    pool_config = DatabaseConfig.get_pool_config(env)
    db_url = DatabaseConfig.get_database_url(env)
    
    engine = create_engine(db_url, **pool_config)
    
    try:
        start_time = time.time()
        with engine.connect() as conn:
            # This should timeout based on statement_timeout setting
            result = conn.execute(text("SELECT pg_sleep(65)"))  # 65 seconds
            print("❌ Query timeout test failed - query should have timed out")
            return False
    except Exception as e:
        execution_time = time.time() - start_time
        if execution_time < 65:  # Should timeout before 65 seconds
            print(f"✅ Query timeout test passed - timed out after {execution_time:.1f} seconds")
            print(f"   Error: {str(e)[:100]}...")
            return True
        else:
            print(f"❌ Query timeout test failed - took {execution_time:.1f} seconds")
            return False


def test_connection_resilience():
    """Test connection resilience and pre_ping functionality"""
    
    print("\n🔧 Testing Connection Resilience...")
    
    env = os.getenv('FLASK_ENV', 'development')
    pool_config = DatabaseConfig.get_pool_config(env)
    db_url = DatabaseConfig.get_database_url(env)
    
    # Enable pre_ping for this test
    pool_config['pool_pre_ping'] = True
    engine = create_engine(db_url, **pool_config)
    
    # Get a connection and keep it
    conn1 = engine.connect()
    
    # Wait for potential connection timeout (simulate idle time)
    print("Simulating idle connection...")
    time.sleep(2)
    
    try:
        # This should work with pre_ping enabled
        result = conn1.execute(text("SELECT 'still_alive' as status"))
        status = result.fetchone()[0]
        print(f"✅ Connection resilience test passed: {status}")
        
        conn1.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection resilience test failed: {e}")
        conn1.close()
        return False


def analyze_pool_sizing():
    """Analyze and recommend pool sizing"""
    
    print("\n📊 Pool Sizing Analysis...")
    
    env = os.getenv('FLASK_ENV', 'development')
    pool_config = DatabaseConfig.get_pool_config(env)
    
    pool_size = pool_config.get('pool_size', 5)
    max_overflow = pool_config.get('max_overflow', 0)
    total_connections = pool_size + max_overflow
    
    print(f"Current pool configuration:")
    print(f"  Base pool size: {pool_size}")
    print(f"  Max overflow: {max_overflow}")
    print(f"  Total possible connections: {total_connections}")
    
    # Get system information for recommendations
    try:
        import psutil
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        print(f"\nSystem resources:")
        print(f"  CPU cores: {cpu_count}")
        print(f"  Memory: {memory_gb:.1f} GB")
        
        # Provide recommendations
        recommended_pool = min(cpu_count * 2, 20)  # 2 connections per core, max 20
        recommended_overflow = recommended_pool
        
        print(f"\nRecommended configuration:")
        print(f"  pool_size: {recommended_pool}")
        print(f"  max_overflow: {recommended_overflow}")
        
        if pool_size < recommended_pool:
            print(f"⚠️  Consider increasing pool_size from {pool_size} to {recommended_pool}")
        elif pool_size > recommended_pool * 2:
            print(f"⚠️  Pool size ({pool_size}) might be too large for {cpu_count} cores")
        else:
            print("✅ Pool size appears appropriate for system resources")
            
    except ImportError:
        print("Install psutil for system resource analysis: pip install psutil")


def main():
    """Run all connection pool tests"""
    
    print("=" * 60)
    print("🏊 Database Connection Pool Verification")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test basic pool functionality
    if not test_connection_pool():
        all_tests_passed = False
    
    # Test query timeouts (skip in testing environment)
    if os.getenv('FLASK_ENV') != 'testing':
        if not test_query_timeout():
            all_tests_passed = False
    
    # Test connection resilience
    if not test_connection_resilience():
        all_tests_passed = False
    
    # Analyze pool sizing
    analyze_pool_sizing()
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 All connection pool tests passed!")
        print("✅ Connection pool is properly configured")
    else:
        print("❌ Some tests failed - review configuration")
        print("📖 Check docs/database-performance-optimization-guide.md for help")
    
    print("=" * 60)
    
    return 0 if all_tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())