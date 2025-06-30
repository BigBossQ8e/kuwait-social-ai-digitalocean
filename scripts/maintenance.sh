#!/bin/bash
#
# Kuwait Social AI - Maintenance Script
# Common maintenance tasks for DigitalOcean deployment
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
show_menu() {
    echo -e "${BLUE}Kuwait Social AI - Maintenance Menu${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. View system status"
    echo "2. Restart services"
    echo "3. Update application"
    echo "4. View logs"
    echo "5. Run backup"
    echo "6. Clear cache"
    echo "7. Database maintenance"
    echo "8. Security check"
    echo "9. Performance tuning"
    echo "0. Exit"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

system_status() {
    echo -e "\n${YELLOW}System Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Droplet info
    if command -v doctl &> /dev/null; then
        DROPLET_ID=$(curl -s http://169.254.169.254/metadata/v1/id 2>/dev/null || echo "")
        if [[ ! -z "$DROPLET_ID" ]]; then
            echo -e "${BLUE}Droplet ID:${NC} $DROPLET_ID"
            echo -e "${BLUE}Graphs:${NC} https://cloud.digitalocean.com/droplets/$DROPLET_ID/graphs"
        fi
    fi
    
    # Services
    echo -e "\n${BLUE}Services:${NC}"
    docker-compose -f /opt/kuwait-social-ai/docker-compose.yml ps
    
    # Resources
    echo -e "\n${BLUE}Resources:${NC}"
    echo -n "CPU: "
    mpstat 1 1 | awk '/Average:/ {printf "%.1f%%\n", 100 - $NF}'
    echo -n "Memory: "
    free | grep Mem | awk '{printf "%.1f%% (%.1fGB/%.1fGB)\n", $3/$2 * 100, $3/1024/1024, $2/1024/1024}'
    echo -n "Disk: "
    df -h / | tail -1 | awk '{print $5 " used (" $3 "/" $2 ")"}'
    
    # Network
    echo -e "\n${BLUE}Network:${NC}"
    echo "Bandwidth this month: $(vnstat -m --oneline | cut -d';' -f11)"
    
    read -p "Press enter to continue..."
}

restart_services() {
    echo -e "\n${YELLOW}Restarting services...${NC}"
    
    cd /opt/kuwait-social-ai
    docker-compose restart
    systemctl restart nginx
    
    echo -e "${GREEN}✓ Services restarted${NC}"
    sleep 2
}

update_application() {
    echo -e "\n${YELLOW}Updating application...${NC}"
    
    # Backup first
    /opt/kuwait-social-ai/scripts/backup.sh
    
    cd /opt/kuwait-social-ai
    
    # Pull latest images
    docker-compose pull
    
    # Restart with new images
    docker-compose up -d
    
    echo -e "${GREEN}✓ Application updated${NC}"
    read -p "Press enter to continue..."
}

view_logs() {
    echo -e "\n${YELLOW}Select log to view:${NC}"
    echo "1. Application logs"
    echo "2. Nginx access logs"
    echo "3. Nginx error logs"
    echo "4. System logs"
    echo "5. Docker logs"
    
    read -p "Choice: " log_choice
    
    case $log_choice in
        1) docker-compose -f /opt/kuwait-social-ai/docker-compose.yml logs -f --tail=100 ;;
        2) tail -f /var/log/nginx/access.log ;;
        3) tail -f /var/log/nginx/error.log ;;
        4) journalctl -f ;;
        5) docker logs -f --tail=100 $(docker ps -q | head -1) ;;
        *) echo "Invalid choice" ;;
    esac
}

run_backup() {
    echo -e "\n${YELLOW}Running backup...${NC}"
    /opt/kuwait-social-ai/scripts/backup.sh
    read -p "Press enter to continue..."
}

