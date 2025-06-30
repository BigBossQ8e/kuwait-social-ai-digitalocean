#!/bin/bash

echo "🔍 Checking Software Versions and Updates"
echo "=========================================="
echo ""

# Check Python versions
echo "1. Python Versions:"
echo "-------------------"
echo -n "System Python 3: "
python3 --version 2>/dev/null || echo "Not installed"

echo -n "System Python: "
python --version 2>/dev/null || echo "Not installed"

echo -n "Latest Python 3 available: "
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew info python@3.12 2>/dev/null | grep "python@3.12:" | head -1 || echo "Check manually"
else
    apt-cache policy python3 2>/dev/null | grep Candidate || echo "Check manually"
fi

echo ""

# Check pip version
echo "2. Pip Versions:"
echo "----------------"
echo -n "System pip3: "
pip3 --version 2>/dev/null || echo "Not installed"

echo -n "Current pip in venv: "
if [ -f "backend/venv/bin/pip" ]; then
    backend/venv/bin/pip --version
else
    echo "Virtual environment not found"
fi

echo ""

# Check Node.js and npm
echo "3. Node.js and npm:"
echo "-------------------"
echo -n "Node.js: "
node --version 2>/dev/null || echo "Not installed"

echo -n "npm: "
npm --version 2>/dev/null || echo "Not installed"

echo -n "Latest Node.js LTS: "
curl -s https://nodejs.org/dist/index.json | grep '"lts"' | head -1 | grep -o 'v[0-9]*\.[0-9]*\.[0-9]*' || echo "Check manually"

echo ""

# Check Git
echo "4. Git Version:"
echo "---------------"
echo -n "Git: "
git --version 2>/dev/null || echo "Not installed"

echo ""

# Check Docker
echo "5. Docker Version:"
echo "------------------"
echo -n "Docker: "
docker --version 2>/dev/null || echo "Not installed"

echo -n "Docker Compose: "
docker-compose --version 2>/dev/null || docker compose version 2>/dev/null || echo "Not installed"

echo ""

# Check system updates (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "6. macOS System Info:"
    echo "---------------------"
    sw_vers
    echo ""
    
    echo "7. Homebrew Updates:"
    echo "--------------------"
    if command -v brew &> /dev/null; then
        echo "Checking outdated packages..."
        brew outdated | head -10 || echo "All packages up to date"
    else
        echo "Homebrew not installed"
    fi
fi

echo ""
echo "8. Python Packages in Backend Virtual Environment:"
echo "--------------------------------------------------"
if [ -f "backend/venv/bin/pip" ]; then
    echo "Checking for outdated packages..."
    backend/venv/bin/pip list --outdated 2>/dev/null | head -20 || echo "Unable to check"
else
    echo "Virtual environment not found"
fi

echo ""
echo "=========================================="
echo "📋 RECOMMENDATIONS:"
echo "=========================================="

# Python version check
python_version=$(python3 --version 2>&1 | grep -o '[0-9]*\.[0-9]*' | head -1)
if [[ $python_version < "3.9" ]]; then
    echo "⚠️  Python 3.9+ recommended (you have Python $python_version)"
else
    echo "✅ Python version is up to date"
fi

# Node.js version check
node_version=$(node --version 2>&1 | grep -o '[0-9]*' | head -1)
if [[ $node_version -lt 18 ]]; then
    echo "⚠️  Node.js 18+ recommended for latest features"
else
    echo "✅ Node.js version is acceptable"
fi

# pip update recommendation
echo ""
echo "To update pip in virtual environment:"
echo "  cd backend && source venv/bin/activate && pip install --upgrade pip"

echo ""
echo "To update all packages in virtual environment:"
echo "  cd backend && source venv/bin/activate && pip install --upgrade -r requirements.txt"