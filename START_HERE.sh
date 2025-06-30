#!/bin/bash

# Kuwait Social AI - Master Deployment Script
# Start here for automated DigitalOcean deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║          🚀 KUWAIT SOCIAL AI PLATFORM 🚀              ║"
echo "║                                                       ║"
echo "║          Automated DigitalOcean Deployment            ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Function to show menu
show_menu() {
    echo -e "${BLUE}Please select an option:${NC}"
    echo ""
    echo "1) 🆕 First-time setup (Configure everything)"
    echo "2) 🔍 Validate deployment readiness"
    echo "3) 🐳 Deploy with Docker Compose"
    echo "4) 📦 Deploy to DigitalOcean App Platform"
    echo "5) 🖥️  Deploy to DigitalOcean Droplet"
    echo "6) 🔒 Configure security settings"
    echo "7) 📚 View deployment guide"
    echo "8) 🚪 Exit"
    echo ""
}

# Function to pause
pause() {
    echo ""
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-8): " choice
    echo ""
    
    case $choice in
        1)
            echo -e "${GREEN}Starting first-time setup...${NC}"
            if [ -f "./setup.sh" ]; then
                ./setup.sh
            else
                echo -e "${RED}Error: setup.sh not found${NC}"
            fi
            pause
            ;;
            
        2)
            echo -e "${GREEN}Validating deployment...${NC}"
            if [ -f "./validate-deployment.sh" ]; then
                ./validate-deployment.sh
            else
                echo -e "${RED}Error: validate-deployment.sh not found${NC}"
            fi
            pause
            ;;
            
        3)
            echo -e "${GREEN}Deploying with Docker Compose...${NC}"
            echo ""
            
            # Check if setup is complete
            if [ ! -f ".env" ]; then
                echo -e "${YELLOW}⚠️  No .env file found. Running setup first...${NC}"
                ./setup.sh
            fi
            
            echo -e "${BLUE}Building and starting containers...${NC}"
            docker-compose up -d --build
            
            echo ""
            echo -e "${GREEN}✅ Deployment complete!${NC}"
            echo ""
            echo "Services running:"
            docker-compose ps
            echo ""
            echo -e "${BLUE}Access your application:${NC}"
            echo "- Frontend: http://localhost"
            echo "- Backend API: http://localhost:5000"
            echo ""
            echo -e "${YELLOW}Initialize the database:${NC}"
            echo "docker-compose exec backend flask db upgrade"
            echo ""
            pause
            ;;
            
        4)
            echo -e "${GREEN}Deploying to DigitalOcean App Platform...${NC}"
            echo ""
            echo -e "${BLUE}Prerequisites:${NC}"
            echo "1. Push your code to GitHub"
            echo "2. Have a DigitalOcean account"
            echo ""
            echo -e "${BLUE}Steps:${NC}"
            echo "1. Go to https://cloud.digitalocean.com/apps"
            echo "2. Click 'Create App'"
            echo "3. Connect your GitHub repository"
            echo "4. Use the generated .do/app.yaml specification"
            echo ""
            echo -e "${YELLOW}Your app.yaml is located at: .do/app.yaml${NC}"
            echo ""
            if [ -f ".do/app.yaml" ]; then
                echo "Preview of your app.yaml:"
                head -20 .do/app.yaml
                echo "..."
            fi
            pause
            ;;
            
        5)
            echo -e "${GREEN}Deploying to DigitalOcean Droplet...${NC}"
            echo ""
            
            if [ ! -f ".env" ]; then
                echo -e "${YELLOW}⚠️  No .env file found. Running setup first...${NC}"
                ./setup.sh
            fi
            
            echo -e "${BLUE}This will install on a Ubuntu droplet${NC}"
            echo ""
            echo "Requirements:"
            echo "- Ubuntu 22.04 LTS droplet"
            echo "- At least 2GB RAM"
            echo "- SSH access to the droplet"
            echo ""
            read -p "Have you created a droplet? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                read -p "Enter your droplet IP: " DROPLET_IP
                echo ""
                echo -e "${BLUE}Commands to run on your droplet:${NC}"
                echo ""
                echo "# 1. SSH into your droplet"
                echo "ssh root@$DROPLET_IP"
                echo ""
                echo "# 2. Clone and setup"
                echo "git clone <your-repo-url> kuwait-social-ai"
                echo "cd kuwait-social-ai"
                echo "chmod +x deploy.sh"
                echo "./deploy.sh"
                echo ""
                echo -e "${YELLOW}The deploy.sh script will:${NC}"
                echo "- Install all dependencies"
                echo "- Configure PostgreSQL"
                echo "- Setup Python environment"
                echo "- Build React frontend"
                echo "- Configure nginx"
                echo "- Create systemd services"
                echo "- Setup firewall"
            fi
            pause
            ;;
            
        6)
            echo -e "${GREEN}Configuring security settings...${NC}"
            if [ -f "./secure-config.sh" ]; then
                ./secure-config.sh
                echo ""
                echo -e "${GREEN}✅ Security configurations created!${NC}"
                echo ""
                echo "Don't forget to:"
                echo "1. Review the generated security settings"
                echo "2. Run ./setup-firewall.sh on your server"
                echo "3. Set up the cron jobs for monitoring"
                echo "4. Configure SSL certificate for HTTPS"
            else
                echo -e "${RED}Error: secure-config.sh not found${NC}"
            fi
            pause
            ;;
            
        7)
            echo -e "${GREEN}Opening deployment guide...${NC}"
            echo ""
            if [ -f "DEPLOY_GUIDE.md" ]; then
                less DEPLOY_GUIDE.md
            else
                echo "Quick deployment options:"
                echo ""
                echo "1. App Platform: Push to GitHub → Create app on DO"
                echo "2. Docker: Run 'docker-compose up -d'"
                echo "3. Manual: Run './deploy.sh' on Ubuntu server"
                echo ""
                echo "See DEPLOY_GUIDE.md for detailed instructions"
            fi
            pause
            ;;
            
        8)
            echo -e "${GREEN}Thank you for using Kuwait Social AI!${NC}"
            echo ""
            echo "Documentation:"
            echo "- README.md - Overview"
            echo "- DEPLOY_GUIDE.md - Deployment instructions"
            echo "- DEPLOYMENT_SUMMARY.md - Your configuration"
            echo ""
            echo -e "${CYAN}Good luck with your deployment! 🚀${NC}"
            echo ""
            exit 0
            ;;
            
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            pause
            ;;
    esac
    
    clear
done