clear_cache() {
    echo -e "\n${YELLOW}Clearing cache...${NC}"
    
    # Clear Redis cache
    docker exec kuwait_social_ai_redis redis-cli FLUSHDB
    
    # Clear nginx cache if configured
    rm -rf /var/cache/nginx/*
    
    # Restart services
    docker-compose -f /opt/kuwait-social-ai/docker-compose.yml restart backend
    systemctl restart nginx
    
    echo -e "${GREEN}✓ Cache cleared${NC}"
    read -p "Press enter to continue..."
}

database_maintenance() {
    echo -e "\n${YELLOW}Database Maintenance${NC}"
    echo "1. Run VACUUM"
    echo "2. Reindex tables"
    echo "3. Analyze statistics"
    echo "4. Check connections"
    echo "5. Back to main menu"
    
    read -p "Choice: " db_choice
    
    case $db_choice in
        1) 
            docker exec kuwait_social_ai_postgres psql -U kuwait_user -d kuwait_social_ai -c "VACUUM ANALYZE;"
            echo -e "${GREEN}✓ VACUUM completed${NC}"
            ;;
        2)
            docker exec kuwait_social_ai_postgres psql -U kuwait_user -d kuwait_social_ai -c "REINDEX DATABASE kuwait_social_ai;"
            echo -e "${GREEN}✓ Reindex completed${NC}"
            ;;
        3)
            docker exec kuwait_social_ai_postgres psql -U kuwait_user -d kuwait_social_ai -c "ANALYZE;"
            echo -e "${GREEN}✓ Analyze completed${NC}"
            ;;
        4)
            docker exec kuwait_social_ai_postgres psql -U kuwait_user -d kuwait_social_ai -c "SELECT pid, usename, application_name, client_addr, state FROM pg_stat_activity;"
            ;;
    esac
    
    read -p "Press enter to continue..."
}

security_check() {
    echo -e "\n${YELLOW}Security Check${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check firewall
    echo -e "${BLUE}Firewall status:${NC}"
    ufw status numbered
    
    # Check fail2ban
    echo -e "\n${BLUE}Fail2ban status:${NC}"
    fail2ban-client status sshd
    
    # Check SSL
    echo -e "\n${BLUE}SSL certificate:${NC}"
    /opt/kuwait-social-ai/monitoring/check-ssl.sh
    
    # Check for updates
    echo -e "\n${BLUE}Security updates:${NC}"
    apt list --upgradable 2>/dev/null | grep -i security || echo "No security updates available"
    
    # Check running processes
    echo -e "\n${BLUE}Unusual processes:${NC}"
    ps aux | grep -v "root\|postgres\|redis\|docker\|nginx" | head -10
    
    read -p "Press enter to continue..."
}

performance_tuning() {
    echo -e "\n${YELLOW}Performance Tuning${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Current settings
    echo -e "${BLUE}Current settings:${NC}"
    echo "Swappiness: $(cat /proc/sys/vm/swappiness)"
    echo "Max connections: $(docker exec kuwait_social_ai_postgres psql -U kuwait_user -t -c "SHOW max_connections;" 2>/dev/null || echo "N/A")"
    
    echo -e "\n${BLUE}Recommendations:${NC}"
    
    # Check if swap exists
    if ! swapon -s | grep -q swap; then
        echo "⚠ No swap configured. Consider adding 4GB swap:"
        echo "  fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile"
    fi
    
    # Check nginx workers
    CORES=$(nproc)
    WORKERS=$(grep "worker_processes" /etc/nginx/nginx.conf | awk '{print $2}' | tr -d ';')
    if [ "$WORKERS" != "$CORES" ] && [ "$WORKERS" != "auto" ]; then
        echo "⚠ Nginx workers ($WORKERS) doesn't match CPU cores ($CORES)"
    fi
    
    read -p "Press enter to continue..."
}

# Main loop
while true; do
    clear
    show_menu
    read -p "Enter choice: " choice
    
    case $choice in
        1) system_status ;;
        2) restart_services ;;
        3) update_application ;;
        4) view_logs ;;
        5) run_backup ;;
        6) clear_cache ;;
        7) database_maintenance ;;
        8) security_check ;;
        9) performance_tuning ;;
        0) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid choice"; sleep 1 ;;
    esac
done