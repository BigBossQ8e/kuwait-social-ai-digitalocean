#!/bin/bash

# Kuwait Social AI - DigitalOcean Deployment Script
# This script sets up the application on a fresh Ubuntu droplet

set -e

echo "🚀 Starting Kuwait Social AI deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3-pip python3-venv nodejs npm nginx postgresql postgresql-contrib redis-server git

# Install Docker and Docker Compose (optional)
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Setup PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
sudo -u postgres psql << EOF
CREATE DATABASE kuwait_social;
CREATE USER kuwait_user WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE kuwait_social TO kuwait_user;
EOF

# Setup backend
echo "🐍 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Copy and setup environment file
if [ ! -f .env ]; then
    cp ../.env.example .env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

# Run database migrations
flask db init || true
flask db migrate -m "Initial migration" || true
flask db upgrade || true

deactivate

# Setup frontend
echo "⚛️ Setting up frontend..."
cd ../frontend-react
npm install
npm run build

# Setup nginx
echo "🌐 Configuring nginx..."
sudo cp nginx.digitalocean.conf /etc/nginx/sites-available/kuwait-social
sudo ln -sf /etc/nginx/sites-available/kuwait-social /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Setup systemd service for backend
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/kuwait-social-backend.service > /dev/null << EOF
[Unit]
Description=Kuwait Social AI Backend
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)/../backend
Environment="PATH=$(pwd)/../backend/venv/bin"
ExecStart=$(pwd)/../backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable kuwait-social-backend
sudo systemctl start kuwait-social-backend

# Setup firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Create upload directories
mkdir -p ../backend/uploads
mkdir -p ../backend/instance

# Set permissions
sudo chown -R $USER:$USER ../backend/uploads
sudo chown -R $USER:$USER ../backend/instance

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file in the backend directory"
echo "2. Restart the backend: sudo systemctl restart kuwait-social-backend"
echo "3. Setup SSL certificate: sudo certbot --nginx -d yourdomain.com"
echo "4. Check service status: sudo systemctl status kuwait-social-backend"
echo "5. View logs: sudo journalctl -u kuwait-social-backend -f"
echo ""
echo "Your application should now be accessible at: http://your-server-ip"