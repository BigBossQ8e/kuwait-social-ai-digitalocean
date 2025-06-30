#!/bin/bash

echo "📦 Preparing Kuwait Social AI for Deployment"
echo "==========================================="
echo ""

# Create deployment directory
DEPLOY_DIR="/tmp/kuwait-social-deploy"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy backend
echo "📁 Preparing backend..."
cp -r backend $DEPLOY_DIR/
cd $DEPLOY_DIR/backend

# Remove unnecessary files
rm -rf venv __pycache__ .pytest_cache
rm -f *.pyc *.pyo *.db app_minimal.py test-imports.py validate_models.py
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Create Dockerfile for backend
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads instance

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:application"]
EOF

cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest

# Copy frontend
echo "📁 Preparing frontend..."
cp -r frontend-react $DEPLOY_DIR/frontend
cd $DEPLOY_DIR/frontend

# Remove node_modules and build artifacts
rm -rf node_modules dist .parcel-cache
rm -f package-lock.json

# Create optimized Dockerfile for frontend
cat > Dockerfile << 'EOF'
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1
EOF

# Create nginx.conf for frontend container
cat > nginx.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Create deployment archive
echo ""
echo "📦 Creating deployment archive..."
cd /tmp
tar -czf kuwait-social-deploy.tar.gz kuwait-social-deploy/

echo ""
echo "✅ Deployment package ready!"
echo "   Location: /tmp/kuwait-social-deploy.tar.gz"
echo "   Size: $(du -h /tmp/kuwait-social-deploy.tar.gz | cut -f1)"
echo ""
echo "Next: Upload to server and deploy"