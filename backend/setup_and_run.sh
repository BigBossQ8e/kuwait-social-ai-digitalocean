#!/bin/bash

echo "Kuwait Social AI - Complete Setup and Run Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "app_factory.py" ]; then
    print_error "Error: app_factory.py not found. Please run this script from the backend directory."
    exit 1
fi

# Step 1: Create virtual environment if it doesn't exist
echo ""
echo "Step 1: Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Created virtual environment"
else
    print_warning "Virtual environment already exists"
fi

# Step 2: Activate virtual environment
echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 3: Upgrade pip
echo ""
echo "Step 3: Upgrading pip..."
python -m pip install --upgrade pip
print_success "Pip upgraded"

# Step 4: Install dependencies
echo ""
echo "Step 4: Installing dependencies..."

# First install critical dependencies
pip install Flask SQLAlchemy Flask-SQLAlchemy Flask-JWT-Extended Flask-CORS python-dotenv
print_success "Installed core Flask dependencies"

# Install additional dependencies
pip install Flask-SocketIO Flask-Limiter redis psutil
print_success "Installed additional dependencies"

# Install from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
    print_success "Installed all requirements"
else
    print_warning "requirements.txt not found"
fi

# Step 5: Set up environment variables
echo ""
echo "Step 5: Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-$(openssl rand -hex 16)
JWT_SECRET_KEY=dev-jwt-secret-$(openssl rand -hex 16)

# Database
DATABASE_URL=postgresql://localhost/kuwait_social_ai

# Disable Telegram bot initially to avoid errors
DISABLE_TELEGRAM_BOT=1

# Server
PORT=5001
HOST=0.0.0.0

# Optional: Add your API keys here
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
EOF
    print_success "Created .env file with default settings"
else
    print_warning ".env file already exists"
fi

# Step 6: Check PostgreSQL
echo ""
echo "Step 6: Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    # Check if database exists
    if psql -lqt | cut -d \| -f 1 | grep -qw kuwait_social_ai; then
        print_success "Database 'kuwait_social_ai' exists"
    else
        print_warning "Database 'kuwait_social_ai' does not exist"
        echo "Creating database..."
        createdb kuwait_social_ai
        print_success "Created database 'kuwait_social_ai'"
    fi
else
    print_warning "PostgreSQL not found. Using SQLite instead."
    # Update .env to use SQLite
    sed -i '' 's|DATABASE_URL=.*|DATABASE_URL=sqlite:///kuwait_social_ai.db|' .env 2>/dev/null || \
    sed -i 's|DATABASE_URL=.*|DATABASE_URL=sqlite:///kuwait_social_ai.db|' .env
fi

# Step 7: Initialize database
echo ""
echo "Step 7: Initializing database..."
export FLASK_APP=app_factory:create_app
flask db init 2>/dev/null || print_warning "Database already initialized"
flask db migrate -m "Initial migration" 2>/dev/null || print_warning "Migration already exists"
flask db upgrade
print_success "Database initialized and migrated"

# Step 8: Create test admin user
echo ""
echo "Step 8: Creating test admin user..."
python create_test_admin.py 2>/dev/null || print_warning "Admin user might already exist"

# Step 9: Run tests
echo ""
echo "Step 9: Running health checks..."
python -c "
from app_factory import create_app
app = create_app('development')
with app.app_context():
    print('✅ App context created successfully')
"

# Step 10: Start the server
echo ""
echo "Step 10: Starting the server..."
echo ""
print_success "Setup complete! Starting Kuwait Social AI..."
echo ""
echo "Available endpoints:"
echo "  - Admin Panel Preview: http://localhost:5001/admin-preview"
echo "  - AI Services Panel: http://localhost:5001/admin-ai"
echo "  - Full Admin Panel: http://localhost:5001/admin-full"
echo "  - Health Check: http://localhost:5001/api/health"
echo "  - Detailed Health: http://localhost:5001/api/health/detailed"
echo ""
echo "Default admin credentials:"
echo "  Email: admin@example.com"
echo "  Password: password"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Start the Flask development server
python run.py 2>/dev/null || python app.py 2>/dev/null || flask run --host=0.0.0.0 --port=5001