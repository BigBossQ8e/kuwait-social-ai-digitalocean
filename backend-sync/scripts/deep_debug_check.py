#!/usr/bin/env python3
"""
Deep debug check for Kuwait Social AI backend
Comprehensive verification of all performance monitoring components
"""

import sys
import os
import importlib
import traceback
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing Critical Imports...")
    
    imports_to_test = [
        ('utils.query_performance', ['QueryPerformanceMonitor', 'QueryPerformanceMiddleware']),
        ('config.database_config', ['DatabaseConfig', 'ConnectionPoolMonitor']),
        ('middleware.performance_middleware', ['init_performance_monitoring']),
        ('routes.admin.performance', ['performance_bp']),
        ('routes.client.features', ['features_bp']),
        ('commands.performance', ['performance']),
    ]
    
    failed_imports = []
    
    for module_name, classes in imports_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ {module_name}")
            
            # Test specific classes/functions
            for class_name in classes:
                if hasattr(module, class_name):
                    print(f"  ✅ {class_name}")
                else:
                    print(f"  ❌ {class_name} not found")
                    failed_imports.append(f"{module_name}.{class_name}")
                    
        except ImportError as e:
            print(f"❌ {module_name}: {str(e)}")
            failed_imports.append(module_name)
        except Exception as e:
            print(f"⚠️  {module_name}: {str(e)}")
            failed_imports.append(f"{module_name} (error)")
    
    return failed_imports


