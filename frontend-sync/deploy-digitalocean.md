# DigitalOcean Deployment Guide

## Deployment Options

### Option 1: DigitalOcean App Platform (Recommended for simplicity)

1. **Prepare your repository**
   ```bash
   # Build the project locally to test
   npm run build
   
   # Commit all changes
   git add .
   git commit -m "Prepare for DigitalOcean deployment"
   git push origin main
   ```

2. **Create App on DigitalOcean**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"
   - Connect your GitHub repository
   - Select the branch (usually `main`)
   - DigitalOcean will auto-detect Node.js app

3. **Configure Build Settings**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Environment Variables:
     ```
     VITE_API_URL = https://your-backend-url.com/api
     ```

4. **Deploy**
   - Review and click "Create Resources"
   - Wait for deployment to complete

### Option 2: DigitalOcean Droplet (More control)

1. **Create a Droplet**
   - Choose Ubuntu 22.04 LTS
   - Select appropriate size (minimum 1GB RAM)
   - Add SSH keys

2. **Connect to Droplet**
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Install Dependencies**
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Node.js 18
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   apt install -y nodejs
   
   # Install nginx
   apt install -y nginx
   
   # Install PM2 (optional, for running backend)
   npm install -g pm2
   ```

4. **Deploy Frontend**
   ```bash
   # Clone your repository
   git clone https://github.com/your-username/your-repo.git
   cd your-repo/application/frontend-react
   
   # Install dependencies and build
   npm install
   npm run build
   
   # Copy build to nginx
   cp -r dist/* /var/www/html/
   
   # Configure nginx
   cp nginx.digitalocean.conf /etc/nginx/sites-available/default
   
   # Restart nginx
   systemctl restart nginx
   ```

5. **Configure Firewall**
   ```bash
   ufw allow 'Nginx Full'
   ufw allow OpenSSH
   ufw enable
   ```

### Option 3: Using Docker on Droplet

1. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **Build and Run**
   ```bash
   # Build the Docker image
   docker build -f Dockerfile.digitalocean -t kuwait-social-frontend .
   
   # Run the container
   docker run -d -p 80:8080 --name frontend kuwait-social-frontend
   ```

## Environment Variables

Create a `.env.production` file with:
```env
VITE_API_URL=https://your-api-domain.com/api
VITE_APP_NAME=Kuwait Social AI
```

## SSL Certificate (for custom domain)

1. **Install Certbot**
   ```bash
   apt install certbot python3-certbot-nginx
   ```

2. **Get Certificate**
   ```bash
   certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

## Important Notes

1. **API URL**: Update `VITE_API_URL` to point to your backend API
2. **Port Configuration**: App Platform uses port 8080, Droplets typically use 80/443
3. **CORS**: Ensure your backend allows requests from your frontend domain
4. **Build Size**: The build folder should be under 500MB for App Platform

## Monitoring

- Use DigitalOcean's built-in monitoring
- Set up alerts for downtime
- Monitor nginx logs: `tail -f /var/log/nginx/access.log`

## Troubleshooting

1. **Build Fails**: Check Node version (should be 18+)
2. **API Connection**: Verify CORS settings and API URL
3. **Static Files Not Loading**: Check nginx configuration
4. **Memory Issues**: Increase Droplet size or optimize build