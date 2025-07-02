# 🔍 Flask Dependencies Check Guide

This guide helps you verify Flask dependencies on both local and production servers for Kuwait Social AI.

## 📋 Quick Commands

### 1. Local Dependency Check

```bash
# Quick visual check
python3 quick_dependency_check.py

# Detailed dependency analysis
python3 check_dependencies.py

# Verify requirements.txt matches installed
python3 verify_requirements.py
```

### 2. Remote/Production Check

```bash
# Check dependencies on production server
./check_remote_dependencies.sh

# Manual check via SSH
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221
cd /opt/kuwait-social-ai/backend
python3 -m pip list | grep -E "Flask|SQLAlchemy|openai|anthropic"
```

### 3. Compare Local vs Production

```bash
# This will automatically compare after running remote check
./check_remote_dependencies.sh
# Look for the "Dependency Comparison" section
```

## 🛠️ Common Dependency Issues & Solutions

### Issue 1: Flask Version Conflicts

**Symptom:** 
```
TypeError: Flask.__init__() got an unexpected keyword argument
```

**Solution:**
```bash
# Check Flask and Werkzeug versions
pip show Flask Werkzeug

# Fix: Ensure compatible versions
pip install Flask==3.0.0 Werkzeug==3.0.1
```

### Issue 2: Missing AI Dependencies

**Symptom:**
```
ModuleNotFoundError: No module named 'crewai'
```

**Solution:**
```bash
# For Python 3.10+
pip install crewai==0.100.0

# For Python 3.9 (limited features)
pip install langchain langchain-openai langchain-anthropic
```

### Issue 3: Database Connection Issues

**Symptom:**
```
OperationalError: could not connect to server
```

**Check:**
```bash
# Verify database packages
pip show psycopg2-binary SQLAlchemy

# Test connection
python3 -c "from app_factory import create_app; app = create_app(); print('DB OK')"
```

## 📊 Dependency Version Matrix

| Package | Min Version | Recommended | Python 3.9 | Python 3.10+ |
|---------|-------------|-------------|------------|--------------|
| Flask | 3.0.0 | 3.0.0 | ✅ | ✅ |
| SQLAlchemy | 2.0.0 | 2.0.23 | ✅ | ✅ |
| crewai | - | 0.100.0 | ❌ | ✅ |
| anthropic | 0.18.0 | 0.55.0 | ✅ | ✅ |
| openai | 1.0.0 | 1.93.0 | ✅ | ✅ |

## 🔄 Sync Dependencies Between Environments

### 1. Export from Local
```bash
# Create clean requirements
pip freeze > requirements.current.txt

# Or use pip-compile for deterministic builds
pip-compile requirements.in -o requirements.txt
```

### 2. Deploy to Production
```bash
# Use the sync script
./sync_to_production.sh

# Then on production
cd /opt/kuwait-social-ai/backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 3. Verify After Deployment
```bash
# Run remote check
./check_remote_dependencies.sh

# Check service
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
  "systemctl status kuwait-backend"
```

## 🎯 Best Practices

1. **Use Virtual Environments**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Pin Versions in Production**
   ```
   # Good
   Flask==3.0.0
   
   # Avoid in production
   Flask>=3.0.0
   ```

3. **Regular Updates**
   ```bash
   # Check outdated packages
   pip list --outdated
   
   # Update safely
   pip install --upgrade -r requirements.txt
   ```

4. **Test Before Deploying**
   ```bash
   # Always test locally first
   python3 wsgi.py
   curl http://localhost:5001/api/health
   ```

## 🚨 Emergency Fixes

### If Production is Down

1. **Quick Rollback**
   ```bash
   ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221
   cd /opt/kuwait-social-ai
   tar -xzf backup_[latest].tar.gz
   systemctl restart kuwait-backend
   ```

2. **Install Missing Critical Package**
   ```bash
   # On production
   cd /opt/kuwait-social-ai/backend
   source venv/bin/activate
   pip install Flask==3.0.0 Flask-SQLAlchemy==3.1.1
   systemctl restart kuwait-backend
   ```

3. **Check Logs**
   ```bash
   journalctl -u kuwait-backend -f
   tail -f /opt/kuwait-social-ai/backend/logs/kuwait-social-ai.log
   ```

## 📝 Report Files

The dependency check scripts create these files:

- `dependency_report_*.json` - Detailed local dependency analysis
- `production_dependency_report_*.json` - Production dependency analysis  
- `dependency_status.txt` - Quick status summary

Keep these for debugging and compliance purposes.

## 💡 Tips

1. Run dependency checks:
   - Before major deployments
   - After adding new packages
   - When debugging import errors
   - As part of CI/CD pipeline

2. For AI features, ensure:
   - Python 3.10+ on production
   - All AI packages installed
   - API keys configured in .env

3. Monitor for security updates:
   ```bash
   pip install pip-audit
   pip-audit
   ```

Remember: Always backup before updating dependencies in production!