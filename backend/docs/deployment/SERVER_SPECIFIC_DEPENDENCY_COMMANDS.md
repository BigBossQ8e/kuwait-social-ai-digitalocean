# 🔍 Server-Specific Dependency Check Commands

This guide provides exact commands for checking dependencies on each server environment.

## 📍 Server Details

### Local Development Server
- **Path**: `/Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend`
- **Python**: System Python 3.9.6 or venv Python 3.11
- **Environment**: Development/Testing

### Production Server (DigitalOcean)
- **Server**: `root@46.101.180.221`
- **Path**: `/opt/kuwait-social-ai/backend`
- **Python**: Python 3.10.12
- **Environment**: Production
- **Domain**: kwtsocial.com

---

## 🖥️ LOCAL SERVER COMMANDS

### 1. Navigate to Backend Directory
```bash
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend
```

### 2. Quick Visual Check
```bash
# From backend directory
python3 quick_dependency_check.py

# Or with full path
python3 /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend/quick_dependency_check.py
```

**Expected Output:**
- Color-coded table showing package status
- ✅ Green = Installed and OK
- ❌ Red = Missing required package
- ⚠️ Yellow = Outdated or optional

### 3. Detailed Dependency Analysis
```bash
# From backend directory
python3 check_dependencies.py

# Or with full path
python3 /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend/check_dependencies.py
```

**Output Files Created:**
- `dependency_report_[timestamp].json` in backend directory
- Contains full package list with versions

### 4. Verify Requirements.txt
```bash
# From backend directory
python3 verify_requirements.py

# Or with full path
python3 /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend/verify_requirements.py
```

**What it checks:**
- Compares requirements.txt with installed packages
- Shows missing packages
- Shows version mismatches

### 5. Check with Virtual Environment (if exists)
```bash
# If using Python 3.11 venv
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend
source venv/bin/activate
python quick_dependency_check.py
python check_dependencies.py
python verify_requirements.py
deactivate
```

---

## 🌐 PRODUCTION SERVER COMMANDS

### Method 1: Automated Remote Check (From Local Machine)

```bash
# Navigate to backend directory first
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend

# Run remote check script
./check_remote_dependencies.sh
```

**What this does:**
1. SSHs to production server
2. Copies dependency checker to server
3. Runs checks on production
4. Downloads report back to local
5. Compares local vs production

### Method 2: Manual SSH Check

```bash
# SSH to production server
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221

# Navigate to backend directory
cd /opt/kuwait-social-ai/backend

# Quick Python and pip check
python3 --version
python3 -m pip --version

# List key packages
python3 -m pip list | grep -E "Flask|SQLAlchemy|openai|anthropic|langchain|crewai"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
    python --version
    pip list | grep -E "Flask|SQLAlchemy|openai|anthropic"
    deactivate
else
    echo "❌ No virtual environment"
fi

# Exit SSH
exit
```

### Method 3: Copy and Run Scripts on Production

```bash
# From local machine - copy scripts to production
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend

# Copy dependency check scripts
scp -i ~/.ssh/kuwait-social-ai-1750866399 \
    check_dependencies.py \
    quick_dependency_check.py \
    verify_requirements.py \
    root@46.101.180.221:/opt/kuwait-social-ai/backend/

# SSH to production and run
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221

cd /opt/kuwait-social-ai/backend

# Run with system Python
python3 quick_dependency_check.py
python3 check_dependencies.py
python3 verify_requirements.py

# Or with venv if it exists
source venv/bin/activate
python quick_dependency_check.py
python check_dependencies.py
python verify_requirements.py
deactivate

# Download reports back to local
exit

# From local machine
scp -i ~/.ssh/kuwait-social-ai-1750866399 \
    root@46.101.180.221:/opt/kuwait-social-ai/backend/dependency_report_*.json \
    ./production_reports/
```

---

## 📊 COMPARING ENVIRONMENTS

### Quick Comparison Commands

```bash
# From local backend directory
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend

# Run this to get both local and remote reports
./check_remote_dependencies.sh

# The script automatically compares and shows differences
```

### Manual Comparison

```bash
# 1. Get local package list
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend
pip freeze > local_packages.txt

# 2. Get production package list
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
    "cd /opt/kuwait-social-ai/backend && python3 -m pip freeze" > production_packages.txt

# 3. Compare
diff local_packages.txt production_packages.txt

# Or use a visual diff tool
# On Mac:
opendiff local_packages.txt production_packages.txt
```

---

## 🚨 TROUBLESHOOTING COMMANDS

### If Scripts Don't Run on Production

```bash
# Check Python version
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
    "python3 --version"

# Install missing tabulate (needed for visual output)
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
    "cd /opt/kuwait-social-ai/backend && python3 -m pip install tabulate"

# Check if scripts have execute permission
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
    "cd /opt/kuwait-social-ai/backend && ls -la *.py | grep check"
```

### Quick Package Install on Production

```bash
# Install a specific package on production
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
    "cd /opt/kuwait-social-ai/backend && source venv/bin/activate && pip install package_name"

# Install from requirements.txt
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
    "cd /opt/kuwait-social-ai/backend && source venv/bin/activate && pip install -r requirements.txt"
```

---

## 📋 One-Line Commands for Quick Checks

### Local Quick Status
```bash
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend && python3 quick_dependency_check.py | grep "Summary" -A 5
```

### Production Flask Version
```bash
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 "cd /opt/kuwait-social-ai/backend && python3 -c 'import flask; print(f\"Flask version: {flask.__version__}\")'"
```

### Check if App Starts on Production
```bash
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 "cd /opt/kuwait-social-ai/backend && python3 -c 'from app_factory import create_app; print(\"✅ App imports OK\")' 2>&1"
```

### Service Status
```bash
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 "systemctl status kuwait-backend --no-pager | head -5"
```

---

## 💾 Output File Locations

### Local Files Created:
```
/Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend/
├── dependency_report_[timestamp].json
├── dependency_status.txt
├── local_packages.txt (if you run pip freeze)
└── production_dependency_report_[timestamp].json (after remote check)
```

### Production Files Created:
```
/opt/kuwait-social-ai/backend/
├── dependency_report_[timestamp].json
├── dependency_status.txt
└── check_dependencies.py (if copied)
```

---

## 🎯 Quick Reference Card

| Task | Local Command | Production Command |
|------|--------------|-------------------|
| Quick Check | `python3 quick_dependency_check.py` | `./check_remote_dependencies.sh` |
| Full Analysis | `python3 check_dependencies.py` | SSH + `python3 check_dependencies.py` |
| Verify Requirements | `python3 verify_requirements.py` | SSH + `python3 verify_requirements.py` |
| Compare Environments | `./check_remote_dependencies.sh` | (Runs from local) |
| Check Flask Version | `python3 -c 'import flask; print(flask.__version__)'` | SSH + same command |
| List All Packages | `pip freeze` | SSH + `pip freeze` |

Remember: Always run from the backend directory for correct results!