#!/bin/bash

echo "=== Fixing Backend Deployment ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai

echo "1. Checking if .env file exists..."
if [ ! -f backend/.env ]; then
    echo "Creating .env file from example..."
    cp backend/.env.example backend/.env 2>/dev/null || cat > backend/.env << 'ENV'
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this

# Database
DATABASE_URL=postgresql://postgres:postgres@kuwait-social-db:5432/kuwait_social_ai

# Redis
REDIS_URL=redis://kuwait-social-redis:6379

# API Keys
OPENAI_API_KEY=your-openai-api-key
GOOGLE_CLOUD_KEY=your-google-cloud-key

# Social Media
INSTAGRAM_CLIENT_ID=your-instagram-client-id
INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret
SNAPCHAT_CLIENT_ID=your-snapchat-client-id
SNAPCHAT_CLIENT_SECRET=your-snapchat-client-secret

# Payment Gateway
MYFATOORAH_API_KEY=your-myfatoorah-api-key
MYFATOORAH_BASE_URL=https://api.myfatoorah.com

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://209.38.176.129:8080,https://kwtsocial.com

# File Upload
MAX_CONTENT_LENGTH=10485760
UPLOAD_FOLDER=/app/uploads
ENV
fi

echo ""
echo "2. Generating secure keys..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update the keys in .env
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" backend/.env
sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" backend/.env

echo ""
echo "3. Fixing MAX_CONTENT_LENGTH type issue..."
# Ensure MAX_CONTENT_LENGTH is numeric
sed -i "s/MAX_CONTENT_LENGTH=.*/MAX_CONTENT_LENGTH=10485760/" backend/.env

echo ""
echo "4. Stopping backend container..."
docker stop kuwait-social-backend
docker rm kuwait-social-backend

echo ""
echo "5. Running backend with proper environment..."
docker run -d \
  --name kuwait-social-backend \
  --network kuwait-social-network \
  --network-alias backend \
  -p 5000:5000 \
  --env-file backend/.env \
  -v $(pwd)/backend/uploads:/app/uploads \
  --restart unless-stopped \
  kuwait-social-backend

echo ""
echo "6. Waiting for backend to start..."
sleep 10

echo ""
echo "7. Checking backend logs..."
docker logs kuwait-social-backend --tail=20

echo ""
echo "8. Running database migrations..."
docker exec kuwait-social-backend flask db upgrade

echo ""
echo "9. Testing backend..."
curl -s http://localhost:5000/api/health || echo "No health endpoint"
echo ""
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}' 2>/dev/null | python3 -m json.tool || echo "Login endpoint test"

echo ""
echo "=== Backend fix complete! ==="
EOF