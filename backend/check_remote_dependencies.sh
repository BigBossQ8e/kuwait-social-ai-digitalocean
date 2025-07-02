#!/bin/bash

# Kuwait Social AI - Remote Dependencies Checker
# This script checks dependencies on production server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Server details
SERVER="root@46.101.180.221"
SSH_KEY="$HOME/.ssh/kuwait-social-ai-1750866399"
REMOTE_PATH="/opt/kuwait-social-ai/backend"

echo "============================================"
echo "🔍 Remote Flask Dependencies Checker"
echo "============================================"
echo ""

# Function to run remote command
run_remote() {
    ssh -i "$SSH_KEY" "$SERVER" "$1"
}

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ SSH key not found at: $SSH_KEY${NC}"
    exit 1
fi

# Check Python version on remote
echo -e "${BLUE}🐍 Checking Python version on production...${NC}"
PYTHON_VERSION=$(run_remote "cd $REMOTE_PATH && python3 --version")
echo "Production Python: $PYTHON_VERSION"

# Check if virtual environment exists
echo -e "\n${BLUE}🔍 Checking for virtual environment...${NC}"
if run_remote "test -d $REMOTE_PATH/venv"; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    VENV_PYTHON="$REMOTE_PATH/venv/bin/python"
    PIP_CMD="$REMOTE_PATH/venv/bin/pip"
else
    echo -e "${YELLOW}⚠️  No virtual environment found - using system Python${NC}"
    VENV_PYTHON="python3"
    PIP_CMD="python3 -m pip"
fi

# Copy dependency checker to remote
echo -e "\n${BLUE}📤 Copying dependency checker to remote...${NC}"
scp -i "$SSH_KEY" check_dependencies.py "$SERVER:$REMOTE_PATH/"

# Run dependency check on remote
echo -e "\n${BLUE}🔍 Running dependency check on production...${NC}"
echo "============================================"
run_remote "cd $REMOTE_PATH && $VENV_PYTHON check_dependencies.py"

# Download the report
echo -e "\n${BLUE}📥 Downloading dependency report...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REMOTE_REPORT=$(run_remote "cd $REMOTE_PATH && ls -t dependency_report_*.json | head -1")
if [ ! -z "$REMOTE_REPORT" ]; then
    scp -i "$SSH_KEY" "$SERVER:$REMOTE_PATH/$REMOTE_REPORT" "./production_dependency_report_$TIMESTAMP.json"
    echo -e "${GREEN}✅ Report downloaded: production_dependency_report_$TIMESTAMP.json${NC}"
fi

# Compare with local
echo -e "\n${BLUE}📊 Comparing with local environment...${NC}"
echo "============================================"

# Run local check
echo "Running local dependency check..."
python3 check_dependencies.py > /dev/null 2>&1

# Create comparison script
cat > compare_dependencies.py << 'EOF'
import json
import sys

def load_report(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def compare_versions(local_report, prod_report):
    print("\n📊 Dependency Comparison: Local vs Production")
    print("=" * 60)
    
    # Compare Python versions
    local_py = local_report.get('python_version', 'Unknown')
    prod_py = prod_report.get('python_version', 'Unknown')
    
    print(f"\nPython Version:")
    print(f"  Local:      {local_py}")
    print(f"  Production: {prod_py}")
    if local_py != prod_py:
        print("  ⚠️  Python versions differ!")
    
    # Compare packages
    print("\n📦 Package Differences:")
    print("-" * 60)
    
    all_categories = set(local_report['checks'].keys()) | set(prod_report['checks'].keys())
    
    for category in sorted(all_categories):
        local_data = local_report['checks'].get(category, {})
        prod_data = prod_report['checks'].get(category, {})
        
        local_packages = {pkg.split('==')[0]: pkg.split('==')[1] for pkg in local_data.get('packages', []) if '==' in pkg}
        prod_packages = {pkg.split('==')[0]: pkg.split('==')[1] for pkg in prod_data.get('packages', []) if '==' in pkg}
        
        all_packages = set(local_packages.keys()) | set(prod_packages.keys())
        
        differences = []
        for pkg in sorted(all_packages):
            local_ver = local_packages.get(pkg, 'Not installed')
            prod_ver = prod_packages.get(pkg, 'Not installed')
            
            if local_ver != prod_ver:
                differences.append(f"  {pkg}: local={local_ver}, prod={prod_ver}")
        
        if differences:
            print(f"\n{category}:")
            for diff in differences:
                print(diff)

# Find latest reports
import glob
import os

local_reports = sorted(glob.glob("dependency_report_*.json"))
prod_reports = sorted(glob.glob("production_dependency_report_*.json"))

if local_reports and prod_reports:
    local_report = load_report(local_reports[-1])
    prod_report = load_report(prod_reports[-1])
    compare_versions(local_report, prod_report)
else:
    print("Error: Could not find reports to compare")
EOF

python3 compare_dependencies.py

# Check for critical issues
echo -e "\n${BLUE}🚨 Checking for critical issues...${NC}"
echo "============================================"

# Check Flask app startup
echo -e "\n${YELLOW}Testing Flask app startup on production...${NC}"
run_remote "cd $REMOTE_PATH && timeout 5 $VENV_PYTHON -c 'from app_factory import create_app; app = create_app(); print(\"✅ Flask app imports successfully\")' 2>&1" || echo -e "${RED}❌ Flask app import failed${NC}"

# Check service status
echo -e "\n${YELLOW}Checking service status...${NC}"
run_remote "systemctl status kuwait-backend --no-pager | head -10" || echo -e "${RED}Service not running${NC}"

# Clean up
rm -f compare_dependencies.py

echo -e "\n${GREEN}✅ Remote dependency check complete!${NC}"
echo ""
echo "💡 Next steps:"
echo "1. Review the comparison output above"
echo "2. Check production_dependency_report_*.json for details"
echo "3. Update requirements.txt if needed"
echo "4. Use sync_to_production.sh to deploy updates"