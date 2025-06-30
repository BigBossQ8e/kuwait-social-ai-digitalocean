#!/bin/bash
# URGENT: Fix Redis Security on Kuwait Social AI Server

cd /opt/kuwait-social-ai

# Backup current docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)

# Create secure docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: kuwait-social-db
    environment:
      POSTGRES_DB: kuwait_social_ai
      POSTGRES_USER: ksai_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"  # Only accessible locally
    networks:
      - app-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: kuwait-social-redis
    command: redis-server --bind 0.0.0.0 --protected-mode yes --requirepass ${REDIS_PASSWORD:-defaultRedisPass123}
    # NO PORTS EXPOSED - Redis only accessible within Docker network
    networks:
      - app-network
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: kuwait-social-backend
    environment:
      DATABASE_URL: postgresql://ksai_user:${DB_PASSWORD}@postgres:5432/kuwait_social_ai
      REDIS_URL: redis://:${REDIS_PASSWORD:-defaultRedisPass123}@redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    volumes:
      - ./backend:/app
      - uploaded_files:/app/uploaded_files
    ports:
      - "127.0.0.1:5000:5000"  # Only accessible locally (nginx will proxy)
    depends_on:
      - postgres
      - redis
    networks:
      - app-network
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: kuwait-social-frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "127.0.0.1:3000:80"  # Only accessible locally (nginx will proxy)
    environment:
      REACT_APP_API_URL: ${REACT_APP_API_URL:-http://localhost:5000}
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
  uploaded_files:
EOF

echo "Docker-compose.yml updated with secure configuration"

# Generate Redis password if not exists
if [ ! -f .env ] || ! grep -q "REDIS_PASSWORD" .env; then
    echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env
    echo "Generated secure Redis password"
fi

# Stop containers
docker-compose down

# Remove old Redis container completely
docker rm -f kuwait-social-redis

# Start with new secure configuration
docker-compose up -d

echo "Containers restarted with secure configuration"

# Wait for services to start
sleep 10

# Verify Redis is no longer exposed
echo "Verifying Redis security..."
if nc -zv 209.38.176.129 6379 -w 2 2>&1 | grep -q succeeded; then
    echo "WARNING: Redis might still be exposed!"
    echo "Check firewall rules: ufw status"
else
    echo "SUCCESS: Redis is NOT accessible from internet!"
fi

# Check if app is still working
curl -s -o /dev/null -w "%{http_code}" https://kwtsocial.com

echo "
COMPLETED! 

Next steps:
1. Test the website: https://kwtsocial.com
2. Check logs: docker-compose logs -f
3. Verify Redis connection: docker-compose exec backend python -c \"import redis; r=redis.from_url('redis://:${REDIS_PASSWORD:-defaultRedisPass123}@redis:6379/0'); print('Redis OK:', r.ping())\"
"
EOF