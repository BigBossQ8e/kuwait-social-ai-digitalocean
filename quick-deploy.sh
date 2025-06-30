#!/bin/bash
# Quick deployment script for DigitalOcean Droplet
# Run this after uploading files to your droplet

set -e

echo "🚀 Kuwait Social AI - Quick Droplet Deployment"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found!"
    echo "Make sure you're in the /root/kuwait-social-ai directory"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Upload your .env file from your local setup"
    exit 1
fi

echo -e "${BLUE}📦 Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

echo -e "${BLUE}📦 Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

echo -e "${BLUE}🔨 Building containers...${NC}"
docker-compose build

echo -e "${BLUE}🚀 Starting services...${NC}"
docker-compose up -d

echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 10

echo -e "${BLUE}🗄️ Running database migrations...${NC}"
docker-compose exec -T backend flask db upgrade || echo "⚠️  Migration failed - database might already be up to date"

echo -e "${BLUE}📊 Checking service status...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Your application should be available at:"
echo "- Frontend: http://$(curl -s ifconfig.me)"
echo "- API: http://$(curl -s ifconfig.me)/api"
echo ""
echo "Next steps:"
echo "1. Point your domain (kwtsocial.com) to IP: $(curl -s ifconfig.me)"
echo "2. Run: certbot --nginx -d kwtsocial.com (for HTTPS)"
echo "3. Check logs: docker-compose logs -f"
echo ""