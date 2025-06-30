#!/bin/bash

echo "🚀 Kuwait Social AI - Server Update Script"
echo "=========================================="
echo ""
echo "This script will update the hosting server with:"
echo "1. Node.js (LTS version)"
echo "2. PostgreSQL client"
echo "3. System security updates"
echo "4. Python packages in virtual environment"
echo ""
echo "Starting updates..."
echo ""

# 1. Apply system security updates first
echo "📦 Step 1: Applying system security updates..."
echo "---------------------------------------------"
sudo apt update
sudo apt upgrade -y

# 2. Install Node.js (LTS version)
echo ""
echo "📦 Step 2: Installing Node.js LTS..."
echo "------------------------------------"
# Using NodeSource repository for latest LTS
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# 3. Install PostgreSQL client
echo ""
echo "📦 Step 3: Installing PostgreSQL client..."
echo "-----------------------------------------"
sudo apt install -y postgresql-client

# Verify installation
echo "PostgreSQL client version: $(psql --version)"

# 4. Update Python packages in virtual environment
echo ""
echo "📦 Step 4: Updating Python packages..."
echo "-------------------------------------"

# Find the Kuwait Social AI directory
APP_DIR="/root/kuwait-social-ai"
if [ ! -d "$APP_DIR" ]; then
    APP_DIR="/opt/kuwait-social-ai"
fi
if [ ! -d "$APP_DIR" ]; then
    APP_DIR="/var/www/kuwait-social-ai"
fi

if [ -d "$APP_DIR/backend/venv" ]; then
    echo "Found virtual environment at: $APP_DIR/backend/venv"
    cd "$APP_DIR/backend"
    
    # Activate virtual environment and update pip first
    source venv/bin/activate
    pip install --upgrade pip
    
    # Update all packages while respecting requirements.txt
    pip install --upgrade -r requirements.txt
    
    echo "Python packages updated successfully"
else
    echo "⚠️  Warning: Could not find virtual environment"
    echo "   Please update Python packages manually"
fi

# 5. Clean up
echo ""
echo "📦 Step 5: Cleaning up..."
echo "------------------------"
sudo apt autoremove -y
sudo apt autoclean

# Final verification
echo ""
echo "✅ Update Summary:"
echo "=================="
echo "1. System updates: $(apt list --upgradable 2>/dev/null | wc -l) packages remaining"
echo "2. Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "3. npm: $(npm --version 2>/dev/null || echo 'Not installed')"
echo "4. PostgreSQL client: $(psql --version 2>/dev/null | cut -d' ' -f3 || echo 'Not installed')"
echo "5. Python: $(python3 --version)"
echo ""
echo "🎉 Server updates completed!"
echo ""
echo "⚠️  Important: You may need to restart services after these updates:"
echo "   - sudo systemctl restart nginx"
echo "   - sudo systemctl restart your-app-service (if using systemd)"
echo "   - Or restart Docker containers if using Docker"