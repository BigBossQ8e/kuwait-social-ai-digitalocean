# 🔧 Kuwait Social AI - Debugging and Testing Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Common Issues and Fixes](#common-issues-and-fixes)
3. [Local Development Testing](#local-development-testing)
4. [DigitalOcean Deployment Testing](#digitalocean-deployment-testing)
5. [API Testing](#api-testing)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the complete setup script
./setup_and_run.sh
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements-minimal.txt

# 3. Set environment variables
cp .env.example .env
# Edit .env with your settings

# 4. Initialize database
flask db upgrade

# 5. Run the application
python run.py
```

---

## 🐛 Common Issues and Fixes

### Issue 1: ModuleNotFoundError: No module named 'flask_socketio'
**Fix:**
```bash
pip install Flask-SocketIO
```

### Issue 2: Telegram Bot Initialization Errors
**Fix:**
```bash
# Disable Telegram bot temporarily
export DISABLE_TELEGRAM_BOT=1

# Or add to .env file:
echo "DISABLE_TELEGRAM_BOT=1" >> .env
```

### Issue 3: Database Connection Failed
**Fix for PostgreSQL:**
```bash
# Create database
createdb kuwait_social_ai

# Or use SQLite instead
export DATABASE_URL=sqlite:///kuwait_social_ai.db
```

### Issue 4: python-telegram-bot Version Mismatch
**Fix:**
```bash
# Upgrade to required version
pip install 'python-telegram-bot==22.2'

# Or downgrade code to v20 (if needed)
pip install 'python-telegram-bot==20.5'
```

---

## 🧪 Local Development Testing

### 1. Health Check Tests
```bash
# Basic health check
curl http://localhost:5001/api/health

# Detailed health check
curl http://localhost:5001/api/health/detailed

# Services status
curl http://localhost:5001/api/health/services
```

### 2. Run Comprehensive Tests
```bash
# Run the debugging script
python3 fix_telegram_and_debug.py

# Run API tests
python3 comprehensive_api_test.py

# Test specific endpoints
python3 test_endpoints.py
```

### 3. Test Admin Panel
Open in browser:
- Preview: http://localhost:5001/admin-preview
- AI Services: http://localhost:5001/admin-ai
- Full Panel: http://localhost:5001/admin-full

### 4. Database Tests
```python
# Test database connection
python3 -c "
from app_factory import create_app
from extensions import db
app = create_app('development')
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
```

---

## 🌊 DigitalOcean Deployment Testing

### 1. Pre-Deployment Checklist
```bash
# Run deployment check script
python3 check_digitalocean_deployment.py
```

### 2. Environment Setup
```bash
# SSH to your droplet
ssh root@your-droplet-ip

# Navigate to app directory
cd /var/www/kuwait-social-ai/backend

# Check environment variables
env | grep -E "(DATABASE_URL|REDIS_URL|SECRET_KEY)"

# Test database connection
python3 -c "import psycopg2; print('PostgreSQL connection OK')"
```

### 3. Service Status Checks
```bash
# Check all services
systemctl status postgresql
systemctl status redis
systemctl status nginx
systemctl status kuwait-social-ai  # Your app service

# Check logs
journalctl -u kuwait-social-ai -f
tail -f /var/log/nginx/error.log
```

### 4. Production Health Checks
```bash
# From your local machine
curl https://your-domain.com/api/health

# Check SSL certificate
curl -vI https://your-domain.com 2>&1 | grep -A 5 "SSL certificate"
```

---

## 🔍 API Testing

### 1. Authentication Test
```bash
# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Save the token
TOKEN="your-jwt-token-here"

# Test authenticated endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/admin/dashboard/overview
```

### 2. Platform Tests
```bash
# Get all platforms
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/admin/platforms

# Toggle platform
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_enabled":true}' \
  http://localhost:5001/api/admin/platforms/1/toggle
```

### 3. Load Testing
```bash
# Install Apache Bench
apt-get install apache2-utils  # Ubuntu/Debian
brew install apache-bench       # macOS

# Simple load test
ab -n 1000 -c 10 http://localhost:5001/api/health
```

---

## 🔧 Troubleshooting

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# In Flask app
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
```

### Check All Imports
```python
# test_imports.py
imports = [
    "from app_factory import create_app",
    "from models import db, User, Client",
    "from services.ai_service import AIService",
    "from extensions import jwt, limiter"
]

for imp in imports:
    try:
        exec(imp)
        print(f"✅ {imp}")
    except Exception as e:
        print(f"❌ {imp}: {e}")
```

### Database Debugging
```sql
-- Check all tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check migrations
SELECT * FROM alembic_version;

-- Check user count
SELECT COUNT(*) FROM users;
```

### Redis Debugging
```bash
# Test Redis connection
redis-cli ping

# Check Redis keys
redis-cli keys "*"

# Monitor Redis commands
redis-cli monitor
```

### Logs Location
- **Local Development**: `logs/kuwait-social-ai.log`
- **DigitalOcean**: `/var/log/kuwait-social-ai/app.log`
- **Nginx**: `/var/log/nginx/error.log`
- **PostgreSQL**: `/var/log/postgresql/postgresql-*.log`

---

## 📊 Performance Monitoring

### 1. Response Time Testing
```python
# test_performance.py
import time
import requests

endpoints = [
    '/api/health',
    '/api/admin/platforms',
    '/api/admin/features'
]

for endpoint in endpoints:
    start = time.time()
    r = requests.get(f'http://localhost:5001{endpoint}')
    elapsed = time.time() - start
    print(f"{endpoint}: {elapsed:.3f}s - Status: {r.status_code}")
```

### 2. Memory Usage
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep python | grep -v grep'

# Check detailed memory
python3 -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

---

## 🚨 Emergency Fixes

### Reset Everything
```bash
# Stop all services
pkill -f python
pkill -f gunicorn

# Clear cache
rm -rf __pycache__ */__pycache__ */*/__pycache__

# Reset database
dropdb kuwait_social_ai
createdb kuwait_social_ai
flask db upgrade

# Restart
./setup_and_run.sh
```

### Disable Problematic Features
```bash
# In .env file
DISABLE_TELEGRAM_BOT=1
DISABLE_REDIS=1
DISABLE_CELERY=1
```

---

## 📝 Testing Checklist

- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Database connected and migrated
- [ ] Environment variables set
- [ ] Health endpoints responding
- [ ] Admin panel accessible
- [ ] Authentication working
- [ ] API endpoints tested
- [ ] Logs showing no errors
- [ ] All services running

---

## 🆘 Getting Help

1. Check logs first: `tail -f logs/*.log`
2. Run debug script: `python3 fix_telegram_and_debug.py`
3. Check health status: `curl localhost:5001/api/health/detailed`
4. Review this guide section by section

Remember: Most issues are related to:
- Missing dependencies
- Database configuration
- Environment variables
- Port conflicts

---

Last updated: 2025-07-02