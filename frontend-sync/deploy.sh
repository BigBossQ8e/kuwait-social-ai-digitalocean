#!/bin/bash

# Deployment script for Kuwait Social AI React Frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="kuwait-social-frontend"
IMAGE_NAME="kuwait-social-ai/frontend"
CONTAINER_NAME="kuwait-social-frontend"
PORT=${PORT:-3000}
ENV=${ENV:-production}
API_URL=${API_URL:-"http://localhost:5000"}

echo -e "${BLUE}🚀 Kuwait Social AI Frontend Deployment Script${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose not found. Using 'docker compose' instead."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Parse command line arguments
case "$1" in
    "build")
        print_info "Building Docker image..."
        docker build -t ${IMAGE_NAME}:latest -t ${IMAGE_NAME}:$(date +%Y%m%d-%H%M%S) .
        print_status "Docker image built successfully"
        ;;
    
    "dev")
        print_info "Starting development environment..."
        npm install
        npm run dev
        ;;
    
    "start")
        print_info "Starting production container..."
        
        # Stop existing container
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        
        # Build and start new container
        docker build -t ${IMAGE_NAME}:latest .
        docker run -d \
            --name ${CONTAINER_NAME} \
            -p ${PORT}:80 \
            -e API_URL=${API_URL} \
            -e APP_ENV=${ENV} \
            -e APP_VERSION=$(date +%Y%m%d-%H%M%S) \
            --restart unless-stopped \
            ${IMAGE_NAME}:latest
        
        print_status "Container started on port ${PORT}"
        print_info "Application URL: http://localhost:${PORT}"
        ;;
    
    "stop")
        print_info "Stopping container..."
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        print_status "Container stopped"
        ;;
    
    "restart")
        print_info "Restarting container..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    "logs")
        print_info "Showing container logs..."
        docker logs -f ${CONTAINER_NAME}
        ;;
    
    "compose-up")
        print_info "Starting full stack with Docker Compose..."
        ${DOCKER_COMPOSE} up -d
        print_status "Full stack started"
        print_info "Frontend: http://localhost:3000"
        print_info "Backend API: http://localhost:5000"
        ;;
    
    "compose-down")
        print_info "Stopping full stack..."
        ${DOCKER_COMPOSE} down
        print_status "Full stack stopped"
        ;;
    
    "deploy-prod")
        print_info "Deploying to production..."
        
        # Build optimized image
        docker build -t ${IMAGE_NAME}:latest -t ${IMAGE_NAME}:prod-$(date +%Y%m%d-%H%M%S) .
        
        # Stop and remove old container
        docker stop ${CONTAINER_NAME}-prod 2>/dev/null || true
        docker rm ${CONTAINER_NAME}-prod 2>/dev/null || true
        
        # Start production container
        docker run -d \
            --name ${CONTAINER_NAME}-prod \
            -p 80:80 \
            -e API_URL=${API_URL} \
            -e APP_ENV=production \
            -e APP_VERSION=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") \
            --restart unless-stopped \
            --memory="512m" \
            --cpus="1.0" \
            ${IMAGE_NAME}:latest
        
        print_status "Production deployment completed"
        print_info "Application URL: http://localhost"
        ;;
    
    "health")
        print_info "Checking container health..."
        if docker exec ${CONTAINER_NAME} curl -f http://localhost/health &>/dev/null; then
            print_status "Container is healthy"
        else
            print_error "Container is not healthy"
            exit 1
        fi
        ;;
    
    "clean")
        print_info "Cleaning up Docker artifacts..."
        docker system prune -f
        docker image prune -f
        print_status "Cleanup completed"
        ;;
    
    "backup")
        print_info "Creating backup..."
        BACKUP_NAME="kuwait-social-frontend-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        tar -czf ${BACKUP_NAME} \
            --exclude=node_modules \
            --exclude=dist \
            --exclude=.git \
            .
        print_status "Backup created: ${BACKUP_NAME}"
        ;;
    
    *)
        echo -e "${BLUE}Usage: $0 {command}${NC}"
        echo ""
        echo -e "${YELLOW}Available commands:${NC}"
        echo "  build         - Build Docker image"
        echo "  dev           - Start development server"
        echo "  start         - Start production container"
        echo "  stop          - Stop container"
        echo "  restart       - Restart container"
        echo "  logs          - Show container logs"
        echo "  compose-up    - Start full stack with Docker Compose"
        echo "  compose-down  - Stop full stack"
        echo "  deploy-prod   - Deploy to production"
        echo "  health        - Check container health"
        echo "  clean         - Clean up Docker artifacts"
        echo "  backup        - Create backup"
        echo ""
        echo -e "${YELLOW}Environment variables:${NC}"
        echo "  PORT          - Port to run on (default: 3000)"
        echo "  ENV           - Environment (default: production)"
        echo "  API_URL       - Backend API URL (default: http://localhost:5000)"
        echo ""
        echo -e "${YELLOW}Examples:${NC}"
        echo "  ./deploy.sh dev"
        echo "  PORT=8080 ./deploy.sh start"
        echo "  API_URL=https://api.example.com ./deploy.sh deploy-prod"
        exit 1
        ;;
esac