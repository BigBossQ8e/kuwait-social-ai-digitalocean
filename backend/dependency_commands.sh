#!/bin/bash

# Kuwait Social AI - Dependency Check Commands Quick Reference
# This script displays server-specific commands for dependency checking

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🔍 Kuwait Social AI - Dependency Check Commands${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Show current location
echo -e "${YELLOW}📍 Current Directory:${NC}"
echo "   $(pwd)"
echo ""

# Local server commands
echo -e "${GREEN}🖥️  LOCAL SERVER COMMANDS:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Navigate to backend:"
echo -e "   ${YELLOW}cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend${NC}"
echo ""
echo "Quick visual check:"
echo -e "   ${YELLOW}python3 quick_dependency_check.py${NC}"
echo ""
echo "Detailed analysis:"
echo -e "   ${YELLOW}python3 check_dependencies.py${NC}"
echo ""
echo "Verify requirements.txt:"
echo -e "   ${YELLOW}python3 verify_requirements.py${NC}"
echo ""
echo "Check Flask version:"
echo -e "   ${YELLOW}python3 -c 'import flask; print(f\"Flask: {flask.__version__}\")'${NC}"
echo ""

# Production server commands
echo -e "${GREEN}🌐 PRODUCTION SERVER COMMANDS:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Automated remote check (run from local):"
echo -e "   ${YELLOW}./check_remote_dependencies.sh${NC}"
echo ""
echo "SSH to production:"
echo -e "   ${YELLOW}ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221${NC}"
echo ""
echo "Production backend path:"
echo -e "   ${YELLOW}cd /opt/kuwait-social-ai/backend${NC}"
echo ""
echo "Check key packages on production:"
echo -e "   ${YELLOW}ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \\
   \"cd /opt/kuwait-social-ai/backend && python3 -m pip list | grep -E 'Flask|SQLAlchemy|openai'\"${NC}"
echo ""
echo "Check service status:"
echo -e "   ${YELLOW}ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \\
   \"systemctl status kuwait-backend --no-pager | head -10\"${NC}"
echo ""

# Quick actions
echo -e "${GREEN}⚡ QUICK ACTIONS:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1) Run local quick check"
echo "2) Run production check"
echo "3) Compare environments"
echo "4) Check Flask app import"
echo "5) Show this help"
echo "q) Quit"
echo ""

# Interactive menu
while true; do
    read -p "Select action (1-5, q): " choice
    case $choice in
        1)
            echo -e "\n${BLUE}Running local quick check...${NC}"
            python3 quick_dependency_check.py
            break
            ;;
        2)
            echo -e "\n${BLUE}Running production check...${NC}"
            ./check_remote_dependencies.sh
            break
            ;;
        3)
            echo -e "\n${BLUE}Comparing environments...${NC}"
            echo "This will run remote check and compare automatically..."
            ./check_remote_dependencies.sh
            break
            ;;
        4)
            echo -e "\n${BLUE}Checking Flask app import...${NC}"
            python3 -c "from app_factory import create_app; print('✅ Local: Flask app imports OK')" 2>&1
            ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
                "cd /opt/kuwait-social-ai/backend && python3 -c 'from app_factory import create_app; print(\"✅ Production: Flask app imports OK\")' 2>&1"
            break
            ;;
        5)
            # Just show help again
            $0
            break
            ;;
        q)
            echo -e "\n${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please select 1-5 or q${NC}"
            ;;
    esac
done

echo -e "\n${GREEN}✅ Done! For more details, see SERVER_SPECIFIC_DEPENDENCY_COMMANDS.md${NC}"