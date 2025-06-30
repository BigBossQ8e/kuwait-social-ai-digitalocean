#!/bin/bash

# Kuwait Social AI - Deployment Validation Script
# Ensures everything is configured correctly for DigitalOcean

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validation results
ERRORS=0
WARNINGS=0

echo -e "${BLUE}🔍 Kuwait Social AI - Deployment Validator${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓ $1 exists${NC}"
        return 0
    else
        echo -e "${RED}✗ $1 is missing${NC}"
        ((ERRORS++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓ $1 directory exists${NC}"
        return 0
    else
        echo -e "${RED}✗ $1 directory is missing${NC}"
        ((ERRORS++))
        return 1
    fi
}

# Function to validate environment variable
check_env_var() {
    if grep -q "^$1=" .env 2>/dev/null; then
        VALUE=$(grep "^$1=" .env | cut -d'=' -f2)
        if [ -n "$VALUE" ] && [ "$VALUE" != "$2" ]; then
            echo -e "${GREEN}✓ $1 is configured${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ $1 needs to be configured${NC}"
            ((WARNINGS++))
            return 1
        fi
    else
        echo -e "${RED}✗ $1 is missing from .env${NC}"
        ((ERRORS++))
        return 1
    fi
}

# Function to check Python package
check_python_package() {
    if grep -q "^$1" backend/requirements.txt 2>/dev/null; then
        echo -e "${GREEN}✓ Python package $1 is included${NC}"
        return 0
    else
        echo -e "${RED}✗ Python package $1 is missing${NC}"
        ((ERRORS++))
        return 1
    fi
}

# Function to check npm package
check_npm_package() {
    if grep -q "\"$1\"" frontend-react/package.json 2>/dev/null; then
        echo -e "${GREEN}✓ NPM package $1 is included${NC}"
        return 0
    else
        echo -e "${RED}✗ NPM package $1 is missing${NC}"
        ((ERRORS++))
        return 1
    fi
}

echo -e "${BLUE}1. Checking directory structure...${NC}"
check_dir "backend"
check_dir "frontend-react"
check_dir "backend/routes"
check_dir "backend/models"
check_dir "backend/services"
check_dir "frontend-react/src"
echo ""

echo -e "${BLUE}2. Checking critical files...${NC}"
check_file ".env"
check_file "docker-compose.yml"
check_file "backend/requirements.txt"
check_file "backend/wsgi.py"
check_file "backend/Dockerfile"
check_file "frontend-react/package.json"
check_file "frontend-react/Dockerfile.digitalocean"
echo ""

echo -e "${BLUE}3. Checking environment configuration...${NC}"
if [ -f ".env" ]; then
    check_env_var "SECRET_KEY" "your-secret-key-here"
    check_env_var "JWT_SECRET_KEY" "your-jwt-secret-key-here"
    check_env_var "DATABASE_URL" "postgresql://user:password@localhost:5432/kuwait_social"
    check_env_var "OPENAI_API_KEY" "your-openai-api-key-here"
    check_env_var "FLASK_APP" ""
    check_env_var "FLASK_ENV" ""
else
    echo -e "${RED}✗ .env file not found. Run ./setup.sh first${NC}"
    ((ERRORS++))
fi
echo ""

echo -e "${BLUE}4. Checking Python dependencies...${NC}"
check_python_package "Flask"
check_python_package "gunicorn"
check_python_package "SQLAlchemy"
check_python_package "openai"
check_python_package "redis"
check_python_package "psycopg2-binary"
echo ""

echo -e "${BLUE}5. Checking frontend dependencies...${NC}"
check_npm_package "react"
check_npm_package "vite"
check_npm_package "@mui/material"
check_npm_package "recharts"
check_npm_package "@reduxjs/toolkit"
echo ""

echo -e "${BLUE}6. Checking DigitalOcean specific files...${NC}"
check_file ".do/app.yaml"
check_file "nginx.digitalocean.conf"
echo ""

echo -e "${BLUE}7. Validating Docker configuration...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    
    # Check if docker-compose.yml is valid
    if docker-compose config &> /dev/null; then
        echo -e "${GREEN}✓ docker-compose.yml is valid${NC}"
    else
        echo -e "${RED}✗ docker-compose.yml has errors${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠ Docker not installed (OK if deploying to App Platform)${NC}"
    ((WARNINGS++))
fi
echo ""

echo -e "${BLUE}8. Checking security configuration...${NC}"
if [ -f ".env" ]; then
    # Check if default passwords are still in use
    if grep -q "your-secret-key-here\|your-jwt-secret-key-here\|secure_password_here" .env; then
        echo -e "${RED}✗ Default secrets detected! Run ./setup.sh to generate secure values${NC}"
        ((ERRORS++))
    else
        echo -e "${GREEN}✓ Secrets appear to be configured${NC}"
    fi
fi

# Check file permissions
if [ -f "deploy.sh" ] && [ -x "deploy.sh" ]; then
    echo -e "${GREEN}✓ deploy.sh is executable${NC}"
else
    echo -e "${YELLOW}⚠ deploy.sh is not executable. Run: chmod +x deploy.sh${NC}"
    ((WARNINGS++))
fi
echo ""

echo -e "${BLUE}9. Checking API endpoints...${NC}"
if [ -f "backend/routes/health.py" ]; then
    echo -e "${GREEN}✓ Health check endpoint exists${NC}"
else
    echo -e "${YELLOW}⚠ Health check endpoint missing${NC}"
    ((WARNINGS++))
fi
echo ""

echo -e "${BLUE}10. Pre-deployment checklist...${NC}"
echo "Please confirm the following:"
echo "□ OpenAI API key is valid and has credits"
echo "□ Database credentials are correct"
echo "□ Domain name is configured (if using custom domain)"
echo "□ SSL certificate will be configured (for production)"
echo "□ Firewall rules are planned"
echo "□ Backup strategy is defined"
echo "□ Monitoring solution is chosen"
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}Validation Summary:${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for deployment.${NC}"
    EXIT_CODE=0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Validation passed with $WARNINGS warnings.${NC}"
    echo -e "${YELLOW}   Review warnings before deploying to production.${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ Validation failed with $ERRORS errors and $WARNINGS warnings.${NC}"
    echo -e "${RED}   Fix errors before deploying.${NC}"
    EXIT_CODE=1
fi

echo ""
echo -e "${BLUE}Next steps:${NC}"
if [ $ERRORS -eq 0 ]; then
    echo "1. Run ./setup.sh if you haven't already"
    echo "2. Review and customize configuration"
    echo "3. Deploy using one of these methods:"
    echo "   - DigitalOcean App Platform"
    echo "   - Docker Compose: docker-compose up -d"
    echo "   - Manual: ./deploy.sh"
else
    echo "1. Fix the errors listed above"
    echo "2. Run this validator again"
    echo "3. Once all checks pass, proceed with deployment"
fi

exit $EXIT_CODE