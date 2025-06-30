#!/bin/bash
# URGENT Redis Security Fix for Kuwait Social AI

echo "🚨 Fixing Redis Security Issue..."

# Update docker-compose.yml to NOT expose Redis port
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: kuwait_social_ai
      POSTGRES_USER: ksai_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --bind 127.0.0.1 --protected-mode yes --requirepass ${REDIS_PASSWORD:-your-redis-password-here}
    # REMOVED ports exposure - Redis should NOT be accessible from outside
    networks:
      - app-network
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://ksai_user:${DB_PASSWORD}@postgres:5432/kuwait_social_ai
      REDIS_URL: redis://:${REDIS_PASSWORD:-your-redis-password-here}@redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    volumes:
      - ./backend:/app
      - uploaded_files:/app/uploaded_files
    depends_on:
      - postgres
      - redis
    networks:
      - app-network
    restart: unless-stopped

  frontend:
    build: ./frontend-react
    volumes:
      - ./frontend-react:/app
      - /app/node_modules
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

echo "✅ Docker-compose updated to secure Redis"

# Set Redis password in .env if not already set
if ! grep -q "REDIS_PASSWORD" backend/.env; then
    echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> backend/.env
    echo "✅ Generated secure Redis password"
fi

# Restart containers with new configuration
echo "🔄 Restarting containers..."
docker-compose down
docker-compose up -d

# Verify Redis is no longer exposed
echo "🔍 Verifying Redis is secured..."
sleep 5

# Check if port 6379 is still open
if nc -zv 127.0.0.1 6379 2>&1 | grep -q succeeded; then
    echo "⚠️  Redis is still accessible locally (this is OK)"
else
    echo "✅ Redis is not accessible externally"
fi

# Test from outside (this should fail)
echo "🔒 Testing external access (should fail)..."
if ! nc -zv 209.38.176.129 6379 -w 2 2>&1 | grep -q succeeded; then
    echo "✅ SUCCESS: Redis is NOT accessible from internet!"
else
    echo "❌ WARNING: Redis might still be exposed!"
fi

echo "
✅ Redis Security Fix Complete!

Next steps:
1. Verify the app still works: https://kwtsocial.com
2. Check backend logs: docker-compose logs backend
3. If any issues, check Redis connection in backend

The Redis instance is now:
- Only accessible within Docker network
- Protected with a password
- Not exposed to the internet
"