# Kuwait Social AI - DigitalOcean Deployment Guide

## 📋 Prerequisites

1. **DigitalOcean Account**
   - Sign up at https://www.digitalocean.com
   - Add payment method
   - Use referral link for $200 credit

2. **Domain Name**
   - Register domain (e.g., kuwait-social-ai.com)
   - Have DNS access ready

3. **Local Tools**
   - Install `doctl` CLI
   - SSH client
   - Terminal access

## 🚀 Deployment Steps

### Step 1: Install DigitalOcean CLI

```bash
# macOS
brew install doctl

# Linux
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
tar xf doctl-1.98.1-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin

# Windows
# Download from: https://github.com/digitalocean/doctl/releases
```

### Step 2: Authenticate

```bash
# Create API token at: https://cloud.digitalocean.com/account/api/tokens
doctl auth init

# Verify authentication
doctl account get
```

### Step 3: Run Deployment Script

```bash
# Clone this repository
git clone <repository-url>
cd digitalocean-hosting

# Make scripts executable
chmod +x scripts/*.sh

# Run deployment
./scripts/deploy.sh
```

### Step 4: Configure DNS

After deployment, update your domain's DNS:

1. Go to your domain registrar
2. Add these records:
   ```
   Type  Name    Value
   A     @       YOUR_FLOATING_IP
   A     www     YOUR_FLOATING_IP
   ```
3. Wait 5-30 minutes for propagation

### Step 5: Setup SSL Certificate

```bash
# SSH into your server
ssh -i ~/.ssh/kuwait-social-ai-KEY appuser@YOUR_FLOATING_IP

# Run SSL setup
sudo ./scripts/ssl-setup.sh
```

### Step 6: Configure Application

1. **Add API Keys**
   ```bash
   sudo nano /opt/kuwait-social-ai/.env
   ```

2. **Add your API keys:**
   - Instagram API credentials
   - Snapchat API credentials
   - OpenAI API key
   - MyFatoorah API key
   - SMTP credentials

3. **Restart services**
   ```bash
   cd /opt/kuwait-social-ai
   docker-compose restart
   ```

## 🔧 Post-Deployment Setup

### Enable Backups

```bash
# If you didn't enable during deployment
doctl compute droplet-action enable-backups YOUR_DROPLET_ID
```

### Setup Monitoring

```bash
# SSH into server
ssh -i ~/.ssh/kuwait-social-ai-KEY appuser@YOUR_FLOATING_IP

# Run monitoring setup
sudo ./scripts/setup-monitoring.sh

# Configure alerts
sudo nano /opt/kuwait-social-ai/monitoring/alerts.conf
```

### Configure DigitalOcean Spaces (Optional)

For off-site backups:

1. Create a Space: https://cloud.digitalocean.com/spaces
2. Generate access keys
3. Update `.env` with Space credentials
4. Test backup: `./scripts/backup.sh`

## 📊 Accessing Your Platform

### Web Access
- Main site: `https://your-domain.com`
- Owner portal: `https://your-domain.com/owner`
- Admin portal: `https://your-domain.com/admin`
- Client portal: `https://your-domain.com/app`

### SSH Access
```bash
ssh -i ~/.ssh/kuwait-social-ai-KEY appuser@YOUR_FLOATING_IP
```

### Monitoring
- DigitalOcean graphs: https://cloud.digitalocean.com/droplets/YOUR_DROPLET_ID/graphs
- Custom monitoring: `do-monitor`
- Logs: `docker-compose logs -f`

## 🛠️ Maintenance

### Daily Tasks
- Check monitoring alerts
- Review backup status
- Monitor bandwidth usage

### Weekly Tasks
```bash
# Run maintenance menu
sudo ./scripts/maintenance.sh

# Check for updates
docker-compose pull

# Review security
fail2ban-client status
```

### Monthly Tasks
- Review DigitalOcean invoices
- Check SSL renewal
- Audit user access
- Performance review

## 🚨 Troubleshooting

### Site Not Loading
```bash
# Check services
docker-compose ps

# Check nginx
sudo nginx -t
sudo systemctl status nginx

# Check logs
docker-compose logs backend
```

### Database Issues
```bash
# Connect to database
docker exec -it kuwait_social_ai_postgres psql -U kuwait_user

# Check connections
SELECT * FROM pg_stat_activity;

# Run maintenance
VACUUM ANALYZE;
```

### High Resource Usage
```bash
# Check resources
htop

# Check disk
df -h

# Check docker
docker stats

# Clear cache
docker exec kuwait_social_ai_redis redis-cli FLUSHDB
```

### SSL Certificate Issues
```bash
# Test renewal
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal

# Check certificate
sudo certbot certificates
```

## 🔒 Security Best Practices

1. **Keep software updated**
   ```bash
   sudo apt update && sudo apt upgrade
   docker-compose pull
   ```

2. **Monitor access logs**
   ```bash
   tail -f /var/log/nginx/access.log
   fail2ban-client status sshd
   ```

3. **Regular backups**
   ```bash
   # Manual backup
   ./scripts/backup.sh
   
   # Verify snapshots
   doctl compute snapshot list
   ```

4. **Firewall management**
   ```bash
   # Check rules
   sudo ufw status numbered
   
   # Add trusted IP
   sudo ufw allow from YOUR_IP to any port 22
   ```

## 📈 Scaling

### Vertical Scaling (Resize Droplet)
```bash
# Power off
doctl compute droplet-action power-off YOUR_DROPLET_ID --wait

# Resize
doctl compute droplet-action resize YOUR_DROPLET_ID --size s-8vcpu-16gb --wait

# Power on
doctl compute droplet-action power-on YOUR_DROPLET_ID --wait
```

### Horizontal Scaling
1. Add load balancer
2. Create additional droplets
3. Configure shared storage
4. Setup database replication

## 💰 Cost Optimization

- **Monitor bandwidth**: Stay under 5TB/month
- **Use snapshots**: Instead of keeping many backups
- **Right-size droplet**: Start with s-4vcpu-8gb
- **Clean old data**: Regular maintenance

## 📞 Getting Help

- **DigitalOcean Support**: https://www.digitalocean.com/support/
- **Community**: https://www.digitalocean.com/community
- **Status Page**: https://status.digitalocean.com
- **Documentation**: https://docs.digitalocean.com