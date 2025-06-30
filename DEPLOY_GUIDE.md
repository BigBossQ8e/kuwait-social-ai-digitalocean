# Kuwait Social AI - DigitalOcean Deployment Guide

## 🔧 Important: CORS Configuration

Before deploying, ensure your CORS settings are properly configured:
- Run `./setup.sh` and provide your domain name when prompted
- This will automatically set the `CORS_ORIGINS` environment variable
- See `CORS_SETUP.md` for detailed CORS configuration instructions

## Prerequisites
- DigitalOcean account
- Domain name (optional but recommended)
- GitHub account (for App Platform deployment)

## Deployment Options

### Option 1: DigitalOcean App Platform (Easiest)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial deployment"
   git remote add origin https://github.com/YOUR_USERNAME/kuwait-social-ai.git
   git push -u origin main
   ```

2. **Create App on DigitalOcean**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"
   - Select your GitHub repository
   - Configure components:

   **Backend Component:**
   - Source Directory: `/backend`
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn --bind :$PORT wsgi:app`
   - Environment Variables: Add from `.env.example`
   - HTTP Port: 5000

   **Frontend Component:**
   - Source Directory: `/frontend-react`
   - Build Command: `npm install && npm run build`
   - Output Directory: `dist`
   - Environment Variables:
     ```
     VITE_API_URL=${APP_URL}/api
     ```

3. **Deploy**
   - Click "Next" through configuration
   - Select instance size (Basic $5/month works for testing)
   - Click "Create Resources"

### Option 2: Docker Compose on Droplet

1. **Create Droplet**
   - Ubuntu 22.04 LTS
   - At least 2GB RAM
   - Select datacenter region

2. **SSH and Deploy**
   ```bash
   # SSH into droplet
   ssh root@your-droplet-ip

   # Clone repository
   git clone https://github.com/YOUR_USERNAME/kuwait-social-ai.git
   cd kuwait-social-ai

   # Copy and edit environment file
   cp .env.example .env
   nano .env  # Edit with your values

   # Run with Docker Compose
   docker-compose up -d

   # Check status
   docker-compose ps
   docker-compose logs -f
   ```

### Option 3: Manual Deployment on Droplet

1. **Run the deployment script**
   ```bash
   ssh root@your-droplet-ip
   git clone https://github.com/YOUR_USERNAME/kuwait-social-ai.git
   cd kuwait-social-ai
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Configure environment**
   ```bash
   cd backend
   nano .env  # Add your configuration
   sudo systemctl restart kuwait-social-backend
   ```

## Post-Deployment Steps

### 1. Setup Domain (Optional)
- Add A record pointing to your server IP
- Update nginx configuration with your domain
- Install SSL certificate:
  ```bash
  sudo certbot --nginx -d yourdomain.com
  ```

### 2. Configure Backend
- Update `.env` with production values
- Set strong SECRET_KEY and JWT_SECRET_KEY
- Add your OpenAI API key
- Configure database URL if using external database

### 3. Database Setup
```bash
cd backend
source venv/bin/activate
flask db upgrade
deactivate
```

### 4. Create Admin User
```bash
cd backend
source venv/bin/activate
flask shell
>>> from models import User, db
>>> admin = User(email='admin@example.com', role='admin')
>>> admin.set_password('secure-password')
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()
```

## Monitoring

### Check Service Status
```bash
# Backend
sudo systemctl status kuwait-social-backend
sudo journalctl -u kuwait-social-backend -f

# Nginx
sudo systemctl status nginx
tail -f /var/log/nginx/access.log

# Docker (if using)
docker-compose ps
docker-compose logs -f
```

### Performance Monitoring
- Use DigitalOcean's built-in monitoring
- Set up alerts for CPU/Memory usage
- Monitor application logs

## Troubleshooting

### Backend not starting
```bash
# Check logs
sudo journalctl -u kuwait-social-backend -n 50

# Test manually
cd backend
source venv/bin/activate
python wsgi.py
```

### Frontend not loading
```bash
# Check nginx
sudo nginx -t
sudo systemctl restart nginx

# Check file permissions
ls -la /usr/share/nginx/html
```

### Database connection issues
```bash
# Test PostgreSQL
sudo -u postgres psql -d kuwait_social

# Check connection string in .env
echo $DATABASE_URL
```

## Security Checklist
- [ ] Changed all default passwords
- [ ] Updated SECRET_KEY and JWT_SECRET_KEY
- [ ] Enabled firewall (ufw)
- [ ] SSL certificate installed
- [ ] Regular security updates scheduled
- [ ] Backup strategy in place

## Backup Strategy
```bash
# Database backup
pg_dump kuwait_social > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf kuwait-social-backup-$(date +%Y%m%d).tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  .
```

## Support
- Check logs first
- DigitalOcean community tutorials
- Open an issue in the repository