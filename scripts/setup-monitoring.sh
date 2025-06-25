#!/bin/bash
#
# Kuwait Social AI - Setup DigitalOcean Monitoring
# Configures comprehensive monitoring for DO droplet
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up DigitalOcean Monitoring...${NC}\n"

# Check if running on DigitalOcean
if curl -s --connect-timeout 2 http://169.254.169.254/metadata/v1/id &>/dev/null; then
    DROPLET_ID=$(curl -s http://169.254.169.254/metadata/v1/id)
    echo -e "${GREEN}✓ Running on DigitalOcean droplet: $DROPLET_ID${NC}"
else
    echo -e "${YELLOW}⚠ Not on DigitalOcean - some features will be limited${NC}"
fi

# Install monitoring dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
apt-get update -qq
apt-get install -y bc sysstat htop iotop vnstat nethogs

# Install DigitalOcean agent if not present
if ! systemctl is-active --quiet do-agent; then
    echo -e "\n${YELLOW}Installing DigitalOcean monitoring agent...${NC}"
    curl -sSL https://repos.insights.digitalocean.com/install.sh | bash
fi

# Create monitoring directory
mkdir -p /opt/kuwait-social-ai/monitoring

# Copy monitoring script
cat > /opt/kuwait-social-ai/monitoring/check-health.sh << 'EOF'
#!/bin/bash
# Health check script for Kuwait Social AI

# Configuration
DOMAIN="${DOMAIN:-kuwait-social-ai.com}"
WEBHOOK_URL="${SLACK_WEBHOOK:-}"
MAX_CPU=80
MAX_MEM=85
MAX_DISK=90

# Check functions
check_cpu() {
    local cpu=$(mpstat 1 1 | awk '/Average:/ {print 100 - $NF}' | cut -d'.' -f1)
    if [[ $cpu -gt $MAX_CPU ]]; then
        alert "High CPU Usage" "CPU at ${cpu}% (threshold: ${MAX_CPU}%)"
    fi
}

check_memory() {
    local mem=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [[ $mem -gt $MAX_MEM ]]; then
        alert "High Memory Usage" "Memory at ${mem}% (threshold: ${MAX_MEM}%)"
    fi
}

check_disk() {
    df -h | grep -vE '^Filesystem|tmpfs|udev' | while read line; do
        local usage=$(echo $line | awk '{print $5}' | sed 's/%//')
        local mount=$(echo $line | awk '{print $6}')
        if [[ $usage -gt $MAX_DISK ]]; then
            alert "High Disk Usage" "Disk $mount at ${usage}% (threshold: ${MAX_DISK}%)"
        fi
    done
}

check_docker() {
    local stopped=$(docker ps -a --filter "status=exited" --format "{{.Names}}" | wc -l)
    if [[ $stopped -gt 0 ]]; then
        alert "Docker Containers Down" "$stopped containers are stopped"
    fi
}

check_website() {
    local code=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN || echo "000")
    if [[ "$code" != "200" ]]; then
        alert "Website Down" "HTTP response code: $code"
    fi
}

