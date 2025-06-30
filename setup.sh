#!/bin/bash

# Kuwait Social AI - Smart Setup Script
# This script automatically configures all secrets and API keys

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to generate secure random strings
generate_secret() {
    openssl rand -hex 32
}

# Function to validate input
validate_input() {
    if [ -z "$1" ]; then
        return 1
    fi
    return 0
}

echo -e "${BLUE}🚀 Kuwait Social AI - Automated Setup${NC}"
echo -e "${BLUE}=====================================/${NC}"
echo ""

# Check if .env exists and ask for overwrite
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists.${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Setup cancelled.${NC}"
        exit 1
    fi
fi

# Create .env file from example
cp .env.example .env

echo -e "${GREEN}✓ Created .env file${NC}"
echo ""

# Auto-generate secrets
echo -e "${BLUE}🔐 Generating secure secrets...${NC}"
SECRET_KEY=$(generate_secret)
JWT_SECRET_KEY=$(generate_secret)
DB_PASSWORD=$(generate_secret | head -c 16)

# Update .env with generated secrets
sed -i.bak "s/your-secret-key-here/$SECRET_KEY/g" .env
sed -i.bak "s/your-jwt-secret-key-here/$JWT_SECRET_KEY/g" .env
sed -i.bak "s/secure_password_here/$DB_PASSWORD/g" .env

echo -e "${GREEN}✓ Generated secure SECRET_KEY${NC}"
echo -e "${GREEN}✓ Generated secure JWT_SECRET_KEY${NC}"
echo -e "${GREEN}✓ Generated secure database password${NC}"
echo ""

# Collect required information
echo -e "${BLUE}📝 Please provide the following information:${NC}"
echo ""

# OpenAI API Key
while true; do
    read -p "Enter your OpenAI API Key (required): " OPENAI_KEY
    if validate_input "$OPENAI_KEY"; then
        sed -i.bak "s/your-openai-api-key-here/$OPENAI_KEY/g" .env
        echo -e "${GREEN}✓ OpenAI API Key configured${NC}"
        break
    else
        echo -e "${RED}OpenAI API Key is required!${NC}"
    fi
done

# Domain configuration
echo ""
read -p "Enter your domain name (or press Enter to skip): " DOMAIN
if validate_input "$DOMAIN"; then
    sed -i.bak "s|https://yourdomain.com|https://$DOMAIN|g" .env
    echo -e "${GREEN}✓ Domain configured: $DOMAIN${NC}"
    
    # Update CORS origins with the actual domain
    sed -i.bak "s|http://localhost:3000,https://yourdomain.com|https://$DOMAIN|g" .env
    echo -e "${GREEN}✓ CORS origins configured for production${NC}"
else
    echo -e "${YELLOW}ℹ️  Using default domain configuration${NC}"
    # For local development, keep the default localhost CORS origins
    sed -i.bak "s|http://localhost:3000,https://yourdomain.com|http://localhost:3000,http://localhost:5173|g" .env
fi

# Email configuration (optional)
echo ""
read -p "Configure email settings? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Email address: " EMAIL
    read -p "Email password/app password: " -s EMAIL_PASS
    echo
    
    if validate_input "$EMAIL" && validate_input "$EMAIL_PASS"; then
        sed -i.bak "s/your-email@gmail.com/$EMAIL/g" .env
        sed -i.bak "s/your-app-password/$EMAIL_PASS/g" .env
        echo -e "${GREEN}✓ Email configuration complete${NC}"
    fi
fi

# Database configuration for DigitalOcean
echo ""
echo -e "${BLUE}🗄️  Database Configuration${NC}"
echo "Choose database option:"
echo "1) Use local PostgreSQL (Docker/Droplet)"
echo "2) Use DigitalOcean Managed Database"
read -p "Select option (1-2): " DB_OPTION

if [ "$DB_OPTION" = "2" ]; then
    echo ""
    echo "Enter your DigitalOcean database connection details:"
    read -p "Host: " DB_HOST
    read -p "Port (25060): " DB_PORT
    DB_PORT=${DB_PORT:-25060}
    read -p "Database name: " DB_NAME
    read -p "Username: " DB_USER
    read -p "Password: " -s DB_MANAGED_PASS
    echo
    
    # Construct connection URL for DigitalOcean with SSL
    DB_URL="postgresql://$DB_USER:$DB_MANAGED_PASS@$DB_HOST:$DB_PORT/$DB_NAME?sslmode=require"
    sed -i.bak "s|postgresql://user:password@localhost:5432/kuwait_social|$DB_URL|g" .env
    echo -e "${GREEN}✓ DigitalOcean Managed Database configured${NC}"
else
    # Use the auto-generated password for local database
    sed -i.bak "s|postgresql://user:password@localhost:5432/kuwait_social|postgresql://kuwait_user:$DB_PASSWORD@localhost:5432/kuwait_social|g" .env
    echo -e "${GREEN}✓ Local database configured${NC}"
fi

# Create frontend .env.production
echo ""
echo -e "${BLUE}⚛️  Configuring Frontend...${NC}"

# Determine API URL based on deployment type
if [ -n "$DOMAIN" ]; then
    VITE_API_URL="https://$DOMAIN/api"
else
    echo "Select frontend API configuration:"
    echo "1) DigitalOcean App Platform (uses \${APP_URL}/api)"
    echo "2) Droplet/VPS deployment (uses /api)"
    read -p "Select option (1-2): " API_OPTION
    
    if [ "$API_OPTION" = "1" ]; then
        VITE_API_URL="\${APP_URL}/api"
    else
        VITE_API_URL="/api"
    fi
fi

# Create frontend env file
cat > frontend-react/.env.production << EOF
# Production environment variables
VITE_API_URL=$VITE_API_URL
VITE_APP_NAME=Kuwait Social AI
VITE_APP_VERSION=1.0.0
EOF

echo -e "${GREEN}✓ Frontend configuration complete${NC}"

# Create deployment-specific configuration
echo ""
echo -e "${BLUE}🚀 Creating deployment configuration...${NC}"

# DigitalOcean App Platform spec
if [ -n "$DOMAIN" ]; then
    cat > .do/app.yaml << EOF
name: kuwait-social-ai
region: nyc
domains:
  - domain: $DOMAIN
    type: PRIMARY

services:
  - name: backend
    github:
      repo: your-github-username/your-repo-name
      branch: main
      deploy_on_push: true
    source_dir: backend
    dockerfile_path: backend/Dockerfile
    http_port: 5000
    routes:
      - path: /api
    envs:
      - key: DATABASE_URL
        type: SECRET
        value: "$DB_URL"
      - key: SECRET_KEY
        type: SECRET
        value: "$SECRET_KEY"
      - key: JWT_SECRET_KEY
        type: SECRET
        value: "$JWT_SECRET_KEY"
      - key: OPENAI_API_KEY
        type: SECRET
        value: "$OPENAI_KEY"
      - key: CORS_ORIGINS
        value: "https://$DOMAIN"
        scope: RUN_TIME
      - key: REDIS_URL
        value: \${redis.DATABASE_URL}
        scope: RUN_TIME
    
  - name: frontend
    github:
      repo: your-github-username/your-repo-name
      branch: main
      deploy_on_push: true
    source_dir: frontend-react
    dockerfile_path: frontend-react/Dockerfile.digitalocean
    http_port: 8080
    routes:
      - path: /
    envs:
      - key: VITE_API_URL
        value: \${APP_URL}/api
        scope: BUILD_TIME

databases:
  - name: redis
    engine: REDIS
    production: false
    cluster_name: kuwait-social-redis
EOF
    echo -e "${GREEN}✓ DigitalOcean App Platform spec created${NC}"
fi

# Create backup of original .env.example
cp .env.example .env.example.original

# Remove backup files
rm -f .env.bak

# Create init script for first-time setup
cat > init-app.sh << 'EOF'
#!/bin/bash
# Initialize the application after deployment

echo "🚀 Initializing Kuwait Social AI..."

# Run database migrations
cd backend
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
flask db upgrade

# Create admin user
python << END
from app_factory import create_app
from models import db, User
import os

app = create_app()
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@kuwaisocial.ai').first()
    if not admin:
        admin = User(
            email='admin@kuwaisocial.ai',
            role='admin',
            is_active=True
        )
        admin.set_password('ChangeMeFirst123!')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin@kuwaisocial.ai")
        print("⚠️  Default password: ChangeMeFirst123!")
        print("🔐 Please change this password immediately!")
    else:
        print("ℹ️  Admin user already exists")
END

deactivate
echo "✅ Initialization complete!"
EOF

chmod +x init-app.sh

# Create summary file
cat > DEPLOYMENT_SUMMARY.md << EOF
# Kuwait Social AI - Deployment Summary

## Generated Configuration

### Security Keys (Auto-generated)
- **SECRET_KEY**: ${SECRET_KEY:0:10}...
- **JWT_SECRET_KEY**: ${JWT_SECRET_KEY:0:10}...
- **DB_PASSWORD**: [SECURED]

### API Configuration
- **OpenAI API Key**: ${OPENAI_KEY:0:10}...

### Database
EOF

if [ "$DB_OPTION" = "2" ]; then
    echo "- **Type**: DigitalOcean Managed Database" >> DEPLOYMENT_SUMMARY.md
    echo "- **Host**: $DB_HOST" >> DEPLOYMENT_SUMMARY.md
else
    echo "- **Type**: Local PostgreSQL" >> DEPLOYMENT_SUMMARY.md
    echo "- **Connection**: localhost:5432" >> DEPLOYMENT_SUMMARY.md
fi

cat >> DEPLOYMENT_SUMMARY.md << EOF

### Domain
- **URL**: ${DOMAIN:-"Not configured"}
- **CORS Origins**: ${DOMAIN:+https://$DOMAIN}${DOMAIN:-"http://localhost:3000,http://localhost:5173"}

### Default Admin Credentials
- **Email**: admin@kuwaisocial.ai
- **Password**: ChangeMeFirst123!
- ⚠️ **IMPORTANT**: Change this password after first login!

## Next Steps

1. **Deploy to DigitalOcean**:
   \`\`\`bash
   git add .
   git commit -m "Configured for deployment"
   git push origin main
   \`\`\`

2. **After deployment, initialize the app**:
   \`\`\`bash
   ./init-app.sh
   \`\`\`

3. **For DigitalOcean App Platform**:
   - Update .do/app.yaml with your GitHub repo
   - Create app from DigitalOcean dashboard

4. **For Droplet deployment**:
   \`\`\`bash
   ./deploy.sh
   \`\`\`

## Security Checklist
- [ ] Change admin password
- [ ] Enable 2FA for admin accounts
- [ ] Configure firewall rules
- [ ] Set up SSL certificate
- [ ] Enable automated backups
- [ ] Configure monitoring alerts

## Important Files
- \`.env\` - Main configuration (DO NOT COMMIT)
- \`init-app.sh\` - First-time setup script
- \`deploy.sh\` - Deployment script
- \`.do/app.yaml\` - DigitalOcean App Platform spec
EOF

echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "- Configuration saved to .env"
echo "- Frontend config saved to frontend-react/.env.production"
echo "- Deployment summary saved to DEPLOYMENT_SUMMARY.md"
echo "- Initialization script created: init-app.sh"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "1. Review DEPLOYMENT_SUMMARY.md for your configuration"
echo "2. Keep your .env file secure and never commit it"
echo "3. Run ./init-app.sh after deployment to initialize the database"
echo "4. Change the default admin password immediately"
echo ""
echo -e "${GREEN}🚀 Ready for deployment to DigitalOcean!${NC}"