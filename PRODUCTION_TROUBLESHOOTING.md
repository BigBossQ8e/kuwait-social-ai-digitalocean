# Production Troubleshooting Guide - kwtsocial.com

## Current Issues
- https://kwtsocial.com/admin-panel/index.html - Error 500
- https://kwtsocial.com/login - Error 500

## Root Causes

### 1. Nginx Configuration Issues
The current nginx configuration may not properly route to the static files or backend services.

### 2. Backend Service Not Running
The Flask/Gunicorn backend service may not be running on port 5000.

### 3. File Permissions
The web server may not have permission to read the static files.

## Quick Fixes

### Step 1: Check Services Status
```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Check if backend is running
sudo systemctl status kuwait-social-backend

# Check if nginx is running
sudo systemctl status nginx

# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if Redis is running
sudo systemctl status redis
```

### Step 2: Check Logs
```bash
# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check backend logs
sudo journalctl -u kuwait-social-backend -f

# Check application logs
tail -f /var/www/kuwait-social-ai/backend/logs/kuwait-social-ai.log
```

### Step 3: Verify File Structure
```bash
# Check if files exist
ls -la /var/www/html/admin-panel/
ls -la /var/www/html/client-dashboard/
ls -la /var/www/html/frontend-react/build/
```

### Step 4: Fix Permissions
```bash
# Set correct ownership
sudo chown -R www-data:www-data /var/www/html/

# Set correct permissions
sudo chmod -R 755 /var/www/html/
```

### Step 5: Update Nginx Configuration
```bash
# Backup current config
sudo cp /etc/nginx/sites-available/kwtsocial.com /etc/nginx/sites-available/kwtsocial.com.backup

# Copy new config
sudo cp nginx-production-fix.conf /etc/nginx/sites-available/kwtsocial.com

# Test nginx config
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### Step 6: Start/Restart Backend Service
```bash
# If using systemd service
sudo systemctl restart kuwait-social-backend

# OR if using Docker
cd /var/www/kuwait-social-ai
sudo docker-compose restart backend

# OR if running manually
cd /var/www/kuwait-social-ai/backend
source venv/bin/activate
gunicorn --config gunicorn_config.py wsgi:application
```

## File Structure Required

```
/var/www/html/
├── admin-panel/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── client-dashboard/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── login/
│   └── index.html
├── signup/
│   └── index.html
└── frontend-react/
    └── build/
        ├── index.html
        ├── static/
        └── ...
```

## Environment Variables Check

```bash
# Check if .env file exists
cat /var/www/kuwait-social-ai/backend/.env

# Required variables:
DATABASE_URL=postgresql://user:pass@localhost/kuwait_social_ai
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
FLASK_ENV=production
```

## Quick Deploy Script

```bash
#!/bin/bash
# Save as fix-production.sh

# Update code
cd /var/www/kuwait-social-ai
git pull origin main

# Build frontend
cd frontend-react
npm install
npm run build
sudo cp -r build/* /var/www/html/frontend-react/build/

# Copy admin panel
sudo cp -r ../admin-panel/* /var/www/html/admin-panel/

# Copy client dashboard
sudo cp -r ../client-dashboard/* /var/www/html/client-dashboard/

# Fix permissions
sudo chown -R www-data:www-data /var/www/html/
sudo chmod -R 755 /var/www/html/

# Restart services
sudo systemctl restart kuwait-social-backend
sudo systemctl reload nginx

echo "Deployment complete!"
```

## Testing After Fix

```bash
# Test backend API
curl https://kwtsocial.com/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'

# Test static files
curl -I https://kwtsocial.com/admin-panel/index.html
curl -I https://kwtsocial.com/dashboard/index.html
```

## If Still Not Working

1. **Check DNS**: Ensure kwtsocial.com points to your server
2. **Check SSL**: Ensure SSL certificates are valid
3. **Check Firewall**: Ensure ports 80 and 443 are open
4. **Check SELinux**: If enabled, may block nginx from proxying

```bash
# Disable SELinux temporarily (if applicable)
sudo setenforce 0

# Check firewall
sudo ufw status
```