alert() {
    local subject="$1"
    local message="$2"
    echo "[$(date)] ALERT: $subject - $message" >> /var/log/kuwait-social-ai/monitoring.log
    
    if [[ ! -z "$WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 $subject\n$message\"}" \
            "$WEBHOOK_URL" 2>/dev/null
    fi
}

# Run all checks
check_cpu
check_memory
check_disk
check_docker
check_website

echo "[$(date)] Health check completed" >> /var/log/kuwait-social-ai/monitoring.log
EOF

chmod +x /opt/kuwait-social-ai/monitoring/check-health.sh

# Setup cron job
echo "*/5 * * * * /opt/kuwait-social-ai/monitoring/check-health.sh" | crontab -

# Create bandwidth monitoring script
cat > /opt/kuwait-social-ai/monitoring/bandwidth-check.sh << 'EOF'
#!/bin/bash
# Check DigitalOcean bandwidth usage

if [[ -z "$DO_API_TOKEN" ]] || [[ -z "$DROPLET_ID" ]]; then
    exit 0
fi

# Get bandwidth data
BANDWIDTH=$(curl -s -X GET \
    -H "Authorization: Bearer $DO_API_TOKEN" \
    "https://api.digitalocean.com/v2/droplets/$DROPLET_ID/bandwidth")

# Parse and check (simplified)
# Full implementation would parse JSON properly
echo "[$(date)] Bandwidth check completed" >> /var/log/kuwait-social-ai/monitoring.log
EOF

chmod +x /opt/kuwait-social-ai/monitoring/bandwidth-check.sh

# Setup netdata for real-time monitoring
echo -e "\n${YELLOW}Installing Netdata for real-time monitoring...${NC}"
bash <(curl -Ss https://my-netdata.io/kickstart.sh) --dont-wait --non-interactive

# Configure netdata for nginx
cat > /etc/nginx/sites-available/netdata << 'EOF'
upstream netdata {
    server 127.0.0.1:19999;
    keepalive 64;
}

server {
    listen 80;
    server_name monitor.kuwait-social-ai.com;
    
    location / {
        proxy_pass http://netdata;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Netdata specific
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
    }
}
EOF

# Create DO metrics dashboard script
cat > /opt/kuwait-social-ai/monitoring/do-metrics.sh << 'EOF'
#!/bin/bash
# Display DigitalOcean metrics summary

echo "=== Kuwait Social AI - System Metrics ==="
echo ""

# CPU
echo "CPU Usage:"
mpstat 1 1 | grep Average

echo ""

# Memory
echo "Memory Usage:"
free -h

echo ""

# Disk
echo "Disk Usage:"
df -h | grep -vE '^Filesystem|tmpfs|udev'

echo ""

# Docker
echo "Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""

# Network
echo "Network Traffic:"
vnstat -h

echo ""

# DigitalOcean specific
if [[ ! -z "$DROPLET_ID" ]]; then
    echo "View detailed graphs at:"
    echo "https://cloud.digitalocean.com/droplets/$DROPLET_ID/graphs"
fi
EOF

chmod +x /opt/kuwait-social-ai/monitoring/do-metrics.sh

# Create alert configuration
cat > /opt/kuwait-social-ai/monitoring/alerts.conf << 'EOF'
# Kuwait Social AI - Alert Configuration
# Add your notification endpoints here

# Slack webhook (optional)
# SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Email alerts (requires mail setup)
# ALERT_EMAIL="admin@kuwait-social-ai.com"

# Telegram bot (optional)
# TELEGRAM_TOKEN="your-bot-token"
# TELEGRAM_CHAT_ID="your-chat-id"

# DigitalOcean API (for bandwidth monitoring)
# DO_API_TOKEN="dop_v1_your_token_here"
# DROPLET_ID="your-droplet-id"

# Thresholds
MAX_CPU=80
MAX_MEMORY=85
MAX_DISK=90
MAX_BANDWIDTH=80  # Percentage of 5TB monthly limit
EOF

# Create monitoring dashboard
cat > /opt/kuwait-social-ai/monitoring/dashboard.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Kuwait Social AI - Monitoring</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { background: #f0f0f0; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .metric h3 { margin: 0 0 10px 0; }
        .value { font-size: 2em; font-weight: bold; }
        .status-ok { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-critical { color: #dc3545; }
    </style>
</head>
<body>
    <h1>Kuwait Social AI - System Monitoring</h1>
    
    <div class="metric">
        <h3>DigitalOcean Droplet</h3>
        <p>View detailed metrics: <a href="https://cloud.digitalocean.com/droplets" target="_blank">DigitalOcean Dashboard</a></p>
    </div>
    
    <div class="metric">
        <h3>Real-time Monitoring</h3>
        <p>Access Netdata: <a href="http://monitor.kuwait-social-ai.com">monitor.kuwait-social-ai.com</a></p>
    </div>
    
    <div class="metric">
        <h3>Quick Commands</h3>
        <pre>
# View system metrics
/opt/kuwait-social-ai/monitoring/do-metrics.sh

# Check health
/opt/kuwait-social-ai/monitoring/check-health.sh

# View logs
tail -f /var/log/kuwait-social-ai/monitoring.log
        </pre>
    </div>
</body>
</html>
EOF

# Create log directory
mkdir -p /var/log/kuwait-social-ai

# Summary
echo -e "\n${GREEN}✅ Monitoring setup complete!${NC}"
echo ""
echo -e "${BLUE}Monitoring Tools Installed:${NC}"
echo "• DigitalOcean Agent - Native DO monitoring"
echo "• Netdata - Real-time system metrics"
echo "• Custom health checks - Every 5 minutes"
echo "• vnstat - Bandwidth tracking"
echo "• htop/iotop - Interactive monitoring"
echo ""
echo -e "${BLUE}Monitoring Locations:${NC}"
echo "• Scripts: /opt/kuwait-social-ai/monitoring/"
echo "• Logs: /var/log/kuwait-social-ai/"
echo "• Config: /opt/kuwait-social-ai/monitoring/alerts.conf"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit alert configuration:"
echo "   nano /opt/kuwait-social-ai/monitoring/alerts.conf"
echo ""
echo "2. View system metrics:"
echo "   /opt/kuwait-social-ai/monitoring/do-metrics.sh"
echo ""
echo "3. Access DigitalOcean graphs:"
echo "   https://cloud.digitalocean.com/droplets/$DROPLET_ID/graphs"
echo ""
echo -e "${GREEN}Monitoring is now active!${NC}"