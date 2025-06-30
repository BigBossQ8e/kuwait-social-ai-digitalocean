#!/bin/bash

echo "🚀 Kuwait Social AI - Fresh Deployment"
echo "======================================"
echo ""

# Configuration
DOMAIN="kwtsocial.com"
SERVER_IP="209.38.176.129"
APP_DIR="/opt/kuwait-social-ai"

# 1. Create application directory
echo "📁 Creating application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# 2. Create .env file
echo "🔐 Creating environment configuration..."
cat > .env << 'EOF'
# Backend Environment Variables
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Database Configuration
DATABASE_URL=postgresql://kuwait_user:secure_password@db:5432/kuwait_social
DB_USER=kuwait_user
DB_PASSWORD=secure_password
DB_NAME=kuwait_social

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# CORS Configuration
CORS_ORIGINS=https://kwtsocial.com

# Frontend URL
FRONTEND_URL=https://kwtsocial.com
EOF

# 3. Create docker-compose.yml
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: kuwait-social-backend
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=wsgi.py
      - FLASK_ENV=production
    env_file:
      - .env
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/logs:/app/logs
    depends_on:
      - db
      - redis
    networks:
      - kuwait-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: kuwait-social-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=https://kwtsocial.com/api
    depends_on:
      - backend
    networks:
      - kuwait-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    container_name: kuwait-social-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=kuwait_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=kuwait_social
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - kuwait-network

  redis:
    image: redis:7-alpine
    container_name: kuwait-social-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - kuwait-network

volumes:
  postgres_data:
  redis_data:

networks:
  kuwait-network:
    driver: bridge
EOF

# 4. Create nginx configuration
echo "🔧 Creating nginx configuration..."
cat > /etc/nginx/sites-available/kwtsocial.com << 'EOF'
server {
    listen 80;
    server_name kwtsocial.com www.kwtsocial.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name kwtsocial.com www.kwtsocial.com;

    ssl_certificate /etc/letsencrypt/live/kwtsocial.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kwtsocial.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/kwtsocial.com /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "✅ Server preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Upload backend and frontend code to $APP_DIR"
echo "2. Update .env file with actual API keys"
echo "3. Run: docker-compose up -d"
echo "4. Initialize database: docker exec kuwait-social-backend flask db upgrade"
echo ""
echo "The server is ready for code deployment!"