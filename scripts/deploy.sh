#!/bin/bash
#
# Kuwait Social AI - DigitalOcean Production Deployment
# Deploys the complete platform on DigitalOcean
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REGION="fra1"  # Frankfurt (best for Kuwait)
SIZE="s-4vcpu-8gb"  # Recommended size
IMAGE="ubuntu-22-04-x64"
DROPLET_NAME="kuwait-social-ai-$(date +%s)"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║         Kuwait Social AI - DigitalOcean Deploy        ║"
    echo "║                  Production Setup                     ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

validate_input() {
    local input=$1
    local type=$2
    
    case $type in
        "domain")
            if [[ ! "$input" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                echo -e "${RED}Invalid domain format${NC}"
                exit 1
            fi
            ;;
        "email")
            if [[ ! "$input" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
                echo -e "${RED}Invalid email format${NC}"
                exit 1
            fi
            ;;
        "ip")
            if [[ ! "$input" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
                echo -e "${RED}Invalid IP format${NC}"
                exit 1
            fi
            ;;
    esac
}

generate_secure_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Print banner
print_banner

# Check doctl
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}doctl CLI not installed. Please install it first:${NC}"
    echo "macOS: brew install doctl"
    echo "Linux: snap install doctl"
    echo "Manual: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check authentication
if ! doctl auth list &> /dev/null; then
    echo -e "${RED}Not authenticated. Run: doctl auth init${NC}"
    exit 1
fi

# Get user input
echo -e "${YELLOW}Please provide the following information:${NC}\n"

read -p "Domain name (e.g., kuwait-social-ai.com): " DOMAIN
validate_input "$DOMAIN" "domain"

read -p "Admin email: " ADMIN_EMAIL
validate_input "$ADMIN_EMAIL" "email"

read -p "Enable automated backups? (+$9.60/month) (Y/n): " ENABLE_BACKUPS
ENABLE_BACKUPS=${ENABLE_BACKUPS:-Y}

# Get SSH access IP
echo -e "\n${YELLOW}Configuring secure SSH access...${NC}"
MY_IP=$(curl -s https://api.ipify.org)
validate_input "$MY_IP" "ip"
echo "Your current IP: $MY_IP"

read -p "Use this IP for SSH access? (Y/n) or enter different IP: " SSH_RESPONSE
if [[ "$SSH_RESPONSE" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    SSH_IP="$SSH_RESPONSE"
    validate_input "$SSH_IP" "ip"
else
    SSH_IP="$MY_IP"
fi

# Generate passwords
echo -e "\n${YELLOW}Generating secure passwords...${NC}"
ADMIN_PASSWORD=$(generate_secure_password)
DB_PASSWORD=$(generate_secure_password)
REDIS_PASSWORD=$(generate_secure_password)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Configuration summary
echo -e "\n${BLUE}Configuration Summary:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Region: Frankfurt (fra1)"
echo "Droplet: 4 vCPU, 8GB RAM, 160GB SSD"
echo "Domain: $DOMAIN"
echo "Admin Email: $ADMIN_EMAIL"
echo "SSH Access: Limited to $SSH_IP"
echo "Backups: $([[ $ENABLE_BACKUPS =~ ^[Yy]$ ]] && echo "Enabled" || echo "Disabled")"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Create SSH key
echo -e "\n${YELLOW}Creating SSH key...${NC}"
SSH_KEY_NAME="kuwait-social-ai-$(date +%s)"
ssh-keygen -t ed25519 -f ~/.ssh/$SSH_KEY_NAME -N "" -C "kuwait-social-ai" >/dev/null 2>&1

# Upload SSH key to DO
SSH_KEY_ID=$(doctl compute ssh-key import $SSH_KEY_NAME --public-key-file ~/.ssh/$SSH_KEY_NAME.pub --format ID --no-header 2>/dev/null || \
    doctl compute ssh-key list --format Name,ID --no-header | grep "^$SSH_KEY_NAME" | awk '{print $2}')

echo -e "${GREEN}SSH key created: $SSH_KEY_NAME${NC}"

# Create cloud-init script
echo -e "\n${YELLOW}Preparing server configuration...${NC}"
cat > /tmp/cloud-init.yaml << EOF
#cloud-config
package_update: true
package_upgrade: true

users:
  - name: appuser
    groups: [docker, sudo]
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh_authorized_keys:
      - $(cat ~/.ssh/$SSH_KEY_NAME.pub)

packages:
  - docker.io
  - docker-compose
  - git
  - nginx
  - certbot
  - python3-certbot-nginx
  - fail2ban
  - ufw
  - unattended-upgrades
  - htop
  - ncdu
  - net-tools

write_files:
  - path: /opt/kuwait-social-ai/.env
    permissions: '0600'
    owner: appuser:appuser
    content: |
      # Domain Configuration
      DOMAIN=$DOMAIN
      ADMIN_EMAIL=$ADMIN_EMAIL
      
      # Security Keys
      SECRET_KEY=$SECRET_KEY
      JWT_SECRET_KEY=$JWT_SECRET
      
      # Database Configuration
      DB_USER=kuwait_user
      DB_PASSWORD=$DB_PASSWORD
      DATABASE_URL=postgresql://kuwait_user:$DB_PASSWORD@postgres:5432/kuwait_social_ai
      
      # Redis Configuration
      REDIS_PASSWORD=$REDIS_PASSWORD
      REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0
      
      # Admin Credentials
      ADMIN_USERNAME=admin@kuwait-social-ai.com
      ADMIN_PASSWORD=$ADMIN_PASSWORD
      
      # Security Settings
      SECURE_HEADERS_ENABLED=true
      FORCE_HTTPS=true
      SESSION_COOKIE_SECURE=true
      SESSION_COOKIE_HTTPONLY=true
      SESSION_COOKIE_SAMESITE=Lax
      CORS_ORIGINS=https://$DOMAIN

runcmd:
  # Configure firewall
  - ufw --force reset
  - ufw default deny incoming
  - ufw default allow outgoing
  - ufw allow from $SSH_IP to any port 22
  - ufw allow 80/tcp
  - ufw allow 443/tcp
  - ufw --force enable
  
  # Configure fail2ban
  - systemctl enable fail2ban
  - systemctl start fail2ban
  
  # Setup Docker
  - systemctl enable docker
  - systemctl start docker
  
  # Clone repository
  - mkdir -p /opt/kuwait-social-ai
  - chown -R appuser:appuser /opt/kuwait-social-ai
  
  # Create docker-compose.yml
  - |
    cat > /opt/kuwait-social-ai/docker-compose.yml << 'EODC'
    version: '3.8'
    
    services:
      postgres:
        image: postgres:15-alpine
        restart: unless-stopped
        environment:
          POSTGRES_DB: kuwait_social_ai
          POSTGRES_USER: kuwait_user
          POSTGRES_PASSWORD: \${DB_PASSWORD}
        volumes:
          - postgres_data:/var/lib/postgresql/data
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U kuwait_user"]
          interval: 10s
          timeout: 5s
          retries: 5
    
      redis:
        image: redis:7-alpine
        restart: unless-stopped
        command: redis-server --requirepass \${REDIS_PASSWORD}
        volumes:
          - redis_data:/data
        healthcheck:
          test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
          interval: 10s
          timeout: 5s
          retries: 5
    
      backend:
        image: kuwait-social-ai/backend:latest
        restart: unless-stopped
        env_file: .env
        depends_on:
          postgres:
            condition: service_healthy
          redis:
            condition: service_healthy
        ports:
          - "127.0.0.1:5000:5000"
        volumes:
          - ./uploads:/app/uploads
          - ./logs:/app/logs
    
    volumes:
      postgres_data:
      redis_data:
    EODC
  
  # Start services
  - cd /opt/kuwait-social-ai && docker-compose pull
  - cd /opt/kuwait-social-ai && docker-compose up -d
  
  # Configure Nginx
  - |
    cat > /etc/nginx/sites-available/kuwait-social-ai << 'EONGINX'
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
    EONGINX
  
  - ln -sf /etc/nginx/sites-available/kuwait-social-ai /etc/nginx/sites-enabled/
  - rm -f /etc/nginx/sites-enabled/default
  - nginx -t && systemctl reload nginx
  
  # Install DigitalOcean monitoring
  - curl -sSL https://repos.insights.digitalocean.com/install.sh | bash
EOF

# Create droplet
echo -e "\n${YELLOW}Creating DigitalOcean droplet...${NC}"
DROPLET_CMD="doctl compute droplet create $DROPLET_NAME \
    --size $SIZE \
    --image $IMAGE \
    --region $REGION \
    --ssh-keys $SSH_KEY_ID \
    --user-data-file /tmp/cloud-init.yaml \
    --format ID,Name,PublicIPv4 \
    --no-header \
    --wait"

if [[ $ENABLE_BACKUPS =~ ^[Yy]$ ]]; then
    DROPLET_CMD="$DROPLET_CMD --enable-backups"
fi

# Execute creation
DROPLET_INFO=$($DROPLET_CMD)
DROPLET_ID=$(echo "$DROPLET_INFO" | awk '{print $1}')
DROPLET_IP=$(echo "$DROPLET_INFO" | awk '{print $3}')

echo -e "${GREEN}✓ Droplet created successfully!${NC}"

# Create floating IP
echo -e "\n${YELLOW}Allocating floating IP...${NC}"
FLOATING_IP=$(doctl compute floating-ip create --region $REGION --format IP --no-header)
doctl compute floating-ip-action assign $FLOATING_IP $DROPLET_ID --wait
echo -e "${GREEN}✓ Floating IP allocated: $FLOATING_IP${NC}"

# Setup firewall
echo -e "\n${YELLOW}Configuring cloud firewall...${NC}"
FIREWALL_NAME="kuwait-social-ai-fw-$(date +%s)"
doctl compute firewall create \
    --name $FIREWALL_NAME \
    --inbound-rules "protocol:tcp,ports:22,sources:address:$SSH_IP/32" \
    --inbound-rules "protocol:tcp,ports:80,sources:address:0.0.0.0/0,sources:address:::/0" \
    --inbound-rules "protocol:tcp,ports:443,sources:address:0.0.0.0/0,sources:address:::/0" \
    --outbound-rules "protocol:tcp,ports:all,destinations:address:0.0.0.0/0,destinations:address:::/0" \
    --outbound-rules "protocol:udp,ports:all,destinations:address:0.0.0.0/0,destinations:address:::/0" \
    --droplet-ids $DROPLET_ID >/dev/null

echo -e "${GREEN}✓ Firewall configured${NC}"

# Save credentials
CREDS_FILE="$HOME/.kuwait-social-ai-do-$(date +%Y%m%d-%H%M%S).txt"
cat > "$CREDS_FILE" << EOC
Kuwait Social AI - DigitalOcean Deployment
Generated: $(date)
==========================================

DROPLET DETAILS
---------------
Droplet ID: $DROPLET_ID
Droplet IP: $DROPLET_IP  
Floating IP: $FLOATING_IP
SSH Key: ~/.ssh/$SSH_KEY_NAME
Region: Frankfurt (fra1)

ACCESS INFORMATION
------------------
SSH: ssh -i ~/.ssh/$SSH_KEY_NAME appuser@$FLOATING_IP
Web: https://$DOMAIN (after DNS setup)

CREDENTIALS
-----------
Admin Email: $ADMIN_EMAIL
Admin Password: $ADMIN_PASSWORD
Database Password: $DB_PASSWORD
Redis Password: $REDIS_PASSWORD

SECURITY NOTES
--------------
- SSH restricted to: $SSH_IP
- Automatic updates enabled
- Fail2ban configured
- Cloud firewall active
- Daily backups: $([[ $ENABLE_BACKUPS =~ ^[Yy]$ ]] && echo "Enabled" || echo "Disabled")

DIGITALOCEAN LINKS
------------------
Droplet: https://cloud.digitalocean.com/droplets/$DROPLET_ID
Graphs: https://cloud.digitalocean.com/droplets/$DROPLET_ID/graphs
Backups: https://cloud.digitalocean.com/droplets/$DROPLET_ID/backups
Firewall: https://cloud.digitalocean.com/networking/firewalls

IMPORTANT: Save this file securely and delete after storing passwords!
EOC

chmod 600 "$CREDS_FILE"

# Clean up
rm -f /tmp/cloud-init.yaml

# Print summary
echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Droplet Information:${NC}"
echo "ID: $DROPLET_ID"
echo "IP: $DROPLET_IP"
echo "Floating IP: $FLOATING_IP"
echo ""

echo -e "${BLUE}Security Features:${NC}"
echo "✓ SSH restricted to $SSH_IP only"
echo "✓ Automated security updates"
echo "✓ Fail2ban protection enabled"
echo "✓ Cloud firewall configured"
echo "✓ Secure passwords generated"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update DNS records:"
echo "   A @ → $FLOATING_IP"
echo "   A www → $FLOATING_IP"
echo ""
echo "2. Wait 5 minutes for setup to complete"
echo ""
echo "3. SSH into server:"
echo "   ssh -i ~/.ssh/$SSH_KEY_NAME appuser@$FLOATING_IP"
echo ""
echo "4. Setup SSL certificate:"
echo "   sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "5. View credentials:"
echo "   cat $CREDS_FILE"
echo ""

echo -e "${BLUE}DigitalOcean Dashboard:${NC}"
echo "https://cloud.digitalocean.com/droplets/$DROPLET_ID"
echo ""

echo -e "${GREEN}Monthly Cost: \$$([[ $ENABLE_BACKUPS =~ ^[Yy]$ ]] && echo "57.60" || echo "48.00") ($(  [[ $ENABLE_BACKUPS =~ ^[Yy]$ ]] && echo "18" || echo "15") KWD)${NC}"
echo ""

echo -e "${RED}⚠️  IMPORTANT: Save credentials from:${NC}"
echo "$CREDS_FILE"