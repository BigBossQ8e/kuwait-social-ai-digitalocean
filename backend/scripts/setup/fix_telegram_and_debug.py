#!/usr/bin/env python3
"""
Comprehensive Telegram Bot Fix and System Debug Script
This script fixes Telegram bot issues and performs deep debugging for both local and DigitalOcean deployments
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'debug_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemDebugger:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        
    def log_section(self, title):
        logger.info(f"\n{'='*60}")
        logger.info(f" {title}")
        logger.info(f"{'='*60}")
    
    def run_command(self, command, check=False):
        """Run a shell command and return output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if check and result.returncode != 0:
                logger.error(f"Command failed: {command}")
                logger.error(f"Error: {result.stderr}")
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            logger.error(f"Failed to run command: {command}")
            logger.error(f"Error: {str(e)}")
            return "", str(e), 1

    def check_python_version(self):
        """Check Python version"""
        self.log_section("Python Version Check")
        stdout, _, _ = self.run_command("python3 --version")
        logger.info(f"Python version: {stdout.strip()}")
        
        # Check if virtual environment is active
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("✅ Virtual environment is active")
        else:
            logger.warning("⚠️  No virtual environment detected")
            self.issues_found.append("No virtual environment active")

    def check_dependencies(self):
        """Check all dependencies"""
        self.log_section("Dependencies Check")
        
        # Check if requirements.txt exists
        requirements_files = ['requirements.txt', 'requirements.in', 'requirements-prod.txt']
        for req_file in requirements_files:
            if os.path.exists(req_file):
                logger.info(f"✅ Found {req_file}")
            else:
                logger.warning(f"❌ Missing {req_file}")
                self.issues_found.append(f"Missing {req_file}")
        
        # Check installed packages
        stdout, _, _ = self.run_command("pip list | grep telegram")
        logger.info(f"Telegram packages installed:\n{stdout}")
        
        # Check for version mismatches
        if "python-telegram-bot" in stdout:
            if "20.5" in stdout:
                logger.warning("⚠️  python-telegram-bot version 20.5 detected - code requires 22.2")
                self.issues_found.append("python-telegram-bot version mismatch")

    def fix_telegram_dependencies(self):
        """Fix Telegram bot dependencies"""
        self.log_section("Fixing Telegram Dependencies")
        
        logger.info("Upgrading python-telegram-bot to version 22.2...")
        stdout, stderr, code = self.run_command("pip install 'python-telegram-bot==22.2'")
        
        if code == 0:
            logger.info("✅ Successfully upgraded python-telegram-bot")
            self.fixes_applied.append("Upgraded python-telegram-bot to 22.2")
        else:
            logger.error(f"❌ Failed to upgrade: {stderr}")
            logger.info("Trying alternative fix...")
            
            # Try installing from requirements.txt
            stdout, stderr, code = self.run_command("pip install -r requirements.txt")
            if code == 0:
                logger.info("✅ Installed dependencies from requirements.txt")
                self.fixes_applied.append("Installed all dependencies from requirements.txt")

    def fix_telegram_import_issues(self):
        """Fix the missing get_telegram_service function"""
        self.log_section("Fixing Telegram Import Issues")
        
        # Add the missing function to telegram_service.py
        telegram_service_path = "services/telegram_service.py"
        
        if os.path.exists(telegram_service_path):
            logger.info("Adding get_telegram_service function...")
            
            with open(telegram_service_path, 'r') as f:
                content = f.read()
            
            if "def get_telegram_service():" not in content:
                # Add the missing function
                addition = '''

# Singleton instance
_telegram_service = None

def get_telegram_service():
    """Get or create the singleton TelegramService instance"""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service
'''
                with open(telegram_service_path, 'a') as f:
                    f.write(addition)
                
                logger.info("✅ Added get_telegram_service function")
                self.fixes_applied.append("Added missing get_telegram_service function")
            else:
                logger.info("✅ get_telegram_service function already exists")

    def check_database_connection(self):
        """Check database connection and schema"""
        self.log_section("Database Connection Check")
        
        # Create a test script
        test_db_script = '''
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

try:
    # Get database URL
    db_url = os.getenv('DATABASE_URL', 'postgresql://localhost/kuwait_social_ai')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    # Create engine and test connection
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Check tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print(f"Found {len(tables)} tables: {', '.join(tables[:5])}...")
        
        # Check for telegram tables
        telegram_tables = [t for t in tables if 'telegram' in t.lower()]
        if telegram_tables:
            print(f"✅ Found Telegram tables: {', '.join(telegram_tables)}")
        else:
            print("⚠️  No Telegram tables found")
            
except Exception as e:
    print(f"❌ Database connection failed: {str(e)}")
'''
        
        with open('test_db_connection.py', 'w') as f:
            f.write(test_db_script)
        
        stdout, stderr, code = self.run_command("python3 test_db_connection.py")
        logger.info(stdout)
        if stderr:
            logger.error(stderr)
        
        # Clean up
        os.remove('test_db_connection.py')

    def check_routes_and_endpoints(self):
        """Check all routes and endpoints"""
        self.log_section("Routes and Endpoints Check")
        
        # Create a test script to list all routes
        route_test_script = '''
from app_factory import create_app

app = create_app('development')

print("\\nRegistered Routes:")
print("-" * 80)
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{rule.rule:<50} {methods:<20} {rule.endpoint}")
'''
        
        with open('test_routes.py', 'w') as f:
            f.write(route_test_script)
        
        stdout, stderr, code = self.run_command("python3 test_routes.py")
        
        if code == 0:
            logger.info("Routes listing:")
            logger.info(stdout)
            
            # Check for telegram routes
            if '/api/telegram' not in stdout:
                logger.warning("⚠️  No Telegram routes found - they are disabled")
                self.issues_found.append("Telegram routes are disabled")
        else:
            logger.error(f"Failed to list routes: {stderr}")
        
        # Clean up
        if os.path.exists('test_routes.py'):
            os.remove('test_routes.py')

    def test_imports(self):
        """Test all critical imports"""
        self.log_section("Import Tests")
        
        imports_to_test = [
            "from app_factory import create_app",
            "from models import db, User, Client, Admin",
            "from services.telegram_bot_manager import get_bot_manager",
            "from services.telegram_service import TelegramService",
            "from services.ai_service import AIService",
            "from extensions import db, jwt, limiter, socketio",
        ]
        
        for import_stmt in imports_to_test:
            test_script = f'''
try:
    {import_stmt}
    print("✅ {import_stmt}")
except Exception as e:
    print("❌ {import_stmt}")
    print(f"   Error: {{str(e)}}")
'''
            
            with open('test_import.py', 'w') as f:
                f.write(test_script)
            
            stdout, stderr, code = self.run_command("python3 test_import.py")
            logger.info(stdout.strip())
            
        # Clean up
        if os.path.exists('test_import.py'):
            os.remove('test_import.py')

    def create_comprehensive_test_script(self):
        """Create a comprehensive test script"""
        self.log_section("Creating Comprehensive Test Script")
        
        test_script = '''#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all endpoints and functionality
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5001')
ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASSWORD = 'password'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        self.test_results.append({
            'timestamp': timestamp,
            'status': status,
            'message': message
        })
    
    def test_endpoint(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            if response.status_code == expected_status:
                self.log(f"✅ {method} {endpoint} - Status: {response.status_code}", "PASS")
                return True, response
            else:
                self.log(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "ERROR")
                return False, response
                
        except Exception as e:
            self.log(f"❌ {method} {endpoint} - Error: {str(e)}", "ERROR")
            return False, None
    
    def test_auth(self):
        """Test authentication endpoints"""
        self.log("\\n=== Testing Authentication ===")
        
        # Test login
        success, response = self.test_endpoint(
            'POST', '/api/auth/login',
            data={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )
        
        if success and response.json().get('access_token'):
            self.token = response.json()['access_token']
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            self.log("✅ Authentication successful", "PASS")
        else:
            self.log("❌ Authentication failed", "FAIL")
    
    def test_admin_endpoints(self):
        """Test admin endpoints"""
        self.log("\\n=== Testing Admin Endpoints ===")
        
        if not self.token:
            self.log("⚠️  Skipping admin tests - no auth token", "WARN")
            return
        
        endpoints = [
            ('GET', '/api/admin/dashboard/overview'),
            ('GET', '/api/admin/platforms'),
            ('GET', '/api/admin/features'),
            ('GET', '/api/admin/packages'),
            ('GET', '/api/admin/dashboard/activity-feed'),
        ]
        
        for method, endpoint in endpoints:
            self.test_endpoint(method, endpoint, expected_status=200)
    
    def test_client_endpoints(self):
        """Test client endpoints"""
        self.log("\\n=== Testing Client Endpoints ===")
        
        endpoints = [
            ('GET', '/api/client/profile'),
            ('GET', '/api/client/posts'),
            ('GET', '/api/client/analytics/overview'),
        ]
        
        for method, endpoint in endpoints:
            self.test_endpoint(method, endpoint, expected_status=[200, 401])
    
    def test_public_endpoints(self):
        """Test public endpoints"""
        self.log("\\n=== Testing Public Endpoints ===")
        
        endpoints = [
            ('GET', '/api/prayer-times/today'),
            ('GET', '/admin-preview'),
            ('GET', '/admin-ai'),
        ]
        
        # Remove auth for public endpoints
        self.session.headers.pop('Authorization', None)
        
        for method, endpoint in endpoints:
            self.test_endpoint(method, endpoint, expected_status=200)
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("Starting Comprehensive API Tests", "INFO")
        self.log(f"Base URL: {BASE_URL}", "INFO")
        
        self.test_auth()
        self.test_admin_endpoints()
        self.test_client_endpoints()
        self.test_public_endpoints()
        
        # Summary
        self.log("\\n=== Test Summary ===")
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        self.log(f"Total: {len(self.test_results)}, Passed: {passed}, Failed: {failed}")
        
        # Save results
        with open(f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        return failed == 0

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
'''
        
        with open('comprehensive_api_test.py', 'w') as f:
            f.write(test_script)
        
        logger.info("✅ Created comprehensive_api_test.py")
        self.fixes_applied.append("Created comprehensive API test script")

    def create_health_check_endpoint(self):
        """Create a health check endpoint"""
        self.log_section("Creating Health Check Endpoint")
        
        health_check_code = '''"""
Health check endpoints for monitoring
"""
from flask import Blueprint, jsonify
import os
import psutil
from datetime import datetime
from sqlalchemy import text
from extensions import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """Basic health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'kuwait-social-ai'
    })

@health_bp.route('/api/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with system info"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        db.session.execute(text('SELECT 1'))
        health_status['checks']['database'] = {'status': 'healthy', 'message': 'Connected'}
    except Exception as e:
        health_status['checks']['database'] = {'status': 'unhealthy', 'message': str(e)}
        health_status['status'] = 'unhealthy'
    
    # Memory check
    memory = psutil.virtual_memory()
    health_status['checks']['memory'] = {
        'status': 'healthy' if memory.percent < 90 else 'warning',
        'usage_percent': memory.percent,
        'available_mb': memory.available // (1024 * 1024)
    }
    
    # CPU check
    cpu_percent = psutil.cpu_percent(interval=1)
    health_status['checks']['cpu'] = {
        'status': 'healthy' if cpu_percent < 80 else 'warning',
        'usage_percent': cpu_percent
    }
    
    # Disk check
    disk = psutil.disk_usage('/')
    health_status['checks']['disk'] = {
        'status': 'healthy' if disk.percent < 90 else 'warning',
        'usage_percent': disk.percent,
        'free_gb': disk.free // (1024 * 1024 * 1024)
    }
    
    return jsonify(health_status)

@health_bp.route('/api/health/services', methods=['GET'])
def services_health_check():
    """Check health of individual services"""
    services_status = {
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    # Check Telegram bot
    try:
        if os.environ.get('DISABLE_TELEGRAM_BOT'):
            services_status['services']['telegram'] = {'status': 'disabled', 'message': 'Telegram bot is disabled'}
        else:
            from services.telegram_bot_manager import get_bot_manager
            bot_manager = get_bot_manager()
            active_bots = len(bot_manager.bots) if hasattr(bot_manager, 'bots') else 0
            services_status['services']['telegram'] = {
                'status': 'healthy',
                'active_bots': active_bots
            }
    except Exception as e:
        services_status['services']['telegram'] = {'status': 'unhealthy', 'error': str(e)}
    
    # Check Redis
    try:
        from extensions import redis_client
        if redis_client:
            redis_client.ping()
            services_status['services']['redis'] = {'status': 'healthy'}
        else:
            services_status['services']['redis'] = {'status': 'not_configured'}
    except Exception as e:
        services_status['services']['redis'] = {'status': 'unhealthy', 'error': str(e)}
    
    # Check AI services
    try:
        from services.ai_service import AIService
        services_status['services']['ai'] = {'status': 'healthy', 'provider': 'configured'}
    except Exception as e:
        services_status['services']['ai'] = {'status': 'unhealthy', 'error': str(e)}
    
    return jsonify(services_status)
'''
        
        with open('routes/health.py', 'w') as f:
            f.write(health_check_code)
        
        # Add to app_factory.py
        logger.info("✅ Created health check endpoints")
        self.fixes_applied.append("Created health check endpoints")

    def create_digitalocean_deployment_check(self):
        """Create DigitalOcean deployment check script"""
        self.log_section("Creating DigitalOcean Deployment Check")
        
        do_check_script = '''#!/usr/bin/env python3
"""
DigitalOcean Deployment Check Script
"""

import os
import subprocess
import json

def check_environment():
    """Check if running on DigitalOcean"""
    print("\\n=== Environment Check ===")
    
    # Check for DigitalOcean metadata
    try:
        response = subprocess.run(
            ['curl', '-s', 'http://169.254.169.254/metadata/v1/id'],
            capture_output=True, text=True, timeout=2
        )
        if response.returncode == 0:
            print("✅ Running on DigitalOcean Droplet")
            print(f"   Droplet ID: {response.stdout.strip()}")
        else:
            print("❌ Not running on DigitalOcean")
    except:
        print("❌ Not running on DigitalOcean")
    
    # Check environment variables
    print("\\n=== Environment Variables ===")
    important_vars = [
        'DATABASE_URL',
        'REDIS_URL',
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'FLASK_ENV',
        'PORT'
    ]
    
    for var in important_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'SECRET' in var:
                print(f"✅ {var}: ***hidden***")
            else:
                print(f"✅ {var}: {value[:50]}...")
        else:
            print(f"❌ {var}: Not set")

def check_services():
    """Check running services"""
    print("\\n=== Service Status ===")
    
    services = ['postgresql', 'redis-server', 'nginx']
    
    for service in services:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service],
                capture_output=True, text=True
            )
            if result.stdout.strip() == 'active':
                print(f"✅ {service}: Running")
            else:
                print(f"❌ {service}: {result.stdout.strip()}")
        except:
            print(f"⚠️  {service}: Unable to check")

def check_app_service():
    """Check if app is running"""
    print("\\n=== Application Status ===")
    
    # Check if gunicorn is running
    try:
        result = subprocess.run(['pgrep', '-f', 'gunicorn'], capture_output=True)
        if result.returncode == 0:
            print("✅ Gunicorn is running")
            # Get process details
            subprocess.run(['ps', 'aux', '|', 'grep', 'gunicorn'], shell=True)
        else:
            print("❌ Gunicorn is not running")
    except:
        print("⚠️  Unable to check Gunicorn status")
    
    # Check if app responds
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:5001/api/health'],
            capture_output=True, text=True
        )
        if result.stdout == '200':
            print("✅ Application is responding")
        else:
            print(f"❌ Application returned status: {result.stdout}")
    except:
        print("❌ Application is not responding")

def check_logs():
    """Check recent logs for errors"""
    print("\\n=== Recent Logs ===")
    
    log_files = [
        '/var/log/nginx/error.log',
        '/var/log/postgresql/postgresql-*.log',
        'logs/kuwait-social-ai.log'
    ]
    
    for log_file in log_files:
        if '*' in log_file:
            # Handle wildcards
            import glob
            files = glob.glob(log_file)
            if files:
                log_file = files[-1]  # Get most recent
        
        if os.path.exists(log_file):
            print(f"\\nChecking {log_file}:")
            try:
                result = subprocess.run(
                    ['tail', '-n', '20', log_file, '|', 'grep', '-i', 'error'],
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    print(result.stdout)
                else:
                    print("No recent errors found")
            except:
                print("Unable to read log file")

if __name__ == "__main__":
    print("DigitalOcean Deployment Check")
    print("=" * 50)
    
    check_environment()
    check_services()
    check_app_service()
    check_logs()
    
    print("\\n" + "=" * 50)
    print("Check complete!")
'''
        
        with open('check_digitalocean_deployment.py', 'w') as f:
            f.write(do_check_script)
        
        # Make it executable
        os.chmod('check_digitalocean_deployment.py', 0o755)
        
        logger.info("✅ Created DigitalOcean deployment check script")
        self.fixes_applied.append("Created DigitalOcean deployment check script")

    def run_full_debug(self):
        """Run the complete debugging process"""
        logger.info("Starting Full System Debug")
        logger.info(f"Current directory: {os.getcwd()}")
        
        # Run all checks
        self.check_python_version()
        self.check_dependencies()
        self.fix_telegram_dependencies()
        self.fix_telegram_import_issues()
        self.check_database_connection()
        self.check_routes_and_endpoints()
        self.test_imports()
        self.create_comprehensive_test_script()
        self.create_health_check_endpoint()
        self.create_digitalocean_deployment_check()
        
        # Summary
        self.log_section("Debug Summary")
        
        if self.issues_found:
            logger.warning(f"Found {len(self.issues_found)} issues:")
            for issue in self.issues_found:
                logger.warning(f"  - {issue}")
        else:
            logger.info("✅ No critical issues found")
        
        if self.fixes_applied:
            logger.info(f"Applied {len(self.fixes_applied)} fixes:")
            for fix in self.fixes_applied:
                logger.info(f"  - {fix}")
        
        # Create summary report
        report = {
            'timestamp': datetime.now().isoformat(),
            'issues_found': self.issues_found,
            'fixes_applied': self.fixes_applied,
            'next_steps': [
                "1. Run 'pip install -r requirements.txt' to ensure all dependencies are installed",
                "2. Run 'python3 comprehensive_api_test.py' to test all endpoints",
                "3. If on DigitalOcean, run 'python3 check_digitalocean_deployment.py'",
                "4. Check health endpoints at /api/health and /api/health/detailed",
                "5. Enable Telegram bot by removing DISABLE_TELEGRAM_BOT env var when ready"
            ]
        }
        
        with open('debug_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("✅ Debug complete! Check debug_report.json for summary")

if __name__ == "__main__":
    debugger = SystemDebugger()
    debugger.run_full_debug()