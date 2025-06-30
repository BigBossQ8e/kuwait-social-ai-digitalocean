#!/bin/bash
#
# Kuwait Social AI - SSL Certificate Setup
# Configures Let's Encrypt SSL for the domain
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Kuwait Social AI - SSL Setup${NC}\n"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Get domain from .env or ask
if [ -f /opt/kuwait-social-ai/.env ]; then
    source /opt/kuwait-social-ai/.env
fi

if [ -z "${DOMAIN:-}" ]; then
    read -p "Enter your domain name: " DOMAIN
fi

if [ -z "${ADMIN_EMAIL:-}" ]; then
    read -p "Enter admin email: " ADMIN_EMAIL
fi

echo -e "${YELLOW}Setting up SSL for: $DOMAIN${NC}\n"

# Update Nginx configuration for SSL
cat > /etc/nginx/sites-available/kuwait-social-ai << EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=api:10m rate=30r/s;

upstream backend {
    server 127.0.0.1:5000;
    keepalive 32;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration (will be added by certbot)
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    client_max_body_size 100M;
    
    # API endpoints
    location /api/ {
        limit_req zone=api burst=50 nodelay;
        
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    # Static files
    location /static/ {
        alias /opt/kuwait-social-ai/frontend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /uploads/ {
        alias /opt/kuwait-social-ai/uploads/;
        expires 7d;
        add_header Cache-Control "public";
        add_header X-Content-Type-Options "nosniff" always;
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://backend/health;
    }
    
    # Main app
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Create certbot webroot
mkdir -p /var/www/certbot

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx

# Get SSL certificate
echo -e "\n${YELLOW}Obtaining SSL certificate...${NC}"
certbot --nginx \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --non-interactive \
    --agree-tos \
    --email $ADMIN_EMAIL \
    --redirect \
    --expand

# Setup auto-renewal
echo -e "\n${YELLOW}Setting up auto-renewal...${NC}"
cat > /etc/cron.d/certbot-renewal << EOF
# Renew SSL certificates twice daily
0 0,12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# Test renewal
echo -e "\n${YELLOW}Testing renewal process...${NC}"
certbot renew --dry-run

# Create SSL monitoring script
cat > /opt/kuwait-social-ai/monitoring/check-ssl.sh << 'EOF'
#!/bin/bash
# Check SSL certificate expiry

DOMAIN="${1:-kuwait-social-ai.com}"
DAYS_WARNING=30

expiry_date=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2)

if [ -z "$expiry_date" ]; then
    echo "Could not check SSL certificate for $DOMAIN"
    exit 1
fi

expiry_epoch=$(date -d "$expiry_date" +%s)
current_epoch=$(date +%s)
days_left=$(( ($expiry_epoch - $current_epoch) / 86400 ))

echo "SSL certificate for $DOMAIN expires in $days_left days"

if [ $days_left -lt $DAYS_WARNING ]; then
    echo "WARNING: Certificate expiring soon!"
    # Send alert if configured
fi
EOF

chmod +x /opt/kuwait-social-ai/monitoring/check-ssl.sh

# Add to monitoring cron
echo "0 9 * * * /opt/kuwait-social-ai/monitoring/check-ssl.sh" >> /tmp/newcron
crontab -l | grep -v check-ssl >> /tmp/newcron || true
crontab /tmp/newcron
rm /tmp/newcron

# Summary
echo -e "\n${GREEN}✅ SSL Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓${NC} SSL certificate installed"
echo -e "${GREEN}✓${NC} Auto-renewal configured"
echo -e "${GREEN}✓${NC} Security headers enabled"
echo -e "${GREEN}✓${NC} HTTP→HTTPS redirect active"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}Your site is now available at:${NC}"
echo "https://$DOMAIN"
echo "https://www.$DOMAIN"
echo ""
echo -e "${YELLOW}SSL Certificate Info:${NC}"
certbot certificates | grep -A 3 "$DOMAIN"