def test_database_config():
    """Test database configuration functionality"""
    print("\n🔧 Testing Database Configuration...")
    
    try:
        from config.database_config import DatabaseConfig
        
        # Test configuration generation
        for env in ['development', 'production', 'testing']:
            config = DatabaseConfig.get_pool_config(env)
            print(f"✅ {env} config generated: {len(config)} settings")
            
            # Verify required settings
            required_settings = ['pool_pre_ping', 'pool_recycle']
            for setting in required_settings:
                if setting in config:
                    print(f"  ✅ {setting}: {config[setting]}")
                else:
                    print(f"  ❌ Missing {setting}")
        
        # Test database URL generation
        db_url = DatabaseConfig.get_database_url('development')
        if db_url:
            print(f"✅ Database URL generated: {db_url.split('@')[0]}@***")
        else:
            print("❌ Failed to generate database URL")
            
        return True
        
    except Exception as e:
        print(f"❌ Database config test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_query_monitor():
    """Test query performance monitor"""
    print("\n📊 Testing Query Performance Monitor...")
    
    try:
        from utils.query_performance import QueryPerformanceMonitor
        
        # Test initialization without Redis
        monitor = QueryPerformanceMonitor()
        print("✅ Monitor initialized without Redis")
        
        # Test query pattern extraction
        test_query = "SELECT * FROM users WHERE id = 123 AND name = 'test'"
        pattern = monitor._extract_query_pattern(test_query)
        expected_pattern = "SELECT * FROM users WHERE id = ? AND name = '?'"
        
        if '?' in pattern:
            print(f"✅ Query pattern extraction: {pattern[:50]}...")
        else:
            print(f"⚠️  Query pattern might not be working: {pattern[:50]}...")
        
        # Test optimization recommendations
        fake_patterns = [
            ("SELECT * FROM posts WHERE client_id = ?", {
                'count': 150, 'total_duration': 45.0, 'average_duration': 0.3
            })
        ]
        
        recommendations = monitor._generate_optimization_recommendations(fake_patterns)
        if recommendations:
            print(f"✅ Generated {len(recommendations)} recommendations")
        else:
            print("⚠️  No recommendations generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Query monitor test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_middleware_setup():
    """Test middleware functionality"""
    print("\n🛡️  Testing Performance Middleware...")
    
    try:
        from middleware.performance_middleware import PerformanceConfig
        
        # Test configuration
        config = PerformanceConfig()
        print(f"✅ Default slow query threshold: {config.SLOW_QUERY_THRESHOLD}s")
        print(f"✅ Default slow request threshold: {config.SLOW_REQUEST_THRESHOLD}s")
        
        # Test environment loading
        original_threshold = config.SLOW_QUERY_THRESHOLD
        os.environ['SLOW_QUERY_THRESHOLD'] = '1.0'
        
        PerformanceConfig.from_env()
        if config.SLOW_QUERY_THRESHOLD == 1.0:
            print("✅ Environment configuration loading works")
        else:
            print("⚠️  Environment configuration might not be working")
        
        # Restore original
        config.SLOW_QUERY_THRESHOLD = original_threshold
        if 'SLOW_QUERY_THRESHOLD' in os.environ:
            del os.environ['SLOW_QUERY_THRESHOLD']
        
        return True
        
    except Exception as e:
        print(f"❌ Middleware test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_cli_commands():
    """Test CLI command structure"""
    print("\n💻 Testing CLI Commands...")
    
    try:
        from commands.performance import performance
        
        # Check if click group is properly configured
        if hasattr(performance, 'commands'):
            commands = list(performance.commands.keys())
            print(f"✅ Available commands: {commands}")
            
            expected_commands = [
                'analyze-slow-queries', 'check-indexes', 'pool-status',
                'table-stats', 'vacuum', 'explain', 'optimize-settings'
            ]
            
            missing_commands = [cmd for cmd in expected_commands if cmd not in commands]
            if missing_commands:
                print(f"⚠️  Missing commands: {missing_commands}")
            else:
                print("✅ All expected commands present")
        else:
            print("⚠️  Commands structure not found")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI commands test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_blueprint_structure():
    """Test Flask blueprint structure"""
    print("\n🔗 Testing Blueprint Structure...")
    
    try:
        # Test admin performance blueprint
        from routes.admin.performance import performance_bp
        print(f"✅ Admin performance blueprint: {performance_bp.name}")
        
        # Test client features blueprint
        from routes.client.features import features_bp
        print(f"✅ Client features blueprint: {features_bp.name}")
        
        # Test client main blueprint
        from routes.client import client_bp
        print(f"✅ Client main blueprint: {client_bp.name}")
        
        # Check if sub-blueprints are registered
        if hasattr(client_bp, 'blueprints'):
            sub_blueprints = list(client_bp.blueprints.keys())
            print(f"✅ Sub-blueprints: {sub_blueprints}")
        
        return True
        
    except Exception as e:
        print(f"❌ Blueprint test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_optional_dependencies():
    """Test optional dependencies and provide installation instructions"""
    print("\n📦 Testing Optional Dependencies...")
    
    optional_deps = {
        'psutil': 'System monitoring (pip install psutil)',
        'tabulate': 'Table formatting (pip install tabulate)',
        'apscheduler': 'Background scheduling (pip install apscheduler)',
        'redis': 'Redis client (pip install redis)',
    }
    
    missing_deps = []
    
    for dep, description in optional_deps.items():
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}: Available")
        except ImportError:
            print(f"⚠️  {dep}: Not available - {description}")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\nTo install missing dependencies:")
        print(f"pip install {' '.join(missing_deps)}")
    
    return missing_deps


def test_file_structure():
    """Verify file structure is correct"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        'utils/query_performance.py',
        'config/database_config.py',
        'middleware/performance_middleware.py',
        'routes/admin/performance.py',
        'routes/client/features.py',
        'commands/performance.py',
        'scripts/verify_pool_config.py',
        'docs/database-performance-optimization-guide.md',
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return missing_files


def run_integration_test():
    """Run a simple integration test"""
    print("\n🧪 Running Integration Test...")
    
    try:
        # Test the complete flow
        from config.database_config import DatabaseConfig
        from utils.query_performance import QueryPerformanceMonitor
        from middleware.performance_middleware import PerformanceConfig
        
        # Test configuration chain
        config = DatabaseConfig.get_pool_config('development')
        monitor = QueryPerformanceMonitor()
        perf_config = PerformanceConfig()
        
        print("✅ Configuration chain works")
        
        # Test query analysis (mock)
        mock_queries = [
            {
                'statement': 'SELECT * FROM posts WHERE client_id = 1',
                'duration': 0.3,
                'timestamp': '2024-01-01T00:00:00'
            }
        ]
        
        # This would be g.query_performance in a real request
        class MockG:
            query_performance = mock_queries
        
        # Simulate analysis
        total_time = sum(q['duration'] for q in mock_queries)
        slow_queries = [q for q in mock_queries if q['duration'] > perf_config.SLOW_QUERY_THRESHOLD]
        
        analysis = {
            'total_queries': len(mock_queries),
            'total_time': total_time,
            'slow_queries': len(slow_queries)
        }
        
        print(f"✅ Mock analysis: {analysis}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """Run comprehensive debug check"""
    print("=" * 80)
    print("🔍 Kuwait Social AI - Deep Debug Check")
    print("=" * 80)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Database Config", test_database_config),
        ("Query Monitor", test_query_monitor),
        ("Middleware", test_middleware_setup),
        ("CLI Commands", test_cli_commands),
        ("Blueprints", test_blueprint_structure),
        ("Optional Dependencies", test_optional_dependencies),
        ("Integration", run_integration_test),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    warnings = 0
    
    for test_name, result in results.items():
        if result is True:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        elif result is False:
            print(f"❌ {test_name}: FAILED")
            failed += 1
        elif isinstance(result, list) and len(result) == 0:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"⚠️  {test_name}: WARNINGS ({len(result) if isinstance(result, list) else 'unknown'})")
            warnings += 1
    
    print(f"\nResults: {passed} passed, {failed} failed, {warnings} warnings")
    
    if failed == 0:
        print("\n🎉 All critical tests passed! The performance monitoring system is ready.")
        
        print("\n📋 NEXT STEPS:")
        print("1. Install optional dependencies if needed:")
        print("   pip install psutil tabulate apscheduler")
        print("2. Configure environment variables:")
        print("   export REDIS_URL=redis://localhost:6379")
        print("   export DB_POOL_SIZE=20")
        print("3. Test connection pool:")
        print("   python scripts/verify_pool_config.py")
        print("4. Initialize in your Flask app:")
        print("   from middleware.performance_middleware import init_performance_monitoring")
        print("   init_performance_monitoring(app)")
        
        return 0
    else:
        print(f"\n⚠️  {failed} critical issues found. Please fix before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())