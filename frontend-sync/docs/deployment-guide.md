# Deployment Guide - Kuwait Social AI Frontend

## 📋 Overview

This guide covers all deployment options for the Kuwait Social AI React frontend, from local development to production deployment.

## 🚀 Quick Start

### Development
```bash
# Clone and setup
git clone <repository>
cd frontend-react
npm install

# Start development server
npm run dev
# or
./deploy.sh dev
```

### Production (Docker)
```bash
# Build and start production container
./deploy.sh start

# Or deploy with custom settings
API_URL=https://api.yourdomain.com ./deploy.sh deploy-prod
```

## 🐳 Docker Deployment

### Single Container
```bash
# Build image
docker build -t kuwait-social-frontend .

# Run container
docker run -d \
  --name kuwait-social-frontend \
  -p 3000:80 \
  -e API_URL=http://your-backend:5000 \
  kuwait-social-frontend
```

### Docker Compose (Recommended)
```bash
# Start full stack
docker-compose up -d

# Production with profiles
docker-compose --profile production up -d
```

## 📝 Environment Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_URL` | Backend API URL | `http://localhost:5000` | Yes |
| `APP_ENV` | Environment | `production` | No |
| `APP_VERSION` | App version | `1.0.0` | No |

### Runtime Configuration
The app uses `window.APP_CONFIG` for runtime configuration:

```javascript
window.APP_CONFIG = {
  API_URL: "http://your-backend:5000",
  APP_ENV: "production",
  FEATURES: {
    PRAYER_TIMES: true,
    COMPETITOR_ANALYSIS: true,
    AI_CONTENT_GENERATION: true,
    ANALYTICS: true
  }
};
```

## 🔧 Build Configuration

### Vite Build Options
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', '@mui/material'],
          charts: ['chart.js', 'react-chartjs-2'],
        }
      }
    }
  }
});
```

### Production Optimizations
- Code splitting by route and vendor
- Asset compression and minification
- Tree shaking for unused code
- Bundle analysis available

## 🌐 Nginx Configuration

### Features
- **Gzip Compression** - Text assets compressed
- **Caching Headers** - Long-term caching for assets
- **Security Headers** - XSS, CSRF protection
- **API Proxy** - Backend API proxying
- **Rate Limiting** - API and auth endpoints
- **Health Checks** - `/health` endpoint
- **SPA Routing** - History API support

### SSL Configuration (Production)
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Your existing configuration
}
```

## ☁️ Cloud Deployment

### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t kuwait-social-frontend .
docker tag kuwait-social-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/kuwait-social-frontend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/kuwait-social-frontend:latest
```

### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/kuwait-social-frontend
gcloud run deploy --image gcr.io/PROJECT-ID/kuwait-social-frontend --platform managed
```

### Azure Container Instances
```bash
# Create resource group and deploy
az group create --name kuwait-social-rg --location eastus
az container create \
  --resource-group kuwait-social-rg \
  --name kuwait-social-frontend \
  --image kuwait-social-frontend \
  --dns-name-label kuwait-social \
  --ports 80
```

## 🔍 Monitoring & Health Checks

### Health Check Endpoint
```bash
curl http://localhost:3000/health
# Response: "healthy"
```

### Container Health
```bash
# Manual health check
./deploy.sh health

# Docker health check
docker inspect --format='{{.State.Health.Status}}' kuwait-social-frontend
```

### Monitoring Stack
- **Logs**: Nginx access/error logs
- **Metrics**: Container resource usage
- **APM**: Application performance monitoring
- **Alerts**: Health check failures

## 🛠️ Deployment Scripts

### deploy.sh Commands
```bash
./deploy.sh build         # Build Docker image
./deploy.sh start         # Start production container
./deploy.sh stop          # Stop container
./deploy.sh restart       # Restart container
./deploy.sh logs          # View logs
./deploy.sh health        # Health check
./deploy.sh clean         # Cleanup Docker artifacts
./deploy.sh backup        # Create backup
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Deploy Frontend
  run: |
    ./deploy.sh build
    ./deploy.sh deploy-prod
  env:
    API_URL: ${{ secrets.API_URL }}
```

## 🔐 Security Considerations

### Production Security
- Environment variables for sensitive data
- HTTPS only in production
- CSP headers configured
- Rate limiting enabled
- CORS properly configured
- No source maps in production

### Network Security
- Backend API on private network
- Database not publicly accessible
- Load balancer with SSL termination
- Firewall rules restricting access

## 📊 Performance

### Build Metrics
- **Initial Bundle**: ~800KB gzipped
- **Vendor Chunk**: ~400KB gzipped
- **App Chunk**: ~300KB gzipped
- **Build Time**: ~30 seconds

### Runtime Performance
- **First Contentful Paint**: <2s
- **Time to Interactive**: <3s
- **Lighthouse Score**: >90
- **Bundle Analysis**: Available via `npm run analyze`

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   ```bash
   # Check API_URL environment variable
   docker exec container-name env | grep API_URL
   
   # Test API connectivity
   docker exec container-name curl -f $API_URL/health
   ```

2. **Static Assets Not Loading**
   ```bash
   # Check nginx configuration
   docker exec container-name nginx -t
   
   # Check file permissions
   docker exec container-name ls -la /usr/share/nginx/html/
   ```

3. **Authentication Issues**
   ```bash
   # Check CORS configuration
   curl -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: X-Requested-With" \
        -X OPTIONS \
        http://your-api/auth/login
   ```

### Debugging
```bash
# Enable debug mode
docker run -e NODE_ENV=development kuwait-social-frontend

# Access container shell
docker exec -it kuwait-social-frontend sh

# View nginx error logs
docker logs kuwait-social-frontend
```

## 🔄 Updates & Rollbacks

### Zero-Downtime Updates
1. Build new image with version tag
2. Start new container on different port
3. Update load balancer to point to new container
4. Stop old container

### Rollback Strategy
```bash
# Tag current version
docker tag kuwait-social-frontend:latest kuwait-social-frontend:backup

# Rollback to previous version
docker run -d --name kuwait-social-frontend-new kuwait-social-frontend:previous-version

# Switch traffic
# Stop old container
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# Docker Swarm
version: '3.8'
services:
  frontend:
    image: kuwait-social-frontend
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
```

### Load Balancing
- Nginx upstream configuration
- AWS Application Load Balancer
- Google Cloud Load Balancer
- Azure Load Balancer

---

## 📞 Support

For deployment issues:
1. Check logs: `./deploy.sh logs`
2. Verify health: `./deploy.sh health`
3. Check configuration: Environment variables and nginx config
4. Review this documentation
5. Contact DevOps team with error details