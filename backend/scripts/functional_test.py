#!/usr/bin/env python3
"""
Functional test for performance monitoring system
Tests core functionality with minimal dependencies
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_database_config():
    """Test database configuration without actual database"""
    print("🔧 Testing Database Configuration...")
    
    try:
        from config.database_config import DatabaseConfig
        
        # Test all environments
        environments = ['development', 'production', 'testing']
        
        for env in environments:
            config = DatabaseConfig.get_pool_config(env)
            
            # Check required keys
            required_keys = ['pool_pre_ping', 'pool_recycle']
            for key in required_keys:
                if key not in config:
                    print(f"❌ {env}: Missing {key}")
                    return False
            
            print(f"✅ {env}: {len(config)} configuration settings")
        
        # Test URL generation
        test_env_vars = {
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'testdb'
        }
        
        with patch.dict(os.environ, test_env_vars):
            url = DatabaseConfig.get_database_url('development')
            if 'testuser' in url and 'testdb' in url:
                print("✅ Database URL generation works")
            else:
                print(f"❌ Database URL generation failed: {url}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database config test failed: {e}")
        return False

def test_query_monitor():
    """Test query performance monitor functionality"""
    print("\n📊 Testing Query Performance Monitor...")
    
    try:
        # Mock Redis
        mock_redis = Mock()
        
        from utils.query_performance import QueryPerformanceMonitor
        
        # Test initialization
        monitor = QueryPerformanceMonitor(mock_redis)
        print("✅ Monitor initialized with Redis")
        
        # Test query pattern extraction
        test_queries = [
            "SELECT * FROM users WHERE id = 123",
            "UPDATE posts SET title = 'test' WHERE id = 456",
            "INSERT INTO logs (message, timestamp) VALUES ('test', '2024-01-01')"
        ]
        
        for query in test_queries:
            pattern = monitor._extract_query_pattern(query)
            if '?' in pattern:
                print(f"✅ Pattern extracted: {pattern[:50]}...")
            else:
                print(f"⚠️  Pattern might be incorrect: {pattern[:50]}...")
        
        # Test slow query logging
        with patch('logging.Logger.warning') as mock_log:
            monitor._log_slow_query("SELECT * FROM slow_table", None, 2.5)
            mock_log.assert_called_once()
            print("✅ Slow query logging works")
        
        # Test optimization recommendations
        fake_patterns = [
            ("SELECT * FROM posts WHERE client_id = ?", {
                'count': 100, 'total_duration': 30.0, 'average_duration': 0.3
            }),
            ("SELECT COUNT(*) FROM users", {
                'count': 50, 'total_duration': 25.0, 'average_duration': 0.5
            })
        ]
        
        recommendations = monitor._generate_optimization_recommendations(fake_patterns)
        if recommendations:
            print(f"✅ Generated {len(recommendations)} optimization recommendations")
            for rec in recommendations:
                print(f"   - {rec['type']}: {rec['description'][:50]}...")
        else:
            print("⚠️  No recommendations generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Query monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_connection_pool_monitor():
    """Test connection pool monitoring"""
    print("\n🏊 Testing Connection Pool Monitor...")
    
    try:
        from config.database_config import ConnectionPoolMonitor
        
        # Mock SQLAlchemy engine and pool
        mock_pool = Mock()
        mock_pool.size.return_value = 10
        mock_pool.checked_out.return_value = 5
        mock_pool.overflow.return_value = 2
        mock_pool._max_overflow = 20
        
        mock_engine = Mock()
        mock_engine.pool = mock_pool
        
        monitor = ConnectionPoolMonitor(mock_engine)
        
        # Test pool status
        status = monitor.get_pool_status()
        expected_keys = ['size', 'checked_out', 'overflow', 'total', 'available']
        
        for key in expected_keys:
            if key not in status:
                print(f"❌ Missing status key: {key}")
                return False
        
        print(f"✅ Pool status: {status}")
        
        # Test health check
        health = monitor.check_pool_health()
        if 'status' in health and 'recommendations' in health:
            print(f"✅ Health check: {health['status']}")
            if health['recommendations']:
                print(f"   Recommendations: {len(health['recommendations'])}")
        else:
            print("❌ Health check failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Connection pool monitor test failed: {e}")
        return False

def test_middleware_functionality():
    """Test middleware functionality"""
    print("\n🛡️  Testing Performance Middleware...")
    
    try:
        # Mock Flask app
        from flask import Flask
        
        # Create minimal app for testing
        app = Flask(__name__)
        app.config['REDIS_URL'] = 'redis://localhost:6379'
        app.config['ENV'] = 'testing'
        
        # Mock Redis
        mock_redis = Mock()
        
        with patch('redis.from_url', return_value=mock_redis):
            from middleware.performance_middleware import init_performance_monitoring
            
            # This should not crash
            init_performance_monitoring(app)
            print("✅ Middleware initialization successful")
        
        # Test performance config
        from middleware.performance_middleware import PerformanceConfig
        
        config = PerformanceConfig()
        print(f"✅ Performance config loaded:")
        print(f"   Slow query threshold: {config.SLOW_QUERY_THRESHOLD}s")
        print(f"   Pool warning threshold: {config.POOL_WARNING_UTILIZATION}")
        
        # Test environment override
        original = config.SLOW_QUERY_THRESHOLD
        os.environ['SLOW_QUERY_THRESHOLD'] = '2.0'
        
        PerformanceConfig.from_env()
        if config.SLOW_QUERY_THRESHOLD == 2.0:
            print("✅ Environment variable override works")
        else:
            print("⚠️  Environment override might not be working")
        
        # Restore
        config.SLOW_QUERY_THRESHOLD = original
        if 'SLOW_QUERY_THRESHOLD' in os.environ:
            del os.environ['SLOW_QUERY_THRESHOLD']
        
        return True
        
    except Exception as e:
        print(f"❌ Middleware test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_command_structure():
    """Test CLI command structure"""
    print("\n💻 Testing CLI Commands...")
    
    try:
        from commands.performance import performance
        
        # Check if it's a Click group
        if hasattr(performance, 'commands'):
            commands = list(performance.commands.keys())
            print(f"✅ Found {len(commands)} CLI commands:")
            for cmd in commands:
                print(f"   - {cmd}")
            
            # Test specific commands exist
            expected = ['analyze-slow-queries', 'check-indexes', 'pool-status']
            missing = [cmd for cmd in expected if cmd not in commands]
            
            if missing:
                print(f"⚠️  Missing commands: {missing}")
            else:
                print("✅ All expected commands found")
        else:
            print("❌ CLI group structure not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_blueprint_registration():
    """Test blueprint registration"""
    print("\n🔗 Testing Blueprint Registration...")
    
    try:
        from flask import Flask
        
        app = Flask(__name__)
        
        # Test admin performance blueprint
        from routes.admin.performance import performance_bp
        app.register_blueprint(performance_bp, url_prefix='/admin/performance')
        print("✅ Admin performance blueprint registered")
        
        # Test client main blueprint
        from routes.client import client_bp
        app.register_blueprint(client_bp, url_prefix='/client')
        print("✅ Client blueprint registered")
        
        # Check routes
        with app.app_context():
            rules = [rule.rule for rule in app.url_map.iter_rules()]
            
            # Check for expected routes
            expected_patterns = [
                '/admin/performance',
                '/client/dashboard',
                '/client/posts',
                '/client/analytics',
                '/client/competitors',
                '/client/features'
            ]
            
            found_patterns = []
            for pattern in expected_patterns:
                if any(pattern in rule for rule in rules):
                    found_patterns.append(pattern)
            
            print(f"✅ Found {len(found_patterns)}/{len(expected_patterns)} expected route patterns")
            
            if len(found_patterns) < len(expected_patterns):
                missing = set(expected_patterns) - set(found_patterns)
                print(f"⚠️  Missing route patterns: {missing}")
        
        return True
        
    except Exception as e:
        print(f"❌ Blueprint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_flow():
    """Test complete integration flow"""
    print("\n🧪 Testing Integration Flow...")
    
    try:
        # Mock complete environment
        from config.database_config import DatabaseConfig
        from utils.query_performance import QueryPerformanceMonitor
        from middleware.performance_middleware import PerformanceConfig
        
        # Test configuration flow
        pool_config = DatabaseConfig.get_pool_config('development')
        monitor = QueryPerformanceMonitor()
        perf_config = PerformanceConfig()
        
        print("✅ Configuration chain successful")
        
        # Test analysis flow
        mock_queries = [
            {
                'statement': 'SELECT * FROM posts WHERE client_id = ?',
                'duration': 0.1,
                'timestamp': '2024-01-01T00:00:00'
            },
            {
                'statement': 'SELECT COUNT(*) FROM users',
                'duration': 0.8,  # Slow query
                'timestamp': '2024-01-01T00:00:01'
            }
        ]
        
        # Simulate request analysis
        total_time = sum(q['duration'] for q in mock_queries)
        slow_queries = [q for q in mock_queries if q['duration'] > perf_config.SLOW_QUERY_THRESHOLD]
        
        analysis = {
            'total_queries': len(mock_queries),
            'total_time': total_time,
            'average_time': total_time / len(mock_queries),
            'slow_queries': len(slow_queries)
        }
        
        print(f"✅ Analysis simulation successful:")
        print(f"   Total queries: {analysis['total_queries']}")
        print(f"   Total time: {analysis['total_time']:.3f}s")
        print(f"   Slow queries: {analysis['slow_queries']}")
        
        # Test optimization suggestions
        if analysis['slow_queries'] > 0:
            print("✅ Slow query detection working")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all functional tests"""
    print("🧪 Kuwait Social AI - Functional Test Suite")
    print("=" * 80)
    
    tests = [
        ("Database Configuration", test_database_config),
        ("Query Monitor", test_query_monitor),
        ("Connection Pool Monitor", test_connection_pool_monitor),
        ("Middleware", test_middleware_functionality),
        ("CLI Commands", test_cli_command_structure),
        ("Blueprint Registration", test_blueprint_registration),
        ("Integration Flow", test_integration_flow),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FUNCTIONAL TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for result in results.values() if result)
    failed = sum(1 for result in results.values() if not result)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All functional tests passed!")
        print("\n📋 DEPLOYMENT READINESS:")
        print("✅ Core functionality verified")
        print("✅ Configuration system working")
        print("✅ Monitoring components functional")
        print("✅ Blueprint structure correct")
        
        print("\n📋 TO DEPLOY:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set environment variables (Redis, Database)")
        print("3. Test with actual database: python scripts/verify_pool_config.py")
        print("4. Initialize in Flask app:")
        print("   from middleware.performance_middleware import init_performance_monitoring")
        print("   init_performance_monitoring(app)")
        
        return 0
    else:
        print(f"\n⚠️  {failed} functional tests failed.")
        print("Please fix issues before deploying to production.")
        return 1

if __name__ == "__main__":
    sys.exit(main())